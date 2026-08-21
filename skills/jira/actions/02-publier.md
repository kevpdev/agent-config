# 02 - Publier

Envoie un brouillon vers Jira, rattache la clé du ticket créé, et gèle le brouillon.

## Input

Le chemin d'un brouillon sous `aidd_docs/backlog/`, dont le contenu est jugé prêt par l'humain.

## Output

Un ticket créé, sa clé écrite dans le frontmatter du brouillon, et un compte rendu qui donne la clé,
l'URL et les champs envoyés. Si l'humain n'a pas autorisé l'écriture, une proposition et aucun appel.

## Process

1. **Lire la mémoire du dépôt.** Y prendre le site Jira, les projets où l'écriture est autorisée, la
   convention de scope, le banc d'essai et le chemin des gabarits de description. Un projet absent de cette liste n'est pas une cible, même
   si l'humain le nomme.
2. **Vérifier que le brouillon n'est pas déjà publié.** Une clé de ticket déjà présente signifie que le
   brouillon est gelé : s'arrêter et le dire. Republier créerait un doublon irréversible.
3. **Résoudre les champs obligatoires en lecture seule**, avec les outils de métadonnées du connecteur,
   avant de composer le moindre appel d'écriture. Une création qui échoue sur un champ manquant coûte
   parfois un ticket à demi créé.
4. **Résoudre le gabarit de description**, en s'arrêtant au premier trouvé de ces trois.
   - La **surcharge du dépôt**, au chemin que la mémoire déclare pour le type visé.
   - Le **défaut du type**, `assets/description-<type>.md`.
   - Le **défaut générique**, `assets/description-defaut.md`.
   - **Une surcharge déclarée mais illisible arrête l'action.** Elle ne retombe pas sur le défaut.
     *Pourquoi : un repli silencieux publie un ticket à la mauvaise forme, et personne ne le voit,
     puisque le ticket existe et qu'il a l'air correct.*
   - Le gabarit résolu remplace l'autre **en entier**, jamais section par section. *Pourquoi :
     fusionner deux gabarits ramène le non-déterminisme que ces trois couches suppriment.*
   - Remplir chaque section depuis le brouillon, et n'en ajouter aucune. Une section que le brouillon
     ne nourrit pas se remplit en le disant, jamais en inventant sa matière.
5. **Mettre le texte en forme** selon [rendu-jira](../references/rendu-jira.md). C'est l'étape que
   personne ne pense à faire, et son oubli se voit dans le ticket publié.
6. **Demander l'autorisation, en une seule question qui porte tout** : le projet et le type visés, le
   résumé exact, la liste des champs envoyés, et le fait que la création est définitive.
   - **NE PAS** poser cette question par morceaux. Un humain qui répond trois fois oui n'a pas donné
     trois approbations, il a cessé de lire.
   - Si le dépôt déclare un garde à jeton, dire aussi le geste attendu, tel que le garde le formule.
7. **Créer le ticket**, un seul appel, jamais en boucle. Un refus par un garde n'est pas une erreur à
   réessayer : c'est la réponse, et elle dit quoi demander.
8. **Écrire la clé** dans le frontmatter, par le champ d'extension du dépôt. À partir de cet instant le
   `status` du brouillon cesse d'être maintenu, le tracker faisant foi sur l'état du ticket.
9. **Poser les liens** dans un appel distinct de la création, chaque lien étant lui aussi une écriture
   soumise à l'autorisation de l'étape 6.
10. **Rendre compte** en donnant la clé, l'URL et les champs envoyés. Ne pas relire le ticket pour le
    recopier dans le dépôt : la copie est précisément ce que le gel interdit.

## Contrôle de sortie

- Aucun appel d'écriture n'a précédé la question d'autorisation de l'étape 6.
- Le projet visé figure dans la liste que la mémoire du dépôt autorise.
- La description envoyée porte toutes les sections du gabarit résolu, et aucune autre.
- Une surcharge de gabarit déclarée et illisible a fait s'arrêter l'action, sans aucun appel
  d'écriture.
- Le texte envoyé respecte [rendu-jira](../references/rendu-jira.md) : aucun paragraphe replié à la
  main, et les puces, titres, tableaux et blocs de code gardent leurs retours.
- Après succès, le frontmatter du brouillon porte la clé du ticket, et le corps du brouillon est
  inchangé.
- Aucun champ du ticket n'a été recopié dans le brouillon au-delà de sa clé.
- Aucun appel à un outil qui modifie un ticket existant, hors la pose de liens autorisée à l'étape 9.
- Sur refus d'un garde, la sortie transmet son message et s'arrête. Aucun second appel du même outil.
- La question de l'étape 6 porte le titre littéral `## Autorisation requise`, suivi du projet, du type,
  du résumé et des champs envoyés. *Pourquoi un intitulé imposé : il rend la demande repérable dans une
  sortie longue, et il sert de signal vérifiable qu'aucune écriture n'a eu lieu sans elle.*

## Test

Scénarios dans [`evals/eval.json`](../evals/eval.json).
