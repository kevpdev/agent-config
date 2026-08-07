# glab, et la base du diff d'une MR

Les commandes en lecture seule, et la seule façon correcte d'établir le périmètre d'une MR.
Tout ce qui suit a été mesuré le 2026-08-07 sur `glab` 1.112, GitLab auto-hébergé.

## Le contrôle d'accès, et ses codes de retour

| Situation | `glab auth status` | un `glab api` quelconque |
|---|---|---|
| token valide, hôte joignable | `0` | `0` |
| token expiré ou révoqué | `1`, message `401 Unauthorized` | `1`, corps `{"message":"401 Unauthorized"}` |
| hôte injoignable, DNS, proxy | `1`, message `dial tcp: lookup …` | `1`, même forme |

Décider sur le code de retour ; la sortie ne sert qu'à dire *pourquoi* à l'utilisateur.

### Quatre pièges de shell qui rendent un faux « rien à signaler »

Le Bash tool lance **zsh**, et ce skill est fait de commandes dont on lit le code de retour ou le nombre
de lignes. Les quatre rendent une sortie *plausible* au lieu d'une erreur.

| Piège | Ce qu'on croit lire | La forme qui marche |
|---|---|---|
| `glab … \| head` | le code de `glab` — c'est celui de `head`, donc `0` | capturer dans une variable, ou tester la commande seule |
| `${PIPESTATUS[0]}` | le code du premier maillon — vide, c'est du bash | tester la commande seule ; en zsh la variable est `pipestatus` |
| `jq` | présent — **il ne l'est pas sur ce poste** | `python3 -c` pour parser le JSON |
| `grep --include=*.java` non quoté | un drapeau — zsh le développe en glob, grep ne le voit jamais | quoter : `grep --include='*.java'` |

Le quatrième rend `no matches found`, indistinguable d'un vrai zéro. *Un contrôle qui rend zéro ne
distingue pas « défaut absent » d'« instrument aveugle » : calibrer sur un cas positif connu avant de
conclure à l'absence.*

## Récupérer la MR

**`glab api` n'accepte pas `-R`, et résout l'hôte GitLab depuis le remote git du répertoire courant.**
Lancé ailleurs — un scratchpad, un autre repo — il rend `404 Project Not Found` même avec un chemin de
projet explicite et correctement encodé, parce qu'il interroge le mauvais hôte. Mesuré deux fois de
suite hors clone, dix secondes après un appel réussi depuis le clone.

Donc : rester dans le clone, ou passer `GITLAB_HOST=<hôte>` dans l'environnement de la commande.
`-R <groupe>/<projet>` ne marche que pour les sous-commandes `glab mr …`.

| Besoin | Commande |
|---|---|
| Les MR ouvertes d'un repo | `glab mr list -R <groupe>/<projet>` |
| Le résumé lisible d'une MR | `glab mr view <iid>` |
| **Les métadonnées complètes** | `glab api "projects/<chemin-urlencodé>/merge_requests/<iid>"` |
| La liste des commits | `glab api "projects/<chemin-urlencodé>/merge_requests/<iid>/commits"` |
| La liste des fichiers touchés | `glab api "projects/<chemin-urlencodé>/merge_requests/<iid>/changes"` |

Le chemin de projet s'encode : `winggy/v3/audit` → `winggy%2Fv3%2Faudit`.

## La base du diff se LIT, elle ne se dérive pas

Lire `diff_refs.base_sha` : par définition le commit contre lequel GitLab a calculé le diff affiché.
Avec `head_sha`, il donne le périmètre exact — `git diff <base_sha>..<head_sha>`.

**Ce champ n'existe que sur l'appel unitaire.** L'endpoint de liste rend `diff_refs: null` — mesuré, une
requête `merge_requests?source_branch=…` rendait `base_sha None` là où `/merge_requests/<iid>` rendait
`6d026d68`.

### Les deux dérivations évidentes sont fausses

**`git merge-base <cible> <tête>`** : sur une MR déjà mergée, la cible contient la branche, et la
merge-base peut être la pointe de la branche elle-même. Mesuré sur une MR mergée dans `develop` :
`git merge-base develop feat/X` rendait le dernier commit de `feat/X`, donc un diff vide.

**Le nombre de commits** : sur la même MR, trois bases différentes — la merge-base, le `base_sha` de
l'API, un point de fork dérivé à la main — rendaient toutes `18` à `git rev-list --count base..tête`,
dont deux avec des diffs différents à deux fichiers près.

Le mécanisme : `A..B` compte ce qui est atteignable depuis `B` et pas depuis `A`. Un hotfix branché sur
la cible puis mergé dans la branche est atteignable des deux côtés, donc l'exclure exclut aussi toute
l'histoire de la cible — le compte ne bouge pas, le diff si.

**Et l'erreur est silencieuse.** Mesuré : une revue conduite sur une base dérivée créditait la MR d'un
correctif déjà présent sur la cible, et manquait entièrement un fichier du diff réel.

## Le contrôle de cohérence

**Comparer les ensembles de chemins, jamais leurs cardinaux.** Deux décomptes égaux ne prouvent pas deux
périmètres identiques, et deux décomptes différents ne prouvent pas une erreur.

- côté GitLab : les `new_path` du tableau `changes`, plus les `old_path` des entrées `renamed_file: true`.
- côté local : `git diff --name-only <base_sha>..<head_sha>`.
- **Chemin local absent de l'ensemble GitLab** → il doit être l'`old_path` d'une entrée
  `renamed_file: true`. Sinon la base ou la tête est fausse : s'arrêter.
- **Chemin GitLab absent du local** → toujours une base ou une tête fausse. S'arrêter.

**Pourquoi pas une soustraction.** GitLab replie un fichier déplacé en une seule entrée ; git ne le
replie que si sa détection de similarité le reconnaît — au-dessus du seuil un `R<score>` sur un chemin
(aucun écart), en dessous une suppression **et** un ajout (écart de 1). Le score suit l'ampleur du
remaniement, pas le déplacement, donc l'écart attendu vaut le nombre de renommages que git a **ratés** —
non devinable avant lecture. Mesuré sur une MR à deux renommages : git n'en reconnaît qu'un (`R082`, un
test déplacé de package), et liste l'autre en deux chemins (un service trop réécrit). Écart réel **1, pas
2** : une règle qui prédit un écart fixe fait s'arrêter sur un périmètre sain.

`git diff --name-status -M` dit lesquels git a reconnus.

## Ce que la lecture seule interdit

Les commandes qui écrivent, jamais appelées : `glab mr note`, `glab mr approve`, `glab mr merge`,
`glab mr update`.
