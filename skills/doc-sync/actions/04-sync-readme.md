# 04 - Synchroniser les README

Met à jour les README de régime reflet par repo, après la memory, en édition ciblée, puis propose un commit doc par repo.

## Input

Les cibles de régime **reflet** classées en action 02 qui touchent un README, et le scope validé. La memory est déjà synchronisée (action 03).

## Output

Les README impactés patchés par edits ciblés (jamais de réécriture complète), un README par repo enfant impacté plus le README parent pour le cross-cutting. Et, en clôture, un commit doc **proposé** (non imposé) par repo touché.

## Process

1. **Ordonner.** Memory d'abord (source relue par `/plan`), README ensuite — donc cette action suit toujours 03.
2. **Analyser (délégué).** Déléguer lecture + analyse à un sous-agent pour préserver le contexte parent :
   > Sous-agent (Explore ou doc-writer) : « Lis le `README.md` du repo <X> et le diff du scope validé. **Relève d'abord la structure et les conventions existantes du README** (sections, format des tables, ton, niveaux de titre) et conforme-t'y. Pour chaque section impactée par le changement, propose les **edits ciblés** reflétant le nouvel état, dans le style existant. Ne touche que les sections concernées. Rends une liste d'edits (section → avant/après), pas le fichier réécrit. »
3. **Appliquer.** Le parent applique les edits validés via `Edit` (ciblé), après les avoir montrés à l'utilisateur.
   - **Jamais de réécriture complète** : le README contient des passages soignés (conventions OS, notes init Docker) qu'une regénération écraserait.
4. **Proposer le commit.** Proposer — sans imposer — un commit doc **par repo touché** (les commits atterrissent dans des repos git différents) :
   ```
   docs: sync memory + README to match <scope>
   ```
   Respecter la règle projet : **pas de commit sans go-ahead explicite**.

## Test

- Chaque README impacté est modifié par edits de section ciblés ; aucun README n'est régénéré en entier.
- En coordinateur, un README par enfant impacté est traité, plus le parent pour le cross-cutting.
- La structure/conventions du README ont été relevées (via le sous-agent) avant tout edit.
- Le commit doc est seulement proposé, par repo ; aucun `git commit` n'est lancé sans go-ahead explicite.
