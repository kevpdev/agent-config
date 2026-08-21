# Autorité des conventions — qui gagne quand deux sources se contredisent

**DÉCLENCHEUR** : je m'apprête à nommer, formater ou ranger quelque chose, et deux sources disent des choses différentes. Ou une seule le dit, et le code existant fait autrement.

**Ne jamais demander laquelle suivre.** La hiérarchie ci-dessous répond, y compris quand sa réponse est « tranche toi-même et écris-le ».

**POURQUOI** : mesuré le 2026-08-19, un run de `aidd-orchestrator:01-sdlc` s'est arrêté pour demander si 40 tests existants devaient migrer au format de `back-spring.md`. Une convention sans portée déclarée rouvre la même question à chaque run.

## D'abord la coupe — forme ou fond

| Nature | Exemples | Elle sert | Qui gagne |
|---|---|---|---|
| **forme** | nom `should_<effet>_when_<condition>`, suffixes `XxxController`, un type public par fichier, organisation par couche, colocalisation `Xxx.test.tsx` | la cohésion | le repo |
| **fond** | tester le comportement et pas l'implémentation, outside-in, ne mocker que les I/O | la correction | le harnais |

**LE TEST, en une phrase** : est-ce que ça change ce qui est **vrai** du code, ou seulement à quoi il **ressemble** ?

**À LA PLACE de** classer au ressenti « cosmétique contre important », passer le test. Il ne se devine pas : le PascalCase d'un composant et le préfixe `use` d'un hook relèvent du **fond**, parce que ce sont des contrats outillés, quand la colocalisation du test reste de la forme.

**POURQUOI la coupe passe avant la hiérarchie** : sans elle, « le repo gagne » laisserait un repo négligent éteindre « ne mocker que les I/O ». La cohésion se négocie, la correction non.

## La hiérarchie — elle ne porte que sur la forme

| Niveau | Source | Ce qui la range là |
|---|---|---|
| **0** | ce qu'un garde déterministe refuse | aucun arbitrage possible, le hook coupe à l'appel |
| **1** | la convention déclarée par le repo : `aidd_docs/memory/`, un fichier de convention, le `CLAUDE.md` du projet | elle vit dans le repo après moi et lie tout le monde qui y touche |
| **2** | la convention du harnais perso : `back-spring.md`, `front-react.md`, `commit-convention.md` | mon défaut, quand le repo ne déclare rien |
| **3** | la forme dominante, **comptée** et non estimée : le fichier édité, puis le module, puis le repo | aucune source ne déclare rien |
| **4** | je tranche et je l'écris en une ligne | aucune forme ne domine |

**POURQUOI le repo passe devant mon harnais**, à l'inverse de la précédence habituelle : une convention médiocre appliquée à 100 % d'un repo vaut mieux qu'une meilleure appliquée à 5 %.

**Le niveau 0 n'est pas théorique** : la mémoire d'un repo peut déclarer un type de commit que le garde refuse à l'appel. Une hiérarchie qui commencerait au niveau 1 promettrait le contraire de ce qui se passe.

**Le niveau 4 se pose quelque part.** Quand le repo porte un `aidd_docs/`, la décision s'écrit dans `aidd_docs/memory/`, jamais en auto-memory (cf. `memory-policy.md`).

## La portée — ce que le run crée, pas ce qu'il croise

| Cas | Ce que je fais |
|---|---|
| une source déclare la convention | je l'applique à ce que le run **crée**, et à rien d'autre |
| le run réécrit déjà du code existant | je le renomme au passage, la réécriture payant déjà le diff |
| le reste du fichier reste hors convention | je le laisse, et je ne le compte **pas** comme un défaut |
| aucune source ne déclare rien | niveau 3, puis niveau 4 |

**POURQUOI la portée s'arrête au neuf** : migrer l'existant dans le même run gonfle le diff et mélange deux intentions. C'est un `refactor` séparé, que l'humain demande.

## Ce que l'inversion ne touche pas

Aucun `CLAUDE.md` de projet ne rouvre `reasoning.md`, `plan-mode.md`, `tooling.md`, `ponctuation.md`, `style.md`, `reponse.md` ni `redaction.md`. Ces règles disent comment je travaille et comment je parle à l'utilisateur, pas à quoi ressemble un artefact du repo.

**POURQUOI le dire nommément** : sans cette liste, « la convention du repo gagne » se lit comme une porte ouverte, et un `CLAUDE.md` pourrait éteindre la discipline de vérification.

**Les cinq cas mesurés qui fondent tout ça** → `rules/references/ref-autorite-des-conventions.md`, dont le trou connu de la hiérarchie sur le défaut d'un framework installé.
