# Les contrôles structurels

Sept contrôles jugeables **sans connaître le métier**, parce qu'ils portent sur la structure du
changement et non sur son sens. Ils s'appliquent à n'importe quel repo, même inconnu.

## Les exemples sont des illustrations, jamais des réponses

Chaque contrôle porte un exemple pour reconnaître la **forme** du défaut. Ils viennent de revues passées
et aucun n'est une prédiction sur la MR en cours : **un exemple ne se rapporte jamais comme un finding
sans avoir été re-mesuré dans le code de cette MR.**

Mesuré sur la première revue conduite avec cette référence : deux des sept exemples ne se reproduisaient
pas. L'un désignait comme défaillant un chemin d'invalidation qui fonctionnait, l'autre décrivait comme
*le défaut* ce que la MR livrait comme *le correctif*. Se fier au premier faisait rapporter un défaut
inexistant **et** manquer le vrai. *Rien ne distingue de l'intérieur « j'ai détecté » de « j'ai
récité » — seule la mesure le fait.*

## 1. Une affirmation de la doc contredite par le code, ou par la doc elle-même

Lire **tout** le fichier de doc touché, pas seulement son diff : l'auteur ne le relit plus en entier,
c'est le seul angle qu'un regard neuf possède structurellement. C'est le contrôle au meilleur rendement.

> Exemple : la doc décrivait le nouveau mécanisme de version du template, et gardait trois paragraphes
> plus loin un avertissement qui *argumentait contre*, en décrivant l'ancien. Le prochain lecteur le
> « répare » à l'envers.

Sévérité : haute quand la partie périmée est prescriptive (un ⚠️, un « ne jamais »).

## 2. Un ajout que rien n'utilise

Lister les identifiants **introduits par la MR** — les lignes ajoutées de `git diff <base>..<head>`, pas
l'état courant du fichier — puis chercher chacun dans le reste du repo.

> Exemple : un item ajouté dans un fichier de template, référencé par aucune action. Le message de
> commit annonçait deux ajouts, un seul était arrivé.

**Le faux positif à écarter d'abord : une référence peut légitimement précéder sa cible.** Une donnée
déclarative peut nommer une clé que le mécanisme **crée** à l'exécution — une opération `add`, un
identifiant généré, une insertion conditionnelle. Mesuré : une première passe rendait 14 identifiants
« inutilisés » qui étaient tous des cibles créées par l'opération qui les nomme. Vérifier le sens de la
relation avant de conclure — un lot de non-défauts fait perdre au contrôle sa crédibilité pour les vrais.

Sévérité : basse en soi, mais c'est le signal le plus fiable d'un travail resté à moitié.

## 3. Un changement qui traverse une frontière de repo sans que le pendant soit livré

Repérer toute valeur qui voyage : un nom de champ posté à un autre service, une route, un contrat
d'événement. **Trouver quel repo regarder**, par coût croissant : la doc et les messages de commit
nomment souvent le destinataire ; sinon la classe qui construit l'appel sortant nomme l'hôte ou la
propriété de configuration ; sinon demander à l'auteur, ce qui coûte moins que deviner.

**Puis chercher le nom sur la branche que la cible de la MR déploie**, pas « sur toutes les branches » :
une MR qui part sur `preprod` a besoin de son pendant sur la `preprod` de l'autre repo, et le trouver
« quelque part » est le piège. Relever aussi l'avance de la branche de développement sur la cible —
c'est ce qui dit si le pendant est en route ou oublié.

> Exemple : un facteur de coût écrit par le service d'audit et censé être consommé par le service de
> calcul. Présent sur `develop` du calculateur, absent de `preprod` et de `prod`.

Sévérité : haute. Invisible dans le diff du repo relu, et invisible aussi pour sa suite de tests, qui
bouchonne l'autre service.

## 4. Un cache sans chemin d'invalidation pour une mutation qui peut le périmer

Énumérer **tous** les chemins d'écriture qui peuvent rendre la valeur fausse, et vérifier que chacun
invalide. Une seule manquante suffit.

Le chemin manquant est rarement celui qu'on soupçonne. Chercher surtout une écriture qui **contourne le
garde d'écriture** : quand le refus d'écrire et l'invalidation sont gouvernés par deux conditions
différentes, il existe une catégorie d'écriture qui passe le refus et saute l'invalidation.

> Exemple : le refus s'appliquait aux collections figées *sauf* pour une catégorie d'écrasement, tandis
> que l'invalidation vivait dans la branche « collection non figée ». Un ré-import sur une collection
> validée passait donc le refus et laissait la baseline périmée. À noter : le recalcul forcé, lui,
> invalidait bien — le chemin qui a l'air suspect n'est pas le chemin fautif.

Sévérité : haute, et le symptôme est différé, donc jamais rattaché à la MR.

## 5. Un garde-fou qui laisse passer quand il ne peut pas conclure

Tout mécanisme dont le métier est de refuser doit refuser **aussi** quand il n'arrive pas à décider. Deux
endroits, et le second est celui qu'on oublie :

- le **chemin d'erreur** — dépendance absente, entrée illisible, racine introuvable ;
- le **chemin nominal**, quand il porte une échappatoire délibérée : une expiration, un délai maximum, un
  `return` au lieu d'un refus au-delà d'un seuil. Là le garde s'ouvre seul, sans aucune erreur, et
  l'hypothèse qui justifie l'ouverture est souvent écrite juste au-dessus. La question est : « et si
  cette hypothèse est fausse ? »

> Exemple : un verrou d'écriture s'auto-libérait au bout de cinq minutes, en supposant qu'un traitement
> bloqué n'atteindrait jamais son bloc final. S'il finit par rendre, il l'atteint — et sa sauvegarde
> ré-insère le document qu'on venait d'autoriser à supprimer. L'hypothèse était documentée, donc
> assumée : ça en fait une **question à l'auteur, pas un défaut mesuré**. Le dire dans ces termes.

Vérifier aussi la **couverture annoncée** : un garde dont la javadoc dit fermer « la surface d'écriture »
et qui n'intercepte qu'un verbe HTTP sur quatre ferme un quart de ce qu'il déclare.

Sévérité : haute. Un garde qui échoue ouvert est pire qu'aucun garde, parce qu'on cesse de surveiller la
zone qu'il ne protège plus.

## 6. Le sens des dépendances entre les nouveaux composants

Sur un découpage de classe ou de module : vérifier que chaque arête va dans un seul sens. Un cycle se
voit sans rien connaître du domaine.

> Exemple : le découpage sortait deux composants dans leur propre bean précisément parce que leurs
> appelants ne les possèdent pas — sans ça le graphe de dépendances du conteneur bouclait. La
> justification était écrite ; la vérifier consistait à suivre les quatre arêtes.

Sévérité : variable. Souvent déjà justifié — lire la justification avant de contester.

## 7. Ce qu'une copie ou une persistance emporte, et ce qu'elle laisse

Un seul déclencheur — un mécanisme de copie ou de persistance touché par la MR — mais deux directions
d'erreur, et ne chercher que la première laisse passer la seconde, qui coûte plus cher.

**Un champ transitoire qui fuit.** À exclure de la persistance, des copies **et** des structures exposées
au client : trois mécanismes distincts, l'annotation qui exclut de la base n'excluant pas de la
sérialisation sortante.

**Une copie qui oublie un champ.** Pour chaque mécanisme de copie, se demander non pas « que copie-t-il »
mais « **que ne copie-t-il pas** ». Une copie qui énumère à la main les champs à reporter (opt-in) laisse
les autres à leur défaut, silencieusement ; une copie par sérialisation puis retrait (opt-out) échoue plus
bruyamment. Le premier type se re-casse à chaque nouveau champ.

> Exemple : deux mécanismes livrés dans la même MR, l'un par aller-retour JSON avec annulation explicite
> de deux caches, l'autre par énumération de six champs à la main. Le correctif embarqué dans cette même
> MR réparait précisément un champ oublié par l'énumération — la classe de défaut survivait donc au
> correctif. Le contrôle « le champ transitoire fuit-il », lui, ressortait propre.

Sévérité : moyenne pour la fuite, haute pour l'omission quand la copie sert de base à un calcul.

## Ce qui n'est PAS dans cette liste

Trois axes sortent du périmètre. Les raisons vivent dans les règles transverses du `SKILL.md`.

| Axe | Destinataire |
|---|---|
| Qualité de code — lisibilité, SOLID, nommage, duplication | `code-reviewer`, ou `aidd-dev:05-review` quand un plan AIDD existe |
| Sécurité — injections, authz, secrets, crypto | `security-reviewer` |
| Valeur métier — ce chiffre est-il le bon, cette maille est-elle la bonne, cette liste est-elle complète | le propriétaire de la spec, via `04-route` |
