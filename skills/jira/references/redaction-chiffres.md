# Chiffres dans un ticket — l'intention partout, une liste datée au plus

Ce que la mise en forme vérifie avant d'envoyer une description à Jira. Le défaut visé est propre aux
tickets techniques : ils décrivent un parc, et le parc bouge sous eux.

## La règle

**Un chiffre qui décrit l'état du parc ne se rafraîchit pas, il se remplace par l'intention.**

- ❌ « la vague touche les 19 dépôts consommateurs »
- ✅ « la vague touche tous les dépôts consommateurs »

La seconde phrase reste vraie à 24 dépôts et à 31. La première est fausse au prochain merge d'un
collègue, et rien ne le signale.

Trois rôles pour un chiffre, et un seul pourrit :

| Rôle | Forme | Dérive-t-il ? |
| --- | --- | --- |
| **preuve datée** — pourquoi la décision se justifie | « mesuré le 2026-03-04 : 19 consommateurs » | non, il est au passé et daté |
| **ordre de grandeur** — ce qui porte l'intention | « une vingtaine de dépôts », « tout le parc » | non |
| **état du parc** — combien il y en a *maintenant* | « les 19 dépôts consommateurs » | oui |

**Une mesure datée ne se corrige jamais.** Elle dit ce qui a été vu ce jour-là, et ça reste vrai.
Quand elle a vieilli, on pose une nouvelle mesure à côté au lieu de réécrire l'ancienne.

## La liste chiffrée, quand elle sert

**Elle n'est pas obligatoire.** On l'écrit quand elle aide le développeur et l'agent à voir vite quels
projets sont impactés, jamais parce qu'un ticket technique aurait besoin d'un tableau.

Quand elle est là, trois contraintes :

1. **Une seule fois dans le ticket.** La liste et son total vivent dans une section unique. Partout
   ailleurs, le texte renvoie à cette section sans répéter ni le compte ni les noms.
2. **Datée dans son titre**, par exemple `## Inventaire — relevé du 2026-03-04`.
3. **Une alerte de péremption**, qui dit de rejouer le relevé avant d'agir et qui nomme la commande ou
   l'appel qui le produit.

Forme de l'alerte :

> ⚠️ **Cette liste est une photo, pas le périmètre.** Rejouer `<la commande>` avant de commencer. Le
> relevé précédent, daté du 2026-02-11, donnait 19 dépôts : deux chantiers ont passé depuis.

**Un critère d'acceptation ne fige jamais un compte.** Il pointe l'instrument, par exemple
« l'inventaire du jour est publié dans le ticket ».

## Pourquoi

Un chiffre recopié dans un ticket est une copie de la réalité, et une copie diverge de sa source sans
que rien ne le signale. L'intention, elle, ne bouge pas tant que le besoin tient.

La verbosité tombe avec. Un ticket qui décrit le parc doit le re-décrire à chaque évolution, quand un
ticket qui dit ce qu'il veut obtenir n'a rien à rafraîchir.

**Ce que coûte le défaut, mesuré sur une session de correction** : cinq occurrences périmées du même
compte, réparties dans quatre tickets, chassées à la main l'une après l'autre. Aucune n'était fausse
à l'écriture.

## Ce que la règle ne dit pas

Elle porte sur la **forme du texte envoyé**, jamais sur le contenu du brouillon ni sur la maturité du
besoin, qui appartiennent au skill `aidd-pm` du type visé.
