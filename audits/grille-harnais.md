# Grille d'audit du harnais

Crible d'admission au contexte permanent : chaque instruction du harnais y passe, une par une. L'objectif est la **stabilité**, pas la perfection — un harnais qui repose le moins possible sur la discipline du modèle dépend le moins possible du modèle.

**Source de vérité** : le harnais lui-même (ce repo). Le vault alimente et optimise, il ne fait pas foi. *(Décidé le 2026-08-10 — inverse l'en-tête actuel d'`ai-principles.md`, à corriger.)*

**Sources consolidées** : `0_INBOX/2026-08-10-refonte-harnais-agent-config.md` (vault pro), `rules/ai-principles.md`, `rules/reasoning.md` (contrat de questions). Deux sources ont été démontées le 2026-08-11 : `rules/workflow.md`, supprimé, ses contraintes d'échec fermé reprises en C2 ; `rules/ai-practices.md`, sorti du permanent vers **`banc-pratiques.md`**, compagnon vivant de cette grille.

---

## Méthode — un audit à la fois

- **Un audit = un domaine, contrat figé.** Les questions de l'audit sont les critères de cette grille, rien d'autre. Une découverte hors grille se capture en une ligne et ne se creuse pas. La grille se révise **entre** deux audits, jamais pendant.
- **Ordre** : `agent-config` (socle) → vault pro → vault perso → projets (qui héritent du socle). Dans chaque domaine, par sous-domaine : `rules/`, `skills/`, `agents/`, `scripts`/hooks, `CLAUDE.md`/output-styles, `settings.json` (bindings, permissions), memory auto. Un sous-agent passe le même crible qu'un skill, pas celui d'un script : il porte de la prose normative et hérite du contexte permanent.
- **Une passe = un sous-domaine.** Le scope concentre le contexte (les fichiers d'un même sous-domaine se comparent entre eux) et borne le coût d'une session d'audit ; un domaine entier se couvre en plusieurs passes, jamais en une. Un hook n'est pas un sous-domaine à part : c'est un script (critères d'échec fermé de **C2**) plus une ligne de trigger dans `settings.json`, chacun audité dans sa passe.
- **Horodatage** : un rapport d'audit est un instantané immuable, nommé `audits/AAAA-MM-JJ-audit-<domaine>.md` ; l'audit suivant du même domaine est un nouveau fichier, jamais un edit. La grille, elle, est vivante et non horodatée — git porte son historique (`git log --oneline -- audits/grille-harnais.md`), pas de champ `version:` manuel qui divergerait au premier edit oublié. Chaque rapport cite en en-tête le commit de la grille contre laquelle il a tourné.
- **Traçabilité** : chaque constat du rapport cite sa mesure (commande + sortie) ou porte « supposé ». Un chiffre repris de la note d'inbox est un chiffre du 2026-08-10 : le remesurer avant de décider.
- **Une règle ne se valide pas en usage courant.** Une observation tirée du travail normal n'a pas de bras de contrôle : on ne sait pas ce que la même tâche aurait donné sans la règle, et l'usage courant ne produit jamais ce contrefactuel. Éprouver une règle demande donc une **session de runs bornée** — périmètre fixé, deux bras, critères de réussite écrits **avant** de lire les réponses. Hors de ce cadre, une observation se consigne comme **observation**, jamais comme preuve, et ne promeut ni ne supprime rien. *Ce point gouverne l'A/B de C1b et le test comportemental de C7, qui le supposaient tous deux sans le dire.*

  **POURQUOI** : l'usage courant ne rend que des anecdotes favorables — celui qui a écrit la règle est celui qui remarque qu'elle a joué. Et une date de mise en test donne l'illusion que la preuve s'accumule, alors que rien ne s'accumule entre cette date et le premier run borné. *Mesuré le 2026-08-11 : cinq pratiques « en test depuis » fin juillet, **zéro observation concluante** — douze jours d'usage courant n'avaient produit aucune preuve, et le label laissait croire le contraire.*

---

## Le crible — cascade de 8 critères

Chaque instruction descend la cascade ; elle sort au premier critère qui la disqualifie. **C1→C5 et C7 se jugent par instruction**, **C8 par fichier** (une fois ses instructions criblées), **C6 est le seul critère global** (un budget est une somme, une instruction seule ne le viole jamais). C7 ne disqualifie pas une instruction, il disqualifie sa formulation.

### C1 — Inférable ?

**Trier d'abord par nature** — les deux natures n'ont ni la même question ni le même test. Une instruction de **fait** transmet une information (une commande, un port, une convention) ; une instruction de **comportement** demande une manière d'agir (vérifier, déléguer, demander avant d'agir, borner une analyse). Le tri tient à une question : *retirer l'instruction laisse-t-elle un trou d'information, ou un trou de conduite ?*

#### C1a — Fait : l'information est-elle retrouvable ?

Un modèle sans cette instruction la retrouverait-il dans le code, la config ou la doc du repo ?

| Cas | Action |
|---|---|
| Inférable, coût de découverte faible | **Supprimer** — laisser inférer |
| Inférable, coût élevé, info stable | Synthèse courte |
| Inférable, coût élevé, info volatile | **Pointeur** vers la source, jamais une copie |
| Non-inférable (décision, contrainte d'env, piège) | Garder → C2 |

**Test** : demander à un contexte neuf (sous-agent sans la règle) de retrouver l'info. S'il y arrive en < 3 appels d'outil, c'est inférable à coût faible *(seuil conventionnel, aucune source ne le porte — révisable entre deux audits)*.

#### C1b — Comportement : le modèle le fait-il déjà sans qu'on le dise ?

| Cas | Action |
|---|---|
| Déjà porté nativement — par le modèle ou par le system prompt du harnais | **Supprimer.** Le coût n'est pas que des mots : une instruction redondante avec le comportement natif produit du **sur**-comportement |
| Fait parfois, jamais de façon fiable | Garder → C2, et viser le déterministe — c'est le cas type d'un hook. **Mais lire le piège ci-dessous avant de conclure** |
| Contredit un défaut du modèle ou de l'outil | Garder → C2. C'est le cœur non-inférable |
| Re-dérivable, mais à un coût que la session repaie chaque fois | Garder → C2, **au dosage ci-dessous**. Sans cette ligne, un invariant que le modèle sait reconstruire en dix appels d'outil n'a nulle part où survivre |

#### Le dosage du « coût élevé » — il vaut pour C1a et pour C1b

**« Trop coûteux à inférer » ne se juge pas seul.** Une règle se paie en mots à **chaque** session. La re-dérivation, elle, ne se paie que quand son déclencheur tombe. Un coût sans sa fréquence ne dit donc rien, et c'est là que le critère devenait vague.

Les deux instruments existent déjà dans cette grille, dans deux critères séparés : **C1a** compte les appels d'outil qu'un contexte neuf demande, **C5** tranche si le déclencheur est un fichier ou un événement rare. Le dosage est leur produit.

| Appels pour re-dériver | Fréquence du déclencheur | Sort |
|---|---|---|
| < 3 | quelle qu'elle soit | **Laisser inférer** |
| ≥ 3 | à chaque session, ou presque | **Garder au permanent** |
| ≥ 3 | événement rare | **Ni l'un ni l'autre** : alerte minimale au permanent, détail en référence ou en corps de skill. C'est la troisième ligne de C5, jusqu'ici jamais reliée à l'axe du coût |

**POURQUOI ce bloc existe** : C1a portait bien un axe de coût (« inférable, coût élevé, info stable → synthèse courte ») mais aucun axe de fréquence, et C1b ne portait aucun des deux. Ses trois premiers cas ne demandent que « le modèle le fait-il », jamais « à quel prix ». Un invariant re-dérivable mais cher traversait donc C1b sans case, exactement comme une instruction de comportement traversait C1 avant que la branche C1b existe.

**Le seuil de 3 appels reste conventionnel**, il est repris de C1a et aucune source ne le porte. Ce qui change, c'est qu'il ne décide plus seul.

**Commencer par lire la page de prompting du modèle courant** (table des sources ci-dessous) : elle tranche gratuitement une partie des cas, en nommant les comportements natifs et en désignant les instructions à retirer — « *Claude Opus 5 verifies its own work without being told to. If your prompt contains explicit verification instructions […] remove them* » (vérifié le 2026-08-11).

**Test, pour ce que la doc ne tranche pas — A/B à bras de contrôle**, jamais une relecture : la même tâche donnée à deux contextes neufs, l'un tenu à l'instruction, l'autre sans, et une différence **mesurée** sur les défauts qui survivent. Sans le bras sans-instruction, on ne mesure que la présence de l'instruction, jamais son effet.

**LE PIÈGE — un suivi irrégulier n'est pas une preuve que l'instruction est nécessaire.** C'est aussi le symptôme documenté d'une couche trop longue : « *If Claude keeps doing something you don't want **despite having a rule against it**, the file is probably too long and the rule is getting lost* » (vérifié le 2026-08-11). Les deux hypothèses prédisent la même observation, et l'intuition va spontanément vers la mauvaise : constater l'oubli pousse à renforcer l'instruction, ce qui allonge la couche et aggrave la cause. **À LA PLACE de** renforcer → l'A/B les sépare, parce que le bras sans-instruction tourne sur une couche plus courte. Si le comportement y est **meilleur** sans la règle, la règle était une victime de la longueur, pas son remède.

**POURQUOI cette branche existe** : C1 ne posait que la question du fait — « retrouverait-il l'**information** », « en < 3 **appels d'outil** ». Une instruction de comportement ne porte aucune information à retrouver, donc elle traversait C1 sans jamais pouvoir être disqualifiée, et la cascade entière s'ouvrait à elle. Mesuré le 2026-08-11 : la passe `rules/` du 2026-08-10 a laissé passer « déléguer par défaut » et « lancer la suite complète après édition d'un fichier de build », alors que la page Opus 5 prescrit l'inverse des deux.

### C2 — Déterminisable ?

Un mécanisme sans LLM (hook, CI, linter, script) peut-il porter l'invariant ?

| L'invariant porte sur | Couche déterministe | Sort de la règle prose |
|---|---|---|
| Un artefact versionné (message de commit, fichier) | hook git `core.hooksPath` + check CI | Réduite à un pointeur vers le garde |
| Une action éphémère de l'agent (commande tapée, écriture réseau) | hook harnais (`PreToolUse`) — **seul mécanisme possible** | Idem |
| Un raisonnement (pas d'appel d'outil observable) | Aucune — le hook ne voit que les tool calls | La prose reste, → C3 |

**Contraintes du mécanisme, non renégociables** — cette grille en est le seul propriétaire depuis la suppression de `workflow.md` le 2026-08-11 : échoue fermé, aucun chemin absolu en dur, calibré sur un cas positif fabriqué à la main. *Les cinq cas mesurés qui les fondent : vault, `3_KNOWLEDGE/Patterns/deterministic-guards-failure-modes.md`.* **Séparation logique/binding** : la logique vit dans un script autonome testable hors agent (`checks/`), le binding propriétaire fait ≤ 10 lignes.

### C3 — Falsifiable ?

La règle gardée en prose porte-t-elle une condition de violation observable — au mieux, sa commande de vérification ?

**Gradient** (du plus sûr au plus faible) :
1. Hook/CI/linter — suivi garanti *(traité en C2)*
2. Règle falsifiable + commande de vérification
3. Impératif court non ambigu — suivi probabiliste
4. Prose vague ou de style — inutile même pour un bon modèle → **supprimer ou reformuler en 2/3**

**Sur un contrat de routage, la commande de vérification est un cas d'éval.** Le niveau 2 s'y lit ainsi, et le verdict reste mécanique : le corpus `evals/eval.json` porte un cas positif, **et un cas `expect_trigger: false` par frère cité en clause NE PAS**. Sans ce cas négatif, l'instruction retombe au niveau 3.

**POURQUOI le cas négatif et pas la simple présence d'un corpus** : vérifier qu'un skill **part** ne vérifie pas qu'il **ne part pas** à tort, et c'est l'autre moitié du contrat que mesurent les collisions de déclencheurs. Un instrument qui se contente de constater le corpus valide donc la moitié d'un contrat en croyant en valider un. Compter les cas négatifs contre les frères nommés referme l'écart sans rien coûter de plus, le verdict restant un comptage.

**L'angle mort qui reste, à dire dans le verdict plutôt qu'à ignorer** : l'instrument compte les cas négatifs, il ne juge pas s'ils sont bien choisis. Et un frère cité en clause NE PAS mais archivé ne peut pas recevoir de cas — le noter, au lieu de compter un manque.

*Le second angle mort de cet instrument est mort avec l'ancien format d'éval : un marqueur absent sur un comportement vert était un faux négatif (mesuré le 2026-08-06 sur `devops-expert`), et le format n'a plus de marqueur.*

**Exception assumée** : `ai-principles.md` ne prescrit rien donc n'est pas falsifiable, mais il est le repli quand une règle concrète est muette. Il se **réduit** (titres + une ligne de pourquoi), il ne se supprime pas.

### C4 — Unique ?

L'instruction existe-t-elle ailleurs (autre règle, skill, `CLAUDE.md`, memory) ?

Une instruction dupliquée s'**élimine**, elle ne se hiérarchise pas : une seule occurrence, et la couche permanente se déclare délibérément partielle (modèle : `mermaid.md` → skill `mermaid-craft`). Un doublon statique est bénin ; un doublon volatil diverge au premier edit.

**Test** : grep du motif central de l'instruction sur `rules/`, `skills/`, les `CLAUDE.md` du domaine.

**Le doublon par conséquence, invisible au grep.** Deux instructions peuvent prescrire le même comportement sans partager un seul mot : elles ne partagent pas un **motif**, elles partagent un **effet**. C4 les rate parce qu'il grep un motif, C8 les rate parce qu'il ne regarde qu'à l'intérieur d'un fichier. **À LA PLACE de** chercher des formulations voisines → énumérer, pour l'instruction jugée, les autres instructions du harnais qui produisent le même geste ; s'il y en a, une seule survit. *Mesuré le 2026-08-11* : **cinq** instructions dans trois fichiers supprimaient chacune, indépendamment, le filtre « vérifier seulement en cas de doute » — `reasoning.md` (la mesure préalable, `PAS DE SECOND RANG`, le trigger « zéro »), `workflow.md` (le pré-vol) et `ai-practices.md` (l'incrément vérifié). *Trois de ces cinq ont disparu du permanent le même jour, par deux décisions qui ne visaient pas ce doublon — le défaut aurait donc pu ne jamais être vu.* Deux d'entre elles étaient un doublon **quasi textuel** que le grep aurait pu voir ; les trois autres, non. Effet cumulé : la vérification devient systématique et plus rien ne hiérarchise laquelle vaut son coût.

**Le périmètre du grep n'est pas le périmètre du doublon.** La couche la plus lourde du contexte permanent — le system prompt du harnais — n'est dans aucun fichier du repo, donc aucun grep ne l'atteint. Pour cette moitié, le test est celui de **C1b** : un contexte neuf sans la règle porte-t-il déjà l'instruction ? *Mesuré le 2026-08-11* : `workflow.md` prescrit « **DÉLÉGUER** par défaut » pendant que Claude Code injecte « *Do not call the AgentTool unless the user requested it* » — deux instructions contradictoires chargées dans la même session. Le grep du repo et de `~/.claude` ne rend rien sur `AgentTool` : la seconde est native, invisible à C4 par construction.

### C5 — Scopée ?

L'instruction vaut-elle partout, ou pour un sous-ensemble de repos/chemins ?

| Cas | Action |
|---|---|
| Domaine limité, identifiable par un chemin | frontmatter `paths:` (modèle : `back-spring.md`, `front-react.md`) |
| **Global par nature — scoper nuirait** | **Garder global, et le dire.** Le verdict est « survit C5 », pas « non applicable » |
| **Déclencheur rare, non identifiable par un chemin** | **Ni `paths:`, ni le permanent en entier.** Garder au permanent l'alerte minimale qui suffit à charger le reste, descendre le détail dans un corps de skill ou une référence non chargée |

Une règle globale qui ne sert qu'un domaine fait payer son poids à toutes les sessions. Mais l'inverse existe et coûte plus cher : `paths:` **conditionne l'activation à un fichier ouvert**, donc l'appliquer à une instruction qui se déclenche sur une intention et non sur un fichier la rend inerte la plupart du temps.

**Le cas mesuré** (2026-08-11, passe `skills/` A) : `paths:` existe bien pour un skill — « Claude loads the skill automatically only when working with files matching the patterns », doc vérifiée. Aucune des 26 descriptions n'y gagne : les ponts vault se déclenchent sur une phrase, les 9 experts répondent à des questions posées sans fichier courant. Poser `paths:` y **réduirait** l'activation au lieu de la cadrer. *Pourquoi cette case existe désormais : sans elle, 26 verdicts ont dû être rendus hors table, et la passe suivante les aurait re-tranchés.*

**Le test qui sépare la troisième ligne des deux premières** : le déclencheur est-il un fichier ou un événement ? Un fichier se nomme dans `paths:`. Un événement n'a aucun chemin, donc l'instruction qui l'attend se fait facturer à chaque session pour servir quelques fois par mois. Exemples d'événements rencontrés : un comptage qui rend « zéro », un diagramme à dessiner, un échec de build, une analyse dont la conclusion appellera des edits.

**C'est aussi la sortie du dosage de C1** (« Le dosage du "coût élevé" »), pour un invariant cher à re-dériver mais rarement déclenché. Les deux critères désignent la même case, chacun par son axe : C1 par le coût, C5 par la fréquence.

**Trois cas tranchés hors table faute de cette ligne, tous le 2026-08-11** :

- **`workflow.md`** : quatre de ses six règles étaient justes mais rares. Une seule a été relocalisée (`plan-mode.md`), les trois autres supprimées faute d'un troisième terme entre `paths:` et le permanent.
- **`reasoning.md`** : les triggers #9, #11 et #10 pesaient 298 mots au permanent pour des événements. #9 et #11 supprimés, #10 comprimé de 166 à 97.
- **`ponctuation.md`**, le cas inverse et le plus coûteux : son ancien `paths:` ne listait que des dossiers du vault, donc la règle était inerte en session de code. C'est précisément là que le défaut était le pire, avec 7,04 points-virgules pour 1 000 mots dans le corpus qui portait les règles du harnais, contre une cible de 1,09. Six jours sans mouvement, et une réécriture complète de la couche n'y avait rien changé.

**Le modèle de découpage existe déjà dans le harnais** : `mermaid.md` garde deux critères au permanent et renvoie le craft au skill `mermaid-craft`, chargé au moment de dessiner. `ponctuation.md` fait de même avec `ref-ponctuation.md`. La part permanente doit suffire à savoir qu'il faut charger le reste, jamais à faire le travail.

**Ce qui descend est la preuve, jamais le critère**, quand le critère est lui-même indéduisible. Une référence non chargée est un bon home pour six corpus et 1 019 occurrences. C'en est un mauvais pour la règle de décision, qu'un contexte neuf devra appliquer sans l'avoir lue. *Mesuré sur #16 de `reasoning.md`, le même jour et quelques heures après l'ajout de cette ligne* : la reco initiale était d'absorber la règle dans cette grille, au motif que ses deux gestes y figuraient déjà. La grille n'est chargée dans aucune session, donc l'absorption aurait rangé le critère hors de portée du moment où il sert. **« C'est déjà écrit ailleurs » n'est une raison de supprimer que si cet ailleurs est chargé.**

*Pourquoi cette ligne existe désormais* : deux passes consécutives ont dû rendre leur verdict principal hors table, et une troisième l'a rendu sur l'axe opposé. Un critère qui envoie trois fois de suite ses verdicts hors de sa propre table ne mesure pas ce qu'il prétend mesurer.

### C6 — Dans le budget ?

Le contexte permanent global tient-il sous le plafond ? Le périmètre est **tout ce qui entre dans chaque session** : les règles non scopées (`rules/` + `wrappers/claude/rules/`), l'output style actif, les blocs `description` des skills montés, et l'index de memory auto du projet courant.

**Le corps d'un skill n'entre pas dans C6** — il ne se charge qu'à l'invocation. Il ne se juge donc que sur C1→C5, C7 et C8, dans sa propre passe. *Pourquoi le borner ici : sans ça, chaque passe de corps rejuge si le budget la concerne, et deux passes répondront différemment.*

**Mesure** :

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

**État au 2026-08-11, fin de journée** : **5 340 mots** de permanent réel — **3 134** de règles + output style, **+ 2 206 de descriptions de skills** sur 26. Les descriptions n'avaient jamais été comptées avant la passe `skills/` A : elles pèsent **41 %** du permanent, et cette part monte à chaque coupe faite ailleurs. **C'est le premier poste du permanent, devant les règles**, et il n'a pas de cible (voir plus bas).

*Trajectoire des règles dans la journée : 4 869 → 4 929 (sixième point d'échec fermé ajouté à `workflow.md`) → 4 023 (suppression du même fichier, +99 pour `plan-mode.md`) → 3 035 (sortie du banc d'essai vers `banc-pratiques.md`) → 3 055 (swap C7 sur `reasoning.md`, +20 : un critère qui gagne son plafond coûte plus de mots que celui qui n'en avait pas) → 2 854 (passe C1b sur `reasoning.md` : deux triggers sans mesure supprimés, un troisième comprimé) → 3 205 (`ponctuation.md` promue de son scope vault vers le global, +351) → 3 152 (dette de ponctuation payée sur les 9 fichiers de la couche) → 3 149 (découpage du trigger #10) → **3 134** (#16 resserré sur son fait indéduisible). Une couche auditée grossit pendant l'audit — remesurer en ouverture de passe, ne jamais reprendre le chiffre du rapport précédent.*

*Ce que la trajectoire montre en plus, et qui n'était pas prévu : la couche a **regagné 295 mots** après avoir touché sa cible, par une promotion justifiée. Une cible tenue n'est donc pas un état acquis, et le seul mouvement monotone de la journée est celui des descriptions de skills, qui n'ont pas bougé faute de passe.*

**Cible de 3 950 : tenue avec 816 mots de marge.** Elle n'a pas été atteinte par la cascade seule, comme la passe du 2026-08-10 l'avait prévu, mais par deux décisions humaines de fond — supprimer `workflow.md`, sortir le banc d'essai. Aucune instruction survivante n'a été coupée pour tenir un chiffre.

**Cible, re-posée le 2026-08-11** : les ~3 950 mots ci-dessous ont été établis sur les **règles seules**. Ils ne sont donc pas un plafond global et ne doivent pas se lire comme tel. Deux plafonds distincts, chacun sur le périmètre qui le concerne :

**LE CHIFFRE N'EST PLUS UN SEUIL, décidé par l'humain le 2026-08-21.** C6 mesure et publie le poids, il ne le compare plus à une cible pour rendre un verdict de dépassement.

**À LA PLACE de** demander « la couche tient-elle sous N mots », demander **« qu'est-ce que la couche a acheté avec sa croissance »**. Une couche qui grossit de 400 mots de fait indéduisible est saine. Une couche qui grossit de 400 mots de quatrième part est en dette, au même poids.

**POURQUOI le seuil sort** : un plafond chiffré fabrique un dilemme que rien ne tranche. Il met en concurrence une instruction survivante et un nombre, alors que la grille interdit par ailleurs de couper l'une pour tenir l'autre — donc il ne pouvait produire qu'une contrainte négative sans issue. Et la doc va dans le même sens, « *find the smallest possible set of high-signal tokens* » est une intention, pas un compte. C'est C1 et C7 qui décident, par instruction ; C6 ne fait que rendre la somme visible et nommer ses contributeurs.

**Ce que C6 rend désormais** : la somme, sa trajectoire depuis la passe précédente, et le `wc -w` par fichier trié. Plus, pour chaque fichier qui a grossi, la nature de ce qui l'a fait grossir. Aucun verdict de « dépassement ».

**Les chiffres ci-dessous restent, comme repères historiques et non comme cibles.**

| Couche | Mesure | Repère | Qui la fait bouger |
|---|---|---|---|
| Règles + output style | `wc -w` ci-dessus | ~3 950 au 2026-08-11, **repère et non cible** | la cascade sur `rules/` |
| Descriptions de skills | script YAML ci-dessus | **pas de cible avant la passe 9** | le nombre de skills, pas leur rédaction |

*Pourquoi pas de cible sur les descriptions* : leur poids est d'abord une fonction du **nombre** de skills installés, pas de leur formulation. Fixer un plafond en mots reviendrait à interdire un 27e skill pour une raison de budget, alors que la vraie question est « ce skill mérite-t-il d'exister ». Le plafond dur qui existe déjà est ailleurs et il est mécanique : 1 536 caractères par entrée, et un budget de listing à 1 % de la fenêtre de contexte au-delà duquel Claude Code **supprime** les descriptions des skills les moins invoqués (doc vérifiée le 2026-08-11). C'est ce seuil-là qu'une passe doit surveiller, pas une somme de mots.

**État au 2026-08-10 (remesuré)** : 5 830 mots — 5 607 de règles (dont `memory-policy.md`, 207) + 223 d'output style. L'estimation initiale « ~40 % retirables » ne s'est pas confirmée : la passe `rules/` du 2026-08-10 mesure ~1 650 mots retirés par la cascade (~30 %).
**Repère** : ~3 950 mots hors output style — plancher mesuré par la passe `rules/` du 2026-08-10 (rapport `2026-08-10-audit-agent-config-rules.md`). Ce n'était déjà **pas un plafond obligatoire** au 2026-08-10, et ce n'est plus une cible du tout depuis le 2026-08-21 : on ne supprime pas une instruction survivante pour tenir un chiffre, donc le chiffre ne doit pas être posé comme un objectif à tenir. *L'arbitrage `ai-practices.md` qui pendait à cette phrase a été rendu le 2026-08-11 — sur le fond, et non sous pression C6 : son argument d'être chargé était mort.*

### C7 — Rentable ?

*Critère **par instruction**, appliqué à chaque survivante de C5, dans la même passe que C1→C5. C6 reste le seul critère global.*

L'instruction achète-t-elle son poids en mots ? C7 ne rejuge pas sa **présence** — C1→C5 l'ont tranchée — mais sa **formulation** : à couverture égale, combien de mots permanents elle coûte.

Décomposer l'instruction en quatre parts — **grille de lecture pour l'audit, jamais gabarit d'écriture** : on analyse une instruction existante avec, on n'impose aucun formulaire à la rédaction. *Pourquoi : la doc pose « Default assumption: Claude is already very smart » — sur-spécifier la forme ferme le modèle au lieu de le guider, et aucune source ne porte de budget par part.*

| Part | Statut |
|---|---|
| Impératif — le quoi, et son alternative si c'est une négation, **jamais l'interdit sec** | Porteur, irréductible |
| Pourquoi — une ligne (méta-règle de `reasoning.md`) | Porteur **si la raison apporte un fait indéduisible**. Sinon compressible |
| Seuil / exception | Porteur **si mesurable** ; sinon c'est un défaut C3 déguisé en précision |
| Preuve, cas vécu, méta-commentaire, relance anti-complaisance | **Compressible** — sort vers un fichier de références chargé à la demande |

**Alerte, par nature d'instruction** — un déclencheur de test, pas un couperet. Le chiffre trie, le test tranche.

| Nature | Alerte | Calibrage |
|---|---|---|
| **Instruction rédigée** (règle, prose normative) | ~60 mots | ~2× la médiane du harnais, 32 mots/bloc remesurée le 2026-08-10 sur 10 fichiers |
| **Contrat de routage** (`description` de skill) | **~130 mots** | ~1,5× la médiane mesurée le 2026-08-11 sur 26 descriptions, soit 86 mots |

**Pourquoi deux seuils et non un** : les deux natures ne paient pas leurs mots pour la même chose. Dans une instruction rédigée, les mots en trop sont de l'argumentation — la quatrième part, compressible. Dans un contrat de routage, les mots en trop sont des **termes déclencheurs**, et ils achètent directement du déclenchement : la doc Anthropic prescrit d'en ajouter, pas d'en retirer, quand un skill sous-déclenche. Appliqué à `skills/` A le 2026-08-11, le seuil unique de 60 mots a marqué **19 dépassements sur 26** sans jamais désigner de part compressible — un instrument qui alerte sur 73 % du corpus ne trie plus rien.

**Calibrage du nouveau seuil, et sa limite** : rejoué sur les mêmes 26 descriptions, 130 mots marque **1 instruction** contre 19 pour l'ancien seuil — l'alerte redevient un pointeur au lieu d'un bruit de fond. Mais elle est dérivée de la médiane du corpus qu'elle juge, donc elle ne se transporte pas : les passes 7 et 9 (skills de vault, autre corpus) **remesurent leur médiane avant d'appliquer l'alerte**, elles n'héritent pas de ce 130.

**Sur un contrat de routage, la quatrième part n'existe pas.** Les trois autres se relisent ainsi : l'impératif est le « quoi », le seuil est la liste de termes déclencheurs, l'exception est la clause « NE PAS utiliser pour → frère ». **Un terme déclencheur est un seuil au sens du tableau ci-dessus : porteur s'il est mesurable, donc s'il est couvert par un cas d'éval.** Sans éval, il n'est pas une précision mais une assertion non testée — un défaut C3 déguisé, et c'est lui qui est compressible. Une clause NE PAS suit la même règle, et son cas est le cas négatif de C3.

| Cas | Action |
|---|---|
| Sous l'alerte, quatrième part absente | **Garder tel quel** |
| Dépassement porté par la quatrième part | **Extraire** la preuve vers les références ; l'instruction garde impératif + pourquoi + trigger |
| Dépassement porté par l'impératif | **Découper** — ce sont plusieurs instructions empilées, chacune repasse en C1 |
| Impératif plus court que pourquoi + preuve | **Red flag** — l'instruction argumente plus qu'elle ne prescrit ; réécrire avant de trancher |

**Test** — comportemental, pas un comptage : retirer la part jugée compressible, donner à un contexte neuf une tâche qui déclenche l'instruction, comparer le comportement. S'il change, la part était porteuse : la remettre et le noter. **Échantillonné** comme le sondage C1 — un test coûte une session, le réserver aux instructions au-dessus de l'alerte ; les autres verdicts C7 se marquent « jugé sur pièce ».

**Mesure** :

```bash
# Mots d'une instruction — plage de lignes issue du découpage du cadrage
sed -n '<début>,<fin>p' <fichier> | wc -w

# Médiane du harnais, pour recalibrer l'alerte
for f in $(grep -L '^paths:' rules/*.md) wrappers/claude/rules/*.md; do
  printf '%s\t%s\t' "$f" "$(grep -c '^\(- \|\*\*[A-ZÀ-Ü]\|#\+ \)' "$f")"; wc -w < "$f"
done
```

*Le compteur de blocs est une approximation (puces, titres, amorces en gras) : il calibre l'alerte, il ne découpe pas — le découpage qui fait foi est manuel.*

Les **cas vécus** sortent du permanent vers un fichier de références chargé à la demande ; la règle garde le trigger et le pourquoi en une ligne.

**POURQUOI ce critère** : le budget de C6 se satisfait en supprimant des instructions entières, donc en perdant de la couverture. C7 récupère les mêmes mots sans rien perdre — il ne coupe que ce qui n'achète aucun comportement. Et sans lui, une instruction bien placée (survivante de C1→C5) est réputée bien écrite : rien ne mesure sa formulation.

### C8 — Cohérent dans son fichier ?

*Critère **par fichier**, rendu une fois toutes ses instructions criblées — et **par couple** dès que le fichier déclare une annexe (référence, compagnon, « le détail vit dans X »). Cette annexe entre dans le périmètre du verdict, même si elle n'est jamais chargée.*

Les instructions survivantes d'un même fichier tiennent-elles ensemble ? Quatre défauts que le verdict par instruction ne voit pas, parce qu'ils vivent **entre** les instructions :

| Défaut | Action |
|---|---|
| Deux instructions se contredisent, ou leurs exceptions se recouvrent en s'opposant | Trancher — une seule survit, ou l'articulation devient explicite |
| Une annexe contredit la **justification** de sa règle | Trancher, en partant du principe que l'annexe est la plus récente — c'est donc la règle qui a vieilli |
| Redondance interne — deux instructions du fichier prescrivent la même chose autrement | Fusionner *(C4 ne l'attrape pas : son grep cherche ailleurs, pas entre voisines)* |
| Instruction orpheline — sans rapport avec le propos du fichier | Déplacer vers son vrai foyer |

**POURQUOI ce critère** : la cascade juge chaque instruction isolément ; un fichier peut être fait d'instructions toutes valides une à une et rester contradictoire — et c'est le fichier entier qu'une session charge, pas l'instruction.

**POURQUOI le couple, et pas seulement le fichier** : la justification d'une règle est souvent écrite ailleurs que la règle, et c'est elle qui périme en premier. *Mesuré le 2026-08-11 sur `ai-practices.md`, qui a traversé deux passes d'audit en affirmant que son chargement conditionnait sa validation, alors que son annexe avait déjà déplacé la validation vers une expérience montée exprès. Aucune des deux affirmations n'était fausse isolément — c'est pour ça qu'aucun critère par instruction ne pouvait la voir.* **Ce que ça ne couvre pas** : une prémisse qui meurt sans qu'aucune annexe ne le dise — décision prise dans le vault, ou en conversation. Rien ne l'attrape, et aucun mécanisme n'est proposé faute de cas mesuré.

---

## Sources normatives par sous-domaine

Contre quoi juger la **conformité de construction** d'un artefact (format, frontmatter, anatomie). On stocke le **pointeur**, jamais une copie (C1 : contenu volatil — la doc a déjà migré de domaine une fois).

**Standards ouverts multi-agents** — la couche portable, à préférer quand elle couvre la fonction :

| Mécanisme | Source | Vérifié |
|---|---|---|
| Skills | <https://agentskills.io/specification> + repo `anthropics/skills` | 2026-08-10, fetch |
| AGENTS.md | <https://agents.md> | supposé (standard connu, non re-fetché) |
| MCP | <https://modelcontextprotocol.io> | supposé |

**Propriétaire Claude Code** — le binding, confiné sous `wrappers/claude/` :

| Mécanisme | Source | Vérifié |
|---|---|---|
| Hooks | <https://code.claude.com/docs/en/hooks> | 2026-08-10, fetch |
| Output styles | <https://code.claude.com/docs/en/output-styles> | 2026-08-10, fetch |
| CLAUDE.md / memory | <https://code.claude.com/docs/en/memory> | 2026-08-10, via agent doc |
| Subagents | <https://code.claude.com/docs/en/sub-agents> | slug confirmé par liens |
| Scripts / checks | pas de doc — la norme est **ShellCheck** + les contraintes de **C2** (échec fermé, calibrage) | — |
| Index complet | <https://code.claude.com/docs/llms.txt> | 2026-08-10 |

**Rédaction d'instructions** — contre quoi juger C1a, C1b et C7, pour que la grille ne se valide pas contre la doctrine qu'elle audite :

| Sujet | Source | Vérifié |
|---|---|---|
| Rédaction de skills (« Does this paragraph justify its token cost? », degrees of freedom) | <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices> | 2026-08-10, fetch |
| Rédaction de prompts/règles (motivation derrière l'instruction, dire quoi faire plutôt que quoi éviter) | <https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-4-best-practices> — l'URL sert désormais la page courante **toutes générations** | 2026-08-11, fetch |
| **Comportements natifs du modèle courant, et instructions à retirer — l'autorité de C1b** | <https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5> — une page par modèle (`prompting-claude-<modèle>`) | 2026-08-11, fetch |
| **Élagage du contexte permanent** (« *Would removing this cause Claude to make mistakes?* », « *If Claude already does something correctly without the instruction, delete it or convert it to a hook* ») | <https://code.claude.com/docs/en/best-practices> | 2026-08-11, fetch |
| CLAUDE.md (< 200 lignes, contexte = bien public) | <https://code.claude.com/docs/en/memory> | 2026-08-10, via agent doc |

**La page par modèle est datée par construction, et c'est le point** : ses prescriptions s'inversent d'une génération à l'autre — ce qu'il fallait dire à un modèle devient ce qu'il faut retirer au suivant. Une passe qui juge C1b contre la page d'une génération précédente valide des instructions que le modèle courant subit. **Relire cette page en ouverture de chaque passe**, et noter dans le rapport contre quel modèle la passe a tourné : c'est ce qui datera ses verdicts quand le modèle changera.

**Point tranché le 2026-08-10** (doc officielle, section AGENTS.md de la page memory) : Claude Code ne lit **pas** `AGENTS.md` nativement — seul `CLAUDE.md` est lu ; s'ils coexistent, `AGENTS.md` est ignoré. Deux ponts documentés : import `@AGENTS.md` en tête de `CLAUDE.md`, ou symlink. **Conséquence** : la couche standard reste possible — le contenu vit dans `AGENTS.md` (portable), `CLAUDE.md` se réduit à l'import. Même motif logique/binding que `checks/` + hook. **Portée** : ce pont ne vaut que pour les `CLAUDE.md` de projet ; les règles globales passent par les symlinks de `sync-rules.sh`, mécanisme distinct à auditer séparément.

---

## Mesures d'inventaire par domaine

À lancer en ouverture d'audit, avant tout jugement :

```bash
# Poids du contexte permanent → la commande de C6 (une seule définition)

# Couche déterministe réelle
ls checks/ 2>/dev/null; ls wrappers/claude/scripts/hooks/
git config core.hooksPath   # sur chaque repo du domaine

# Doublons inter-couches (par motif jugé, pas de regex unique)
# Symlinks de règles à jour (bash obligatoire : shebang bash, `set -o pipefail` casse sous dash)
bash wrappers/claude/scripts/sync-rules.sh
```

---

## Écarts déjà identifiés (seed — à confirmer par l'audit, pas acquis)

D'après la note d'inbox du 2026-08-10 :

- [x] `tooling.md` (449 mots) → migré le 2026-08-11 en `wrappers/claude/scripts/hooks/guard-bash-tooling.py` (**pas** `checks/`, cf. ligne ci-dessous), règle réduite à 120 mots. Câblé dans `settings.json`, batterie de 31 cas, calibré live et sur 987 commandes de transcripts.
- [x] `ai-practices.md` (988 au moment de la sortie) → **sorti du permanent le 2026-08-11**, fusionné avec son fichier de références en `audits/banc-pratiques.md`, compagnon vivant de cette grille. Motif décisif, et il n'est pas C6 : le fichier se justifiait d'être chargé par « une pratique jamais chargée n'est jamais exercée, donc jamais validable », or les cinq seuils de sortie exigent désormais un **bras de contrôle** — une expérience montée exprès, que le chargement n'achète pas. Deux affirmations contradictoires dans deux fichiers d'un même couple, chacune juste isolément : le défaut C4 que la grille venait de nommer le matin même. `rules/references/` ne garde plus que `ref-reasoning.md`, adossé à une règle vivante.
- [x] `reasoning.md` (1 100 → 1 051), `workflow.md` (1 055 → 945, puis 1 005 avec le sixième point d'échec fermé) → cas vécus descendus le 2026-08-11 dans `rules/references/ref-reasoning.md` et `ref-workflow.md`, triggers et commandes gardés. Gain réel 58 % de la projection : une part du dépassement de longueur était de l'instruction, pas de l'anecdote.
- [x] **`workflow.md` supprimé le 2026-08-11** (1 005 mots), sans relocalisation de ses six règles. Motif de la décision, prise par l'humain : une règle douteuse — surtout instaurée à chaud après un incident — se supprime plutôt que se teste, parce que tester chaque règle douteuse coûte plus que la re-découvrir si elle manquait vraiment. Deux règles étaient des rustines que la page Opus 5 contredit (« déléguer par défaut », inversée ; la vérification séparée après édition de build). Les quatre autres étaient justes mais **facturées à chaque session pour servir quelques fois par mois** — le défaut était C5, pas C1b. Seule survivante, reformulée et déplacée : la sortie d'analyse → `wrappers/claude/rules/plan-mode.md` (99 mots), sous le wrapper parce qu'elle nomme un mécanisme propriétaire. `ref-workflow.md` supprimé, ses cinq cas mesurés versés au vault (`3_KNOWLEDGE/Patterns/deterministic-guards-failure-modes.md`).
- [x] **C1b rejoué sur `reasoning.md` le 2026-08-11** → `audits/2026-08-11-audit-agent-config-rules-reasoning-c1b.md`. **1 071 → 870 mots** (−201). Découpage à 19 instructions ; **une seule sort en C1b** (#2, doublon avec le system prompt natif, non appliqué — voir ci-dessous). Ce qui a été appliqué relève de **C5**, pas de C1b : les triggers #9 (échec CI, 54) et #11 (session log, 78) supprimés — aucun cas mesuré dans l'annexe, et l'instruction #1 produit déjà le même geste ; le trigger #10 (comptage à « zéro ») comprimé de 166 à **97**, sa quatrième part étant **déjà présente mot pour mot dans `ref-reasoning.md`**. La correction de l'hypothèse d'ouverture est le résultat principal : la page Opus 5 prescrit de retirer la **re-vérification de sa propre sortie**, jamais le **grounding**, et ce fichier ne fait que du grounding. **Ne concerne pas** `tooling.md` ni `commit-convention.md` : ils portent du fait, pas du comportement.
  - [x] **#2 supprimé le 2026-08-11** (29 mots) → **870 → 841**, couche à **2 825**. Seul verdict C1b de la passe, appliqué après arbitrage. Le motif décisif n'est pas le doublon mais la **volatilité** : garder le seul increment de #2 sur le natif (la couverture des blocs de pensée, que le natif exempte explicitement) aurait été une règle dont tout le contenu amende un texte non versionné, non differable, qui change à chaque release du harnais. La grille le dit — « un doublon statique est bénin ; un doublon volatil diverge au premier edit ». Ce qui est perdu, et c'est réel : la contrainte ne couvre plus le raisonnement interne. Aucune citation ailleurs (grep sur deux formulations, hors `audits/`).
  - [x] **#16 resserré le 2026-08-11, et gardé global après un renversement de reco.** Le bloc pesait **80 mots, pas les 49 enregistrés** ici et dans le rapport, chiffre d'avant sa réécriture. Ramené à **65** en coupant les deux seules phrases qui violaient sa propre règle (« une raison indéduisible achète du transfert au cas non prévu. Une raison déduisible ne fait payer que des mots. »), le pointeur de doc replié dans l'impératif.
    - **Le renversement est le résultat réutilisable.** La reco initiale était de supprimer le bloc et d'absorber sa condition dans la ligne 182 de cette grille, au motif que la ligne 181 portait déjà son composant de forme. L'argument tombe sur un fait qu'il ne prenait pas en compte : **cette grille n'est chargée dans aucune session.** Or le fait porté par #16 est de la classe qu'il dit lui-même de garder, puisque deux pages de doc du même éditeur prescrivent l'inverse l'une de l'autre et qu'un contexte neuf tombe sur l'une des deux, jamais sur la réconciliation. Preuve que ça ne se devine pas : le harnais disait « **toujours** le pourquoi » jusqu'au fetch des deux pages. **« C'est déjà écrit ailleurs » n'est une raison de supprimer que si cet ailleurs est chargé** — versé à la ligne C5 correspondante.
    - **Ce que la ligne 182 faisait**, et c'est corrigé : elle citait #16 comme autorité en prenant son label et en laissant tomber sa condition, donc elle lisait « Porteur » sec là où la règle dit « si la raison apporte un fait indéduisible ». La ligne 183 juste en dessous portait déjà la forme conditionnelle exacte qui manquait.
    - **La ligne FORME n'est pas inférable non plus**, contrairement à ce que la reco initiale supposait : **25 impératifs négatifs pour 15 portant une alternative** dans la couche, soit ~60 % de pratique. *Limite de l'instrument, à ne pas oublier en rejouant* : les deux greps comptent des lignes, pas des instructions appariées, donc le taux est indicatif.
    - **Troisième chiffre périmé de la journée** : 49 contre 80 mesurés, après les « 15 obligations » et le couple « 12 avant, 10 après ». Même cause chaque fois, un chiffre relu contre une version du fichier qui a bougé depuis. C'est le même défaut que les recommandations d'audit survivant à leur motif (AP3/AP4, `ref-ai-practices.md`), appliqué aux nombres.
  - [x] **#10 découpé le 2026-08-11**, en deux blocs de **40 et 54 mots**, chacun sous l'alerte C7 de 60 que la paire dépassait à 97. **Le gain en mots est quasi nul, et il faut le dire : 97 → 94.** Le découpage ne comprime pas, il corrige l'**unité de mesure** : C7 se juge par instruction, or l'alerte était appliquée à deux instructions empilées sous un seul trigger. *Le vrai gain est ailleurs, et il se mesure* : « calibrer l'instrument » était rangé sous le déclencheur « un comptage qui rend zéro », alors que le geste se fait **avant** de compter. Les deux calibrages du 2026-08-11 (la règle de build supprimée, le compteur de ponctuation, cf. `ref-ponctuation.md` « calibré avant tout comptage ») ont tous deux eu lieu avant que le comptage rende quoi que ce soit, donc hors du déclencheur annoncé. **Le bloc sous-déclenchait**, et aucun comptage de mots ne pouvait le révéler. Ce cas relève de la troisième ligne de C5, ajoutée le même jour : déclencheur événementiel, alerte minimale au permanent, détail dans la référence.
  - [ ] **CAPTURE C4 du 2026-08-11, à verser à la passe `skills/`** : `skills/mr-review/references/glab-et-base-du-diff.md:28-30` restitue le geste de calibrage en italique, appliqué à quatre pièges zsh/glab qui rendent chacun un faux zéro (`no matches found` indistinguable d'un vrai zéro). Ce n'est **pas** un doublon du permanent, puisqu'un corps de skill ne se charge qu'à l'invocation (cf. C6). C'est la règle générale instanciée sur un instrument précis, ce qu'une référence doit faire. À confirmer légitime, ou à réduire à un pointeur, dans la passe des corps de skill. **Non traité, et volontairement** : on n'ouvre pas un fichier de skill pendant que la passe `skills/` court.
  - [ ] **CAPTURE C7 du 2026-08-11** : le POURQUOI du contrat de questions (« le tri d'une découverte est un jugement ») pèse **71 mots en une seule unité**, donc au-dessus de l'alerte sans l'excuse de l'empilement qui a servi à #10. Les trois autres dépassements du fichier (147, 110, 66) sont des listes de deux à trois instructions, non concernées par une alerte qui se juge par instruction. *Ce que ça dit de l'instrument* : un découpage sur les lignes vides compte des paquets, pas des instructions, et il faut donc lire chaque dépassement avant de le traiter.
  - [x] **Chiffre corrigé, et sa correction ne se laisse pas fixer à un entier.** « 15 obligations de vérification distinctes » était faux. Le rapport de la passe annonce « 12 avant, 10 après » : **ce couple ne se reproduit pas non plus**, il compte un bloc de trop. Recompté bloc par bloc sur le fichier courant, la fourchette défendable est **7 à 9**, et deux conventions de comptage la font varier : les deux sous-puces du #10 comptent-elles pour une obligation ou deux, et le #8 (« ce que tue une mesure ») est-il une obligation ou le POURQUOI du #3 ? *Ce que ça enseigne, au-delà du chiffre* : « nombre d'obligations » n'est pas une grandeur mesurable sans convention écrite — trois valeurs annoncées en un jour sur le même fichier. À la place d'un entier, citer la convention ou ne pas citer de chiffre.
  - [x] **Swap appliqué le 2026-08-11** : `PAS DE SECOND RANG` → `SEUIL AU COÛT, PAS À L'ENJEU`. L'ancienne clause interdisait tout triage sans jamais dire où s'arrêter, et Opus 5 l'appliquait littéralement à chaque détail ; la nouvelle donne le plafond qui manquait — un appel d'outil → mesurer sans arbitrer, plus cher → marquer « supposé ». **Ce que ce swap n'est pas** : un verdict C1b. C'est du **C7**, de la formulation. Le fichier gagne 20 mots (1 051 → 1 071) et garde ses **15 obligations de vérification distinctes**, dont cinq convergentes (cf. C4, doublon par conséquence) — le volume est intact, donc la passe C1b reste entièrement à faire.
- [x] `ai-principles.md` (558 → 474) → réduit aux titres + une ligne portant le pourquoi le 2026-08-11 ; en-tête inversé (le repo fait foi).
  - [x] **Fusion AP3 / AP4 : non fondée, refermée le 2026-08-11 sans édition.** Le rapport du 2026-08-10 concluait au recouvrement sur une seule pièce — « AP4 le déclare lui-même », par la phrase *« Prolonge "adapter le médium à la nature de l'intention", côté exécution »* (`c677daf`). **Cette phrase a été supprimée le même jour** par la réduction « titre + une ligne » : `grep -c "Prolonge"` → 0. La recommandation avait survécu à son motif. Cartesian check sur les textes courants : AP3 ne prescrit rien sur la lecture d'un ordre, AP4 rien sur le choix d'un format — ils partagent le mot « intention », pas l'acte ni l'acteur (conception vs conduite). Aucun ne se déduit de l'autre, donc fusionner détruirait de l'information. *Leçon de méthode, la deuxième en deux jours* : une recommandation d'audit se relit contre la version courante du fichier, jamais contre celle qui l'a produite — cf. le même défaut sur `ref-ai-practices.md`.
- [ ] **CAPTURE C4 du 2026-08-11 — AP4 contre le system prompt natif.** AP4 (« déduire ce que l'utilisateur veut obtenir avant d'exécuter la forme exacte qu'il a tapée ») voisine avec une instruction native de Claude Code, section *Delivering work* : « *acting on the actual request rather than on speculation about what lies behind it. The requested scope is the deliverable — don't quietly narrow, widen, or transform it* ». Vérifié absent du repo **et** de `~/.claude` : c'est du natif, donc invisible à tout grep du domaine — le deuxième cas de cet angle mort après « déléguer par défaut ». Tension réelle seulement si AP4 s'étend au **périmètre** ; nulle s'il reste borné au **mode / format / outil**, ce que son texte dit déjà. **Non creusé, et volontairement** : borner AP4 de huit mots serait un jugement, pas une mesure. Le trancher demande un A/B à bras de contrôle → à verser à la passe C1b de `ai-principles.md`, pas à traiter au fil de l'eau.
- [ ] Gardes `guard-no-claude-in-commit.sh`, `guard-no-remote-write.py` → `git mv` vers `checks/` (séparation logique/binding). **Non fait, et le nouveau garde ne l'a pas anticipé** : `wrappers/claude/scripts/` est symlinké vers `~/.claude/scripts/`, donc `settings.json` y désigne ses hooks par `~/.claude/scripts/hooks/…`. Un `checks/` à la racine sortirait de l'arbre du symlink et imposerait un chemin absolu dans `settings.json`. Le déplacement reste défendable, mais il déplace les trois gardes **et** leur binding d'un coup — arbitrage à part.
- [ ] Couche 1 absente : 0 hook git sur 25 repos Winggy, 0 check CI de commits sur 19 (C2 : les deux gardes sont le seul filet)
- [ ] **PARKÉ le 2026-08-11 — le test de C7 en skill déclenché à la main.** Motif du parking : l'audit `skills/` est en cours, on n'ouvre pas un skill neuf pendant. Ce qui est établi : le protocole marche (trois verdicts nets rendus le 2026-08-11), mais **aucune prose ne le déclenche** — deux tentatives, trois contextes neufs, 0/3. Une instruction qui demande de lancer une expérience séparée avant de finir la tâche perd contre « finir la tâche », que son déclencheur soit de premier ordre ou non. Preuves : `banc-pratiques.md`, section « Ce que la prose ne peut pas déclencher ». À reprendre après l'audit `skills/`, en skill invoqué par l'humain — jamais en règle.
