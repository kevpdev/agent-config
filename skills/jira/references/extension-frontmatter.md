# L'extension de frontmatter qui porte la clé du ticket

## Le problème

Les cinq types de backlog du framework AIDD verrouillent leur frontmatter par une clause identique,
« A Task carries no other field », déclinée sur chaque type dans son `references/relations.md`. Et le
test de leur action de persistance refuse explicitement « un champ optionnel non supporté ».

Or **aucun de ces champs ne porte l'identité du ticket dans un tracker externe**. Le framework prévoit
la relation entre artefacts, jamais le pont vers l'outil de ticketing.

## L'extension est licite, et le framework le dit lui-même

Le type task porte `work_kind`, décrit comme utilisable « only when the project uses it ». Le framework
admet donc qu'un projet ajoute un champ à condition de le déclarer.

**Le dépôt déclare donc un champ, un seul, qui porte la clé du ticket.** Son nom vit dans la mémoire du
dépôt, pas ici. Ce fichier explique pourquoi il existe, la mémoire dit comment il s'appelle.

*Pourquoi ce partage :* ce skill est partagé publiquement, donc le nom d'un champ propre à un projet n'y
entre pas. Et un projet qui aurait déjà un autre nom pour cette idée ne devrait pas avoir à le changer.

## Le champ est aussi l'interrupteur du gel

| État du brouillon | Le champ | Le `status` |
| --- | --- | --- |
| avant publication | absent | maintenu par les skills `aidd-pm` |
| après publication | porte la clé | **cesse d'être maintenu** |

**POURQUOI le gel plutôt qu'une synchronisation** : après publication, le tracker fait foi sur les
champs que l'équipe peut modifier, résumé et description compris. Maintenir le `status` du brouillon en
plus créerait une seconde copie de l'état, et la résolution d'un conflit entre les deux n'aurait aucun
vainqueur naturel.

**CONSÉQUENCE** : un ticket corrigé dans le tracker ne déclenche aucune resynchronisation du brouillon.
Le brouillon est l'instantané de ce qui a été soumis. Ce que le dépôt garde en exclusivité, c'est le
raisonnement du découpage, les mesures et les alternatives écartées, qui vivent dans le dossier de
cadrage et non dans le brouillon.
