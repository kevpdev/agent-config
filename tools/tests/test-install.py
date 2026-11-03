#!/usr/bin/env python3
"""Calibre `tools/install.py` sur une cible fabriquée, sans toucher la config vivante.

Pourquoi cette batterie existe : un installateur qui ne voit rien rend « aucun écart »
exactement comme un installateur qui voit juste. Seuls un positif et un négatif par
classe d'écart, exhibés à la main, distinguent les deux (`rules/reasoning.md`,
calibrage avant comptage).

Pourquoi une cible fabriquée : la cible réelle est la config de la session en cours, et
`--fix` y écrit. Le script est lancé en sous-processus, avec `HOME` redirigé quand le
cas porte sur le rendu des chemins. `XDG_CONFIG_HOME` et `GIT_CONFIG_GLOBAL` visent toujours
un dossier temporaire, pour qu'aucun cas n'écrive dans le vrai `~/.config/git/ignore`.

Sortie : 0 si tous les cas passent, 1 si un cas échoue.
"""

from __future__ import annotations

import atexit
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SCRIPT = os.path.join(REPO, "tools", "install.py")

# Un faux `codegraph` en tête du PATH : aucune batterie ne lance le vrai installateur.
# Il note ses arguments et CLAUDE_CONFIG_DIR, puis écrit l'entrée là où le vrai l'écrit.
FAUX_BIN = tempfile.mkdtemp(prefix="faux-codegraph-")
atexit.register(shutil.rmtree, FAUX_BIN, True)
FAUX_LOG = os.path.join(FAUX_BIN, "appels.jsonl")
with open(os.path.join(FAUX_BIN, "codegraph"), "w", encoding="utf-8") as f:
    f.write(f"""#!{sys.executable}
import json, os, sys
dossier = os.environ.get("CLAUDE_CONFIG_DIR")
with open({FAUX_LOG!r}, "a") as f:
    f.write(json.dumps({{"args": sys.argv[1:], "config_dir": dossier}}) + "\\n")
fichier = os.path.join(dossier, ".claude.json") if dossier else os.path.expanduser("~/.claude.json")
os.makedirs(os.path.dirname(fichier), exist_ok=True)
donnees = json.load(open(fichier)) if os.path.exists(fichier) else {{}}
donnees.setdefault("mcpServers", {{}})["codegraph"] = {{"type": "stdio", "command": "codegraph"}}
json.dump(donnees, open(fichier, "w"))
""")
os.chmod(os.path.join(FAUX_BIN, "codegraph"), 0o755)


# Le git global de chaque lancement : un XDG_CONFIG_HOME et un fichier de config vides,
# partagés par défaut, remplaçables par cas.
GIT_ISOLE = tempfile.mkdtemp(prefix="git-isole-")
atexit.register(shutil.rmtree, GIT_ISOLE, True)
XDG_DEFAUT = os.path.join(GIT_ISOLE, "xdg")
GITCONFIG_DEFAUT = os.path.join(GIT_ISOLE, "gitconfig")
open(GITCONFIG_DEFAUT, "w").close()
MOTIF = "**/.claude/worktrees/"


def appels_faux() -> list[dict]:
    if not os.path.exists(FAUX_LOG):
        return []
    with open(FAUX_LOG, encoding="utf-8") as f:
        return [json.loads(l) for l in f]


def lancer(cible, *argv, home=None, xdg=XDG_DEFAUT, gitconfig=GITCONFIG_DEFAUT):
    """Lance l'installateur, rend (code, sortie fusionnée)."""
    env = dict(os.environ)
    env["XDG_CONFIG_HOME"] = xdg
    env["GIT_CONFIG_GLOBAL"] = gitconfig
    env.pop("CLAUDE_SETTINGS_FILE", None)
    env.pop("CLAUDE_CONFIG_DIR", None)
    env["PATH"] = FAUX_BIN + os.pathsep + env.get("PATH", "")
    if home:
        env["HOME"] = home
    r = subprocess.run(
        [sys.executable, SCRIPT, "--agent", "claude", "--target", cible, *argv],
        capture_output=True, text=True, env=env,
    )
    return r.returncode, r.stdout + r.stderr


def lire_settings(cible, nom="settings.json"):
    with open(os.path.join(cible, nom), encoding="utf-8") as f:
        return json.load(f)


def commandes(settings):
    sortie = [h["command"] for groupes in settings.get("hooks", {}).values()
              for g in groupes for h in g.get("hooks", [])]
    if "statusLine" in settings:
        sortie.append(settings["statusLine"]["command"])
    return sortie


def main() -> int:
    if not os.path.exists(SCRIPT):
        print(f"  FAIL  install.py introuvable à {SCRIPT}")
        print("✗ 1 échec(s).")
        return 1

    echecs = 0

    def cas(nom, condition):
        nonlocal echecs
        print(f"  {'ok  ' if condition else 'FAIL'}  {nom}")
        if not condition:
            echecs += 1

    code, liste = lancer("/nulle-part", "--list")
    attendus = [l for l in liste.splitlines() if " -> " in l]
    cas("list : sort en 0 et rend des liens", code == 0 and len(attendus) > 0)

    with tempfile.TemporaryDirectory() as racine:
        autre_home = os.path.join(racine, "home")
        os.makedirs(autre_home)
        cible = os.path.join(racine, "cfg")

        # Cible vide : tout est absent, et rien n'est écrit.
        code, sortie = lancer(cible, "--check", home=autre_home)
        cas("vide : des écarts sortent en 1", code == 1)
        cas("vide : un ABSENT par lien attendu", sortie.count("ABSENT") == len(attendus))
        cas("vide : settings.json signalé", "settings.json" in sortie and "model" in sortie)
        cas("vide : --check n'écrit rien", not os.path.exists(cible))
        cas("vide : serveur MCP absent de .claude.json", ".claude.json mcpServers.codegraph : absent" in sortie)
        cas("vide : --check ne lance pas l'installateur", appels_faux() == [])
        ignore_defaut = os.path.join(XDG_DEFAUT, "git", "ignore")
        cas("vide : motif git ignore absent signalé",
            f"git ignore {MOTIF} : absent ({ignore_defaut})" in sortie)
        cas("vide : --check n'écrit pas le git ignore", not os.path.exists(ignore_defaut))

        # --fix pose tout, puis --check est propre.
        code, _ = lancer(cible, "--fix", home=autre_home)
        cas("fix : sort en 0", code == 0)
        appels = appels_faux()
        cas("fix : installateur lancé une fois, sur la cible",
            len(appels) == 1 and appels[0]["config_dir"] == cible
            and appels[0]["args"] == ["install", "-t", "claude", "-l", "global", "-y"])
        cas("fix : .claude.json écrit dans la cible", os.path.exists(os.path.join(cible, ".claude.json")))
        with open(ignore_defaut, encoding="utf-8") as f:
            cas("fix : git ignore créé avec le motif", f.read() == f"{MOTIF}\n")
        code, sortie = lancer(cible, "--check", home=autre_home)
        cas("fix puis check : aucun écart", code == 0 and "aucun écart" in sortie)

        regle = os.path.join(cible, "rules", "style.md")
        cas("fix : lien de règle vers le repo",
            os.readlink(regle) == os.path.join(REPO, "rules", "style.md"))
        cas("fix : lien de dossier pour hooks/tests",
            os.readlink(os.path.join(cible, "scripts", "hooks", "tests"))
            == os.path.join(REPO, "wrappers", "claude", "hooks", "tests"))

        # Rendu des chemins : hors du home, absolu.
        cmds = commandes(lire_settings(cible))
        cas("rendu hors home : plus aucun ~/.claude",
            cmds and not any("~/.claude" in c for c in cmds))
        cas("rendu hors home : chemin absolu de la cible",
            any(f"{cible}/scripts/hooks/guard-bash-tooling.py" in c for c in cmds))

        # Lien redirigé.
        os.unlink(regle)
        os.symlink("/ailleurs/style.md", regle)
        code, sortie = lancer(cible, "--check", home=autre_home)
        cas("redirigé : signalé", code == 1 and "MAUVAISE CIBLE" in sortie and "style.md" in sortie)
        lancer(cible, "--fix", home=autre_home)
        cas("redirigé : réparé par --fix",
            os.readlink(regle) == os.path.join(REPO, "rules", "style.md"))

        # Orphelin : un lien vers le repo dont la source n'existe pas.
        orphelin = os.path.join(cible, "rules", "disparue.md")
        os.symlink(os.path.join(REPO, "rules", "disparue.md"), orphelin)
        code, sortie = lancer(cible, "--check", home=autre_home)
        cas("orphelin : signalé", code == 1 and "ORPHELIN" in sortie and "disparue.md" in sortie)
        lancer(cible, "--fix", home=autre_home)
        cas("orphelin : retiré par --fix", not os.path.lexists(orphelin))

        # Intrus : un vrai fichier dans le dossier des règles.
        intrus = os.path.join(cible, "rules", "a-la-main.md")
        with open(intrus, "w") as f:
            f.write("x\n")
        code, sortie = lancer(cible, "--check", home=autre_home)
        cas("intrus : signalé", code == 1 and "INTRUS" in sortie and "a-la-main.md" in sortie)
        code, _ = lancer(cible, "--fix", home=autre_home)
        cas("intrus : jamais supprimé, même en --fix", os.path.exists(intrus) and code == 1)
        os.unlink(intrus)

        # Pas un lien : un vrai fichier à la place d'un lien attendu.
        os.unlink(regle)
        with open(regle, "w") as f:
            f.write("copie\n")
        code, sortie = lancer(cible, "--fix", home=autre_home)
        cas("pas un lien : signalé et laissé", code == 1 and "PAS UN LIEN" in sortie
            and not os.path.islink(regle))
        os.unlink(regle)
        lancer(cible, "--fix", home=autre_home)

        # Dossier propre à la machine dans skills/.
        os.makedirs(os.path.join(cible, "skills", "synced", "x"))
        code, sortie = lancer(cible, "--check", home=autre_home)
        cas("skills/synced : ignoré", code == 0 and "synced" not in sortie)

        # Clés propres à la machine conservées.
        s = lire_settings(cible)
        s["voice"] = {"enabled": True}
        s["hooks"].setdefault("UserPromptSubmit", []).append(
            {"hooks": [{"type": "command", "command": "codegraph prompt-hook"}]})
        with open(os.path.join(cible, "settings.json"), "w") as f:
            json.dump(s, f)
        code, sortie = lancer(cible, "--check", home=autre_home)
        cas("machine : ses clés ne sont pas des écarts", code == 0)
        s["model"] = "haiku"
        with open(os.path.join(cible, "settings.json"), "w") as f:
            json.dump(s, f)
        lancer(cible, "--fix", home=autre_home)
        s = lire_settings(cible)
        cas("machine : clés et hooks conservés après --fix",
            s.get("voice") == {"enabled": True} and "codegraph prompt-hook" in commandes(s))
        cas("machine : clé du repo réappliquée", s.get("model") != "haiku")

        # policy/deny.yaml traduit en permissions.deny, à côté des allow de la machine.
        deny = s.get("permissions", {}).get("deny", [])
        cas("deny : service.json interdit à toute profondeur",
            "Read(//**/.config/opencode/service.json)" in deny)
        cas("deny : clé SSH privée interdite à toute profondeur", "Read(//**/.ssh/id_ed25519)" in deny)
        cas("deny : une entrée à exception n'est pas traduite", not any(".env.*" in d for d in deny))
        cas("deny : écriture sous .git à toute profondeur", "Edit(//**/.git/**)" in deny)
        cas("deny : écriture de ~/.zshrc ancrée au home", "Edit(~/.zshrc)" in deny)
        cas("deny : écriture sous /etc ancrée à la racine", "Edit(//etc/**)" in deny)
        s["permissions"]["allow"] = ["Bash(ls:*)"]
        s["permissions"]["deny"] = deny[1:]
        with open(os.path.join(cible, "settings.json"), "w") as f:
            json.dump(s, f)
        code, sortie = lancer(cible, "--check", home=autre_home)
        cas("deny : une interdiction retirée est un écart", code == 1 and "permissions.deny" in sortie)
        lancer(cible, "--fix", home=autre_home)
        s = lire_settings(cible)
        cas("deny : allow de la machine conservé et deny rétabli",
            s["permissions"].get("allow") == ["Bash(ls:*)"] and s["permissions"]["deny"] == deny)

        # Rendu des chemins : sous le home, écrit avec ~.
        home = os.path.join(racine, "h2")
        cible_home = os.path.join(home, ".claude")
        os.makedirs(home)
        lancer(cible_home, "--fix", home=home)
        cmds = commandes(lire_settings(cible_home))
        cas("rendu sous le home : ~/.claude/scripts gardé",
            any(c == "bash ~/.claude/scripts/hooks/guard-no-claude-in-commit.sh" for c in cmds))
        cas("rendu sous le home : aucun chemin absolu",
            not any(home in c for c in cmds))
        cas("mcp sous le home : $HOME/.claude.json, sans CLAUDE_CONFIG_DIR",
            appels_faux()[-1]["config_dir"] is None and os.path.exists(os.path.join(home, ".claude.json"))
            and not os.path.exists(os.path.join(cible_home, ".claude.json")))
        n = len(appels_faux())
        code, _ = lancer(cible_home, "--fix", home=home)
        cas("mcp présent : l'installateur n'est pas relancé", code == 0 and len(appels_faux()) == n)

        # --repo change la source des liens, pas le reste.
        code, sortie = lancer(cible, "--check", "--repo", "/autre/repo", home=autre_home)
        cas("--repo : les liens visent l'autre repo",
            code == 1 and "MAUVAISE CIBLE" in sortie and "/autre/repo/" in sortie)

    # Fichier d'exclusion global de git : chaque cas a son propre git isolé.
    with tempfile.TemporaryDirectory() as racine:
        cible = os.path.join(racine, "cfg")
        lancer(cible, "--fix")
        gitconfig = os.path.join(racine, "gitconfig")
        open(gitconfig, "w").close()

        # Ligne déjà présente : aucun écart, fichier inchangé octet pour octet.
        xdg = os.path.join(racine, "xdg-present")
        ignore = os.path.join(xdg, "git", "ignore")
        os.makedirs(os.path.dirname(ignore))
        avant = f"*.swp\n{MOTIF}   \n".encode()
        with open(ignore, "wb") as f:
            f.write(avant)
        code, sortie = lancer(cible, "--check", xdg=xdg, gitconfig=gitconfig)
        cas("git ignore présent : aucun écart", code == 0 and "git ignore" not in sortie)
        code, sortie = lancer(cible, "--fix", xdg=xdg, gitconfig=gitconfig)
        with open(ignore, "rb") as f:
            cas("git ignore présent : --fix ne touche pas le fichier",
                code == 0 and f.read() == avant and "git ignore" not in sortie)

        # Autre ligne sans saut de ligne final : le motif va sur une ligne à lui.
        xdg = os.path.join(racine, "xdg-sans-fin")
        ignore = os.path.join(xdg, "git", "ignore")
        os.makedirs(os.path.dirname(ignore))
        with open(ignore, "w", encoding="utf-8") as f:
            f.write("*.swp")
        code, sortie = lancer(cible, "--check", xdg=xdg, gitconfig=gitconfig)
        cas("git ignore sans le motif : signalé", code == 1 and f"git ignore {MOTIF} : absent" in sortie)
        code, sortie = lancer(cible, "--fix", xdg=xdg, gitconfig=gitconfig)
        with open(ignore, encoding="utf-8") as f:
            cas("git ignore sans saut final : motif ajouté sur une nouvelle ligne, l'autre gardée",
                code == 0 and f.read() == f"*.swp\n{MOTIF}\n" and f"ajouté     git ignore {MOTIF}" in sortie)

        # core.excludesFile défini : c'est ce fichier qui est écrit, pas celui de XDG.
        xdg = os.path.join(racine, "xdg-ignore")
        declare = os.path.join(racine, "declare", "exclusions")
        config = os.path.join(racine, "gitconfig-declare")
        with open(config, "w", encoding="utf-8") as f:
            f.write(f"[core]\n\texcludesFile = {declare}\n")
        code, sortie = lancer(cible, "--check", xdg=xdg, gitconfig=config)
        cas("core.excludesFile : l'écart nomme le fichier déclaré", code == 1 and f"({declare})" in sortie)
        code, _ = lancer(cible, "--fix", xdg=xdg, gitconfig=config)
        with open(declare, encoding="utf-8") as f:
            cas("core.excludesFile : le fichier déclaré reçoit le motif", code == 0 and f.read() == f"{MOTIF}\n")
        cas("core.excludesFile : le fichier XDG n'est pas créé",
            not os.path.exists(os.path.join(xdg, "git", "ignore")))

        # core.excludesFile déclaré dans un fichier inclus par [include] : il est suivi.
        xdg = os.path.join(racine, "xdg-include")
        inclus = os.path.join(racine, "inclus", "exclusions")
        config_inclus = os.path.join(racine, "gitconfig-inclus")
        with open(config_inclus, "w", encoding="utf-8") as f:
            f.write(f"[core]\n\texcludesFile = {inclus}\n")
        config = os.path.join(racine, "gitconfig-include")
        with open(config, "w", encoding="utf-8") as f:
            f.write(f"[include]\n\tpath = {config_inclus}\n")
        code, sortie = lancer(cible, "--check", xdg=xdg, gitconfig=config)
        cas("[include] : l'écart nomme le fichier déclaré dans l'inclus", code == 1 and f"({inclus})" in sortie)
        code, _ = lancer(cible, "--fix", xdg=xdg, gitconfig=config)
        recu = open(inclus, encoding="utf-8").read() if os.path.exists(inclus) else None
        cas("[include] : le fichier de l'inclus reçoit le motif", code == 0 and recu == f"{MOTIF}\n")
        cas("[include] : le fichier XDG n'est pas créé", not os.path.exists(os.path.join(xdg, "git", "ignore")))

        # Un octet hors UTF-8 dans une autre ligne : ni plantage, ni octet perdu.
        xdg = os.path.join(racine, "xdg-latin1")
        ignore = os.path.join(xdg, "git", "ignore")
        os.makedirs(os.path.dirname(ignore))
        with open(ignore, "wb") as f:
            f.write(b"caf\xe9.tmp\n")
        code, sortie = lancer(cible, "--check", xdg=xdg, gitconfig=gitconfig)
        cas("octet hors UTF-8 : --check signale sans planter",
            code == 1 and f"git ignore {MOTIF} : absent" in sortie and "Traceback" not in sortie)
        code, sortie = lancer(cible, "--fix", xdg=xdg, gitconfig=gitconfig)
        with open(ignore, "rb") as f:
            cas("octet hors UTF-8 : --fix ajoute le motif et garde l'octet",
                code == 0 and f.read() == b"caf\xe9.tmp\n" + MOTIF.encode() + b"\n")

    code, sortie = lancer("/nulle-part", "--list", "--agent", "inconnu")
    cas("agent inconnu : refusé", code != 0)

    # OpenCode : sa config s'appelle opencode.json, et `{repo}` y vise la racine des liens.
    with tempfile.TemporaryDirectory() as tmp:
        cible = os.path.join(tmp, "opencode")
        code, sortie = lancer(cible, "--fix", "--agent", "opencode")
        cas("opencode : liens posés", code == 0 and os.path.islink(os.path.join(cible, "plugins", "harness-guards")))
        cas("opencode : scripts/worktree.sh posé, comme sous Claude",
            os.readlink(os.path.join(cible, "scripts", "worktree.sh")).endswith("tools/worktree.sh"))
        cas("opencode : aucun settings.json", not os.path.exists(os.path.join(cible, "settings.json")))
        config = os.path.join(cible, "opencode.json")
        instructions = lire_settings(cible, "opencode.json").get("instructions") if os.path.exists(config) else None
        cas("opencode : instructions vise rules/*.md du repo",
            instructions == [os.path.join(REPO, "rules", "*.md")])
        with open(config, encoding="utf-8") as f:
            donnees = json.load(f)
        donnees["model"] = "machine/choix"
        with open(config, "w", encoding="utf-8") as f:
            json.dump(donnees, f)
        code, sortie = lancer(cible, "--check", "--agent", "opencode")
        cas("opencode : clé machine, --check sans écart", code == 0)
        code, sortie = lancer(cible, "--fix", "--agent", "opencode")
        cas("opencode : clé machine conservée après --fix",
            lire_settings(cible, "opencode.json").get("model") == "machine/choix")
        code, sortie = lancer(cible, "--check", "--agent", "opencode", "--repo", "/autre/repo")
        cas("opencode : --repo déplace aussi instructions",
            code == 1 and "/autre/repo/rules/*.md" in sortie)
        policies = lire_settings(cible, "opencode.json").get("policies", [])
        cas("opencode : policies interdit service.json hors du dossier de travail",
            {"action": "tool.use", "resource": "read:*/.config/opencode/service.json", "effect": "deny"} in policies)
        cas("opencode : policies interdit les jetons AWS hors du dossier de travail",
            {"action": "tool.use", "resource": "read:*/.aws/credentials", "effect": "deny"} in policies)
        cas("opencode : policies interdit l'écriture sous .git hors du dossier de travail",
            {"action": "tool.use", "resource": "edit:*/.git/*", "effect": "deny"} in policies)
        cas("opencode : ~/.zshrc n'a que sa forme absolue",
            [p["resource"] for p in policies if p["resource"].endswith("/.zshrc")]
            == [f"edit:{os.path.expanduser('~')}/.zshrc"])
        cas("opencode : /etc reste ancré à la racine",
            {"action": "tool.use", "resource": "edit:/etc/*", "effect": "deny"} in policies)
        exemple = [i for i, p in enumerate(policies) if p["resource"] == "read:*/.env.example"]
        variantes = [i for i, p in enumerate(policies) if p["resource"] == "read:*/.env.*"]
        cas("opencode : .env.example relevé après le deny de .env.*",
            exemple and variantes and policies[exemple[0]]["effect"] == "allow" and exemple[0] > variantes[0])
        serveurs = lire_settings(cible, "opencode.json").get("mcp", {}).get("servers", {})
        cas("opencode : mcp.servers.codegraph lancé par la commande déclarée",
            serveurs.get("codegraph", {}).get("command") == ["codegraph", "serve", "--mcp"]
            and serveurs["codegraph"].get("type") == "local")
        donnees = lire_settings(cible, "opencode.json")
        donnees["mcp"]["servers"]["autre"] = {"type": "remote", "url": "https://x"}
        with open(config, "w", encoding="utf-8") as f:
            json.dump(donnees, f)
        code, sortie = lancer(cible, "--fix", "--agent", "opencode")
        cas("opencode : serveur de la machine conservé",
            code == 0 and "autre" in lire_settings(cible, "opencode.json")["mcp"]["servers"])
        cas("opencode : aucun installateur lancé", all(a["config_dir"] != cible for a in appels_faux()))

    # Une entrée de deny.yaml mal formée arrête l'installation.
    spec = importlib.util.spec_from_file_location("install", SCRIPT)
    install = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(install)
    with tempfile.TemporaryDirectory() as tmp:
        for nom, contenu in (("entrée à action inconnue", "- {id: x, action: shell, fin: a, raison: r}\n"),
                             ("entrée sans fin", "- {id: x, action: read, raison: r}\n")):
            chemin = os.path.join(tmp, "deny.yaml")
            with open(chemin, "w", encoding="utf-8") as f:
                f.write(contenu)
            try:
                install.charger_deny(chemin)
                refuse = False
            except SystemExit:
                refuse = True
            cas(f"deny.yaml : {nom} refusée", refuse)
        chemin = os.path.join(tmp, "servers.yaml")
        with open(chemin, "w", encoding="utf-8") as f:
            f.write("- {nom: x, commande: [x], raison: r}\n")
        try:
            install.charger_mcp(chemin)
            refuse = False
        except SystemExit:
            refuse = True
        cas("servers.yaml : serveur sans installateur Claude refusé", refuse)

    print(f"{'✓' if not echecs else '✗'} {echecs} échec(s).")
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())
