---
name: cadre-prompt
description: >-
  Transforme une ébauche de demande en prompt cadré, structuré selon le type de demande détecté
  (exécution, analyse, exploration) : ajoute les critères d'acceptation, le contrat de questions et
  son hors-périmètre, ou la condition d'arrêt, selon ce qui manque. Rend un prompt rédigé
  immédiatement, trous comblés par des hypothèses marquées, une question au maximum, puis le capture
  dans l'inbox du vault. S'appelle par "/cadre-prompt" en tête de message, l'ébauche à la suite ;
  "--chat" sort le prompt dans la conversation au lieu du vault. NE PAS utiliser
  pour dérouler le développement depuis une note de cadrage (→ aidd-orchestrator:01-sdlc), pour fiabiliser une
  application qui appelle un LLM et mesurer une régression de prompt (→ ai-engineering), ni pour un
  snapshot visuel de l'avancement destiné à l'humain (→ vault-recap-raisonnement).
argument-hint: <l'ébauche à cadrer> [--chat]
disable-model-invocation: true
---

# cadre-prompt

Prend une ébauche de demande et rend un prompt cadré. Le gabarit des trois formes vit dans
[`assets/squelette-prompt.md`](assets/squelette-prompt.md), le corps ci-dessous porte la méthode.

> [!important] Ne jamais cadrer une demande qui n'a pas été soumise comme ébauche
> Une demande ordinaire, même mal formulée, s'exécute ou se répond. Elle ne se reformule pas.
> *Pourquoi : détourner une demande normale en questionnaire remplace la réponse attendue par du
> travail administratif, et c'est le seul vrai risque de ce skill.*

## Le diagnostic, avant le gabarit

L'objectif est presque toujours présent dans une ébauche. Ce qui manque, c'est **où ça s'arrête et
ce qu'on fait du résultat**, et ça dépend du type de demande.

| Type | Ce qui le reconnaît | Ce qui manque presque toujours | Ce que le prompt gagne |
|---|---|---|---|
| **Exécution** | un verbe d'action sur un objet identifié | de quoi savoir que c'est fini | des critères d'acceptation vérifiables, et ce qu'on ne touche pas |
| **Analyse** | une ou plusieurs questions dont la réponse est un document | la borne | un contrat de questions figé, son hors-périmètre, et le livrable nommé |
| **Exploration** | des questions ouvertes empilées, sans dire ce qu'on en fera | la condition d'arrêt | un budget, un « ne conclus pas », et la consigne de capturer les découvertes hors contrat |

**L'exploration est le type qu'on n'écrit jamais, et le plus coûteux.** Une règle de réponse saine
demande à l'agent de ne pas freiner pendant une exploration. Sans borne déclarée, il ne s'arrête donc
pas, et l'échange part en tunnel. *Pourquoi le nommer explicitement : le manque n'est pas une
maladresse d'écriture, c'est une borne absente, et aucune relecture de style ne la fait apparaître.*

**Deux types dans une même ébauche se scindent, ils ne s'arbitrent pas.** Rendre deux prompts.
*Pourquoi : un prompt mixte fait exécuter pendant l'exploration, ou explorer pendant l'exécution.*

## Méthode

1. **Vérifier le déclencheur.** L'utilisateur soumet-il un texte *comme* ébauche à cadrer ? Si non,
   ne pas cadrer, répondre à sa demande.
2. **Détecter le type** avec le tableau ci-dessus. Si deux types cohabitent, scinder.
3. **Récolter le contexte de session**, seulement s'il y en a. Deux natures, et une seule interdite.
   - Les **faits mesurés**, chacun avec la commande ou la source qui l'a produit.
   - Les **prémisses fausses** rencontrées, y compris et surtout les erreurs de l'agent lui-même.
   - ⛔ **Jamais les conclusions, recommandations ou arbitrages de la session.** *Pourquoi : un fait
     mesuré se réfute en une commande, une conclusion se contente d'être crue. Transportée, elle fait
     ratifier par la session neuve ce qu'elle devait tester.*
4. **Combler les trous par des hypothèses marquées**, jamais par une question. Chaque hypothèse porte
   le préfixe `⚠️ supposé :` et atterrit dans la section finale du prompt. *Pourquoi : une hypothèse
   fausse et visible se corrige en une ligne, une question bloque la production.*
5. **Poser une question, au maximum, et seulement si la réponse change la sortie.** Sinon aucune.
   *Pourquoi : le budget d'attention de l'utilisateur est la ressource rare de l'échange, et un
   questionnaire le dépense avant que le travail commence.*
6. **Rédiger le prompt** à partir du gabarit de son type, en bloc de code copiable.
7. **Capturer**, une fois le prompt rédigé et pas avant. Trois branches, et la première est le défaut.
   *Pourquoi cet ordre : le repli garde ainsi toujours un prompt à afficher, au lieu de perdre le
   travail avec la délégation.*
   - Ouvrir `vault-capture` avec le prompt et un titre court, puis confirmer le chemin absolu créé.
   - **`--chat` dans les arguments** → sauter la capture, rendre le prompt dans la réponse. Pour un
     petit prompt qu'on relance tout de suite.
   - **`vault-capture` s'arrête sur son garde-fou** (vault absent) → rendre le prompt dans la réponse,
     en disant que la capture n'a pas eu lieu.

## Règles transverses

- **Le prompt part dans l'inbox du vault par défaut, et l'écriture appartient à `vault-capture`.** Ce
  skill ne l'écrit jamais lui-même. *Pourquoi : la résolution de la racine absolue et le garde-fou
  « vault absent » vivent là-bas. Les recopier ici serait le doublon qu'interdit la R6 de
  `skill-craft`, et c'est la dérive que sa convention annonce comme invisible au lint.*
- **`--chat` n'écrit rien.** Le prompt sort dans la conversation, et le vault n'est pas touché.
- **Le prompt cite des chemins, jamais des résumés de fichiers.** *Pourquoi : un résumé périme sans
  le dire, un chemin se relit.*
- **Ce qui est mesuré et ce qui est supposé restent visuellement distincts** dans le prompt produit.
  *Pourquoi : un doute non signalé se lit comme une affirmation, et la session neuve le propagera.*
- **Le prompt nomme le mode d'exécution attendu** quand il en dépend, par exemple le plan mode pour
  une analyse qui conclura sur des modifications. *Pourquoi : sans lui, l'agent enchaîne sur les
  éditions au lieu de faire valider l'approche.*

## Contrôle de sortie

- Le prompt produit porte les sections du gabarit de son type, aux conditions d'omission que le
  gabarit énonce.
- Chaque hypothèse est préfixée `⚠️ supposé :`. Un grep du préfixe rend autant de lignes que la
  section finale en compte.
- Une question au maximum accompagne la sortie. Deux questions ou plus sont un échec de l'étape 5.
- Aucune recommandation, conclusion ni arbitrage de la session en cours n'apparaît dans le prompt.
  Relire la sortie en cherchant les verbes de décision (« il faut », « je propose », « donc on »).
- Un type « exploration » porte une condition d'arrêt explicite. Un type « analyse » porte un
  hors-périmètre non vide. Un type « exécution » porte des critères d'acceptation vérifiables.
- Le prompt est rendu en bloc de code, copiable d'un seul geste.
- Le chemin absolu du fichier d'inbox est confirmé à l'utilisateur. En `--chat` ou sur repli, le
  prompt est dans la réponse et la raison de l'absence de capture est dite.
- Rien n'a été écrit dans le repo courant, quelle que soit la branche.

## Test

Scénarios dans [`evals/eval.json`](evals/eval.json), tous négatifs : le skill étant à invocation
manuelle, le contrat qui compte pour lui est de ne jamais partir tout seul.

Ce qui **échoue ouvert** ne s'y teste pas, et se relit à la main : la passation en fin de session
riche, où le skill transporte volontiers les conclusions de la session en produisant une sortie
parfaitement plausible. Relire la sortie contre le ⛔ de l'étape 3 avant de capturer.
