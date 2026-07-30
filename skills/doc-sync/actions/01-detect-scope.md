# 01 - Détecter topologie et scope

Détecte où vit le code et la doc, propose un scope de commits, et le fait confirmer avant toute édition.

## Input

- Le CWD (repo courant).
- Opt-in éventuel « WIP non commité » — réservé au cas rare où le code est figé mais pas encore commité, et toujours averti (« tu documentes du non-validé »).

## Output

- La topologie retenue : mono-repo, ou coordinateur avec la liste des repos enfants, **le home memory de chaque enfant (distribué / centralisé)**, et le/les doc(s) confirmée(s) comme contrat partagé.
- Par repo concerné, le scope validé après élagage : range de commits (`base...HEAD`) + liste de fichiers. Le code s'ancre toujours dans l'enfant ; en centralisé, la cible memory de cet enfant est le sous-dossier `aidd_docs/memory/<child>/` du parent.

## Process

1. **Détecter.** Établir la topologie. L'autorité (régimes du routeur) est universelle ; seul change **où chercher le code** et **combien de homes de doc** existent.
   - **Mono-repo** (défaut) : `aidd_docs/memory/` + `README.md` à la racine, code dans le repo courant. Un seul boulot : sync la doc-reflet du repo contre son propre code.
   - **Coordinateur** : le CWD contient des sous-dossiers qui sont des **projets enfants** — versionnés à part (`<child>/.git`) **ou** simplement rangés là dans un monorepo — et héberge une doc-contrat partagé enjambant ces enfants. Le **code** de chaque enfant vit dans `<child>/` ; la **memory-reflet** de l'enfant a deux homes possibles, à résoudre **par enfant** :
     - **distribué** : l'enfant porte son propre `aidd_docs/memory/` + `README.md` (chaque enfant = un mono-repo chez lui).
     - **centralisé** : l'enfant est code-only (pas de `aidd_docs/`) et sa memory est namespacée dans le parent (`aidd_docs/memory/<child>/`, `aidd_docs/internal/decisions/<child>/`) ; seul le `README.md` reste dans l'enfant.
     Conséquence pour le commit, **si l'enfant est versionné à part** (colonne `VCS = propre`) : en distribué, memory et README de l'enfant atterrissent dans **l'enfant** ; en centralisé, le commit **memory** atterrit dans le **parent** et le commit **README** dans l'**enfant** (deux repos git). **Si l'enfant est versionné par le parent** (`VCS = parent`, cas du monorepo), il n'y a qu'un repo : **un seul commit**, et rien à répartir. Ne pas tenter un `git -C <child>` là où il n'y a pas de `.git` — la commande échoue et le boulot s'arrête sur un faux problème.
   - Commandes de détection :
     ```
     # enfants + home memory de chacun, en une passe (implémentation unique)
     bash "$HOME/.claude/skills/_shared/detect-children.sh" --long
     # candidats contrat partagé au parent (pas de nom figé) — top-level only
     ls aidd_docs/memory/*.md 2>/dev/null
     ```
   - **Ne pas réimplémenter la détection ici.** La règle, ses trois contre-exemples mesurés et le `basename` du home memory vivent dans les commentaires du script — un seul home (R6). Une copie locale dériverait sans que rien ne le signale, et c'est précisément ce qui s'est produit : la version recopiée cherchait un `.git` sur deux niveaux, donc voyait **0** enfant sur un monorepo et ratait un enfant rangé plus profond.
   - Sortie utile ici : la colonne **MEMORY** donne directement le verdict par enfant (`distribué` / `centralisé (memory/<nom>)` / `aucune`). La colonne **VCS** dit si l'enfant peut porter son propre commit — décisif pour l'étape de commit ci-dessous : en monorepo (`parent`), memory et README atterrissent dans le **même** repo, il n'y a pas deux commits à répartir.
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

- La topologie est explicite : mono-projet, ou coordinateur avec la liste d'enfants **produite par `_shared/detect-children.sh --long`** — jamais par une commande recopiée sur place. Trois symptômes signalent que la détection a été réimplémentée à côté : un coordinateur dont les enfants sont groupés (`backend/<x>`) qui ressort « mono-repo », un monorepo dont les projets ne ressortent pas du tout, ou tous les enfants classés « sans memory ».
- Le script tourne et rend un résultat non vide sur un coordinateur. Contrôle à jouer depuis la racine du parent :
  ```
  bash "$HOME/.claude/skills/_shared/detect-children.sh" --long
  ```
  Chaque ligne porte ses trois attributs. `VCS` vaut `propre` ou `parent` ; `BUILD` nomme le manifeste trouvé ou `aucun` ; `MEMORY` vaut `distribué`, `centralisé (memory/<nom>)` ou `aucune`. Un enfant à `BUILD = aucun` est normal (dépôt de doc ou de config) et n'est pas une erreur de détection.
- En coordinateur, aucune doc n'est traitée en contrat partagé sans confirmation utilisateur explicite.
- Le scope présenté est un range de commits (`base...HEAD`), jamais le working tree — sauf opt-in WIP averti.
- Aucune édition n'a eu lieu à ce stade : la sortie est seulement la topologie + le scope confirmé.
