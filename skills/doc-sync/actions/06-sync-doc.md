# 06 - Synchroniser un document reflet

Réécrit chaque document de régime reflet selon les règles de son type et les faits du diff, document par document, après validation.

## Input

Les lignes de régime reflet de `scope.md`, et le diff du scope s'il y en a un.

## Output

Les documents réécrits, `check-doc.py` vert sur chacun, et un commit proposé par repo, en nommant sa branche.

## Process

1. **Se poser sur une branche de doc**, avant la première écriture et dans chaque repo qui recevra un commit : `docs/TICKET` si les commits du scope portent un seul ticket, `docs/sync-AAAA-MM-JJ` sinon.
   - La convention du repo passe devant ce défaut, quand il en déclare une (mémoire `vcs`, `CONTRIBUTING.md`).
2. **Charger les règles du type.** Lire `references/types/TYPE.md`, puis `.doc-rules/TYPE.md` à la racine du repo s'il existe. Le repo gagne sur la forme.
3. **Mesurer avant.** Lancer `python3 "$(readlink -f "$SKILLS_ROOT/doc-sync")/../../tools/check-doc.py" DOC` et garder ses défauts.
   - *Pourquoi ce chemin : `tools/` n'est pas lié dans la config de l'agent, seul le dossier du skill l'est.*
4. **Proposer les edits** par sous-agent, pour garder le contexte : « Lis DOC, ses règles de type et le diff du scope. Relève sa structure et son ton. Rends une liste d'edits, section par section, avant et après. Ne rends pas le fichier réécrit. »
   - En diff, des edits ciblés sur les sections que le diff touche, plus les défauts de `check-doc.py` dans ces sections.
   - En `--audit`, la restructuration selon le type est permise. Le sous-agent rend alors un plan de restructuration avant tout edit.
   - **Garde.** Vérifier par une commande chaque constat factuel du sous-agent (chemin, valeur, compte) avant de le montrer. Un constat non vérifié se marque « supposé » ou sort. *Pourquoi : mesuré le 2026-10-27, un sous-agent a proposé de corriger un « 80 % » juste, en lisant un plafond en dollars comme un pourcentage.*
5. **Faire valider, document par document**, puis appliquer par edits ciblés.
   - **Garde.** Un edit hors de la liste validée se montre avant d'être appliqué, jamais après.
6. **Mesurer après.** Relancer `check-doc.py`. Un défaut restant se montre et se justifie, ou se corrige.
7. **Proposer le commit**, un par repo, en nommant sa branche. En coordinateur centralisé, la mémoire se commite au parent et le README chez l'enfant. Rendre aussi la branche que le run a quittée.

## Test

| Cas | Preuve |
| --- | --- |
| `python3 tools/check-doc.py DOC` après l'action | rend 0, ou chaque défaut restant est justifié dans la sortie du run |
| `git rev-parse --abbrev-ref HEAD` dans chaque repo touché | rend une branche `docs/`, sauf exclusion citée de la convention du repo |
| `git log -1` après l'action, sans accord donné | aucun commit nouveau |
| les hunks de `git diff DOC` contre la liste d'edits validée | aucun hunk sans edit validé correspondant |
