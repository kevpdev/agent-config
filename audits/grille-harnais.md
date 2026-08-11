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

**Sur un contrat de routage, la commande de vérification est un scénario d'éval.** Le niveau 2 s'y lit : un `evals/eval.json` existe, et il porte des `trigger_markers` pour le comportement jugé. Sans lui, l'instruction retombe au niveau 3 — et le verdict est mécanique, pas interprétatif : `ls <skill>/evals/`.

**Deux angles morts de cet instrument, à dire dans le verdict plutôt qu'à ignorer** :
- Un scénario qui vérifie que le skill **part** ne vérifie pas qu'il **ne part pas** à tort. Un corpus d'évals sans scénario négatif ne falsifie qu'une moitié du contrat, et c'est l'autre moitié que mesurent les collisions de déclencheurs.
- Un marqueur absent avec un comportement entièrement vert est un faux négatif de l'instrument, pas un non-déclenchement (mesuré le 2026-08-06 sur `devops-expert`).

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

Une règle globale qui ne sert qu'un domaine fait payer son poids à toutes les sessions. Mais l'inverse existe et coûte plus cher : `paths:` **conditionne l'activation à un fichier ouvert**, donc l'appliquer à une instruction qui se déclenche sur une intention et non sur un fichier la rend inerte la plupart du temps.

**Le cas mesuré** (2026-08-11, passe `skills/` A) : `paths:` existe bien pour un skill — « Claude loads the skill automatically only when working with files matching the patterns », doc vérifiée. Aucune des 26 descriptions n'y gagne : les ponts vault se déclenchent sur une phrase, les 9 experts répondent à des questions posées sans fichier courant. Poser `paths:` y **réduirait** l'activation au lieu de la cadrer. *Pourquoi cette case existe désormais : sans elle, 26 verdicts ont dû être rendus hors table, et la passe suivante les aurait re-tranchés.*

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

**État au 2026-08-11, fin de journée** : **5 261 mots** de permanent réel — **3 055** de règles + output style, **+ 2 206 de descriptions de skills** sur 26. Les descriptions n'avaient jamais été comptées avant la passe `skills/` A : elles pèsent désormais **42 %** du permanent, et cette part monte à chaque coupe faite ailleurs. **C'est le premier poste du permanent, devant les règles**, et il n'a pas de cible (voir plus bas).

*Trajectoire des règles dans la journée : 4 869 → 4 929 (sixième point d'échec fermé ajouté à `workflow.md`) → 4 023 (suppression du même fichier, +99 pour `plan-mode.md`) → 3 035 (sortie du banc d'essai vers `banc-pratiques.md`) → **3 055** (swap C7 sur `reasoning.md`, +20 : un critère qui gagne son plafond coûte plus de mots que celui qui n'en avait pas). Une couche auditée grossit pendant l'audit — remesurer en ouverture de passe, ne jamais reprendre le chiffre du rapport précédent.*

**Cible de 3 950 : tenue avec 915 mots de marge.** Elle n'a pas été atteinte par la cascade seule, comme la passe du 2026-08-10 l'avait prévu, mais par deux décisions humaines de fond — supprimer `workflow.md`, sortir le banc d'essai. Aucune instruction survivante n'a été coupée pour tenir un chiffre.

**Cible, re-posée le 2026-08-11** : les ~3 950 mots ci-dessous ont été établis sur les **règles seules**. Ils ne sont donc pas un plafond global et ne doivent pas se lire comme tel. Deux plafonds distincts, chacun sur le périmètre qui le concerne :

| Couche | Mesure | Cible | Qui la fait bouger |
|---|---|---|---|
| Règles + output style | `wc -w` ci-dessus | ~3 950 | la cascade sur `rules/` |
| Descriptions de skills | script YAML ci-dessus | **pas de cible avant la passe 9** | le nombre de skills, pas leur rédaction |

*Pourquoi pas de cible sur les descriptions* : leur poids est d'abord une fonction du **nombre** de skills installés, pas de leur formulation. Fixer un plafond en mots reviendrait à interdire un 27e skill pour une raison de budget, alors que la vraie question est « ce skill mérite-t-il d'exister ». Le plafond dur qui existe déjà est ailleurs et il est mécanique : 1 536 caractères par entrée, et un budget de listing à 1 % de la fenêtre de contexte au-delà duquel Claude Code **supprime** les descriptions des skills les moins invoqués (doc vérifiée le 2026-08-11). C'est ce seuil-là qu'une passe doit surveiller, pas une somme de mots.

**État au 2026-08-10 (remesuré)** : 5 830 mots — 5 607 de règles (dont `memory-policy.md`, 207) + 223 d'output style. L'estimation initiale « ~40 % retirables » ne s'est pas confirmée : la passe `rules/` du 2026-08-10 mesure ~1 650 mots retirés par la cascade (~30 %).
**Cible** : ~3 950 mots hors output style — plancher mesuré par la passe `rules/` du 2026-08-10 (rapport `2026-08-10-audit-agent-config-rules.md`), **pas un plafond obligatoire**. Décidé le 2026-08-10 : on ne supprime pas une instruction survivante pour tenir un chiffre. *L'arbitrage `ai-practices.md` qui pendait à cette phrase a été rendu le 2026-08-11 — sur le fond, et non sous pression C6 : son argument d'être chargé était mort.*

### C7 — Rentable ?

*Critère **par instruction**, appliqué à chaque survivante de C5, dans la même passe que C1→C5. C6 reste le seul critère global.*

L'instruction achète-t-elle son poids en mots ? C7 ne rejuge pas sa **présence** — C1→C5 l'ont tranchée — mais sa **formulation** : à couverture égale, combien de mots permanents elle coûte.

Décomposer l'instruction en quatre parts — **grille de lecture pour l'audit, jamais gabarit d'écriture** : on analyse une instruction existante avec, on n'impose aucun formulaire à la rédaction. *Pourquoi : la doc pose « Default assumption: Claude is already very smart » — sur-spécifier la forme ferme le modèle au lieu de le guider, et aucune source ne porte de budget par part.*

| Part | Statut |
|---|---|
| Impératif — le quoi, avec son alternative si c'est une négation | Porteur, irréductible |
| Pourquoi — une ligne (méta-règle de `reasoning.md`) | Porteur |
| Seuil / exception | Porteur **si mesurable** ; sinon c'est un défaut C3 déguisé en précision |
| Preuve, cas vécu, méta-commentaire, relance anti-complaisance | **Compressible** — sort vers un fichier de références chargé à la demande |

**Alerte, par nature d'instruction** — un déclencheur de test, pas un couperet. Le chiffre trie, le test tranche.

| Nature | Alerte | Calibrage |
|---|---|---|
| **Instruction rédigée** (règle, prose normative) | ~60 mots | ~2× la médiane du harnais, 32 mots/bloc remesurée le 2026-08-10 sur 10 fichiers |
| **Contrat de routage** (`description` de skill) | **~130 mots** | ~1,5× la médiane mesurée le 2026-08-11 sur 26 descriptions, soit 86 mots |

**Pourquoi deux seuils et non un** : les deux natures ne paient pas leurs mots pour la même chose. Dans une instruction rédigée, les mots en trop sont de l'argumentation — la quatrième part, compressible. Dans un contrat de routage, les mots en trop sont des **termes déclencheurs**, et ils achètent directement du déclenchement : la doc Anthropic prescrit d'en ajouter, pas d'en retirer, quand un skill sous-déclenche. Appliqué à `skills/` A le 2026-08-11, le seuil unique de 60 mots a marqué **19 dépassements sur 26** sans jamais désigner de part compressible — un instrument qui alerte sur 73 % du corpus ne trie plus rien.

**Calibrage du nouveau seuil, et sa limite** : rejoué sur les mêmes 26 descriptions, 130 mots marque **1 instruction** contre 19 pour l'ancien seuil — l'alerte redevient un pointeur au lieu d'un bruit de fond. Mais elle est dérivée de la médiane du corpus qu'elle juge, donc elle ne se transporte pas : les passes 7 et 9 (skills de vault, autre corpus) **remesurent leur médiane avant d'appliquer l'alerte**, elles n'héritent pas de ce 130.

**Sur un contrat de routage, la quatrième part n'existe pas.** Les trois autres se relisent ainsi : l'impératif est le « quoi », le seuil est la liste de termes déclencheurs, l'exception est la clause « NE PAS utiliser pour → frère ». **Un terme déclencheur est un seuil au sens du tableau ci-dessus : porteur s'il est mesurable, donc s'il est couvert par un scénario d'éval.** Sans éval, il n'est pas une précision mais une assertion non testée — un défaut C3 déguisé, et c'est lui qui est compressible.

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
- [ ] **Rejouer C1b sur `reasoning.md`** (1 071 mots, 35 % de la couche). La passe du 2026-08-10 a tourné contre une grille sans C1b et contre la page de prompting de la génération précédente : son verdict sur ce fichier ne vaut pas. **Ne concerne pas** `tooling.md` ni `commit-convention.md` : ils portent du fait, pas du comportement, donc C1a s'y applique et leurs verdicts tiennent.
  - [x] **Swap appliqué le 2026-08-11** : `PAS DE SECOND RANG` → `SEUIL AU COÛT, PAS À L'ENJEU`. L'ancienne clause interdisait tout triage sans jamais dire où s'arrêter, et Opus 5 l'appliquait littéralement à chaque détail ; la nouvelle donne le plafond qui manquait — un appel d'outil → mesurer sans arbitrer, plus cher → marquer « supposé ». **Ce que ce swap n'est pas** : un verdict C1b. C'est du **C7**, de la formulation. Le fichier gagne 20 mots (1 051 → 1 071) et garde ses **15 obligations de vérification distinctes**, dont cinq convergentes (cf. C4, doublon par conséquence) — le volume est intact, donc la passe C1b reste entièrement à faire.
- [x] `ai-principles.md` (558 → 474) → réduit aux titres + une ligne portant le pourquoi le 2026-08-11 ; en-tête inversé (le repo fait foi). Reste ouvert, non tranché : AP3 et AP4 se recouvrent, candidats à fusion.
- [ ] Gardes `guard-no-claude-in-commit.sh`, `guard-no-remote-write.py` → `git mv` vers `checks/` (séparation logique/binding). **Non fait, et le nouveau garde ne l'a pas anticipé** : `wrappers/claude/scripts/` est symlinké vers `~/.claude/scripts/`, donc `settings.json` y désigne ses hooks par `~/.claude/scripts/hooks/…`. Un `checks/` à la racine sortirait de l'arbre du symlink et imposerait un chemin absolu dans `settings.json`. Le déplacement reste défendable, mais il déplace les trois gardes **et** leur binding d'un coup — arbitrage à part.
- [ ] Couche 1 absente : 0 hook git sur 25 repos Winggy, 0 check CI de commits sur 19 (C2 : les deux gardes sont le seul filet)
- [ ] **PARKÉ le 2026-08-11 — le test de C7 en skill déclenché à la main.** Motif du parking : l'audit `skills/` est en cours, on n'ouvre pas un skill neuf pendant. Ce qui est établi : le protocole marche (trois verdicts nets rendus le 2026-08-11), mais **aucune prose ne le déclenche** — deux tentatives, trois contextes neufs, 0/3. Une instruction qui demande de lancer une expérience séparée avant de finir la tâche perd contre « finir la tâche », que son déclencheur soit de premier ordre ou non. Preuves : `banc-pratiques.md`, section « Ce que la prose ne peut pas déclencher ». À reprendre après l'audit `skills/`, en skill invoqué par l'humain — jamais en règle.
