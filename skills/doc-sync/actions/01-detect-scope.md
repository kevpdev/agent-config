# 01 - Détecter topologie et scope

Détecte où vit le code et la doc, propose un scope, et le fait confirmer avant toute édition. Le scope est un range de commits en sync, le banc de mémoire en `--audit`.

## Input

- Le CWD (repo courant).
- Opt-in éventuel « WIP non commité » — réservé au cas rare où le code est figé mais pas encore commité, et toujours averti (« tu documentes du non-validé »).
- Mode **`--audit`** éventuel : l'entrée est le **banc de mémoire** au home résolu, pas un diff de commits. Les étapes 1 et 2 ci-dessous ne changent pas, les étapes 3 et 4 prennent leur branche d'audit.

## Output

- La topologie retenue : mono-repo, ou coordinateur avec la liste des repos enfants, **le home memory de chaque enfant (distribué / centralisé)**, et le/les doc(s) confirmée(s) comme contrat partagé.
- Par repo concerné, le scope validé après élagage : un range de commits (`base...HEAD`) plus sa liste de fichiers, ou — en `--audit` — la liste des fichiers de mémoire retenus avec leur décompte de mots. Le code s'ancre toujours dans l'enfant ; en centralisé, la cible memory de cet enfant est le sous-dossier `aidd_docs/memory/<child>/` du parent.

## Process

1. **Détecter.** Établir la topologie. L'autorité (les régimes de [regimes-de-doc.md](../references/regimes-de-doc.md)) est universelle ; seul change **où chercher le code** et **combien de homes de doc** existent.
   - **Mono-repo** (défaut) : `aidd_docs/memory/` + `README.md` à la racine, code dans le repo courant. Un seul boulot : sync la doc-reflet du repo contre son propre code.
   - **Coordinateur** : le CWD contient des sous-dossiers qui sont des **projets enfants** — versionnés à part (`<child>/.git`) **ou** simplement rangés là dans un monorepo — et héberge une doc-contrat partagé enjambant ces enfants. Le **code** de chaque enfant vit dans `<child>/` ; la **memory-reflet** de l'enfant a deux homes possibles, à résoudre **par enfant** :
     - **distribué** : l'enfant porte son propre `aidd_docs/memory/` + `README.md` (chaque enfant = un mono-repo chez lui).
     - **centralisé** : l'enfant est code-only (pas de `aidd_docs/`) et sa memory est namespacée dans le parent (`aidd_docs/memory/<child>/`, `aidd_docs/internal/decisions/<child>/`) ; seul le `README.md` reste dans l'enfant.
     Conséquence pour le commit, **si l'enfant est versionné à part** (colonne `VCS = propre`) : en distribué, memory et README de l'enfant atterrissent dans **l'enfant** ; en centralisé, le commit **memory** atterrit dans le **parent** et le commit **README** dans l'**enfant** (deux repos git). **Si l'enfant est versionné par le parent** (`VCS = parent`, cas du monorepo), il n'y a qu'un repo : **un seul commit**, et rien à répartir. Ne pas tenter un `git -C <child>` là où il n'y a pas de `.git` — la commande échoue et le boulot s'arrête sur un faux problème.
   - Commandes de détection :
     ```
     # enfants + home memory de chacun, en une passe (implémentation unique)
     bash "$SKILLS_ROOT/_shared/detect-children.sh" --long
     # candidats contrat partagé au parent (pas de nom figé) — top-level only
     ls aidd_docs/memory/*.md 2>/dev/null
     ```
   - **Se lancer depuis la racine du parent, et nulle part ailleurs.** Le script énumère `backend/` et
     `frontend/` relativement au répertoire courant, donc lancé d'ailleurs il rend
     `aucun enfant : topologie mono-projet` — un **faux zéro silencieux** sur la commande que cette
     action désigne comme faisant autorité. Vérifié le 2026-08-21 : 31 enfants depuis la racine,
     « mono-projet » depuis `aidd_docs/memory/`.
   - **Si `$SKILLS_ROOT` est vide, s'arrêter au lieu de chercher le script.** La commande devient
     `bash "/_shared/…"` et sort en 127, ce qui accuse le script au lieu de la config — un sous-agent
     est parti le chercher par un `find /`. *La cause a été tranchée le 2026-08-27 : le bloc `env` de
     `~/.claude/settings.local.json` n'atteint pas le shell, la variable s'exporte depuis le profil du
     shell de lancement. `README.md`, section `SKILLS_ROOT`, porte la mesure et la preuve de config.*
   - **Ne pas réimplémenter la détection ici.** La règle, ses trois contre-exemples mesurés et le `basename` du home memory vivent dans les commentaires du script — un seul home (R6). Une copie locale dériverait sans que rien ne le signale, et c'est précisément ce qui s'est produit : la version recopiée cherchait un `.git` sur deux niveaux, donc voyait **0** enfant sur un monorepo et ratait un enfant rangé plus profond.
   - Sortie utile ici : la colonne **MEMORY** donne directement le verdict par enfant (`distribué` / `centralisé (memory/<nom>)` / `aucune`). La colonne **VCS** dit si l'enfant peut porter son propre commit — décisif pour l'étape de commit ci-dessous : en monorepo (`parent`), memory et README atterrissent dans le **même** repo, il n'y a pas deux commits à répartir.
2. **Confirmer le contrat.** Le contrat partagé n'a **pas de nom de fichier conventionné** — ne pas grep un `shared-contract.md` en dur. Repérer le/les candidat(s) (souvent `shared-contract.md`, mais ça peut être `contract.md`, `api-contract.md`, une section d'un doc…), puis **faire confirmer à l'utilisateur quelle(s) doc(s) du parent tiennent le rôle de contrat partagé** avant de les traiter en régime décision.
   - Si aucune ne joue ce rôle, le coordinateur se réduit au Boulot 1 (chaque enfant chez lui) et il n'y a pas de contrat à traiter en décision.
3. **Ancrer.** Par repo concerné, déterminer le point de référence. Git ne connaît pas les frontières de tâche : un range capture tout ce qui a bougé dedans, d'où l'élagage humain de l'étape 4. Déterminer la branche principale (`git symbolic-ref refs/remotes/origin/HEAD`, fallback `main`), puis choisir le scope :

   | Situation | Scope proposé |
   |---|---|
   | Branche feature ≠ main | `git diff --name-only $(git merge-base main HEAD)...HEAD` (commits only) |
   | Dev direct sur main, commité | depuis le dernier commit doc : `base=$(git log -1 --format=%H -- README.md aidd_docs/memory/)` puis `git diff --name-only $base...HEAD` |
   | Features mergées, doc oubliée | mode `--reconcile` (→ action 07), l'ancre git est non fiable |
   | WIP figé non commité (opt-in averti) | `git diff --name-only HEAD` + avertir que c'est du non-validé |
   | **Contrat partagé (coordinateur)** | **toujours `--reconcile`** (→ action 07) : le contrat est une décision, on le compare au code des enfants à HEAD |
   | **Audit du banc (`--audit`)** | **pas d'ancre git** : le scope est le banc au home résolu à l'étape 1, énuméré avec son **décompte de mots par fichier** |

   - **En `--audit`, ne pas chercher de base.** Il n'y a rien à comparer entre deux états : l'audit juge ce que le banc porte, pas ce qu'une tâche a changé. Un `merge-base` calculé là ne sert à rien et fait croire à un périmètre qui n'existe pas.

4. **Confirmer.** Lister **commits + fichiers** du scope retenu, par repo (`git log --oneline $base...HEAD`), et demander de **confirmer ou élaguer** (par commit, ou filtre de chemin) — surtout sur main où des commits de plusieurs tâches se mélangent. N'avancer qu'avec le scope validé.
   - **En `--audit`, l'élagage n'est plus une précaution, c'est la condition d'entrée.** Rendre le décompte **fichier par fichier** du home résolu (`wc -w <home>/*.md`), puis proposer par défaut **un seul fichier**, le plus lourd de la racine @-importée. Les suivants passent en runs séparés. Élargir reste possible, **nommément**, mais c'est l'humain qui décide de payer.
     - *Pourquoi un fichier et non la racine entière, mesuré le 2026-08-21 : un scope de 5 fichiers (10 226 mots) a rendu **31 constats** à la passe 1, à couverture partielle (~85 %). Le cycle de l'action 05 en tolère trois passes, il n'en efface pas 31 — l'audit rend alors un backlog au lieu d'un banc à jour. Le seul `architecture.md` en a rendu 15, ce qui est déjà la limite haute de ce qu'une passe répare.*
     - *Pourquoi le décompte d'abord, avant même la proposition : c'est lui qui dit quel fichier passe en premier, et il permet d'élaguer sur un fait au lieu du ressenti. Un scope proposé sans chiffre se valide en bloc.*
     - **Ne pas confondre le scope et le home.** Le décompte porte sur tout le home, la proposition sur un fichier. Rendre l'un sans l'autre fait croire soit que le banc est petit, soit qu'il faut tout prendre.

## Test

- La topologie est explicite : mono-projet, ou coordinateur avec la liste d'enfants **produite par `_shared/detect-children.sh --long`** — jamais par une commande recopiée sur place. Trois symptômes signalent que la détection a été réimplémentée à côté : un coordinateur dont les enfants sont groupés (`backend/<x>`) qui ressort « mono-repo », un monorepo dont les projets ne ressortent pas du tout, ou tous les enfants classés « sans memory ».
- **`$SKILLS_ROOT` est peuplée avant de croire la détection** : `echo "[$SKILLS_ROOT]"` rend un chemin, pas `[]`. Vide, la commande sort en 127 et accuse le script au lieu de la config.
- Le script tourne et rend un résultat non vide sur un coordinateur. Contrôle à jouer depuis la racine du parent :
  ```
  bash "$SKILLS_ROOT/_shared/detect-children.sh" --long
  ```
  Chaque ligne porte ses trois attributs. `VCS` vaut `propre` ou `parent` ; `BUILD` nomme le manifeste trouvé ou `aucun` ; `MEMORY` vaut `distribué`, `centralisé (memory/<nom>)` ou `aucune`. Un enfant à `BUILD = aucun` est normal (dépôt de doc ou de config) et n'est pas une erreur de détection.
  **Contrôle calibré** : la même commande lancée depuis un sous-dossier doit rendre « mono-projet ». Si elle rend des enfants des deux endroits, le script a changé et ce prérequis est à réécrire ; si elle rend « mono-projet » des deux, le `cwd` était faux.
- En coordinateur, aucune doc n'est traitée en contrat partagé sans confirmation utilisateur explicite.
- Le scope présenté est un range de commits (`base...HEAD`), jamais le working tree — sauf opt-in WIP averti.
- **En `--audit`, aucun range de commits n'apparaît dans la sortie.** Un `base...HEAD` affiché signifie que l'étape 3 a pris la branche du diff au lieu de celle de l'audit.
- **En `--audit`, le scope validé porte un décompte de mots par fichier**, et le défaut proposé était **un seul fichier**. Un scope d'audit sans chiffre par fichier n'a pas été présenté, il a été supposé ; un scope d'audit qui propose d'office plusieurs fichiers n'a pas été borné.
- Aucune édition n'a eu lieu à ce stade : la sortie est seulement la topologie + le scope confirmé.
