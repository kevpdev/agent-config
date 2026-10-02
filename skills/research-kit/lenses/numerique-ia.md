# Lentille : numérique et IA

Domaines : intelligence artificielle, développement logiciel, réseaux, systèmes, sécurité informatique, outils numériques.

Charger quand la question porte sur un logiciel, un langage, une bibliothèque, un modèle d'IA, un protocole ou une vulnérabilité. Lire aussi `lenses/_technique.md`. Les noms de sources sont donnés de mémoire et se vérifient en ouvrant la page.

## Sources fiables

- **Documentation officielle** de l'outil ou du langage, à la version concernée.
- **Spécifications et normes** : documents de normalisation de l'Internet, standards des organismes de normalisation.
- **Journaux de changements, notes de version, dépôts de code** : l'historique des commits et les tickets sont des sources primaires pour un comportement.
- **Bases de vulnérabilités** : bases CVE et bases nationales de vulnérabilités, avis de sécurité des éditeurs, avec le score et la version affectée.
- **Recherche** : articles relus ou prépublications de conférences reconnues, étiquetés selon leur statut (SRC5).

## Sources à traiter avec prudence

- Benchmarks d'éditeur sur son propre produit, et classements de modèles sans protocole publié (SRC4).
- Réponses de forums et de questions-réponses : utiles comme piste, souvent obsolètes ou liées à une version.
- Tutoriels et billets de blog sans date ni version.
- Annonces de lancement et communiqués : l'annonce n'est pas la disponibilité.
- Réseaux sociaux : un message est un signalement (V10).

## Cadres d'analyse

- **Version d'abord** : toute affirmation indique la version, la date de la source et la date de la dernière vérification.
- **Reproductibilité** : un comportement se confirme par un essai ou par la documentation, pas par un seul témoignage.
- **Compromis explicites** : performance, coût, maintenabilité, sécurité, dépendances, verrouillage chez un fournisseur.
- **Modèles d'IA** : tâche évaluée, jeu de test, protocole, contamination possible des données d'entraînement, variance entre exécutions.

## Pièges propres

- Version obsolète : l'API, l'option ou le tarif décrits ont changé (SRC2).
- Benchmark d'éditeur ou résultat obtenu sur une configuration que l'utilisateur n'aura pas (RAI5).
- « Ça marche chez moi » pris pour une garantie (RAI2).
- Capacité d'un modèle d'IA déduite d'une démonstration choisie (RAI4).
- Confusion entre ce que dit la documentation et ce que fait réellement le logiciel.
- Références de bibliothèques ou de fonctions inventées : toute référence technique se vérifie dans la documentation avant d'être citée (VER2).

## Prudence et fraîcheur

- Versions, API, tarifs, capacités de modèles : sujet **évolutif**, voire **temps réel** pour les annonces récentes.
- Sécurité informatique : décrire la vulnérabilité, son impact et sa correction. Ne produire aucun code d'exploitation. Lecture seule : aucune commande n'est exécutée, aucun test n'est lancé contre un système tiers.
- Conseil de configuration sur un système en production, ou touchant des données de personnes : domaine à risque, mentionner de tester dans un environnement isolé et de consulter le responsable du système.
