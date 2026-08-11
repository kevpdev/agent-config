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

« Trop technique » et « flou » ne sont mesurés par aucun des cinq compteurs, et ne le seront pas. Un zéro sur les quatre premiers ne vaut donc jamais « la réponse est claire ». C'est le trigger « un comptage qui rend zéro » de `reasoning.md` appliqué à cet instrument.

**Le test qui tranche** se joue sur les sessions suivantes : rejouer `mesure-reponses.py` et comparer aux cinq lignes de baseline. Si les demandes de reformulation ne baissent pas, le défaut n'était pas dans le découpage, et il faut chercher côté hook bloquant. Un hook qui **rappelle** est déjà réfuté, puisque `style.md` était chargé pendant les 269 réponses mesurées.
