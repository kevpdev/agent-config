# Références — `style.md`, `profil.md`, `reponse.md`, `redaction.md`

Les mesures qui fondent le découpage par médium. Jamais chargé automatiquement.

---

## Le découpage était par lieu, il devait être par médium (2026-08-11)

**Le symptôme, rapporté par l'utilisateur puis mesuré** : trop verbeux, flou et technique en chat. Comptage sur la session du jour, 269 réponses dont 114 de fond.

| Mesure | Valeur | Comparaison |
|---|---|---|
| Demandes de reformulation | **12 sur 113 prompts** (11 %) | dont « je n'ai pas compris, explique plus simplement », « c'est flou ce que tu viens de me dire » |
| Ouvertures sur une phrase abstraite | **39 sur 114** | |
| Phrases de plus de 30 mots | **240 sur 1 431** (17 %) | |
| Tirets cadratins / 1 000 mots | **13,67** | contre 2,17 dans les fichiers après la dette payée le même jour |
| Points-virgules / 1 000 mots | **1,74** | cible de 1,09 |

**Le corpus des réponses était 6 fois pire que le point de départ des fichiers** (10,85). La dette de ponctuation avait été payée dans les fichiers pendant que les réponses ne l'étaient pas, parce qu'aucune commande du repo ne mesurait une réponse. D'où `wrappers/claude/scripts/mesure-reponses.py`.

## Trois causes, aucune n'étant « la règle est mal écrite »

**1. Les consignes manquantes existaient, dans un fichier jamais actif en même temps.** `vault-style.md` portait « cerveau fatigué ou enfant de 10 ans doit comprendre », « sujet + verbe + objet », « voix active », « jargon maîtrisé », « l'exemple d'abord, la règle après ». Sa `description` disait « override le style chat quand le CWD est le vault », et le `settings.json` du vault épinglait `"outputStyle": "vault-style"`.

**2. Le mécanisme ne sait pas exprimer le bon axe.** `outputStyle` est un scalaire, donc un style par session, donc il exprime le **lieu**. Le contenu dépend du **médium**. Or les deux médiums coexistent : le même jour, une édition de `reasoning.md` et une réponse de chat dans le même tour. **Un mécanisme un-par-session ne peut pas porter une distinction qui change à l'intérieur du tour.**

**3. Deux règles chargées se disputaient la première ligne.** `style.md` disait « verdict d'abord, la première ligne est la réponse ». `profil.md` disait « ouvrir sur l'exemple ou l'analogie, l'inverse de l'ordre académique ». L'ordre académique gagnait 39 fois sur 114.

**Le mot « concret » faisait deux métiers**, ce qui rendait le conflit invisible. `style.md` le définissait comme « un chemin de fichier, un chiffre, une citation ». `profil.md` comme « exemple, schéma, analogie ». **73 réponses sur 114 ouvraient sur un chiffre ou un chemin**, donc satisfaisaient le premier sens en manquant le second. Un chiffre est vérifiable et n'explique rien.

**Ce que la résolution ne coûte pas** : les deux prescriptions tiennent ensemble dès que le verdict est lui-même concret. Cas travaillé du même soir, une réponse ouvrant sur la citation « cerveau fatigué ou enfant de 10 ans doit comprendre », qui était à la fois le verdict et l'ancre.

## Pourquoi le contenu quitte les wrappers

Une rule globale est injectée dans les sous-agents, vérifié le 2026-07-20 par sondage d'un sous-agent `general-purpose` sans aucune lecture disque. Un output style, non. Tout critère laissé dans `chat-style.md` ou `vault-style.md` ne traversait donc ni un sous-agent ni un second wrapper. `wrappers/` n'en compte qu'un aujourd'hui, `claude`, donc la contrainte multi-agent est tenue par principe et non validée sur une seconde instance.

**Les deux output styles ne sont pas supprimés**, et le binding `outputStyle` n'est pas vidé : un style absent rend la main au style par défaut de l'outil, comportement non vérifié. Garder les deux fichiers coûte 111 et 184 mots et ne parie sur rien.

## Coût du redécoupage, et une estimation ratée d'un facteur 3,4

| | Avant | Estimé au plan | Mesuré |
|---|---|---|---|
| Couche permanente | 3 134 | ~3 323 | **3 770 avant coupe** |
| Écart | | +189 | **+636** |

L'estimation a raté parce qu'elle chiffrait le contenu déplacé sans chiffrer les POURQUOI écrits pour l'accompagner. Les blocs de mesure ajoutés à `style.md` et `reponse.md` pesaient à eux seuls plus que l'écart annoncé. **Leçon d'instrument** : une estimation de mots posée sur du contenu à déplacer ignore le contenu à écrire, qui n'existe pas encore au moment où on estime.

Corrigé en appliquant la troisième ligne de C5, écrite le matin même : la preuve descend ici, le critère reste chargé.

## Parler comme à un collègue — les paires avant/après (2026-08-11)

L'utilisateur a nommé le défaut lui-même : « tu ne parles pas comme un humain ordinaire avec un langage familier, comme d'un collègue à collègue, mais comme un scientifique ou un ingénieur ultra technique. Parfois j'ai l'impression que tu parles à l'IA et non à un humain. » C'est ce que « flou et trop technique » voulait dire, et aucun des cinq compteurs ne le voit.

**91 phrases de la même session** portaient au moins deux termes de jargon maison, ou un terme et plus de 34 mots. Cinq extraites, réécrites à côté.

| ❌ Écrit | ✅ Réécrit |
|---|---|
| « Comme `reasoning.md` porte lui-même le trigger "un comptage qui rend zéro", je calibrerai l'instrument sur un cas positif connu avant de conclure. La règle supprimée de `workflow.md` est du *legacy harness scaffolding* textuel. » | « Avant de dire "j'ai trouvé zéro problème", je vérifie que mon test sait en trouver un. Je lui donne un cas que je sais mauvais. S'il ne le voit pas, mon zéro ne prouve rien. » |
| « L'item C1b sur `reasoning.md` reste ouvert avec un sous-item pour le swap. C'est du C7, les 15 obligations de vérification sont intactes. » | « Le gros du travail sur ce fichier reste à faire. Ce qu'on vient de changer, c'est la formulation, pas le fond. » |
| « Le dépassement n'est pas porté par de l'argumentation mais par l'impératif. » | « Ce n'est pas du bavardage qu'il faut couper, il y a deux consignes collées ensemble. » |
| « Hors périmètre : `back-spring.md` et `front-react.md`, scopés par `paths:` donc hors couche chargée. » | « Je n'ai pas compté ces deux fichiers. Ils ne se chargent que quand tu ouvres du Java ou du TypeScript. » |
| « Cible 3 950 tenue avec 915 de marge, et elle n'a pas été atteinte par la cascade mais par tes deux décisions de fond. » | « L'objectif était 3 950 mots, on est à 3 035, donc c'est tenu large. Mais le gain vient de tes deux décisions de supprimer des fichiers, pas de l'audit. » |

**Les trois tics, dans l'ordre de nuisance** :

1. **Le nom abstrait qui remplace le verbe.** « Le dépassement est porté par l'impératif » au lieu de « il y a deux consignes collées ».
2. **Le code interne balancé comme si le lecteur l'avait en tête.** Un identifiant d'audit, un nom de couche, un critère numéroté.
3. **Trois idées dans une phrase**, tenues par un deux-points et un tiret. C'est le seul des trois qu'un compteur de longueur approche, et il ne l'attrape qu'à moitié.

**Une référence doit se rappeler en trois mots.** Contrainte d'environnement rapportée le même jour : l'utilisateur travaille en onglets de terminal et relit la dernière réponse à froid, sans le fil au-dessus. Un « #16 » ou un « #10 » renvoyant à un tableau de 19 lignes affiché vingt réponses plus haut ne veut plus rien dire. La règle vit dans `reponse.md`, parce que le défaut naît du défilement d'une conversation et non d'un support relu.

## Ce que les compteurs ne voient pas

« Flou » n'est mesuré par aucun des sept compteurs et ne le sera pas. Un zéro ne vaut donc jamais « la réponse est claire ». C'est le trigger « un comptage qui rend zéro » de `reasoning.md` appliqué à cet instrument. Le sixième, la longueur, ne fait pas exception : 150 mots creux restent creux.

**Corrigé le 2026-08-12** : cette section affirmait aussi que « trop technique » ne serait jamais mesuré. C'était faux d'un de ses trois tics. L'ouverture-étiquette a une forme, donc elle se compte, et le septième compteur la compte. Les deux autres tics restent invisibles.

**Le test qui tranche** se joue sur les sessions suivantes : rejouer `mesure-reponses.py` et comparer aux six lignes de baseline. Si les demandes de reformulation ne baissent pas, le défaut n'était pas dans le découpage, et il faut chercher côté hook bloquant. Un hook qui **rappelle** est déjà réfuté, puisque `style.md` était chargé pendant les 269 réponses mesurées.

## Le seul axe de style sans compteur était le seul à ne pas bouger (2026-08-12)

Session Winggy-v3, ticket VW3-3219 puis VW3-3233. La consigne en vigueur disait « couches progressives : la couche 1 donne la reco et une ligne de pourquoi, les détails sur demande ». Rejeu de `mesure-reponses.py`, plus un comptage de longueur qu'il ne savait pas faire :

| | Session VW3-3233 | Session `18cd7832`, même projet | Baseline 2026-08-11 |
|---|---|---|---|
| Réponses de fond | 12 | 11 | 258 |
| **Médiane** | **289 mots** | 109 mots | non mesurée |
| Moyenne | 265 | 164 | non mesurée |
| Max | 425 | 550 | non mesurée |
| Au-delà de 200 mots | **10 sur 12** | ~4 sur 11 | non mesurée |
| Tirets cadratins | 4,09 / 1 000 | — | 13,93 |
| Ouvertures abstraites | 5 sur 12 | — | 39 sur 112 |

Distribution complète : `[79, 124, 207, 251, 266, 277, 289, 297, 310, 317, 340, 425]`.

**Le défaut n'est pas la réponse trop longue, c'est l'absence de réponses courtes.** Deux sur douze passent sous 200 mots. La session de comparaison en a une majorité, avec un maximum pourtant plus haut (550). Une règle qui viserait la moyenne ou le pic raterait les deux fois.

**Cause, établie en lisant l'instrument** : `mesure-reponses.py` calculait `mots` comme un total, l'affichait en en-tête et ne le divisait jamais par le nombre de réponses. Des axes de style que le harnais surveille, les couches progressives étaient le **seul sans compteur**, alors que ce même fichier écrit que le test qui tranche est « rejouer `mesure-reponses.py` et comparer aux baselines ». Un axe non mesuré ne se corrige pas, exactement comme la ponctuation avant 2026-08-11.

**Cause seconde, un conflit d'autorité** : `aidd-dev/01-plan/actions/04-plan.md:19` ordonne « Show the complete plan and its phases with a confidence score (0 to 10, ✓ reasons and ✗ risks) ». Cet impératif concret a produit la réponse de 425 mots. Un impératif de skill bat une préférence de dosage, et il continuera de le faire tant que la règle n'écrit pas l'exception. D'où l'exception nommée dans `reponse.md` : le contenu prescrit par un skill va dans l'artefact, le chat garde la couche 1 et l'offre.

## Un auto-diagnostic non mesuré a sur-accusé deux règles sur trois (2026-08-12)

Interrogé sur ce qui avait failli, l'agent a désigné `reponse.md:10-12`, trois lignes. La mesure n'en retient qu'une.

| Ligne | Accusée | Verdict après mesure |
|---|---|---|
| `:10` « Une ancre visuelle par bloc » | oui | **à tort.** Les quatre paragraphes en gras portaient chacun **une** ancre. Le défaut était le nombre de blocs, pas les ancres par bloc |
| `:11` « Tableau dès qu'on compare 2 options ou plus » | oui | **à tort.** Elle porte déjà son déclencheur. Enfreinte une fois (4 variantes de script comparées en prose) : défaut d'application, pas de rédaction |
| `:12` « Couches progressives » | oui | **à raison.** Aucun déclencheur, aucun geste, aucun seuil, aucun compteur |

**Ce que ça coûte quand on ne mesure pas** : réécrire `:10` et `:11` aurait ajouté du texte à la couche permanente pour corriger des défauts inexistants, et aurait fait perdre à `:11` un déclencheur qu'elle avait déjà. L'auto-diagnostic d'un agent sur son propre tour est une hypothèse, au même titre qu'une prémisse de codebase non vérifiée.

**Ce qui reste vrai de l'auto-diagnostic** : les deux tirets cadratins comptés à la main dans la réponse fautive. La règle de ponctuation, elle, est bien formée — tableau de substitutions, ❌/✅, section TEST — et a été enfreinte quand même. Une bonne formulation réduit le taux de faute, elle ne l'annule pas.

## Le mode rapport a une forme, et elle se compte (2026-08-12)

Deuxième signalement du même défaut en deux jours. Le 2026-08-11 : « tu parles comme un scientifique ou un ingénieur ultra technique ». Le 2026-08-12 : « tu as tendance à parler en mode rapport pour décrire ta conclusion après une tâche, alors que je veux que tu parles comme un humain avec un langage familier et simple ».

Entre les deux, le travail avait porté sur la **longueur** des réponses. Le ton n'avait pas bougé, et c'est logique : la seule prescription qui le couvrait, la section « Ton et voix » de `profil.md`, ne disait pas **quand** elle s'applique. Une règle sans déclencheur se lit comme un conseil d'ambiance.

**Ce que la formulation du jour apporte de neuf** : le moment. Le mode rapport revient au compte rendu de fin de tâche, pas n'importe où dans la conversation.

### L'ouverture-étiquette

Le tic a une forme repérable : un nom sans verbe, suivi de deux-points. Extraits de la session Winggy-v3 `f6734970`, tous authentiques :

> « Mesure décisive : … », « Piège de nommage repéré : … », « Commité : … », « Plan écrit : … », « Ordre proposé dans la note, inchangé : … », « Hors contrat, capturé sans creuser : … », « Ce que l'analyse a tranché : … »

Aucune n'a de sujet qui fait quelque chose. C'est du libellé de rapport posé à la place d'une phrase parlée.

### La mesure

Regex calibrée avant comptage, sur un positif et un négatif écrits à la main. Positif : « Coût : reponse.md passe à 591 mots ». Négatif : « Ouais, tu as raison. Regarde ma réponse d'il y a deux minutes : ». Le calibrage est embarqué dans le script et se rejoue à chaque exécution.

| Session | Réponses de fond | Ouvertures-étiquettes | Pour 1 000 mots |
|---|---|---|---|
| Winggy-v3 `f6734970` | 20 | 31 | 6,6 |
| Winggy-v3 `18cd7832` | 11 | 17 | **9,4** |
| Winggy-v3 `7abd0441` | 2 | 1 | 2,1 |
| agent-config `83cc4366` | 119 | **223** | 6,1 |
| agent-config `c15637e6` | 56 | 77 | **5,3** |
| agent-config `5ce2b1c0` | 43 | 69 | 6,4 |
| agent-config `01b10955` | 3 | 5 | 5,7 |

**423 occurrences.** Hors les deux sessions de moins de cinq réponses, le taux tient entre 5,3 et 9,4 dans les deux projets. Ce n'est pas un accident de session, c'est le régime permanent. Dans la session du jour, **18 réponses de fond sur 20** en portent au moins une.

### Ce que ça règle en plus, sans règle supplémentaire

Le même signalement portait une seconde contrainte : l'utilisateur change d'onglet et relit une réponse à froid, sans le fil au-dessus, et il ne doit pas avoir à faire défiler pour comprendre. L'ouverture-étiquette est précisément ce qui casse ça. « Mesure décisive : » n'apprend rien à qui n'a pas le contexte, alors que « ce qui a tranché sur le placement du curl, c'est… » se lit seul. Le geste sujet-verbe répare les deux défauts d'un coup.

**Ce qui n'a donc pas été touché** : `reponse.md:8-9`, « toute référence se rappelle en trois mots », qui porte déjà l'exemple de l'identifiant renvoyant à un tableau plus haut et déjà le POURQUOI des onglets de terminal. Elle est bien écrite et mal appliquée. La réécrire aurait ajouté du texte sans corriger quoi que ce soit, l'erreur exacte mesurée le matin même sur deux règles accusées à tort.

### Le remboursement

Le bloc « Couper à la reco » écrit la veille pesait **273 mots sur les 614** de `reponse.md`, soit 44 % du fichier pour une seule puce. Deux de ses cinq sous-lignes ne faisaient que raconter le ratage du jour, et les deux étaient déjà écrites plus haut dans ce fichier-ci. Coupées, remplacées par un renvoi d'une ligne.

| | Avant | Estimé au plan | Mesuré |
|---|---|---|---|
| `reponse.md` | 614 mots | ~430 | **546** |
| `profil.md` | 445 mots | ~535 | **663** |
| Net | | **−94** | **+150** |

**L'estimation s'est trompée de signe, et pour la deuxième fois de la même manière.** La section « Coût du redécoupage » plus haut dans ce fichier documente déjà le même ratage, d'un facteur 3,4 le 2026-08-11, avec sa cause : une estimation posée sur du contenu à déplacer ignore le contenu à écrire, qui n'existe pas au moment où on estime. Ici, le déplacement était nul (le contenu descendu existait déjà en double) et tout le poids venait de l'écriture neuve. La leçon avait été écrite et n'a pas été appliquée le lendemain.

**Ce qui justifie de payer quand même** : le ton est le défaut signalé deux jours de suite, et c'était le dernier axe sans déclencheur ni compteur. La règle de ponctuation avait établi la forme qui marche, un tableau « à la place de / écrire », qui fait bouger un chiffre là où un dosage ne fait rien.

**Ce qui reste non tenu par un instrument** : aucun des trois hooks branchés ne peut aider. `guard-bash-tooling`, `guard-no-claude-in-commit` et `guard-no-remote-write` sont des `PreToolUse` sur Bash, ils ne voient jamais un texte de réponse. Le test est donc différé, au rejeu du compteur dans deux ou trois sessions.
