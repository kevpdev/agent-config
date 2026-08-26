# 03 - Contrôler

Passe les contrôles jugeables sans contexte métier, et délègue tout le reste.

## Input

Le périmètre confirmé par `02-scope`, et la branche locale préparée par `01-prep`.

## Output

Une liste de findings. Chacun porte sa preuve : un chemin de fichier, une commande reproductible, ou
la citation qui le contredit. Plus la mention explicite de ce qui a été délégué, et à qui.

## Process

1. **Charger.** Ouvrir `references/controles-structurels.md`. Les sept contrôles y vivent avec un
   exemple concret chacun, pour reconnaître la forme du défaut.
2. **Passer.** Dérouler les contrôles dans l'ordre de la référence. Ne pas s'arrêter au premier
   trouvé : ils sont indépendants, et celui qu'on saute est celui que personne ne verra.
3. **Prouver.** Chaque finding cite sa source, mesurée à l'instant. Une observation sans preuve
   consultable ne sort pas, un doute non signalé se lisant comme une affirmation.
   - **Garde.** Un finding qui reprend un exemple de la référence sans mesure faite dans le code de
     cette MR ne sort pas. Les exemples illustrent une forme de défaut, ils ne prédisent rien.
   - Un contrôle qui ne trouve rien se déclare quand même. Un silence ne distingue pas « rien à
     signaler » de « pas regardé ».
4. **Déléguer.** Appeler les destinataires listés en fin de référence. Ne pas rejouer leurs critères
   ici, même partiellement.
   - **L'axe sécurité s'engage sur une décision, pas sur un mot.** Le critère est : la MR change-t-elle
     une **valeur** sensible (un secret, une clé, une chaîne de connexion), une **décision d'accès**
     (rôle, permission, filtre d'autorisation), ou le traitement d'une **donnée personnelle** ? Un
     fichier qui contient le mot `password` sans en porter la valeur ni la décision, une description de
     propriété auto-générée ou un nom de champ dans un schéma, ne l'engage pas.
   - *Pourquoi :* un critère qui déclenche sur la présence d'un jeton fait engager un axe entier sur un
     faux positif, et un axe engagé pour rien apprend au reviewer à ignorer le critère la fois suivante.
5. **Écarter.** Mettre de côté tout ce qui demande de juger la valeur métier, sans tenter d'y répondre.
   Ces éléments partent à `04-route`.
6. **Peser la taille.** Compter ce que la MR mêle : combien de natures de commit (`02-scope`), combien
   de repos, combien de tickets. Le résultat conditionne le premier paragraphe de `04-route`.

## Test

| Cas | Preuve |
| --- | --- |
| relire chaque finding rendu | chacun porte un chemin de fichier ou une commande, aucun n'est une impression |
| compter les contrôles nommés dans la sortie | les sept apparaissent, y compris ceux sans trouvaille |
| chercher la mention de délégation dans la sortie | la qualité de code est marquée déléguée, avec le nom du skill appelé |
| relire la liste des questions de valeur métier | elle est à part, et aucune n'est accompagnée d'une réponse proposée |
| comparer chaque finding à l'exemple correspondant de `references/controles-structurels.md` | aucun ne recopie l'exemple, chacun cite une mesure faite dans le code de cette MR |
