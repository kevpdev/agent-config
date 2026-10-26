#!/usr/bin/env python3
"""Driver Claude Code : lancer une session neuve, lire ses transcripts.

Tout ce que `run-skill-evals.py` et `mesure-reponses.py` savent de Claude vit ici. Un
autre agent fournit les mêmes fonctions dans `tools/drivers/<agent>.py`, et les deux
scripts restent inchangés (cadrage `audits/2026-10-22-cadrage-harnais-agnostique.md`,
structure cible).

Interface commune aux drivers :

- `DEFAULT_MODEL`, `DEFAULT_JOBS`, `ARTIFACT_MODE` ;
- `prepare(repo_root, out_dir)` rend le contexte d'une passe, ou lève `SessionError` ;
- `run_session(ctx, case, workdir, model, timeout)` rend (skills ouverts, skills listés
  ou None, texte final, coût) ;
- `conversations(source)` rend une liste de `{titre, replies, prompts}`.
"""

from __future__ import annotations

import glob
import json
import os
import shutil
import subprocess

DEFAULT_MODEL = "opus"
DEFAULT_JOBS = 4
ARTIFACT_MODE = True


class SessionError(Exception):
    """La session ne peut pas rendre de quoi conclure."""


# --- évals -----------------------------------------------------------------


def prepare(repo_root: str, out_dir: str) -> dict:
    claude = shutil.which("claude")
    if not claude:
        raise SessionError("`claude` introuvable dans le PATH")
    return {"bin": claude}


def run_session(ctx: dict, case: dict, workdir: str, model: str, timeout: int):
    """Lance une session neuve. Rend (skills ouverts, skills listés, texte final, coût)."""
    cmd = [
        ctx["bin"],
        "-p",
        case["query"],
        "--model",
        model,
        "--output-format",
        "stream-json",
        "--verbose",
        "--no-session-persistence",
        "--permission-mode",
        "bypassPermissions",
    ]
    if not case.get("artifact"):
        cmd += ["--tools", "Skill"]
    try:
        proc = subprocess.run(
            cmd,
            cwd=workdir,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise SessionError(f"session au-delà de {timeout}s") from exc

    stream_path = os.path.join(os.path.dirname(workdir), "run.jsonl")
    with open(stream_path, "w", encoding="utf-8") as handle:
        handle.write(proc.stdout)

    opened, available, result, cost = parse_stream(proc.stdout)
    if not result or not str(result).strip():
        raise SessionError(f"sortie vide (rc={proc.returncode}) → {stream_path}")
    return opened, available, result, cost


def parse_stream(stdout: str):
    """Lit le `stream-json` de `claude -p`. Un appel à l'outil `Skill` nomme le skill ouvert."""
    opened, available, result, cost = [], None, None, 0.0
    for line in stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        kind = event.get("type")
        if kind == "system" and event.get("subtype") == "init":
            listed = event.get("skills")
            if isinstance(listed, list):
                available = [str(item) for item in listed]
        elif kind == "assistant":
            for block in event.get("message", {}).get("content", []):
                if block.get("type") == "tool_use" and block.get("name") == "Skill":
                    name = block.get("input", {}).get("skill")
                    if name:
                        opened.append(str(name))
        elif kind == "result":
            result = event.get("result")
            cost = event.get("total_cost_usd") or 0.0
    return opened, available, result, cost


# --- transcripts -----------------------------------------------------------


def conversations(source: str | None) -> list[dict]:
    """Un transcript, celui passé en argument ou le dernier de `~/.claude/projects`."""
    path = source
    if not path:
        pat = os.path.expanduser("~/.claude/projects/*/*.jsonl")
        cands = sorted(glob.glob(pat), key=os.path.getmtime)
        if not cands:
            raise SessionError("aucun transcript trouvé, passer le chemin en argument")
        path = cands[-1]
    replies, prompts = charge(path)
    return [{"titre": "transcript : %s" % path, "replies": replies, "prompts": prompts}]


def charge(path):
    """Rend (réponses assistant, prompts utilisateur) en texte brut."""
    replies, prompts = [], []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            try:
                e = json.loads(line)
            except ValueError:
                continue
            m = e.get("message") or {}
            role, c = m.get("role"), m.get("content")
            if not role or c is None:
                continue
            if isinstance(c, str):
                txt = c
            else:
                txt = "\n".join(
                    b.get("text", "")
                    for b in c
                    if isinstance(b, dict) and b.get("type") == "text"
                )
            txt = txt.strip()
            if not txt:
                continue
            if role == "assistant":
                replies.append(txt)
            elif role == "user" and not txt.startswith("<"):
                prompts.append(txt)
    return replies, prompts
