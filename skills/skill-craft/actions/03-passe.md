# 03 - Passer en lot

Rejoue la validation sur plusieurs skills à la fois, corrige ce qui est mécanique, et rend un tableau OK/KO.

## Input

Une liste de noms de skills, ou rien, qui vaut tout le corpus de `skills/`.

## Output

Un tableau rendu dans le chat, une ligne par skill du lot : **deux verdicts distincts**, celui du lint et celui du jugement, le nombre de passes de correction, et la raison quand c'est KO. Les corrections sont écrites dans le repo, jamais commitées.

## Process

1. **Contrôler l'arbre.** `git status --porcelain -- skills/` doit être vide, sinon s'arrêter et le dire. *Pourquoi : un diff de passe mêlé à un travail en cours ne se relit pas.* Les modifications hors `skills/` ne comptent pas.
2. **Balayer.** Un seul appel à `python3 wrappers/claude/scripts/lint-skills.py`, sans `--skill` pour tout le corpus, ou avec un `--skill` répété par nom. Sa sortie est la liste de travail et se prend telle quelle.
   - **Garde.** Un code de sortie 2 est un instrument hors service, pas un corpus rouge. S'arrêter et remonter la cause, sans lancer un seul correcteur.
3. **Répartir.** Un sous-agent correcteur par skill rouge, tous lancés dans un seul message. *Pourquoi en parallèle : les skills sont indépendants, et la convention le prévoit en « Doctrine subagents », ligne « parallélisable ».*
   > Sous-agent : « Corrige le skill `<nom>` contre `skills/skill-craft/references/skill-authoring-fr.md` et les gabarits de `skills/skill-craft/assets/`, que tu lis d'abord. Boucle : corriger, relancer `python3 wrappers/claude/scripts/lint-skills.py --skill <nom>`, recommencer, sans dépasser la borne de passes que fixe la convention en « Frame–Deliver–Checker ». Un défaut dont le message du lint dit "aucun équivalent au gabarit" ne se devine pas : arrête-toi là, ne touche plus à rien, et rends la raison. Ne modifie aucun autre skill. Rends le code de sortie final du lint et la liste de ce que tu as changé. »
   - **Un skill arrêté sur arbitrage ne stoppe pas le lot.** Les autres correcteurs vont au bout. *Pourquoi : la valeur d'une passe est ce qu'elle ferme sans moi, et un lot qui s'arrête au premier cas dur ne ferme rien.*
4. **Relire ce que le lint ne voit pas.** Un sous-agent validateur neuf par skill devenu vert.
   > Sous-agent : « Lis `skills/skill-craft/actions/02-validate.md` et joue-la telle quelle sur le skill `<nom>`. Tu ne corriges rien : rends le rapport. »
   - **Garde.** Le validateur d'un skill n'est jamais son correcteur. Un contexte qui vient de corriger jugerait sa propre prose (convention, « Frame–Deliver–Checker »).
   - **Garde.** Un rapport rouge ne relance pas le correcteur, il entre au tableau tel quel. *Pourquoi : un message du lint nomme le home de sa correction, un constat de validateur décrit une dérive dont la réparation est un choix de conception. Mesuré sur `vault-load` le 2026-08-26, lint vert et validateur rouge sur un mode promis que le vault avait retiré le 2026-06-30.*
5. **Rendre le tableau.** Une ligne par skill du lot, ceux arrêtés sur arbitrage compris, avec leur raison. Un skill vert au lint et rouge au jugement se lit comme tel, les deux colonnes ne se fusionnent pas. Proposer le commit, ne pas le faire seul.

## Test

| Cas | Preuve |
| --- | --- |
| `python3 wrappers/claude/scripts/lint-skills.py --skill <chaque skill du lot>` après la passe | rend 0, sauf les skills rendus KO sur arbitrage |
| `git status --porcelain` après la passe | ne montre que des fichiers sous `skills/`, et aucun commit n'a été créé |
| relecture du tableau rendu | chaque skill du lot y figure, y compris ceux qu'un arbitrage a arrêtés |
| un skill du lot dont le lint est vert et le validateur rouge | deux verdicts séparés au tableau, et aucun correcteur relancé sur lui |
| la passe lancée sur un arbre sale sous `skills/` | s'arrête à l'étape 1, aucun sous-agent lancé |
