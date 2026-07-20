# 01 - Détecter topologie et scope

Détecte où vit le code et la doc, propose un scope de commits, et le fait confirmer avant toute édition.

## Input

- Le CWD (repo courant).
- Opt-in éventuel « WIP non commité » — réservé au cas rare où le code est figé mais pas encore commité, et toujours averti (« tu documentes du non-validé »).

## Output

- La topologie retenue : mono-repo, ou coordinateur avec la liste des repos enfants et le/les doc(s) confirmée(s) comme contrat partagé.
- Par repo concerné, le scope validé après élagage : range de commits (`base...HEAD`) + liste de fichiers.

## Process

1. **Détecter.** Établir la topologie. L'autorité (régimes du routeur) est universelle ; seul change **où chercher le code** et **combien de homes de doc** existent.
   - **Mono-repo** (défaut) : `aidd_docs/memory/` + `README.md` à la racine, code dans le repo courant. Un seul boulot : sync la doc-reflet du repo contre son propre code.
   - **Coordinateur** : le CWD contient des sous-dossiers qui sont des repos git autonomes (`<child>/.git`), chacun avec son `aidd_docs/` + `README.md`, ET héberge une doc-contrat partagé enjambant ces enfants.
   - Commandes de détection :
     ```
     # enfants = sous-dossiers ayant leur propre .git
     ls -d */.git 2>/dev/null | sed 's#/.git##'
     # candidats contrat partagé au parent (pas de nom figé)
     ls aidd_docs/memory/*.md 2>/dev/null
     ```
2. **Confirmer le contrat.** Le contrat partagé n'a **pas de nom de fichier conventionné** — ne pas grep un `shared-contract.md` en dur. Repérer le/les candidat(s) (souvent `shared-contract.md`, mais ça peut être `contract.md`, `api-contract.md`, une section d'un doc…), puis **faire confirmer à l'utilisateur quelle(s) doc(s) du parent tiennent le rôle de contrat partagé** avant de les traiter en régime décision.
   - Si aucune ne joue ce rôle, le coordinateur se réduit au Boulot 1 (chaque enfant chez lui) et il n'y a pas de contrat à traiter en décision.
3. **Ancrer.** Par repo concerné, déterminer le point de référence. Git ne connaît pas les frontières de tâche : un range capture tout ce qui a bougé dedans, d'où l'élagage humain de l'étape 4. Déterminer la branche principale (`git symbolic-ref refs/remotes/origin/HEAD`, fallback `main`), puis choisir le scope :

   | Situation | Scope proposé |
   |---|---|
   | Branche feature ≠ main | `git diff --name-only $(git merge-base main HEAD)...HEAD` (commits only) |
   | Dev direct sur main, commité | depuis le dernier commit doc : `base=$(git log -1 --format=%H -- README.md aidd_docs/memory/)` puis `git diff --name-only $base...HEAD` |
   | Features mergées, doc oubliée | mode `--reconcile` (→ action 05), l'ancre git est non fiable |
   | WIP figé non commité (opt-in averti) | `git diff --name-only HEAD` + avertir que c'est du non-validé |
   | **Contrat partagé (coordinateur)** | **toujours `--reconcile`** (→ action 05) : le contrat est une décision, on le compare au code des enfants à HEAD |

4. **Confirmer.** Lister **commits + fichiers** du scope retenu, par repo (`git log --oneline $base...HEAD`), et demander de **confirmer ou élaguer** (par commit, ou filtre de chemin) — surtout sur main où des commits de plusieurs tâches se mélangent. N'avancer qu'avec le scope validé.

## Test

- La topologie est explicite : mono-repo, ou coordinateur avec liste d'enfants issue de `ls -d */.git`.
- En coordinateur, aucune doc n'est traitée en contrat partagé sans confirmation utilisateur explicite.
- Le scope présenté est un range de commits (`base...HEAD`), jamais le working tree — sauf opt-in WIP averti.
- Aucune édition n'a eu lieu à ce stade : la sortie est seulement la topologie + le scope confirmé.
