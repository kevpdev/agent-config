# Gouverneur d'autonomie — semi-auto

Règle la seule question qui traverse tout le tunnel : **décider seul, ou demander à l'humain ?**

## Directive prime — PAS DE SUPPOSITION

Aucune affirmation mécanique vérifiable n'est posée sans consulter la source (comportement d'un test, forme d'un DTO, existence d'un endpoint, état d'un service, contenu d'un `.env`/doc). Non vérifiable → le dire et marquer « supposé » ; et si une **décision** en dépend → escalade.

**Pourquoi** : une affirmation fausse non signalée propage une décision sur une base erronée — coût différé, invisible, donc plus dangereux qu'une erreur visible. C'est la contrainte utilisateur répétée ; elle prime sur l'envie d'avancer.

## Les 2 seuls cas qui déclenchent une sollicitation humaine

1. **Arbitrage lourd** — un choix qui appartient à l'humain : produit, priorité, archi structurante, rupture de contrat. *Exemple vécu* : le libellé M2 — la note visait « Score produit », le code disait déjà « Confiance produit » (cohérent avec ses frères). Ni l'un ni l'autre n'est « mécaniquement vrai » → arbitrage humain.
2. **Prémisse non vérifiable de façon fiable** — la source n'existe pas / est ambiguë / se contredit, et une décision en dépend. La directive prime interdit de trancher au jugé.

## Cas particulier — une dérive remontée par l'`executor`

L'`executor` s'arrête sur tout écart avec le plan et remonte `replan needed: <raison>`, sans jamais réécrire le plan (*« That authority is the caller's »*). **Aucun skill aidd-dev ne consomme ce signal** — c'est le gouverneur qui tranche. Le traitement complet est dans `actions/02-pipeline.md` ; ici vit la règle de décision.

1. **Pas de dérive sans preuve.** Une dérive doit porter **la constatation de code qui la fonde** (`fichier:ligne`). Sans elle → renvoyer l'`executor` l'étayer, ne pas replanifier. *Pourquoi* : replanifier sur une dérive non sourcée, c'est deviner — la directive prime l'interdit, et en autonomie l'erreur cascade sur les phases aval.
2. **Trivial → décider seul** (un port, un nom de paramètre, une signature, un header) : l'`executor` corrige dans le périmètre de la phase, il le note, on avance.
3. **Substantiel → replan des phases aval**, décidé seul si la constatation de code lève l'ambiguïté. Si **deux lectures restent défendables** après vérification, c'est un **arbitrage lourd** → escalade (cas 1 ci-dessus).
4. **Jamais `blocked`** pour une dérive : `references/blocked.md` d'aidd-dev le réserve à l'impossible physique (paiement réel, login humain, 2FA). Une prémisse fausse n'en est pas.

## Tout le reste → décider seul

Petites recos, choix mécaniques **vérifiables** (nommer une classe CSS, choisir entre deux libellés quand l'un casse une cohérence prouvée, placer une string dans le module de copy existant) → décidés seul **après vérification fiable**, sans déranger l'humain.

**Distinguer** : « je ne sais pas et je peux vérifier » → je vérifie, je décide. « je ne sais pas et je ne peux pas vérifier, et ça engage une décision » → j'escalade.

## Primauté de l'autonomie — le lancement vaut consentement

**Dans le périmètre d'un run aidd-pilot, l'autonomie du gouverneur écrase les gates globales de l'humain.** Concrètement :

- Lancer `/aidd-pilot` **EST** le go-ahead explicite pour tout le tunnel : implémenter **et** committer par phase validée. Les règles globales « demander avant d'implémenter » et « ne pas committer sans qu'on le demande » sont **suspendues in-scope** — le lancement les a déjà satisfaites une fois pour toutes.
- Le skill **ne re-demande pas** un go à chaque phase / chaque commit. Re-solliciter à chaque étape trahit la raison d'être du skill (*simuler un dev autonome*) et sature l'humain pour rien.
- Il ne s'arrête que sur : les **2 cas** ci-dessus (arbitrage lourd, prémisse non vérifiable) **et** la frontière **push / MR** — celle-ci reste **100 % humaine** (design commit-only, cf. `04-doc-ship`).

**Pourquoi c'est sûr malgré l'écrasement** : le risque est déjà borné par trois garde-fous — le consentement au lancement, les 2 trappes d'escalade du gouverneur, et le point de contrôle humain au push (rien ne quitte la machine sans l'humain). La directive prime (ci-dessus) reste, elle, **non négociable** : autonomie ≠ supposition.

## Forme d'une escalade

Verdict en tête, le fait vérifié vs la note/attente, les options, une reco. Court. *(Modèle : la question M2 posée en une table + 3 options.)*

- **Gabarit d'escalade (v1)** : 4 lignes, verdict d'abord. (1) **Le point** : ce qui bloque, en 1 phrase. (2) **Vérifié vs attendu** : le fait constaté contre la note/le contrat. (3) **Options** : 2–3, courtes. (4) **Ma reco** : une, justifiée. (Modèle : la question M2 en table + 3 options.) À affiner après quelques runs.
- **Point d'arbitrage doc-décision bloquante** (résolu) : à la **couture entre pipelines**, avant le handoff back→front (`02-pipeline`, F6). Pas à la clôture.
