# 01 - Échafauder

De l'intention à un skill complet, prêt à vérifier.

## Input

L'intention du skill, en prose libre :

- Le but, en une phrase : ce qu'il fait, et quand on l'appelle.
- Le domaine : outil (un nom, ex. `jira`) ou activité (un verbe, ex. `review`).
- Les actions pressenties, si elles sont déjà en tête. Sinon on les dégage à l'étape 4.

## Output

Une arborescence sous `skills/<nom>/` : `SKILL.md`, un `actions/NN-<slug>.md` par action, `evals/eval.json`, plus `references/` et `assets/` si une action en a besoin.

## Process

1. **Lire.** Ouvrir [`../references/skill-authoring-fr.md`](../references/skill-authoring-fr.md) et les deux gabarits d'`../assets/` avant d'écrire quoi que ce soit. Toutes les règles citées plus bas y sont définies, elles ne sont pas recopiées ici.
2. **Nommer.** Choisir le nom selon la section « Nommage » de la convention, préfixe de domaine compris, puis appliquer son « Check de collision ».
   - **Garde.** Un recouvrement de description avec un skill installé arrête la création : remonter le choix (fusionner, renommer, resserrer) au lieu d'ajouter un deuxième candidat sur la même phrase.
3. **Choisir la forme.** Responsabilité unique et aucune connaissance à différer → mono-fichier, la méthode sous `## Process`. Plusieurs actions distinctes ou de la référence à charger à la demande → routeur plus `actions/`. Dans le doute, commencer mono-fichier.
4. **Cadrer les actions**, si routeur. Découper le but en actions à responsabilité unique, une action valant une étape vérifiable. Numéroter seulement si l'ordre est strict.
5. **Trancher le mode d'invocation.** Question explicite : ce skill écrit-il un fichier versionné, committe-t-il, pousse-t-il, supprime-t-il, ou envoie-t-il sur le réseau ?
   - **Garde.** Ce point se tranche **avant** d'écrire la description, jamais après : le mode change la forme de la description (R13), donc le décider ensuite oblige à la réécrire, et personne ne la réécrit.
6. **Copier `skill-template.md`** et le remplir. Le gabarit porte la liste des sections, leur ordre et leur statut — ne rien inventer à côté, ne rien réordonner. Le flux mermaid en `TD` montre chaque chemin, branches et retours de boucle compris : une branche dite en prose est une branche manquante du flux.
7. **Copier `action-template.md`** une fois par action, si routeur. Quatre sections, ni plus ni moins.
8. **Répartir les critères de vérification**, c'est le point où un skill part de travers.
   - Un critère qui **décide en cours de route** (« si tout candidat revient rouge, ne pas passer à l'action suivante ») devient une étape `**Garde.**` du `## Process`, sous-puce de l'étape qu'elle borne.
   - Un critère qui **constate** (« le fichier est relu, aucun placeholder ne survit ») devient une ligne du `## Test`, observable par exécution réelle.
   - Un critère qui juge **si le skill marche** (il part sur telle requête, il cède la main à un frère) va dans `evals/`, jamais inline : il demande une session neuve, donc il ne peut pas s'évaluer au milieu d'une exécution.
9. **Sortir les données lourdes.** Un gabarit à copier va dans `assets/`, une donnée à lire va dans `references/`. L'action cite le fichier par un lien relatif dans la phrase qui l'utilise, ne l'inline pas.
10. **Écrire les cas d'éval.** Un `evals/eval.json` en données pures, aux champs définis par R7 — jamais un nom d'outil ni un nom d'agent. R7 porte aussi la composition du corpus, exception des skills à invocation manuelle comprise, et il en est le seul home.
11. **Rédiger en français.** Tout le contenu, labels d'étapes et cellules de table compris. Seuls les huit en-têtes de structure restent en anglais. Si une source anglaise a servi, réécrire la prose au lieu de la traduire mot à mot.
12. **Déléguer la vérification.** Ne jamais jouer `02-validate` dans ce contexte, le confier à un sous-agent générique (Explore, general-purpose) qui n'a pas écrit le skill. *Pourquoi : la convention, section « Frame–Deliver–Checker ».*
    > Sous-agent : « Lis `skills/skill-craft/actions/02-validate.md` et joue-la telle quelle sur le skill `<nom>`. Tu n'as pas écrit ce skill et tu ne le corriges pas : rends le rapport, rien d'autre. »
    - **Garde.** Ne pas rendre la main tant que le lint sort rouge. Un skill livré non conforme fabrique la dette que ce skill existe pour éviter.

## Test

| Cas | Preuve |
| --- | --- |
| `python3 wrappers/claude/scripts/lint-skills.py --skill <nom>` sur le skill neuf | rend 0 |
| `python3 -c "import json; json.load(open('skills/<nom>/evals/eval.json'))"` | parse, chaque cas portant `skill` et `query` |
| relecture du corpus d'évals contre R7 | la composition attendue y est, exception des skills à invocation manuelle comprise |
| `grep -rn "supprimer cette ligne" skills/<nom>/` | ne rend rien, la ligne d'instruction du gabarit n'a pas survécu |
