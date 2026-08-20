# Rendu du texte envoyé à Jira

Ce que devient le markdown d'un brouillon quand il traverse le connecteur. Mesuré le 2026-08-20 par
aller-retour sur un ticket d'essai, en envoyant les deux formes dans le même champ pour les comparer.

## La règle

**Un paragraphe tient sur une seule ligne.** Pas de repli manuel, quelle que soit sa longueur.

**Gardent leurs retours à la ligne** : les puces, les titres, les tableaux et les blocs de code.

## Ce que la mesure a montré

| Envoyé | Relu |
| --- | --- |
| un paragraphe long sur **une seule ligne** | une seule ligne, intact |
| le même genre de paragraphe **replié à la main** | chaque ligne suivie d'un saut forcé, la phrase coupée en plein milieu |
| des puces en `-` | structure intacte, le tiret normalisé en `*` |
| un tableau en pipes | intact |
| un bloc de code délimité | intact, retours internes gardés |

**POURQUOI la règle existe** : Jira conserve les retours à la ligne du texte reçu, et les transforme en
sauts de ligne voulus. Un paragraphe replié par l'éditeur arrive donc coupé, et le lecteur du ticket
voit une mise en page que personne n'a demandée.

## Deux détails d'outillage, mesurés le même jour

**Le markdown suffit.** Le connecteur accepte du markdown en entrée et le convertit lui-même. Fabriquer
de l'ADF à la main n'apporte rien.

**On ne peut pas relire la structure réelle.** Demander l'ADF en format de réponse est **ignoré** sur le
champ de description : le connecteur rend du markdown dans tous les cas. La lecture des sauts forcés
est donc une déduction depuis cette ré-écriture, et non une lecture directe des nœuds. Elle tient,
parce que les deux espaces en fin de ligne ne sortent que d'un nœud de saut forcé.

⚠️ **Supposé, non vérifié** : qu'un commentaire passe par le même convertisseur que la description.
Le vérifier avant de s'appuyer sur un essai fait en commentaire pour conclure sur une description.
