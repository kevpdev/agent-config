# 03 - Cadrer la mémoire

Décide ce qui mérite d'exister en mémoire avant d'écrire une ligne : garder, pointer, ou sortir.

## Input

- Les cibles de régime **reflet** classées en action 02 qui touchent la memory (`aidd_docs/memory/*`).
- L'état du banc au home résolu par l'action 01 : `<enfant>/aidd_docs/memory/` (distribué) ou
  `aidd_docs/memory/<enfant>/` au parent (centralisé).
- Le scope validé, qui donne les candidats issus du diff. En `--audit` il n'y a pas de diff : les candidats sont **chaque fait porté par les fichiers du scope**, et la seconde source de l'étape 2 devient la source unique.

## Output

Un plan de mémoire, une ligne par candidat : le fait, le fichier qui le rend inférable ou « aucun »,
le verdict (**garder** / **pointeur vers `<chemin>`** / **sortir**), et la réconciliation. Rien n'est
écrit à ce stade.

## Process

1. **Charger.** Lire [memory-criteria.md](../references/memory-criteria.md), puis les quatre poids du
   framework dans `aidd-context/skills/10-learn/references/assessment.md`. Le second fait foi sur les
   quatre poids, le premier ajoute les trois dimensions qui manquent.
2. **Lister les candidats.** Deux sources, dans cet ordre. D'abord ce que le scope apporte de neuf.
   Ensuite ce que le banc porte **déjà** sur les fichiers que la passe va toucher — un candidat n'est
   pas seulement un fait à ajouter, c'est aussi un fait en place dont la présence se rejuge.
   - *Pourquoi rejuger l'existant : une passe qui n'examine que le neuf laisse grossir le banc à chaque
     run, et le critère ne mord jamais sur ce qui est déjà là.*
   - **En `--audit`, la première source est vide et la seconde s'élargit.** Aucun fait neuf n'arrive,
     et « les fichiers que la passe va toucher » sont **tous** ceux du scope. Le mécanisme ne change
     pas, seul l'ensemble grandit. *Pourquoi le noter : sans cette ligne, l'étape cherche un diff
     qu'elle ne trouve pas et rend zéro candidat sur un banc qu'elle n'a pas lu.*
   - **Sur un retour de l'action 05, ne pas relister.** Le périmètre est alors les seuls constats
     routés, pas le banc entier. *Pourquoi : relister rouvre des candidats déjà tranchés, ce qui fait
     grossir le lot au lieu de le réduire — et c'est exactement le signal que l'action 05 lit pour
     arrêter le cycle.*
3. **Mesurer avant de noter.** Pour chaque candidat, nommer le fichier qui le porte dans le code ou la
   config. Aucun fichier → non inférable. Un fichier → relever le coût de ré-inférence et la
   stabilité.
   - **Nommer le fichier, ne pas l'estimer.** Un candidat dont le fichier source n'a pas été ouvert
     n'est pas mesuré, il est supposé — et il se marque comme tel.
4. **Trancher.** Appliquer le verdict en trois issues du critère. Les deux conditions de l'exception
   (coût élevé **et** dérive faible) sont conjointes : une seule remplie donne un pointeur, pas un
   « garder ».
5. **Réconcilier.** Classer chaque verdict dans la taxonomie de `10-learn` — `new`, `covered`,
   `updates`, `supersedes`, `retracts`. Un candidat `covered` ne descend pas en action 04.
6. **Afficher le coût.** Compter les mots de la racine du banc (`wc -w`) et rendre le chiffre tel quel,
   sans le comparer à une cible — il n'y en a pas. Un plan qui fait **grossir** cet ensemble nomme ce
   qu'il ajoute et pourquoi le critère le retient ; un plan qui le réduit n'a rien à justifier.
7. **Rendre le plan.** Le montrer avant de descendre en action 04. Un verdict « sortir » ou
   « pointeur » sur un fait que l'humain a écrit à la main se **soumet**, il ne s'applique pas seul.
   - *Pourquoi cette asymétrie : décrire ce que le code fait est un constat, retirer une phrase qu'un
     humain a jugée utile est une décision.*

## Test

- Chaque candidat porte un verdict et une réconciliation, ou est marqué « supposé » faute de source
  ouverte.
- Chaque candidat nomme le fichier qui le rend inférable, ou porte la mention « aucun ».
- Un candidat inférable, à coût de ré-inférence faible **ou** à dérive forte, ne ressort jamais en
  « garder » : il ressort en pointeur ou en sortie.
- Un candidat qui ne fait que recopier un fichier du disque ressort en pointeur, jamais en « garder ».
- Le plan cite le décompte de mots de la racine. S'il la fait grossir, il nomme ce qui l'a fait grossir.
- Aucun candidat n'est sorti pour atteindre un chiffre : chaque sortie cite le volet du critère qui la
  motive.
- Aucun fichier de mémoire n'a été modifié par cette action.
