# Critère d'inclusion en mémoire

Ce qui mérite d'exister dans un banc de mémoire AIDD, et ce qui n'y a pas sa place. Lu par
`03-frame-memory` pour trancher, par `04-deliver-memory` pour écrire, et tendu au checker par
`05-check-memory` en extension de sa checklist.

## Ce que ce fichier ajoute au framework

Le framework note déjà chaque candidat de 0 à 10 sur quatre poids — Durability, Reuse, Project fit,
Risk — dans `aidd-context/skills/10-learn/references/assessment.md`, qui **fait foi** sur les quatre.
Ses règles de contenu vivent dans `aidd-context/skills/02-project-memory/references/memory-rules.md`.
Ne pas les recopier ici : deux copies divergent au premier edit.

Aucun des quatre poids ne regarde si le fait est **reconstructible**. Un fait durable, réutilisable,
pertinent et risqué à oublier peut se relire en trois secondes dans un `pom.xml`. Il note 10 partout
et n'a rien à faire en mémoire. D'où les trois dimensions ci-dessous.

| Dimension | La question | Comment la mesurer |
| --- | --- | --- |
| **Inférable** | un agent le reconstruit-il depuis le repo sans qu'on le lui dise ? | nommer le fichier qui le porte. Aucun fichier → non inférable |
| **Coût de ré-inférence** | combien de fichiers, de repos, de commandes pour le rebâtir ? | compter les lectures. Un fichier → faible. Plusieurs repos → élevé |
| **Stabilité** | le fait bouge-t-il quand le code bouge ? | un numéro de port, une version, un décompte dérivent. Une décision, un piège, un « pourquoi » non |

## Le verdict — trois issues, jamais une quatrième

1. **Garder** le fait **non inférable** ou **spécifique au repo** : une décision, une convention, un
   piège vécu, le « pourquoi » d'un choix, un défaut consigné avec son arbitrage.
2. **Garder aussi**, par exception nommée, le fait **inférable dont le coût de ré-inférence est élevé
   et la dérive faible**. Le cas visé est le graphe d'appels inter-services que seule la lecture de
   dix-sept dépôts reconstitue.
3. **Sortir tout le reste**, et laisser un **pointeur de chemin** — jamais une copie.

**Les deux conditions de l'exception sont conjointes.** *Pourquoi la stabilité la ferme : un fait
dérivable et volatil recopié devient faux en silence, et rien ne le signale. Le coût de ré-inférence
mesure ce qu'on économise, la stabilité mesure combien de temps l'économie tient.*

**Le refus qui se prononce sans rien scorer** : une entrée qui ne fait que **recopier un fichier
présent sur le disque** n'entre pas. Ni un arbre de fichiers, ni un schéma, ni une liste de scripts,
ni un extrait de config. Le pointeur de chemin la remplace. *Pourquoi : la copie et sa source ne
divergent pas au même rythme, donc la copie devient un piège au lieu d'un raccourci.*

## Déduplication — un fait, un home

Le home est là où le fait est **produit**, pas là où il est pratique de le lire.

| Nature du fait | Son home |
| --- | --- |
| comportement du code, endpoint, schéma | le repo qui l'implémente |
| détail d'outillage d'un enfant (prérequis, piège, variante) | la fiche de cet enfant |
| commande qui fait **porte**, et son prérequis bloquant | l'index racine, par contrat de `memory-bootstrap` |
| décision, arbitrage, contrat partagé | régime décision, il se signale et ne se réécrit pas |

L'autre côté porte un chemin. **Signaler un doublon nomme les deux chemins et lequel garde le fait** —
le gabarit est la table « Duplicated facts » de `02-project-memory/assets/report.md`.

## Le piège — deux tests avant de l'écrire

Un piège coûte plus de mots que le fait qu'il corrige, parce qu'il doit nommer la source et la mauvaise
conclusion. C'est pour ça qu'une passe de correction fait grossir ce qu'elle corrige, et les deux tests
ci-dessous sont ce qui l'en empêche. Aucun ne demande de jugement.

**Test d'existence — d'où part le lecteur quand il se trompe ?**

| Il part de | Verdict |
| --- | --- |
| le **code** : un fichier absent, une valeur contre-intuitive, un comportement qui contredit son nom | le piège se justifie |
| une **copie fausse de la mémoire** | **supprimer la copie**, et n'écrire aucun piège |

*Pourquoi ce test : dans le second cas, la copie supprimée emporte la mauvaise conclusion avec elle, et
le piège ne documenterait plus qu'une ancienne erreur de la mémoire. Mesuré le 2026-08-21 sur deux
cycles d'audit : c'est ce second cas qui a produit l'essentiel d'un +28 % sur le fichier le plus lourd
du banc.*

**Test du home — combien de cibles partagent la cause ?**

| Cibles | Où le piège vit |
| --- | --- |
| une | chez elle |
| plusieurs | chez la **cause**, une seule fois. Les symptômes se **suppriment**, ils ne s'annotent pas |
| la cause n'a pas de fiche | la créer. C'est le signal qu'un producteur n'est pas documenté |

*Pourquoi supprimer et non annoter : mesuré le 2026-08-21, trois causes uniques portaient 54, 52 et 11
mentions dans le banc. Annotées une par une, elles coûtent autant de fois les mots et laissent autant
d'endroits où diverger. C'est le « un fait, un home » de la section au-dessus, appliqué à la cause au
lieu du fait — et la cause la plus dupliquée du banc mesuré n'avait aucune fiche.*

**Le renvoi va du symptôme vers la cause**, de fiche à fiche. `memory-bootstrap` n'interdit que le
renvoi d'une fiche vers l'**index**, et pour une raison qui ne s'applique pas ici : une back-référence
est un doublon à maintenir, quand un pointeur vers la cause est ce qui **remplace** un doublon.

**Trois calibrages**, à rejouer si ces tests sont réécrits. Un critère qui ne rend pas ces trois verdicts
est mal écrit.

| Cas | Verdict attendu |
| --- | --- |
| `mvnw` commité sans le bit `x`, donc `./mvnw` seul rend « Permission non accordée » | le lecteur part du code, **piège légitime**. Plusieurs cibles, donc home unique chez la cause |
| une fiche affirmait un fichier « présent » alors qu'il est absent du repo | le lecteur partait d'une copie fausse, **suppression, aucun piège** |
| un service dont on cherche le `Dockerfile` et qui n'en a pas, parce qu'un dépôt tiers porte l'image partagée | le lecteur part du code, **piège légitime**, home chez le dépôt qui porte l'image |

## Verbosité — mesurer le coût, sans fixer de cible

**Aucun plafond chiffré.** *Pourquoi, mesuré le 2026-08-20 : une passe menée sous un plafond de 6 000
mots sur la racine du banc a fini à 9 591, et le seul fichier qui l'en empêchait était le graphe
d'appels inter-services — précisément l'exception nommée plus haut. Un chiffre que le contenu légitime
ne permet pas d'atteindre ne borne rien, il met sous pression de rogner ce qui compte pour faire le
compte.*

**À LA PLACE**, trois gestes. Ils rendent le coût **visible** sans donner de nombre à atteindre.

- **Afficher le décompte, à chaque passe.** `wc -w aidd_docs/memory/*.md | tail -1` sur la racine,
  celle que le bloc `<aidd_project_memory>` charge à chaque session. Le chiffre se rend, il ne se
  compare à rien.
- **Justifier une hausse, jamais une valeur.** Une passe qui fait grossir l'ensemble @-importé nomme
  ce qu'elle ajoute et pourquoi le critère le retient. **Pour chaque piège écrit, elle nomme de quel
  côté du test d'existence il tombe** : un piège du second type est une régression, pas une correction. Une passe qui le réduit n'a rien à justifier.
  *Pourquoi cette asymétrie : le sens de variation est un fait, un niveau est un jugement.*
  - **Le cas nommé — une passe de pointeur monte, et c'est normal.** Remplacer une copie par un
    pointeur coûte **plus** de mots que la copie dès que celle-ci est un jeton court, un numéro de
    port ou une version : nommer `backend/docky/docker-compose.yml` prend plus de place que `3002`.
    Une telle passe justifie sa hausse en nommant **les copies retirées et le fichier qui les porte
    désormais**, jamais en commentant le delta.
    *Mesuré le 2026-08-21 sur un `architecture.md` : 3 438 → 3 557 mots, cinq copies de config
    retirées, deux affirmations fausses corrigées, dont +48 mots pour un piège qui manquait.*
    **NE PAS en déduire** qu'une hausse due à un pointeur n'a rien à justifier : n'importe quelle
    hausse se raconte comme un pointeur, et cette porte ne se referme plus. Le geste reste de
    justifier, seule l'**unité** change — des copies nommées, pas un nombre de mots.
    *Pourquoi ce cas est indispensable : sans lui, l'asymétrie ci-dessus récompense la passe qui
    garde la copie, puisque la copie est moins chère en mots que son pointeur. C'est l'incitation
    exactement inverse du refus dur.*
  - **Le second cas nommé — une consolidation monte, et le mot n'est pas son unité.** Ramener un fait
    dupliqué à un seul home coûte **plus** de mots que ses copies, parce qu'une copie allude et qu'un
    home documente. Une telle passe rend le **nombre de homes du fait**, avant et après. Elle ne
    justifie rien en mots.
    *Mesuré le 2026-08-21 : le fait « les Dockerfile vivent dans `backend/devops/docker/` » vivait en
    48 mentions réparties sur 17 fiches. Après consolidation dans une fiche `devops` neuve, il en
    reste un home plus quatre mentions légitimes, et le banc passe de 47 630 à 48 037 mots, soit
    **+407**. La passe a fait exactement ce que le test du home prescrit, et le décompte de mots l'a
    notée en régression.*
    **NE PAS lire ce cas comme une dispense.** Il ne couvre que la passe qui **supprime** les
    symptômes. Une passe qui les annote monte aussi, et elle n'a rien consolidé — c'est le décompte
    de homes, pas celui de mots, qui sépare les deux.
- **Relire ce qui dépasse ses pairs**, sans obligation de le réduire : au-delà de **2× la médiane** de
  son home, un fichier se relit contre le critère. C'est un déclencheur de lecture, pas une cible de
  coupe — un fichier peut passer la relecture et rester au-dessus.

**Compter en mots, jamais en lignes.** *Pourquoi : mesuré sur un `architecture.md`, les libellés
multilignes des nœuds Mermaid pesaient 125 lignes pour 266 mots. Une réduction estimée à 230 lignes a
fini à 315.*

**Le refus reste la seule borne dure**, et il porte sur le fait, pas sur la taille : une entrée qui
recopie un fichier du disque n'entre pas. Un banc dont chaque entrée passe le critère a la taille
qu'il doit avoir.

## Contrôle de sortie

Un candidat passe s'il porte, en une ligne chacun :

- le fichier qui le rend inférable, ou la mention « aucun » ;
- son coût de ré-inférence et sa stabilité, quand le verdict s'appuie sur l'exception ;
- son verdict — garder / pointeur vers `<chemin>` / sortir ;
- sa réconciliation dans la taxonomie de `10-learn` (`new`, `covered`, `updates`, `supersedes`,
  `retracts`).

Un candidat sans le fichier nommé **ni** la mention « aucun » n'a pas été mesuré : il ne passe pas.
