#!/usr/bin/env python3
"""Driver OpenCode : lancer une session neuve, lire ses conversations dans `opencode.db`.

Même interface que `tools/drivers/claude.py`, qui la décrit.

LA SESSION D'ÉVAL
    Le worktree est installé dans un dossier de config jetable (`install.py --agent
    opencode --fix`), auquel on ajoute l'agent `skill-only` : `permission` refuse tout
    sauf l'outil `skill`. C'est l'équivalent de `claude -p --tools Skill`. Mesuré le
    2026-10-26 : sous cet agent, la session ouvre `security-reviewer`, ne lance ni
    `shell` ni `read`, et dit n'avoir que `skill`. L'agent n'est jamais posé dans le
    vivant `~/.config/opencode`.

    Les variables sont celles de `tools/bench/opencode.sh` : `OPENCODE_CONFIG_DIR` sur le
    dossier jetable, `OPENCODE_DISABLE_CLAUDE_CODE=1` pour ne pas charger `~/.claude`, et
    aucune variable `CLAUDE*` ni `ANTHROPIC*`. Le 2026-10-26, un modèle du banc a envoyé
    à son fournisseur un jeton de la session Claude qui le lançait.

    Skills ouverts, texte et coût se lisent sur la sortie `--format json`. Les skills
    exposés ne sont que dans `opencode.db`, sous `core/skill-guidance`, lus par
    `tools/bench/opencode-report.py`.

LE MODÈLE
    Un modèle de l'abonnement Go seulement, choisi et contrôlé par
    `tools/bench/opencode-go.py`, comme le banc. Avant chaque session, sa consommation
    locale doit rester sous 80 % de chaque fenêtre, sinon `SessionError`. Sur une erreur de
    limite Go, la session est rejouée une fois avec le modèle suivant de la chaîne.

PAS DE MODE ARTEFACT
    Constater un fichier demande des outils ouverts et `--auto`, donc un shell libre sur
    la machine pour un modèle gratuit qui envoie à son fournisseur tout ce qu'il lit.
    Un cas `artifact` s'arrête sans verdict.

LES CONVERSATIONS
    Une conversation par couple (modèle, `ponctuation.md` chargée ou non), toutes sessions
    confondues. Le modèle est celui de chaque message assistant. Un prompt est compté avec
    le modèle du premier message assistant de sa session. Les sessions dont le dossier
    est sous le dossier temporaire sont écartées : ce sont les bancs et les évals.
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
# Plusieurs `--standalone` écrivent dans la même base : non mesuré, donc un à la fois.
DEFAULT_JOBS = 1
ARTIFACT_MODE = False
AGENT = "skill-only"
DB = os.path.expanduser("~/.local/share/opencode/opencode.db")
REGLE = "ponctuation.md"


class SessionError(Exception):
    """La session ne peut pas rendre de quoi conclure."""


def _bench(repo_root: str, nom: str):
    path = os.path.join(repo_root, "tools", "bench", f"{nom}.py")
    spec = importlib.util.spec_from_file_location(nom.replace("-", "_"), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _rapport(repo_root: str):
    return _bench(repo_root, "opencode-report")


GO = _bench(os.path.dirname(os.path.dirname(HERE)), "opencode-go")
DEFAULT_MODEL = GO.CHAINE[0]


# --- évals -----------------------------------------------------------------


def prepare(repo_root: str, out_dir: str) -> dict:
    opencode = shutil.which("opencode")
    if not opencode:
        raise SessionError("`opencode` introuvable dans le PATH")
    config = os.path.join(out_dir, "opencode-config")
    os.makedirs(config, exist_ok=True)
    install = os.path.join(repo_root, "tools", "install.py")
    proc = subprocess.run(
        ["python3", install, "--agent", "opencode", "--target", config, "--fix"],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise SessionError(f"installation dans {config} en échec : {proc.stderr.strip()[-300:]}")
    ajouter_agent(os.path.join(config, "opencode.json"))
    return {"bin": opencode, "config": config, "rapport": _rapport(repo_root), "db": DB, "go": GO}


def ajouter_agent(path: str) -> None:
    """Pose l'agent `skill-only` dans l'opencode.json du dossier jetable."""
    with open(path, encoding="utf-8") as handle:
        config = json.load(handle)
    config.setdefault("agent", {})[AGENT] = {
        "mode": "primary",
        "description": "évals de déclenchement : l'outil skill et rien d'autre",
        "permission": {"*": "deny", "skill": "allow"},
    }
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(config, handle, indent=2)


def environnement(config: str) -> dict:
    env = {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE", "ANTHROPIC"))}
    env["OPENCODE_CONFIG_DIR"] = config
    env["OPENCODE_DISABLE_CLAUDE_CODE"] = "1"
    return env


def run_session(ctx: dict, case: dict, workdir: str, model: str, timeout: int):
    """Lance une session neuve. Rend (skills ouverts, skills listés, texte final, coût)."""
    if case.get("artifact"):
        raise SessionError("mode artefact non couvert sous OpenCode (shell libre)")
    go = ctx["go"]
    stdout, rc = _lancer(ctx, case, workdir, model, timeout)
    opened, session, result, cost, erreur = parse_stream(stdout)
    if go.est_limite_go(erreur) and go.suivant(model):
        model = go.suivant(model)
        stdout, rc = _lancer(ctx, case, workdir, model, timeout)
        opened, session, result, cost, erreur = parse_stream(stdout)

    stream_path = os.path.join(os.path.dirname(workdir), "run.jsonl")
    with open(stream_path, "w", encoding="utf-8") as handle:
        handle.write(stdout)
    if not result or not result.strip():
        cause = f", {erreur}" if erreur else ""
        raise SessionError(f"sortie vide (rc={rc}{cause}) → {stream_path}")
    available = None
    if session:
        rapport = ctx["rapport"]
        vus = rapport.skills_vus(rapport.ouvrir(ctx["db"]), [session])
        available = sorted(vus) if vus else None
    return opened, available, result, cost


def _lancer(ctx: dict, case: dict, workdir: str, model: str, timeout: int) -> tuple[str, int]:
    """Contrôle le quota du modèle, puis lance la session. Rend (stdout, code)."""
    go = ctx["go"]
    if os.path.isfile(ctx["db"]):
        motif = go.controler(go.ouvrir(ctx["db"]), model, int(time.time() * 1000))
    else:
        motif = None if model.startswith(go.PREFIXE) else f"{model} n'est pas un modèle Go"
    if motif:
        raise SessionError(motif)
    cmd = [ctx["bin"], "run", "--standalone", "--format", "json",
           "--agent", AGENT, "--model", model, case["query"]]
    try:
        proc = subprocess.run(
            cmd,
            cwd=workdir,
            env=environnement(ctx["config"]),
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise SessionError(f"session au-delà de {timeout}s") from exc
    return proc.stdout, proc.returncode


def parse_stream(stdout: str):
    """Lit la sortie `--format json`. Rend (skills ouverts, session, texte, coût, erreur)."""
    opened, session, texts, cost, erreur = [], None, [], 0.0, None
    for line in stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        session = session or event.get("sessionID")
        part = event.get("part") or {}
        kind = event.get("type")
        if kind == "tool_use" and part.get("tool") == "skill":
            name = (part.get("state") or {}).get("input", {}).get("id")
            if name:
                opened.append(str(name))
        elif kind == "text" and part.get("text"):
            texts.append(part["text"])
        elif kind == "step_finish":
            cost += part.get("cost") or 0.0
        elif kind == "error":
            e = event.get("error") or {}
            erreur = f"{e.get('type', 'error')} : {str(e.get('message', ''))[:120]}"
    return opened, session, "\n".join(texts), cost, erreur


# --- conversations ---------------------------------------------------------


def conversations(source: str | None) -> list[dict]:
    """Les réponses de la base, par modèle et par présence de `ponctuation.md`."""
    import sqlite3

    db = source or DB
    if not os.path.isfile(db):
        raise SessionError(f"base introuvable : {db}")
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    temp = os.path.realpath(tempfile.gettempdir()) + os.sep
    groupes: dict[tuple, dict] = {}
    for sid, directory in con.execute("select id, directory from session_v2"):
        if os.path.realpath(directory or "").startswith(temp):
            continue
        avec = REGLE in regles_chargees(con, sid)
        replies, prompts, premier = [], [], None
        for kind, data in con.execute(
                "select type, data from session_message where session_id = ? order by seq", (sid,)):
            d = json.loads(data)
            if kind == "user":
                txt = str(d.get("text") or "").strip()
                if txt and not txt.startswith("<"):
                    prompts.append(txt)
            elif kind == "assistant":
                txt = "\n".join(i.get("text", "") for i in d.get("content", [])
                                if i.get("type") == "text").strip()
                modele = nom_modele(d.get("model"))
                premier = premier or modele
                if txt:
                    replies.append((modele, txt))
        for modele, txt in replies:
            g = groupes.setdefault((modele, avec), {"replies": [], "prompts": [], "sessions": set()})
            g["replies"].append(txt)
            g["sessions"].add(sid)
        if premier:
            groupes.setdefault((premier, avec), {"replies": [], "prompts": [], "sessions": set()})[
                "prompts"].extend(prompts)
    return [
        {"titre": "modèle %s, %s %s, %d session(s)"
                  % (modele, REGLE, "chargée" if avec else "absente", len(g["sessions"])),
         "replies": g["replies"], "prompts": g["prompts"]}
        for (modele, avec), g in sorted(groupes.items())
        if g["replies"]
    ]


def nom_modele(model) -> str:
    if isinstance(model, dict):
        return "%s/%s" % (model.get("providerID", "?"), model.get("id") or model.get("modelID") or "?")
    return str(model or "?")


def regles_chargees(con, sid: str) -> set[str]:
    """Noms des fichiers de `core/instructions` de la session."""
    r = con.execute("select initial_values from instruction_state where session_id = ?", (sid,)).fetchone()
    h = json.loads(r[0]).get("core/instructions") if r else None
    blob = con.execute("select value from instruction_blob where hash = ?", (h,)).fetchone() if h else None
    return {os.path.basename(i.get("path", "")) for i in json.loads(blob[0])} if blob else set()
