# Grille d'audit du harnais

Crible d'admission au contexte permanent : chaque instruction du harnais y passe, une par une. L'objectif est la **stabilité**, pas la perfection — un harnais qui repose le moins possible sur la discipline du modèle dépend le moins possible du modèle.

**Source de vérité** : le harnais lui-même (ce repo). Le vault alimente et optimise, il ne fait pas foi. *(Décidé le 2026-08-10, appliqué à `ai-principles.md` le 2026-08-11.)*

**Sources consolidées** : `0_INBOX/2026-08-10-refonte-harnais-agent-config.md` (vault pro), `rules/ai-principles.md`, `rules/reasoning.md` (contrat de questions). Deux sources ont été démontées le 2026-08-11 : `rules/workflow.md`, supprimé, ses contraintes d'échec fermé reprises dans l'axe B ; `rules/ai-practices.md`, sorti du permanent vers **`banc-pratiques.md`**, compagnon vivant de cette grille.

---

## Méthode — un audit à la fois

- **Un audit = un domaine, contrat figé.** Les questions de l'audit sont les critères de cette grille, rien d'autre. Une découverte hors grille se capture en une ligne et ne se creuse pas. La grille se révise **entre** deux audits, jamais pendant.
- **Ordre** : `agent-config` (socle) → vault pro → vault perso → projets (qui héritent du socle). Dans chaque domaine, par sous-domaine : `rules/`, `skills/`, `agents/`, `scripts`/hooks, `CLAUDE.md`/output-styles, `settings.json` (bindings, permissions), memory auto. Un sous-agent passe le même crible qu'un skill, pas celui d'un script : il porte de la prose normative et hérite du contexte permanent.
- **Une passe = un sous-domaine.** Le scope concentre le contexte (les fichiers d'un même sous-domaine se comparent entre eux) et borne le coût d'une session d'audit ; un domaine entier se couvre en plusieurs passes, jamais en une. Un hook n'est pas un sous-domaine à part : c'est un script (contraintes du **garde déterministe**, axe B) plus une ligne de trigger dans `settings.json`, chacun audité dans sa passe.
- **Horodatage** : un rapport d'audit est un instantané immuable, nommé `audits/AAAA-MM-JJ-audit-<domaine>.md` ; l'audit suivant du même domaine est un nouveau fichier, jamais un edit. La grille, elle, est vivante et non horodatée — git porte son historique (`git log --oneline -- audits/grille-harnais.md`), pas de champ `version:` manuel qui divergerait au premier edit oublié. Chaque rapport cite en en-tête le commit de la grille contre laquelle il a tourné.
- **Traçabilité** : chaque constat du rapport cite sa mesure (commande + sortie) ou porte « supposé ». Un chiffre repris de la note d'inbox est un chiffre du 2026-08-10 : le remesurer avant de décider.
- **Une règle ne se valide pas en usage courant.** Une observation tirée du travail normal n'a pas de bras de contrôle : on ne sait pas ce que la même tâche aurait donné sans la règle, et l'usage courant ne produit jamais ce contrefactuel. Éprouver une règle demande donc une **session de runs bornée** — périmètre fixé, deux bras, critères de réussite écrits **avant** de lire les réponses. Hors de ce cadre, une observation se consigne comme **observation**, jamais comme preuve, et ne promeut ni ne supprime rien. *Ce point gouverne l'A/B de l'axe A et le test comportemental du relevé de formulation, qui le supposaient tous deux sans le dire.*

  **POURQUOI** : l'usage courant ne rend que des anecdotes favorables — celui qui a écrit la règle est celui qui remarque qu'elle a joué. Et une date de mise en test donne l'illusion que la preuve s'accumule, alors que rien ne s'accumule entre cette date et le premier run borné. *Mesuré le 2026-08-11 : cinq pratiques « en test depuis » fin juillet, **zéro observation concluante** — douze jours d'usage courant n'avaient produit aucune preuve, et le label laissait croire le contraire.*

---

## Le crible — deux axes, deux contrôles, deux relevés

Chaque instruction reçoit **une valeur sur chaque axe**, et le croisement rend son verdict. Les deux
contrôles se rendent après, une fois toutes les instructions d'un fichier criblées. Les deux relevés
ne rendent aucun verdict, ils publient une mesure.

**Il n'y a plus de cascade, et ce n'est pas un choix de forme.** Les huit passes rendaient déjà des
verdicts multi-critères sur une même instruction (« C5 + C4 » le 2026-08-25, « C7 + C1 + C2 » sur une
même description le 2026-08-11), alors que la cascade prescrivait de sortir au premier critère
disqualifiant. Le profil décrit ce que les passes font ; la cascade décrivait ce qu'elles étaient
censées faire. *Refonte décidée le 2026-08-26, base de preuve dans
`audits/2026-08-26-cadrage-grille-cible.md`.*

**Correspondance avec l'ancienne nomenclature**, parce que les huit rapports horodatés citent C1 à C8
par leur nom et qu'un rapport immuable ne se réécrit pas :

| Ancien | Devenu | Pourquoi |
|---|---|---|
| C1a — inférable | valeur *reconstructible du repo* de l'axe A | c'est une origine parmi cinq, pas une question à part |
| C1b — déjà natif | valeurs *natif du modèle* / *natif du harnais* de l'axe A | son A/B n'a jamais tourné en 8 passes : c'est un contrôle documentaire |
| C2 — déterminisable | valeur *garde déterministe* de l'axe B | le mécanisme est une destination, pas un critère |
| C3 — falsifiable | **contrôle 1, testabilité** | mécanisable de bout en bout, il n'a pas sa place dans un jugement de présence |
| C4 — unique | axe A entier | « existe-t-il déjà ailleurs » est la même question, seul l'ailleurs change |
| C5 — scopée | axe B entier | ses trois lignes étaient trois destinations |
| C6 — budget | **relevé 1, poids** | zéro instruction disqualifiée en 8 passes |
| C7 — rentable | **relevé 2, formulation** | il ne juge jamais la présence, seulement l'écriture |
| C8 — cohérent | **contrôle 2, cohérence** | élargi au groupe, sa portée s'arrêtait au fichier |

---

### Axe A — d'où vient ce que l'instruction porte ?

Une seule valeur, testée dans cet ordre. La première qui répond ferme l'axe.

| Valeur | Test |
|---|---|
| **natif du modèle** | la page de prompting du modèle courant le nomme, ou prescrit de le retirer |
| **natif du harnais** | le system prompt de l'outil le porte. **Énumération à la main, aucun grep ne l'atteint** |
| **ailleurs dans le harnais** | grep du motif central, **puis** énumération des instructions à même effet |
| **reconstructible du repo** | sondage d'un contexte neuf, compté en appels d'outil |
| **nulle part** | aucune des quatre |

**Commencer par lire la page de prompting du modèle courant** (table des sources plus bas). Elle
tranche gratuitement une partie des cas — « *Claude Opus 5 verifies its own work without being told
to. If your prompt contains explicit verification instructions […] remove them* » (vérifié le
2026-08-11). Noter dans le rapport contre quel modèle la passe a tourné : c'est ce qui datera ses
verdicts quand le modèle changera.

**La distinction qui a décidé une passe entière** : la page vise la re-vérification de sa **propre
sortie**, jamais le **grounding** — consulter une source externe avant d'affirmer. Une règle qui ne
fait que du grounding ne relève pas du natif. *`audits/2026-08-11-…-rules-reasoning-c1b.md`.*

**Le piège du natif, à lire avant de conclure.** Un suivi irrégulier n'est pas une preuve que
l'instruction est nécessaire. C'est aussi le symptôme documenté d'une couche trop longue : « *If
Claude keeps doing something you don't want **despite having a rule against it**, the file is
probably too long and the rule is getting lost* » (vérifié le 2026-08-11). Les deux hypothèses
prédisent la même observation, et l'intuition va vers la mauvaise. **À LA PLACE de** renforcer
l'instruction, monter l'A/B : le bras sans-instruction tourne sur une couche plus courte, donc un
comportement **meilleur** sans la règle dit qu'elle était une victime de la longueur.

**Le grep ne couvre pas la valeur « natif du harnais », par construction.** La couche la plus lourde
du contexte permanent n'est dans aucun fichier du repo. Trois occurrences mesurées, chacune invisible
à tout grep du domaine : « déléguer par défaut » contre « *Do not call the AgentTool unless the user
requested it* », AP4 contre la section *Delivering work*, et l'instruction #2 de `reasoning.md`
contre la section *Corrections*. **Aucun instrument n'existe pour cette valeur**, et une passe qui
l'invoque cite le system prompt tel qu'injecté dans sa session, en le disant.

**Le doublon par conséquence, invisible au grep.** Deux instructions peuvent prescrire le même
comportement sans partager un mot : elles partagent un **effet**, pas un motif. **À LA PLACE de**
chercher des formulations voisines, énumérer les autres instructions du harnais qui produisent le
même geste. *Cinq instructions dans trois fichiers supprimaient chacune le filtre « vérifier
seulement en cas de doute », dont trois qu'aucun grep ne pouvait voir — `2026-08-10-…-rules.md`.*

**Le seuil de sondage** : moins de 3 appels d'outil, c'est reconstructible à coût faible. *Seuil
conventionnel, aucune source ne le porte.* **Il ne décide pas seul**, voir le dosage sous l'axe B.

**Ce que le sondage ne peut pas faire, et il faut le dire dans le verdict** : un sous-agent hérite
des règles globales, donc son contexte n'est jamais neuf. Le résultat est une approximation, marquée
telle quelle. *Mesuré le 2026-08-10, deux passes, `-c1-c4.md:32`.*

---

### Axe B — à quel moment l'instruction doit-elle être chargée ?

Une seule valeur. C'est un axe de **placement**, pas de portée.

| Valeur | Test |
|---|---|
| **un garde déterministe** | l'invariant porte sur un artefact versionné ou un appel d'outil observable |
| **le permanent** | le déclencheur tombe à chaque session ou presque, ou la re-dérivation coûte ≥ 3 appels |
| **une couche chargée à la demande** | le déclencheur est un **événement**, ou l'instruction relève d'un **niveau** — référence, corps de skill, action |
| **nulle part** | l'axe A la donne déjà portée **au même moment de chargement** |

#### Le garde déterministe

| L'invariant porte sur | Mécanisme |
|---|---|
| un artefact versionné (message de commit, fichier) | hook git `core.hooksPath` + check CI |
| une action éphémère de l'agent (commande tapée, écriture réseau) | hook harnais `PreToolUse` — **seul mécanisme possible** |
| le **routage** d'un skill à effet de bord | `disable-model-invocation: true`, un champ de frontmatter |
| un raisonnement (aucun appel d'outil observable) | aucun — le hook ne voit que les tool calls |

**Contraintes du mécanisme, non renégociables** : échoue fermé, aucun chemin absolu en dur, calibré
sur un cas positif fabriqué à la main. *Les cinq cas mesurés qui les fondent : vault,
`3_KNOWLEDGE/Patterns/deterministic-guards-failure-modes.md`.* **Séparation logique/binding** : la
logique vit dans un script autonome testable hors agent, le binding propriétaire fait ≤ 10 lignes.

**La couverture partielle est le cas courant, pas l'exception.** Un linter prend souvent la
**présence** d'un invariant en laissant le **jugement** à la prose (checkstyle sur la Javadoc,
`eslint-plugin-testing-library` sur le rôle avant `testId`). Le verdict est alors « réduire à
l'increment », jamais « sortir ». *Trois cas, `2026-08-10-…-rules.md`.*

#### Le permanent, et le dosage qui l'ouvre

**Un coût sans sa fréquence ne dit rien.** Une règle se paie en mots à **chaque** session. La
re-dérivation ne se paie que quand son déclencheur tombe. Le dosage est le produit des deux axes.

| Appels pour re-dériver | Fréquence du déclencheur | Placement |
|---|---|---|
| < 3 | quelle qu'elle soit | **nulle part** — laisser reconstruire |
| ≥ 3 | à chaque session, ou presque | **le permanent** |
| ≥ 3 | événement rare | **à la demande** — alerte minimale au permanent, détail plus bas |

#### La couche chargée à la demande

**Le test qui la sépare du permanent** : le déclencheur est-il un **fichier**, un **événement**, ou
un **niveau** ?

- Un **fichier** se nomme dans un frontmatter `paths:`. Attention, `paths:` conditionne l'activation
  à un fichier ouvert : l'appliquer à une instruction qui se déclenche sur une intention la rend
  inerte la plupart du temps. *Aucune des 26 descriptions de skills n'y gagnait, mesuré le
  2026-08-11.*
- Un **événement** n'a aucun chemin. L'instruction qui l'attend se fait facturer à chaque session
  pour servir quelques fois par mois. Exemples rencontrés : un comptage qui rend « zéro », un
  diagramme à dessiner, un échec de build, une analyse dont la conclusion appellera des edits.
- Un **niveau** est le cas d'un corps de skill : l'instruction est au bon endroit du harnais mais au
  mauvais étage — de la logique métier dans un routeur, un critère dans une action au lieu d'une
  référence. *Quatre verdicts le 2026-08-25, sur `doc-sync`.*

**La part gardée au permanent doit suffire à savoir qu'il faut charger le reste, jamais à faire le
travail.** Modèles existants : `mermaid.md` renvoie au skill `mermaid-craft`, `ponctuation.md` à
`ref-ponctuation.md`.

**Ce qui descend est la preuve, jamais le critère**, quand le critère est lui-même indéduisible. Une
référence non chargée est un bon home pour six corpus et 1 019 occurrences. C'en est un mauvais pour
la règle de décision, qu'un contexte neuf devra appliquer sans l'avoir lue. **« C'est déjà écrit
ailleurs » n'est une raison de supprimer que si cet ailleurs est chargé.** *Mesuré sur #16 de
`reasoning.md` le 2026-08-11, par le renversement d'une reco.*

---

### Le verdict — ternaire, lu du croisement

| Verdict | Quand |
|---|---|
| **garder tel quel** | l'axe A rend « nulle part », ou l'axe B place ailleurs qu'où l'instruction vit |
| **réduire à l'increment** | l'axe A la donne partiellement portée : seul ce que la source ne couvre pas survit |
| **sortir** | l'axe A la donne portée **entièrement**, au même moment de chargement que l'axe B désigne |

**Le terme du milieu est celui qui manquait.** Neuf verdicts des passes précédentes l'ont réclamé
sans jamais l'obtenir, tous sur la même forme : le natif porte l'impératif, l'instruction porte un
piège mesuré ou une asymétrie que le natif ignore. **Écrire l'increment gardé**, en mots, dans le
verdict : sans lui la réduction est une intention, pas une action.

**Deux instructions de même contenu mais d'axe B différent ne sont pas des copies.** Le contenu se
répète, la fonction non. *Mesuré le 2026-08-11 : la clause `NE PAS` du frontmatter **route**, la
liste de frères du corps **retient**. Couper la seconde comme un doublon fait tomber les redirections
correctes de 7/9 à 5/9, et le verdict a été abandonné sur cette mesure.* C'est le seul verdict de
tout le corpus qu'une mesure externe a réfuté, et il vient d'une comparaison de contenus sans
comparaison de moments.

**Quand deux instructions partagent contenu **et** moment, une seule survit, et elle ne se
hiérarchise pas.** Le foyer se désigne par **où le geste se fait**, pas par l'ancienneté ni par le
niveau. La couche qui perd se déclare délibérément partielle. Un doublon statique est bénin, un
doublon volatil diverge au premier edit.

---

### Contrôle 1 — testabilité

Rendu par instruction, après les deux axes. **La règle gardée en prose porte-t-elle une condition de
violation observable ?**

| Niveau | Ce qu'il vaut |
|---|---|
| 1 | garde déterministe — suivi garanti *(c'est une valeur de l'axe B, pas un niveau à atteindre ici)* |
| 2 | règle falsifiable **+ sa commande de vérification, son cas d'éval, ou son calibrage** |
| 3 | impératif court non ambigu — suivi probabiliste |
| 4 | prose vague ou de style — **supprimer ou reformuler en 2/3** |

**Sur un contrat de routage, la commande de vérification est un cas d'éval**, et le verdict reste un
comptage : le corpus porte un cas positif, **et un cas `expect_trigger: false` par frère cité en
clause NE PAS**. Sans ce cas négatif, l'instruction retombe au niveau 3. *Vérifier qu'un skill part
ne vérifie pas qu'il ne part pas à tort, et c'est l'autre moitié du contrat.*

**Un corpus d'éval ne suffit pas s'il ne discrimine rien.** Trois évals sur neuf étaient vertes alors
que le modèle **nu**, privé du skill, passait les mêmes critères. Le niveau 2 exige donc qu'au moins
un critère soit **échoué par le bras nu**. *Mesuré le 2026-08-11, annexe de déclenchement.*

**Une règle de jugement se teste par ses calibrages.** Un critère non mécanisable n'est ni un hook,
ni une commande, ni un impératif court, et il n'était donc nulle part. Ses cas de calibrage, avec
leur verdict attendu, **sont** sa commande de vérification. *Cas R13 de `doc-sync`, 2026-08-25.*

**Deux angles morts, à dire dans le verdict plutôt qu'à ignorer** : l'instrument compte les cas
négatifs, il ne juge pas s'ils sont bien choisis. Et un frère cité en clause NE PAS mais archivé ne
peut pas recevoir de cas — le noter, au lieu de compter un manque.

**Exception assumée** : `ai-principles.md` ne prescrit rien donc n'est pas falsifiable, mais il est
le repli quand une règle concrète est muette. Il se **réduit** (titres + une ligne de pourquoi), il
ne se supprime pas.

---

### Contrôle 2 — cohérence

Rendu **par fichier**, **par couple** dès que le fichier déclare une annexe, et **par groupe** dès
que plusieurs fichiers appliquent un même moule. Les trois portées sont obligatoires : cinq des six
défauts que ce contrôle a manqués venaient d'une portée trop étroite.

| Défaut | Portée | Action |
|---|---|---|
| deux instructions se contredisent, ou leurs exceptions se recouvrent en s'opposant | fichier | trancher, ou rendre l'articulation explicite |
| redondance interne — deux instructions du fichier prescrivent la même chose autrement | fichier | fusionner |
| instruction orpheline, sans rapport avec le propos du fichier | fichier | déplacer — **sauf si son vrai foyer n'est pas chargé**, auquel cas garder et le dire |
| une articulation vraie mais **tue**, qu'un lecteur citant un extrait conclurait fausse | fichier | l'écrire |
| une annexe contredit la **justification** de sa règle | couple | trancher, en partant du principe que l'annexe est la plus récente |
| l'annexe ne fonde qu'une part des instructions du fichier | couple | relever la couverture. Un `TRIGGER` sans cas mesuré se marque « instauré sans mesure » |
| une section promet plus que son corpus ne contient (un `## Test` qui annonce un cas absent) | couple | soit le cas existe, soit la promesse sort |
| **un moule appliqué partiellement** — une case que la moitié du groupe remplit | **groupe** | trancher dans un sens, et le porter dans la convention pour que le suivant ne re-tranche pas |
| deux sources **extérieures** au fichier prescrivent des défauts opposés | groupe | nommer le conflit dans la règle qui revendique l'autorité |

**POURQUOI la portée de groupe** : le prénom présent dans 5 corps d'experts sur 9, et la sortie en
`references/` faite par 8 sur 9, sont des incohérences réelles qui ne vivent dans **aucun** fichier.
Un verdict par instruction ne les voit pas, un verdict par fichier non plus. *Mesuré le 2026-08-11.*

---

### Relevé 1 — le poids

**Aucun verdict de dépassement.** Décidé par l'humain le 2026-08-21, et confirmé par le cadrage du
2026-08-26 : un plafond chiffré fabrique un dilemme que rien ne tranche, puisqu'il met une
instruction survivante en concurrence avec un nombre, alors que la grille interdit par ailleurs de
couper l'une pour tenir l'autre.

**À LA PLACE de** demander « la couche tient-elle sous N mots », demander **« qu'est-ce que la couche
a acheté avec sa croissance »**. Une couche qui grossit de 400 mots de fait indéduisible est saine.
Une couche qui grossit de 400 mots de preuve est en dette, au même poids.

**Périmètre** : tout ce qui entre dans chaque session — les règles non scopées, l'output style actif,
les blocs `description` des skills montés, l'index de memory auto du projet courant. **Le corps d'un
skill n'y entre pas**, il ne se charge qu'à l'invocation.

```bash
wc -w $(grep -L '^paths:' rules/*.md) wrappers/claude/rules/*.md \
      wrappers/claude/output-styles/chat-style.md

# + les blocs `description` des skills montés (~/.claude/skills → skills/)
# Parseur YAML obligatoire, pas de regex : elle avale le marqueur de bloc `>-`
# et l'indentation, et surcompte de ~1 % (mesuré le 2026-08-11).
python3 -c "
import re,glob,yaml
print(sum(len(yaml.safe_load(re.match(r'---\n(.*?)\n---\n',open(f,encoding='utf-8').read(),re.S).group(1))['description'].strip().split()) for f in glob.glob('skills/*/SKILL.md')))"

# + MEMORY.md de la memory auto du projet courant, variable par projet
```

**Ce que le relevé rend** : la somme, sa trajectoire depuis la passe précédente, le `wc -w` par
fichier trié, et pour chaque fichier qui a grossi, la **nature** de ce qui l'a fait grossir.

**Remesurer en ouverture de passe, ne jamais reprendre le chiffre du rapport précédent.** Une couche
auditée grossit pendant l'audit, et une cible touchée n'est pas un état acquis : la couche a regagné
295 mots après avoir atteint sa cible le 2026-08-11, par une promotion justifiée.

*Le seul plafond dur qui existe est mécanique et il est ailleurs : 1 536 caractères par entrée de
description, et un budget de listing à 1 % de la fenêtre au-delà duquel Claude Code **supprime** les
descriptions des skills les moins invoqués (doc vérifiée le 2026-08-11).*

---

### Relevé 2 — la formulation

**Aucun verdict non plus.** L'alerte trie, elle ne tranche pas, et un dépassement n'est pas un
défaut. Décomposer l'instruction en quatre parts — **grille de lecture pour l'audit, jamais gabarit
d'écriture** :

| Part | Statut |
|---|---|
| impératif — le quoi, et son alternative si c'est une négation, **jamais l'interdit sec** | porteur, irréductible |
| pourquoi — une ligne | porteur **si la raison apporte un fait indéduisible**. Sinon compressible |
| seuil / exception | porteur **si mesurable** ; sinon c'est un défaut de testabilité déguisé en précision |
| preuve, cas vécu, méta-commentaire | **compressible** — sort vers une référence chargée à la demande |

**Le seuil se remesure par corpus, il ne s'hérite jamais.** Alerte à 2× la médiane des blocs
normatifs du corpus courant. **Les médianes déjà mesurées vivent dans `audits/axes-protocole.md`, qui en est le seul
foyer** — les recopier ici les ferait diverger, et c'est déjà arrivé une fois.

**Sur un contrat de routage, la quatrième part n'existe pas.** L'impératif est le « quoi », le seuil
est la liste de termes déclencheurs, l'exception est la clause « NE PAS utiliser pour → frère ». Un
terme déclencheur est un seuil, donc porteur **s'il est couvert par un cas d'éval** ; sans éval, il
n'est pas une précision mais une assertion non testée, et c'est lui qui est compressible.

| Cas | Lecture |
|---|---|
| sous l'alerte, quatrième part absente | rien à faire |
| **sous l'alerte, quatrième part présente** | extractible quand même. Le poids d'un fichier n'est pas la somme de ses dépassements |
| dépassement porté par la quatrième part | l'extraire, l'instruction garde impératif + pourquoi + trigger |
| **dépassement déjà dans une référence non chargée** | **rien à faire** — la référence *est* la destination |
| dépassement porté par l'impératif | ce sont plusieurs instructions empilées, chacune repasse aux deux axes |
| impératif plus court que pourquoi + preuve | **red flag** — l'instruction argumente plus qu'elle ne prescrit |
| dépassement porté par du **décoratif** (persona, prénom, teaser) | il n'achète aucun comportement observable. Trancher au niveau du groupe |

**Deux artefacts d'instrument à connaître avant de lire un chiffre.** Un découpage automatique compte
des paquets, pas des instructions : il fusionne une section avec son tableau, et empile deux
impératifs sous un seul trigger. **Le découpage manuel du cadrage fait foi.** Et l'alerte dérive de
la médiane du corpus qu'elle juge, donc elle se desserre quand le corpus grossit — 32 à 36 mots en
dix jours, mesuré le 2026-08-21.

```bash
# Mots d'une instruction — plage de lignes issue du découpage du cadrage
sed -n '<début>,<fin>p' <fichier> | wc -w

# Médiane du corpus, pour recalibrer l'alerte
for f in $(grep -L '^paths:' rules/*.md) wrappers/claude/rules/*.md; do
  printf '%s\t%s\t' "$f" "$(grep -c '^\(- \|\*\*[A-ZÀ-Ü]\|#\+ \)' "$f")"; wc -w < "$f"
done
```

**Test comportemental, échantillonné** : retirer la part jugée compressible, donner à un contexte
neuf une tâche qui déclenche l'instruction, comparer. S'il change, la part était porteuse. Un test
coûte une session, donc le réserver aux instructions au-dessus de l'alerte. Les autres se marquent
« jugé sur pièce ». *Ce test n'a jamais été joué en 8 passes, et chaque rapport le dit.*

---

## Sources normatives par sous-domaine

Contre quoi juger la **conformité de construction** d'un artefact (format, frontmatter, anatomie). On stocke le **pointeur**, jamais une copie (axe A : contenu volatil — la doc a déjà migré de domaine une fois).

**Skills perso de `skills/`** — la convention locale fait foi, elle est versionnée avec les skills qu'elle borde :

| Mécanisme | Source | Vérifié |
|---|---|---|
| Anatomie d'un skill et d'une action | `skills/skill-craft/assets/skill-template.md` et `action-template.md` | versionnés, `lint-skills.py` dérive d'eux sa liste de sections |
| Les règles autour de l'anatomie (frontmatter, nommage, subagents, ce qui se vérifie) | `skills/skill-craft/references/skill-authoring-fr.md` | versionné, section « Le rang des sources » |

**La source support se relit en ouverture d'une passe `skills/`**, comme la page de prompting par modèle plus bas. Si le standard ouvert a bougé depuis sa date de vérification, le delta devient un **constat du rapport**, une révision de la convention proposée à l'humain entre deux audits, jamais une correction en silence (règle transverse d'`audit-harnais` : la grille ne se touche pas pendant l'audit).

**Un écart déjà assumé n'est pas un constat.** La convention le porte avec ses deux valeurs et son motif, comme R5 sur le plafond de description, 1 536 caractères contre 1 024 dans la spec. Le rapport ne le compte que si le motif a disparu ou si les valeurs ont changé.

**Standards ouverts multi-agents** — la couche portable, à préférer quand elle couvre la fonction :

| Mécanisme | Source | Vérifié |
|---|---|---|
| Skills (**support** : les skills perso se jugent contre la convention ci-dessus) | <https://agentskills.io/specification> + repo `anthropics/skills` | 2026-08-10, fetch |
| AGENTS.md | <https://agents.md> | supposé (standard connu, non re-fetché) |
| MCP | <https://modelcontextprotocol.io> | supposé |

**Propriétaire Claude Code** — le binding, confiné sous `wrappers/claude/` :

| Mécanisme | Source | Vérifié |
|---|---|---|
| Hooks | <https://code.claude.com/docs/en/hooks> | 2026-08-10, fetch |
| Output styles | <https://code.claude.com/docs/en/output-styles> | 2026-08-10, fetch |
| CLAUDE.md / memory | <https://code.claude.com/docs/en/memory> | 2026-08-10, via agent doc |
| Subagents | <https://code.claude.com/docs/en/sub-agents> | slug confirmé par liens |
| Scripts / checks | pas de doc — la norme est **ShellCheck** + les contraintes du **garde déterministe** (échec fermé, calibrage) | — |
| Index complet | <https://code.claude.com/docs/llms.txt> | 2026-08-10 |

**Rédaction d'instructions** — contre quoi juger l'axe A et le relevé de formulation, pour que la grille ne se valide pas contre la doctrine qu'elle audite :

| Sujet | Source | Vérifié |
|---|---|---|
| Rédaction de skills (« Does this paragraph justify its token cost? », degrees of freedom) | <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices> | 2026-08-10, fetch |
| Rédaction de prompts/règles (motivation derrière l'instruction, dire quoi faire plutôt que quoi éviter) | <https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-4-best-practices> — l'URL sert désormais la page courante **toutes générations** | 2026-08-11, fetch |
| **Comportements natifs du modèle courant, et instructions à retirer — l'autorité de l'axe A** | <https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5> — une page par modèle (`prompting-claude-<modèle>`) | 2026-08-11, fetch |
| **Élagage du contexte permanent** (« *Would removing this cause Claude to make mistakes?* », « *If Claude already does something correctly without the instruction, delete it or convert it to a hook* ») | <https://code.claude.com/docs/en/best-practices> | 2026-08-11, fetch |
| CLAUDE.md (< 200 lignes, contexte = bien public) | <https://code.claude.com/docs/en/memory> | 2026-08-10, via agent doc |

**La page par modèle est datée par construction, et c'est le point** : ses prescriptions s'inversent d'une génération à l'autre — ce qu'il fallait dire à un modèle devient ce qu'il faut retirer au suivant. Une passe qui juge l'axe A contre la page d'une génération précédente valide des instructions que le modèle courant subit. **Relire cette page en ouverture de chaque passe**, et noter dans le rapport contre quel modèle la passe a tourné : c'est ce qui datera ses verdicts quand le modèle changera.

**Point tranché le 2026-08-10** (doc officielle, section AGENTS.md de la page memory) : Claude Code ne lit **pas** `AGENTS.md` nativement — seul `CLAUDE.md` est lu ; s'ils coexistent, `AGENTS.md` est ignoré. Deux ponts documentés : import `@AGENTS.md` en tête de `CLAUDE.md`, ou symlink. **Conséquence** : la couche standard reste possible — le contenu vit dans `AGENTS.md` (portable), `CLAUDE.md` se réduit à l'import. Même motif logique/binding que `checks/` + hook. **Portée** : ce pont ne vaut que pour les `CLAUDE.md` de projet ; les règles globales passent par les symlinks de `sync-rules.sh`, mécanisme distinct à auditer séparément.

---

## Mesures d'inventaire par domaine

À lancer en ouverture d'audit, avant tout jugement :

```bash
# Poids du contexte permanent → la commande du relevé de poids (une seule définition)

# Couche déterministe réelle
ls checks/ 2>/dev/null; ls wrappers/claude/scripts/hooks/
git config core.hooksPath   # sur chaque repo du domaine

# Doublons inter-couches (par motif jugé, pas de regex unique)
# Symlinks de règles à jour (bash obligatoire : shebang bash, `set -o pipefail` casse sous dash)
bash wrappers/claude/scripts/sync-rules.sh
```

