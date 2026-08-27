# 06 - Synchroniser les README

Met à jour les README de régime reflet par repo, après la memory, en édition ciblée, puis propose un commit doc par repo.

## Input

Les cibles de régime **reflet** classées en action 02 qui touchent un README, et le scope validé. La memory est déjà cadrée, écrite et contrôlée (actions 03 à 05).

## Output

Les README impactés patchés par edits ciblés (jamais de réécriture complète), un README par repo enfant impacté plus le README parent pour le cross-cutting. Et, en clôture, un commit doc **proposé** (non imposé) par repo touché.

## Process

0. **Se poser sur une branche de doc, avant la première édition.** Le pré-vol de l'action 01 a posé chaque dépôt sur sa branche par **défaut**, et cette branche-là est celle que les environnements servent : elle est protégée, ses merge requests passent souvent en fast-forward only, et un commit doc n'y atterrit pas.
   - Créer la branche depuis le défaut où le dépôt est posé, **un par dépôt qui recevra un commit** :

     | Scope | Branche |
     |---|---|
     | les commits du scope portent **un seul** ticket | `docs/<ticket>`, ex. `docs/VW3-3220` |
     | plusieurs tickets mêlés, ou mode `--audit` | `docs/sync-<yyyy-mm-dd>` |

     Le ticket se déduit des messages de commit du scope validé. Le préfixe `docs/` et la forme `type/<ticket>` viennent de la convention du projet — la lire, ne pas l'inventer : chez Winggy-v3 c'est `aidd_docs/memory/vcs.md`, § Branch Naming Convention.
   - **En coordinateur centralisé, deux dépôts reçoivent un commit, donc deux branches** : la memory au parent, le README chez l'enfant. Les créer séparément, avec le même nom de branche pour que la paire se retrouve.
   - *Pourquoi cette étape est ici et pas à l'action 01 : le pré-vol doit laisser le dépôt sur son défaut, sinon les actions 02 à 05 liraient le code de la branche de doc. La bascule n'a lieu qu'au moment où on va écrire.*
1. **Ordonner.** Memory d'abord (source relue par `/plan`), README ensuite — donc cette action suit toujours 03.
2. **Analyser (délégué).** Déléguer lecture + analyse à un sous-agent pour préserver le contexte parent :
   > Sous-agent (Explore ou doc-writer) : « Lis le `README.md` du repo `<X>` et le diff du scope validé. **Relève d'abord la structure et les conventions existantes du README** (sections, format des tables, ton, niveaux de titre) et conforme-t'y. Pour chaque section impactée par le changement, propose les **edits ciblés** reflétant le nouvel état, dans le style existant. Ne touche que les sections concernées. Rends une liste d'edits (section → avant/après), pas le fichier réécrit. »
3. **Appliquer.** Le parent applique les edits validés via `Edit` (ciblé), après les avoir montrés à l'utilisateur.
   - **Jamais de réécriture complète** : le README contient des passages soignés (conventions OS, notes init Docker) qu'une regénération écraserait.
4. **Proposer le commit.** Proposer — sans imposer — un commit doc **par repo touché**, en **nommant la branche** où il atterrit (les commits atterrissent dans des repos git différents, sur les branches créées à l'étape 0). En coordinateur **centralisé**, un même changement enfant produit deux commits dans deux repos : la **memory** dans le **parent** (`aidd_docs/memory/<enfant>/`), le **README** dans l'**enfant** — les proposer séparément.
   ```
   docs: sync memory + README to match <scope>
   ```
   Respecter la règle projet : **pas de commit sans go-ahead explicite**.
   - **L'agent commite en local, il n'ouvre aucune merge request.** C'est la répartition que porte la convention VCS du projet (chez Winggy-v3, `aidd_docs/memory/vcs.md` : l'humain ouvre, commente, ferme et merge). Rendre en clôture, par dépôt, la branche de doc et la branche que le pré-vol avait quittée — les deux noms dont l'utilisateur a besoin pour reprendre la main.

## Test

- Chaque README impacté est modifié par edits de section ciblés ; aucun README n'est régénéré en entier.
- En coordinateur, un README par enfant impacté est traité, plus le parent pour le cross-cutting.
- La structure/conventions du README ont été relevées (via le sous-agent) avant tout edit.
- Le commit doc est seulement proposé, par repo, **et la proposition nomme sa branche** ; aucun `git commit` n'est lancé sans go-ahead explicite.
- **Aucune édition n'a eu lieu sur une branche par défaut.** `git rev-parse --abbrev-ref HEAD` sur chaque dépôt touché rend une branche `docs/…`, jamais le défaut que le pré-vol avait résolu. Une édition commitée sur le défaut est un défaut de cette action, pas un raccourci.
- La clôture rend, par dépôt, la branche de doc **et** la branche quittée par le pré-vol.
