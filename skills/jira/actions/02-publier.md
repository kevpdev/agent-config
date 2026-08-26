# 02 - Publier

Envoie un brouillon vers Jira, rattache la clé du ticket créé, et gèle le brouillon.

## Input

Le chemin d'un brouillon sous `aidd_docs/backlog/`, dont le contenu est jugé prêt par l'humain.

## Output

Un ticket créé, sa clé écrite dans le frontmatter du brouillon, et un compte rendu qui donne la clé,
l'URL et les champs envoyés. Si l'humain n'a pas autorisé l'écriture, une proposition et aucun appel.

## Process

1. **Lire la mémoire du dépôt.** Y prendre le site Jira, les projets où l'écriture est autorisée, la
   convention de scope, le banc d'essai et le chemin des gabarits de description.
   - **Garde.** Un projet absent de la liste que la mémoire autorise n'est pas une cible, même si
     l'humain le nomme.
2. **Vérifier que le brouillon n'est pas déjà publié.** Une clé de ticket déjà présente signifie que le
   brouillon est gelé : s'arrêter et le dire. Republier créerait un doublon irréversible.
3. **Résoudre les champs obligatoires en lecture seule**, avec les outils de métadonnées du connecteur,
   avant de composer le moindre appel d'écriture. Une création qui échoue sur un champ manquant coûte
   parfois un ticket à demi créé.
4. **Résoudre le gabarit de description**, en s'arrêtant au premier trouvé de ces trois.
   - La **surcharge du dépôt**, au chemin que la mémoire déclare pour le type visé.
   - Le **défaut du type**, `assets/description-<type>.md`.
   - Le **défaut générique**, `assets/description-defaut.md`.
   - **Garde.** Une surcharge déclarée mais illisible arrête l'action, sans aucun appel d'écriture.
     Elle ne retombe pas sur le défaut. *Pourquoi : un repli silencieux publie un ticket à la mauvaise
     forme, et personne ne le voit, puisque le ticket existe et qu'il a l'air correct.*
   - Le gabarit résolu remplace l'autre **en entier**, jamais section par section. *Pourquoi :
     fusionner deux gabarits ramène le non-déterminisme que ces trois couches suppriment.*
   - Remplir chaque section depuis le brouillon, et n'en ajouter aucune. Une section que le brouillon
     ne nourrit pas se remplit en le disant, jamais en inventant sa matière.
5. **Mettre le texte en forme** selon [rendu-jira](../references/rendu-jira.md). C'est l'étape que
   personne ne pense à faire, et son oubli se voit dans le ticket publié.
6. **Demander l'autorisation, sous le titre littéral `## Autorisation requise`, en une seule question
   qui porte tout** : le projet et le type visés, le résumé exact, la liste des champs envoyés, et le
   fait que la création est définitive.
   - **NE PAS** poser cette question par morceaux. Un humain qui répond trois fois oui n'a pas donné
     trois approbations, il a cessé de lire.
   - Si le dépôt déclare un garde à jeton, dire aussi le geste attendu, tel que le garde le formule.
   - *Pourquoi un intitulé imposé :* il rend la demande repérable dans une sortie longue, et il sert
     de signal vérifiable qu'aucune écriture n'a eu lieu sans elle.
7. **Créer le ticket**, un seul appel, jamais en boucle.
   - **Garde.** Un refus par un garde n'est pas une erreur à réessayer : c'est la réponse, et elle dit
     quoi demander. Transmettre son message et s'arrêter, sans second appel du même outil.
8. **Écrire la clé** dans le frontmatter, par le champ d'extension du dépôt. À partir de cet instant le
   `status` du brouillon cesse d'être maintenu, le tracker faisant foi sur l'état du ticket.
   - Le corps du brouillon reste inchangé, et aucun autre champ du ticket n'y est recopié.
9. **Poser les liens** dans un appel distinct de la création, chaque lien étant lui aussi une écriture
   soumise à l'autorisation de l'étape 6.
10. **Rendre compte** en donnant la clé, l'URL et les champs envoyés. Ne pas relire le ticket pour le
    recopier dans le dépôt : la copie est précisément ce que le gel interdit.

## Test

| Cas | Preuve |
| --- | --- |
| une publication complète, de bout en bout | aucun appel d'écriture n'a précédé la question portant le titre `## Autorisation requise`, et le projet visé figure dans la liste que la mémoire du dépôt autorise |
| la description envoyée | elle porte toutes les sections du gabarit résolu, et aucune autre |
| un brouillon dont la mémoire déclare une surcharge de gabarit illisible | l'action s'arrête, aucun appel d'écriture n'a lieu |
| le texte envoyé, relu dans le ticket | aucun paragraphe replié à la main, et les puces, titres, tableaux et blocs de code gardent leurs retours, comme [rendu-jira](../references/rendu-jira.md) le mesure |
| le brouillon après succès | son frontmatter porte la clé du ticket, son corps est inchangé, et aucun champ du ticket n'y est recopié au-delà de la clé |
| la trace des appels de la session | aucun appel à un outil qui modifie un ticket existant, hors la pose de liens de l'étape 9 |
| un appel refusé par un garde déterministe | la sortie transmet le message du garde et s'arrête, sans second appel du même outil |
