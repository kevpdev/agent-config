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

## Ce que les compteurs ne voient pas

« Trop technique » et « flou » ne sont mesurés par aucun des cinq compteurs, et ne le seront pas. Un zéro sur les quatre premiers ne vaut donc jamais « la réponse est claire ». C'est le trigger « un comptage qui rend zéro » de `reasoning.md` appliqué à cet instrument.

**Le test qui tranche** se joue sur les sessions suivantes : rejouer `mesure-reponses.py` et comparer aux cinq lignes de baseline. Si les demandes de reformulation ne baissent pas, le défaut n'était pas dans le découpage, et il faut chercher côté hook bloquant. Un hook qui **rappelle** est déjà réfuté, puisque `style.md` était chargé pendant les 269 réponses mesurées.
