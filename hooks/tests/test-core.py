#!/usr/bin/env python3
"""Batterie du cœur des gardes, sur l'entrée normalisée de `hooks/check.py`.

Pourquoi cette batterie existe : les batteries de `wrappers/claude/hooks/tests/`
passent par l'adaptateur Claude. Un second agent n'aura que ce contrat-ci, donc le
cœur doit être prouvé sans aucun JSON de Claude. Elle couvre aussi
`no_remote_write`, qui n'avait aucune batterie.

Ce qui est vérifié : la DÉCISION (passe, refus, illisible), pas le libellé du refus.
Chaque garde a au moins un refus et un passage, sinon un garde muet passerait
pour un garde juste.

Sortie : 0 si tous les cas passent, 1 si un cas échoue.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
CHECK = os.path.join(REPO, "hooks", "check.py")

PASSE, REFUS, ILLISIBLE = 0, 2, 1
NOMS = {PASSE: "PASSE", REFUS: "REFUS", ILLISIBLE: "ILLISIBLE"}
echecs = 0


def lancer(entree: str, *argv) -> int:
    r = subprocess.run([sys.executable, CHECK, *argv], input=entree,
                       capture_output=True, text=True)
    return r.returncode


def verifier(nom, attendu, garde, action="shell", command="", paths=(), cwd="/tmp",
             skills_used=None):
    global echecs
    evenement = {"event": "pre_tool", "action": action, "command": command,
                 "paths": list(paths), "cwd": cwd, "session": "test",
                 "skills_used": skills_used}
    obtenu = lancer(json.dumps(evenement), "--guard", garde)
    if obtenu == attendu:
        print(f"  OK    {nom:<58} {NOMS[obtenu]}")
    else:
        print(f"  ECHEC {nom:<58} attendu={NOMS[attendu]} obtenu={NOMS.get(obtenu, obtenu)}")
        echecs += 1


print("=== no_ai_in_commit ===")
verifier("signature Co-Authored-By", REFUS, "no_ai_in_commit",
         command='git commit -m "fix: x\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"')
verifier("nommer Claude n'est pas signer", PASSE, "no_ai_in_commit",
         command='git commit -m "fix: Claude"')
verifier("format non conventionnel", REFUS, "no_ai_in_commit", command='git commit -m "wip"')
verifier("format conventionnel", PASSE, "no_ai_in_commit",
         command='git commit -m "feat(hooks): add the core"')
verifier("PR signée", REFUS, "no_ai_in_commit",
         command='gh pr create --title "x" --body "Generated with [Claude Code]"')
verifier("fichier de message par variable", REFUS, "no_ai_in_commit",
         command='git commit -F "$S/msg.txt"')
verifier("action edit, hors périmètre", PASSE, "no_ai_in_commit", action="edit",
         paths=["/tmp/x"])

print("=== bash_tooling ===")
verifier("./mvnw direct", REFUS, "bash_tooling", command="./mvnw test")
verifier("forme prescrite", PASSE, "bash_tooling", command="bash -lc 'sh ./mvnw test'")
verifier("heredoc imbriqué", REFUS, "bash_tooling",
         command="bash -lc 'cat >> f << EOF\ncontenu\nEOF'")

print("=== no_remote_write ===")
# Hôtes déclarés et config ssh temporaires : la batterie ne nomme aucun serveur réel.
NRW = tempfile.mkdtemp()
with open(os.path.join(NRW, "hosts"), "w") as fh:
    fh.write("# hôtes protégés\nprotege-test\n")
with open(os.path.join(NRW, "ssh_config"), "w") as fh:
    fh.write("Host protege-test\n  HostName 203.0.113.7\nHost alias-bis\n  HostName 203.0.113.7\n")
os.environ["AGENT_CONFIG_PROTECTED_HOSTS"] = os.path.join(NRW, "hosts")
os.environ["AGENT_CONFIG_SSH_CONFIG"] = os.path.join(NRW, "ssh_config")
verifier("écriture via ssh sur un hôte déclaré", REFUS, "no_remote_write",
         command="ssh protege-test docker compose down")
verifier("lecture via ssh sur un hôte déclaré", PASSE, "no_remote_write",
         command="ssh protege-test docker ps")
verifier("session ssh interactive sur un hôte déclaré", REFUS, "no_remote_write",
         command="ssh protege-test")
verifier("upload scp vers un hôte déclaré", REFUS, "no_remote_write",
         command="scp f.txt protege-test:/tmp/")
verifier("autre alias vers la même IP", REFUS, "no_remote_write",
         command="ssh alias-bis rm -rf /srv")
verifier("écriture ssh vers un hôte non déclaré", PASSE, "no_remote_write",
         command="ssh bac-a-sable docker compose down")
verifier("curl POST vers l'API d'un hôte déclaré", REFUS, "no_remote_write",
         command="curl -X POST http://203.0.113.7:8080/api/orders -d '{}'")
verifier("curl GET vers l'API d'un hôte déclaré", PASSE, "no_remote_write",
         command="curl http://203.0.113.7:8080/api/orders")
for nom, commande in [
    ("curl --json", "curl --json '{}' http://203.0.113.7/x"),
    ("curl -XPOST collé", "curl -XPOST http://203.0.113.7/x"),
    ("curl options groupées -sd", "curl -sd '{}' http://203.0.113.7/x"),
    ("curl sans schéma", "curl -X POST 203.0.113.7/x -d 1"),
    ("sudo curl -X DELETE", "sudo curl -X DELETE http://203.0.113.7/x"),
    ("wget --post-data", "wget --post-data=a=1 http://203.0.113.7/x"),
    ("curl avec identifiants dans l'URL", "curl -X POST http://user:pw@203.0.113.7/x"),
]:
    verifier(nom + " vers un hôte déclaré", REFUS, "no_remote_write", command=commande)
verifier("curl -o collé (valeur commençant par d)", PASSE, "no_remote_write",
         command="curl -o/tmp/data.json http://203.0.113.7/x")
verifier("curl --request-target n'est pas un verbe", PASSE, "no_remote_write",
         command="curl --request-target /x http://203.0.113.7/")
verifier("curl -X GET vers un hôte déclaré", PASSE, "no_remote_write",
         command="curl -X GET http://203.0.113.7/x")
verifier("curl POST local", PASSE, "no_remote_write",
         command="curl -X POST http://localhost:8080/api/orders -d '{}'")
verifier("git push hors périmètre, écrit dans l'en-tête", PASSE, "no_remote_write",
         command="git push protege-test:repo main")
verifier("edit d'un chemin local", PASSE, "no_remote_write", action="edit",
         paths=["/tmp/x.txt"])
os.environ["AGENT_CONFIG_PROTECTED_HOSTS"] = os.path.join(NRW, "absent")
verifier("sans liste déclarée, rien n'est protégé", PASSE, "no_remote_write",
         command="ssh protege-test docker compose down")


def statut(hotes):
    with open(os.path.join(NRW, "hosts"), "w") as fh:
        fh.write(hotes)
    os.environ["AGENT_CONFIG_PROTECTED_HOSTS"] = os.path.join(NRW, "hosts")
    return subprocess.run([sys.executable, os.path.join(REPO, "hooks", "no_remote_write.py"),
                           "--status"], capture_output=True, text=True).stdout


def verifier_statut(nom, hotes, attendu):
    global echecs
    sortie = statut(hotes)
    if attendu in sortie:
        print(f"  OK    {nom:<58} statut")
    else:
        print(f"  ECHEC {nom:<58} sortie={sortie!r}")
        echecs += 1


verifier_statut("liste vide signalée", "", "aucune cible déclarée")
verifier_statut("alias sans Host ssh signalé", "protege-test\nfantome\n",
                "1 sur 2 cibles ne résolvent vers aucun HostName ssh (fantome)")
verifier_statut("liste vivante", "protege-test\n", "1 cible(s) vivante(s)")
for var in ("AGENT_CONFIG_PROTECTED_HOSTS", "AGENT_CONFIG_SSH_CONFIG"):
    del os.environ[var]
shutil.rmtree(NRW)

print("=== pr_merge_checks ===")
# Fake `gh` first in PATH: on `pr checks` it prints FAKE_GH_CHECKS and exits with
# FAKE_GH_RC, and appends its working directory and arguments to the call log.
PMC = tempfile.mkdtemp()
PMC_BIN = os.path.join(PMC, "bin")
PMC_LOG = os.path.join(PMC, "calls")
PMC_EMPTY = os.path.join(PMC, "empty")
os.makedirs(PMC_BIN)
os.makedirs(PMC_EMPTY)
with open(os.path.join(PMC_BIN, "gh"), "w") as fh:
    fh.write('#!/bin/sh\nprintf \'%s\\t%s\\n\' "$(pwd -P)" "$*" >> "$FAKE_GH_LOG"\n'
             'printf \'%b\' "$FAKE_GH_CHECKS"\nexit "${FAKE_GH_RC:-0}"\n')
os.chmod(os.path.join(PMC_BIN, "gh"), 0o755)
PMC_PATH = os.environ["PATH"]
os.environ["PATH"] = PMC_BIN + os.pathsep + PMC_PATH
os.environ["FAKE_GH_LOG"] = PMC_LOG
GREEN_OUTPUT = ("ci\\tpass\\t5s\\thttps://x\\n"
                "GitGuardian Security Checks\\tpass\\t1s\\thttps://y\\n"
                "codeql\\tskipping\\t0\\thttps://z\\n")
PENDING_OUTPUT = "ci\\tpending\\t0\\thttps://x\\n"


def merge(name, expected, command, output=GREEN_OUTPUT, rc=0, cwd=None, fragment=None,
          call=None, directory=None):
    """Run the guard and compare its verdict, its reason and the fake gh call log.

    `call` is the argument line expected in the log, None meaning gh must not be
    called. `directory` is where gh must have run, `fragment` a piece of the reason.
    """
    global echecs
    open(PMC_LOG, "w").close()
    os.environ["FAKE_GH_CHECKS"] = output
    os.environ["FAKE_GH_RC"] = str(rc)
    event = {"event": "pre_tool", "action": "shell", "command": command, "paths": [],
             "cwd": cwd or PMC, "session": "test", "skills_used": None}
    r = subprocess.run([sys.executable, CHECK, "--guard", "pr_merge_checks"],
                       input=json.dumps(event), capture_output=True, text=True)
    with open(PMC_LOG) as fh:
        log = [line.rstrip("\n").split("\t", 1) for line in fh if line.strip()]
    gaps = []
    if r.returncode != expected:
        gaps.append(f"attendu={NOMS[expected]} obtenu={NOMS.get(r.returncode, r.returncode)}")
    if fragment and fragment not in r.stderr:
        gaps.append(f"raison sans {fragment!r} : {r.stderr.strip()!r}")
    if call is None and log:
        gaps.append(f"gh appelé : {log}")
    if call is not None and [entry[1] for entry in log] != [call]:
        gaps.append(f"appels {[entry[1] for entry in log]} au lieu de {[call]}")
    if directory and log and log[0][0] != os.path.realpath(directory):
        gaps.append(f"gh lancé dans {log[0][0]} au lieu de {os.path.realpath(directory)}")
    if gaps:
        print(f"  ECHEC {name:<58} " + " ; ".join(gaps))
        echecs += 1
    else:
        print(f"  OK    {name:<58} {NOMS[r.returncode]}")


merge("checks pass et skipping", PASSE, "gh pr merge 5 --squash", call="pr checks 5")
merge("gh pr view, hors périmètre", PASSE, "gh pr view 5")
merge("git merge, hors périmètre", PASSE, "git merge main")
merge("--disable-auto ne merge rien", PASSE, "gh pr merge 5 --disable-auto")
merge("un check en échec", REFUS, "gh pr merge 5", fragment="security",
      output="ci\\tpass\\t5s\\thttps://x\\nsecurity\\tfail\\t34s\\thttps://y\\n", rc=1,
      call="pr checks 5")
merge("un check en attente", REFUS, "gh pr merge 5", output=PENDING_OUTPUT, rc=8,
      call="pr checks 5")
merge("un état inconnu", REFUS, "gh pr merge 5",
      output="ci\\tneutral\\t0\\thttps://x\\n", call="pr checks 5")
merge("aucun check rapporté", REFUS, "gh pr merge 5", output="", call="pr checks 5")
merge("gh pr checks en erreur", REFUS, "gh pr merge 5", output="", rc=1,
      fragment="pas pu être lus", call="pr checks 5")
merge("sortie illisible", REFUS, "gh pr merge 5", output="pas de colonnes\\n",
      fragment="pas pu être lus", call="pr checks 5")
os.environ["PATH"] = PMC_EMPTY
merge("gh absent du PATH", REFUS, "gh pr merge 5", fragment="pas pu être lus")
os.environ["PATH"] = PMC_BIN + os.pathsep + PMC_PATH

# `gh pr checks` runs where a `cd` placed before the merge leads, not in the session cwd.
repo_dir = os.path.join(PMC, "depot")
os.makedirs(os.path.join(repo_dir, "sous"))
merge("cd absolu en tête", PASSE, f"cd {repo_dir} && gh pr merge 5", call="pr checks 5",
      directory=repo_dir)
merge("cd relatif en tête", PASSE, "cd sous && gh pr merge 5", cwd=repo_dir,
      call="pr checks 5", directory=os.path.join(repo_dir, "sous"))
saved_home = os.environ.get("HOME")
os.environ["HOME"] = PMC
merge("cd ~/… en tête", PASSE, "cd ~/depot && gh pr merge 5", call="pr checks 5",
      directory=repo_dir)
os.environ["HOME"] = saved_home
merge("sans cd, le cwd de session", PASSE, "gh pr merge 5", cwd=repo_dir,
      call="pr checks 5", directory=repo_dir)
merge("cd après le merge, ignoré", PASSE, "gh pr merge 5 && cd ailleurs", cwd=repo_dir,
      call="pr checks 5", directory=repo_dir)

# The selector and repository passed to `gh pr checks` are the merge's own.
merge("sans argument : la branche courante", PASSE, "gh pr merge --squash",
      call="pr checks")
merge("par URL", PASSE, "gh pr merge https://github.com/o/r/pull/5",
      call="pr checks https://github.com/o/r/pull/5")
merge("par branche", PASSE, "gh pr merge feature-x -d", call="pr checks feature-x")
merge("-R o/r", PASSE, "gh pr merge 5 -R o/r --squash", call="pr checks 5 -R o/r")
merge("--repo=o/r", PASSE, "gh pr merge --repo=o/r 5", call="pr checks 5 -R o/r")
merge("gh pr -R o/r merge", PASSE, "gh pr -R o/r merge 2", call="pr checks 2 -R o/r")
merge("gh --repo o/r pr merge", PASSE, "gh --repo o/r pr merge 2", call="pr checks 2 -R o/r")
merge("GH_REPO en préfixe", PASSE, "GH_REPO=o/r gh pr merge 2", call="pr checks 2 -R o/r")
merge("GH_REPO en variable", REFUS, "GH_REPO=$R gh pr merge 2")
merge("--auto suit les checks", REFUS, "gh pr merge 5 --auto --squash",
      output=PENDING_OUTPUT, rc=8, call="pr checks 5")
merge("--auto sur checks verts", PASSE, "gh pr merge 5 --auto", call="pr checks 5")
for name, command in [
    ("--subject x 5", "gh pr merge --subject x 5"),
    ("-t x 5", "gh pr merge -t x 5"),
    ("-F msg.txt 5", "gh pr merge -F msg.txt 5"),
    ('-b "corps" 5', 'gh pr merge -b "un corps" 5'),
    ("-A a@b.c 5", "gh pr merge -A a@b.c 5"),
    ("--match-head-commit sha 5", "gh pr merge --match-head-commit abc123 5"),
    ("--delete-branch=false 5", "gh pr merge --delete-branch=false 5"),
]:
    merge("option à valeur : " + name, PASSE, command, call="pr checks 5")

# A digit glued to `<` or `>` is a file descriptor, a digit followed by a space is the
# selector, and a digit before `&>` is always the selector.
merge("redirection 2>&1 sans sélecteur", PASSE, "gh pr merge --squash 2>&1", call="pr checks")
merge("sélecteur puis >/dev/null", PASSE, "gh pr merge 2 >/dev/null", call="pr checks 2")
merge("sélecteur puis > fichier 2>&1", PASSE, "gh pr merge 2 > /tmp/out 2>&1",
      call="pr checks 2")
merge("sélecteur puis &>/dev/null", PASSE, "gh pr merge 12 &>/dev/null", call="pr checks 12")

merge("--watch et merge dans le même appel", REFUS,
      "gh pr checks 5 --watch && gh pr merge 5", fragment="appel séparé",
      output=PENDING_OUTPUT, rc=8, call="pr checks 5")
merge("guillemet non fermé", REFUS, 'gh pr merge 5 -b "corps')
merge("sélecteur en variable", REFUS, "for n in 5 6; do gh pr merge $n; done")
merge("sélecteur en substitution", REFUS, "gh pr merge `cat n`")
merge("gh lancé par xargs", REFUS, "echo 2 | xargs gh pr merge")
merge("gh lancé par parallel", REFUS, "parallel gh pr merge ::: 2 3")
merge("heredoc lu par bash", REFUS, "bash <<'EOF'\ngh pr merge 5\nEOF")
merge("heredoc lu par sh -s", REFUS, "sh -s <<EOF\ncd /x && gh pr merge 5\nEOF")
merge("continuation de ligne avant le sélecteur", PASSE,
      "gh pr merge \\\n  12 --squash --delete-branch", call="pr checks 12")
merge("continuation de ligne après gh", PASSE, "gh \\\n  pr merge 12", call="pr checks 12")
merge("continuation de ligne au milieu du sélecteur", PASSE, "gh pr merge 1\\\n2",
      call="pr checks 12")
merge("heredoc dont une ligne finit par \\, puis merge", PASSE,
      "git commit -F - <<'EOT'\nfeat(hooks): x \\\nEOT\ngh pr merge 2", call="pr checks 2")
merge("gh pr merge cité entre guillemets", PASSE, 'grep -n "gh pr merge" README.md')
merge("heredoc qui cite gh pr merge, apostrophe comprise", PASSE,
      "git commit -F - <<'EOF'\nfeat(hooks): refuse gh pr merge when checks aren't green\nEOF")
merge("heredoc écrit dans un script .sh", PASSE, "cat > run.sh <<'EOF'\ngh pr merge 5\nEOF")
os.environ["PATH"] = PMC_PATH
for var in ("FAKE_GH_LOG", "FAKE_GH_CHECKS", "FAKE_GH_RC"):
    os.environ.pop(var, None)
shutil.rmtree(PMC)

print("=== no_secret_read ===")
with tempfile.TemporaryDirectory() as projet:
    sous = os.path.join(projet, "sub")
    for nom, attendu, commande, cwd in [
        ("cat .env", REFUS, "cat .env", projet),
        ("grep d'une clé dans .env", REFUS, "grep API_KEY .env", projet),
        ("variante .env.production", REFUS, "cat .env.production", projet),
        ("redirection < vers grep", REFUS, "grep x < .env", projet),
        ("chemin relatif depuis un sous-dossier", REFUS, "cat ../.env", sous),
        ("sqlite3 sur opencode.db", REFUS, 'sqlite3 ~/.local/share/opencode/opencode.db "select 1"', projet),
        ("source d'un cp", REFUS, "cp ~/.claude/.credentials.json /tmp/x", projet),
        ("dans une chaîne", REFUS, "echo ok && head -3 .env", projet),
        ("exception .env.example", PASSE, "cat .env.example", projet),
        ("ls ne lit pas le contenu", PASSE, "ls -la .env", projet),
        ("test -f ne lit pas le contenu", PASSE, "test -f .env && echo oui", projet),
        ("squelette par cp", PASSE, "cp .env.example .env", projet),
        ("écriture par >", PASSE, "printf 'A=1\\n' > .env", projet),
        ("ajout par >>", PASSE, "echo DEBUG=1 >> .env", projet),
        ("sed -i écrit sans sortir", PASSE, "sed -i s/0/1/ .env", projet),
        ("chargé par docker compose", PASSE, "docker compose --env-file .env up", projet),
        ("chargé par source", PASSE, "source .env && pytest", projet),
        ("programme sur l'entrée standard", PASSE, "python3 app.py < .env", projet),
        ("heredoc qui nomme un secret, écrit et non lu", PASSE,
         "cat >> deny.yaml <<'EOF'\nfin: .ssh/id_rsa\nEOF", projet),
        ("commande après le heredoc, toujours jugée", REFUS, "cat > a <<EOF\nx\nEOF\ncat .env", projet),
        ("clé SSH privée", REFUS, "cat ~/.ssh/id_ed25519", projet),
        ("jetons AWS", REFUS, "cat ~/.aws/credentials", projet),
        ("jeton de la CLI GitHub", REFUS, "grep token ~/.config/gh/hosts.yml", projet),
        ("clé privée de certificat", REFUS, "cat server.key", projet),
        ("clé SSH publique", PASSE, "cat ~/.ssh/id_ed25519.pub", projet),
        ("empreinte par ssh-keygen", PASSE, "ssh-keygen -lf ~/.ssh/id_ed25519", projet),
        ("ls du dossier SSH", PASSE, "ls ~/.ssh", projet),
    ]:
        verifier(nom, attendu, "no_secret_read", command=commande, cwd=cwd)
verifier("action edit, hors périmètre", PASSE, "no_secret_read", action="edit", paths=["/p/.env"])

print("=== no_sensitive_write ===")
with tempfile.TemporaryDirectory() as projet:
    for nom, attendu, commande in [
        ("rm -rf .git", REFUS, "rm -rf .git"),
        ("rm d'un objet sous .git", REFUS, "rm .git/index.lock"),
        ("ajout à ~/.zshrc", REFUS, "echo 'export X=1' >> ~/.zshrc"),
        ("redirection sans espace", REFUS, "echo x>$HOME/.bashrc"),
        ("sed -i sur ~/.ssh/config", REFUS, "sed -i s/a/b/ ~/.ssh/config"),
        ("mv vers authorized_keys", REFUS, "mv cle.pub ~/.ssh/authorized_keys"),
        ("mv qui retire known_hosts", REFUS, "mv ~/.ssh/known_hosts /tmp/kh"),
        ("sudo tee dans /etc", REFUS, "echo 1 | sudo tee /etc/hosts"),
        ("destination d'un cp sous /usr", REFUS, "cp outil /usr/local/bin/outil"),
        ("cp -t vers /boot", REFUS, "cp -t /boot vmlinuz"),
        ("dd of= sous /boot", REFUS, "dd if=img of=/boot/efi.img"),
        ("dans une chaîne", REFUS, "ls && rm -f ~/.profile"),
        ("git écrit .git sans le nommer", PASSE, "git commit -m 'fix: x'"),
        ("lecture de ~/.zshrc", PASSE, "cat ~/.zshrc"),
        ("copie depuis ~/.zshrc", PASSE, "cp ~/.zshrc /tmp/sauvegarde"),
        ("lecture sous /etc", PASSE, "grep x /etc/hosts"),
        (".gitignore n'est pas .git", PASSE, "echo x > .gitignore"),
        (".zshrc versionné dans un dépôt", PASSE, "echo x >> dotfiles/.zshrc"),
        ("redirection vers /dev/null", PASSE, "ls 2>/dev/null"),
        ("variable inconnue, chemin indécidable", PASSE, "rm -rf $S/t/base/.git"),
        ("$HOME est résolu", REFUS, "rm $HOME/.ssh/config"),
        ("2>&1 ne nomme aucun fichier", PASSE, "cp a b 2>&1"),
        ("sed sans -i n'écrit rien", PASSE, "sed s/a/b/ ~/.zshrc"),
        ("heredoc qui nomme ~/.zshrc, écrit ailleurs", PASSE,
         "cat > note.md <<'EOF'\nrm ~/.zshrc\nEOF"),
    ]:
        verifier(nom, attendu, "no_sensitive_write", command=commande, cwd=projet)
verifier("edit sous .git", REFUS, "no_sensitive_write", action="edit", paths=["/repo/.git/config"])
verifier("edit de ~/.ssh/config", REFUS, "no_sensitive_write", action="edit",
         paths=[os.path.expanduser("~/.ssh/config")])
verifier("edit d'un fichier ordinaire", PASSE, "no_sensitive_write", action="edit",
         paths=["/repo/src/app.py"])
verifier("action read, hors périmètre", PASSE, "no_sensitive_write", action="read",
         paths=["/repo/.git/config"])

print("=== aidd_skill_lookup ===")
with tempfile.TemporaryDirectory() as aidd:
    os.mkdir(os.path.join(aidd, ".git"))
    verifier("geste sans skill aidd", REFUS, "aidd_skill_lookup",
             command='gh issue create --title x', cwd=aidd, skills_used=[])
    verifier("geste après un skill aidd", PASSE, "aidd_skill_lookup",
             command='gh issue create --title x', cwd=aidd,
             skills_used=["aidd-vcs:04-issue-create"])
    verifier("skills inconnus : échoue ouvert", PASSE, "aidd_skill_lookup",
             command='gh issue create --title x', cwd=aidd, skills_used=None)
    verifier("sortie aidd-skip", PASSE, "aidd_skill_lookup",
             command='gh issue create --title x # aidd-skip: test', cwd=aidd, skills_used=[])
verifier("outside a git repository", PASSE, "aidd_skill_lookup",
         command='gh issue create --title x', cwd="/tmp", skills_used=[])

print("=== contrat de check.py ===")
for nom, entree, attendu in [
    ("entrée non JSON", "pas du json", ILLISIBLE),
    ("entrée JSON qui n'est pas un objet", "[1]", ILLISIBLE),
    ("tous les gardes, commande anodine", json.dumps({"action": "shell", "command": "ls"}), PASSE),
    ("tous les gardes, commit signé",
     json.dumps({"action": "shell", "cwd": "/tmp",
                 "command": 'git commit -m "fix: x\n\nCo-Authored-By: Claude"'}), REFUS),
]:
    obtenu = lancer(entree)
    if obtenu == attendu:
        print(f"  OK    {nom:<58} {NOMS[obtenu]}")
    else:
        print(f"  ECHEC {nom:<58} attendu={NOMS[attendu]} obtenu={NOMS.get(obtenu, obtenu)}")
        echecs += 1

print("=== aucun format d'agent dans le cœur ===")
fuites = [
    f"{f}:{n}" for f in sorted(os.listdir(os.path.join(REPO, "hooks"))) if f.endswith(".py")
    for n, ligne in enumerate(open(os.path.join(REPO, "hooks", f), encoding="utf-8"), 1)
    if any(k in ligne for k in ("tool_input", "hookSpecificOutput", "tool_name"))
]
if fuites:
    print("  ECHEC champs Claude dans hooks/ : " + ", ".join(fuites))
    echecs += 1
else:
    print("  OK    aucun tool_input, tool_name ni hookSpecificOutput")

print(f"{'✓' if echecs == 0 else '✗'} {echecs} échec(s).")
sys.exit(1 if echecs else 0)
