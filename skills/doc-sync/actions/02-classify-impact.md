# 02 - Classer l'impact

Pour chaque fichier du scope validé, détermine le régime (reflet/décision) et la surface doc cible.

## Input

Le scope validé de l'action 01 : la liste de fichiers changés, par repo.

## Output

Une classification par fichier : `chemin → impact → régime → cible doc`. Ou, si rien d'impactant, un constat d'arrêt (« aucune surface doc touchée »).

## Process

1. **Classer.** Pour chaque fichier du scope, déterminer l'impact, le régime, puis la surface cible. Le régime commande le traitement aval (reflet → réécrit, décision → signalé).

   | Pattern de chemin | Impact | Régime | Cible doc |
   |---|---|---|---|
   | `migration/`, `*Entity*`, `*Repository*`, `.sql` | schéma DB | reflet | memory `database.md` + README (section DB/archi) |
   | `*Controller*`, `*Dto*`, `*Request*`, `*Response*` | contrat API | reflet côté repo, **décision** côté contrat partagé | memory `api-docs.md` + README (section API) + **signaler** l'écart au contrat partagé (→ action 05) |
   | `*Service*`, `*Config*`, `*Orchestrator*` | archi/comportement | reflet | memory `codebase-map.md` + README (section archi/pipeline) |

2. **Cibler.** Les **noms de sections README ne sont pas figés** : viser « la section qui couvre X ». La structure réelle du README (lue au préalable, cf. action 04) fait foi.
3. **Router par régime.** Les cibles reflet partent vers les actions 03 (memory) puis 04 (README). Les cibles décision (contrat partagé, ADR, memory `decisions`) partent vers l'action 05 (signaler, ne pas écraser). En coordinateur, la classification vaut par repo : chaque enfant contre son propre code, le contrat partagé au parent.
4. **Arrêter si vide.** Si rien d'impactant (fix pur, test, refacto interne sans surface publique) → **le dire et s'arrêter**. Ne pas inventer de mises à jour pour justifier le run.

## Test

- Chaque fichier du scope reçoit un régime (reflet ou décision) et une cible doc, ou est explicitement écarté comme sans impact.
- Un fichier `*Controller*`/`*Dto*` en contexte coordinateur est marqué décision côté contrat partagé (routé vers 05), pas réécrit d'office.
- Un scope sans surface publique impactée produit un arrêt annoncé, aucune cible inventée.
