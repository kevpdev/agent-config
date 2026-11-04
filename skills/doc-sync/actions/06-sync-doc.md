# 06 - Synchroniser un document reflet

Réécrit chaque document de régime reflet selon les règles de son type et les faits du diff, document par document. Chaque edit appliqué se rend dans le compte rendu.

## Input

Les lignes de régime reflet de `scope.md`, et le diff du scope s'il y en a un.

## Output

Les documents réécrits, `check-doc.py` vert sur chacun, la liste des edits appliqués, et un commit par repo, ou sa proposition quand `rules/aidd.md` garde la question.

## Process

1. **Se poser sur une branche de doc**, avant la première écriture et dans chaque repo qui recevra un commit : `docs/TICKET` si les commits du scope portent un seul ticket, `docs/sync-AAAA-MM-JJ` sinon.
   - La convention du repo passe devant ce défaut, quand il en déclare une (mémoire `vcs`, `CONTRIBUTING.md`).
   - **Garde, avant la branche.** `git status --porcelain -- <documents reflet du scope>` doit être vide dans chaque repo. Sinon, s'arrêter et nommer les fichiers modifiés, sauf opt-in « WIP non commité » posé par `01-detect-scope`. *Pourquoi : écraser des modifications non commitées est un effet de bord au sens de R13 de `skill-craft`, et les mêler aux edits du run les rend inséparables pour git.*
2. **Charger les règles du type.** Lire `references/types/TYPE.md`, puis `.doc-rules/TYPE.md` à la racine du repo s'il existe. Le repo gagne sur la forme.
3. **Mesurer avant.** Lancer `python3 "$(readlink -f "$SKILLS_ROOT/doc-sync")/../../tools/check-doc.py" DOC` et garder ses défauts.
   - *Pourquoi ce chemin : `tools/` n'est pas lié dans la config de l'agent, seul le dossier du skill l'est.*
4. **Proposer les edits** par sous-agent, pour garder le contexte : « Lis DOC, ses règles de type et le diff du scope. Relève sa structure et son ton. Rends une liste d'edits, section par section, avant et après. Ne rends pas le fichier réécrit. »
   - En diff, des edits ciblés sur les sections que le diff touche, plus les défauts de `check-doc.py` dans ces sections.
   - En `--audit`, la restructuration selon le type est permise. Le sous-agent rend alors un plan de restructuration avant tout edit.
   - **Garde.** Vérifier par une commande chaque constat factuel du sous-agent (chemin, valeur, compte) avant de l'appliquer. Un constat non vérifié n'est pas appliqué. Il se cite « supposé » dans le compte rendu. *Pourquoi : mesuré le 2026-10-27, un sous-agent a proposé de corriger un « 80 % » juste, en lisant un plafond en dollars comme un pourcentage.*
5. **Appliquer par edits ciblés**, puis rendre chaque edit dans le compte rendu, document par document, avec son texte avant et après.
   - En `--audit`, montrer d'abord le plan de restructuration et attendre l'accord. *Pourquoi : une restructuration change ce que dit le document, pas seulement ses lignes.*
   - Un edit hors de la liste du sous-agent se marque « hors liste » dans le compte rendu.
6. **Mesurer après.** Relancer `check-doc.py`. Un défaut restant se montre et se justifie, ou se corrige.
7. **Commiter** selon `rules/aidd.md`, section « Git sur une branche de travail », un commit par repo, une fois `check-doc.py` vert ou chaque défaut restant justifié. En coordinateur centralisé, la mémoire se commite au parent et le README chez l'enfant. Rendre aussi la branche que le run a quittée.
   - Si la branche n'a pas été créée par ce run, le commit se propose au lieu de se lancer.

## Test

| Cas | Preuve |
| --- | --- |
| `python3 tools/check-doc.py DOC` après l'action | rend 0, ou chaque défaut restant est justifié dans la sortie du run |
| `git rev-parse --abbrev-ref HEAD` dans chaque repo touché | rend une branche `docs/`, sauf exclusion citée de la convention du repo |
| `git log -1 --name-only` dans chaque repo touché | un commit sur la branche créée par le run, limité aux documents du scope, ou la question posée si le repo interdit le commit ou si la branche existait déjà |
| un document reflet du scope modifié et non commité, sans opt-in WIP | arrêt avant la branche, le fichier est nommé, `git diff` inchangé |
| les hunks de `git show -- DOC` contre la liste d'edits du compte rendu | aucun hunk absent du compte rendu |
| chaque constat cité « supposé » dans le compte rendu | aucun hunk correspondant dans `git show -- DOC` |
| un run `--audit` | le plan de restructuration est montré, et aucun edit n'est appliqué avant l'accord |
