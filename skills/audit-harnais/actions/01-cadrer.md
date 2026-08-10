# 01 - Cadrer

Du domaine demandé à un contrat figé et une liste d'instructions à cribler. Rien ne se juge ici.

## Input

Le domaine à auditer (`agent-config`, vault pro, vault perso, ou un projet) et le sous-domaine de la passe (`rules/`, `skills/`, scripts/hooks…). **Une passe = un sous-domaine** (la grille, section Méthode, porte le pourquoi). Sans précision, suivre l'ordre des domaines et sous-domaines de la grille ; si la demande couvre un domaine entier, proposer le découpage en passes ici, avant tout inventaire.

## Output

En tête de session d'audit : le commit de la grille, le contrat énoncé, l'inventaire du domaine, et la liste numérotée des instructions à cribler (fichier + intitulé court par instruction).

## Process

1. **Relever.** Le commit de la grille : `git log --oneline -1 -- audits/grille-harnais.md`, et son état de travail : `git diff --stat -- audits/grille-harnais.md`. Si la grille porte des modifications non commitées, le signaler et proposer de committer d'abord. Ne jamais l'éditer soi-même. *Pourquoi : le rapport cite ce commit pour être rejouable ; un audit contre une grille sale ne se rejoue pas.*
2. **Figer.** Énoncer le contrat : les critères de la grille sur ce domaine, rien d'autre. Lister les exclusions demandées par l'utilisateur (rapports à ne pas lire, critères hors passe). Le contrat ne se rouvre plus (`rules/reasoning.md`, contrat de questions).
3. **Inventorier.** Lancer les mesures d'inventaire de la grille (section « Mesures d'inventaire par domaine ») et lister les sous-domaines dans son ordre. Consigner les sous-domaines vides (memory absente, pas de `checks/`) comme mesurés, pas comme oubliés.
4. **Découper.** Ouvrir chaque fichier du domaine et le découper en instructions : un bloc normatif autonome (une règle avec son pourquoi, un interdit, une obligation, un trigger). Numéroter `<fichier>#<n>`. Un fichier mono-règle donne une instruction ; `workflow.md` en donne cinq. (Le pourquoi de cette unité de travail : règle transverse du routeur.)
5. **Annoncer.** Rendre le contrat et la liste à l'utilisateur avant de cribler. Un désaccord de découpage se corrige ici, pas après les mesures.

## Si ça casse

- **La grille est sale et l'utilisateur veut poursuivre quand même** → poursuivre, mais le contrat et l'en-tête du rapport porteront l'état sale : les verdicts ne seront pas rejouables.
- **Un fichier de l'inventaire est illisible ou exclu par le contrat** → « hors crible » avec sa raison ; ne jamais le découper de mémoire.
- **Le désaccord de découpage persiste à l'annonce** → stop, pas de criblage : cribler sur un découpage contesté produit des verdicts à refaire.

## Contrôle de sortie

- Le commit de la grille est relevé et son état de travail (propre ou sale) est dit explicitement.
- Le contrat énonce les critères couverts, le sous-domaine de la passe, ET les exclusions ; aucun verdict n'a encore été rendu.
- Chaque fichier de l'inventaire apparaît dans la liste d'instructions, ou porte la mention explicite « hors crible » avec sa raison (config pure, sous-domaine vide).

## Test

Scénarios dans `evals/eval.json` — notamment le refus d'auditer en éditant une grille sale.
