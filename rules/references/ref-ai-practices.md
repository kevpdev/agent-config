# Références — `rules/ai-practices.md`

Les cas mesurés qui fondent chaque « EN TEST DEPUIS », et le registre des pratiques écartées du banc d'essai. Même contrat que `ref-workflow.md` : jamais chargé automatiquement, l'instruction et son pourquoi restent dans la règle, seule la preuve chiffrée descend ici.

**Statut particulier de ce fichier** : sur un banc d'essai, la preuve n'est pas qu'une justification — c'est le dossier d'instruction de la promotion. La règle garde donc le **statut** (date, n=, réussite ou échec), qui change la façon de traiter la pratique ; ici vivent le détail et le **seuil de sortie**.

**POURQUOI un seuil déclaré, et pas une revue périodique** : sans condition écrite, rien ne déclenche la décision. Les cinq pratiques ci-dessous sont toutes restées à une seule observation depuis leur inscription (2026-07-30 au 2026-08-05) — non parce que la preuve manquait, mais parce qu'aucun moment n'obligeait à poser la question. Le seuil règle ça en attachant le déclencheur à **l'ajout d'une observation** : le seul instant où la réponse peut changer est aussi celui où l'on ouvre ce fichier.

**Qui décide** : ce repo, à la passe `/audit-harnais`, qui lit déjà ces fichiers. Le vault est un bac à sable et une base de connaissance sur projets concrets — il alimente le banc, il ne le juge pas (décidé le 2026-08-10, cf. `audits/grille-harnais.md:5`).

---

## 1. Livrer par incréments vérifiés — 2026-07-30

**Confirmée par un échec, n=1 sans contrefactuel.** 400 lignes écrites et validées en bloc → **7 affirmations non vérifiées, dont 2 fausses**.

Pas de contrefactuel : on ne sait pas ce qu'aurait donné la même passe découpée en incréments. La pratique tient donc sur un mécanisme plausible (la relecture en bloc invite à rationaliser), pas sur une comparaison.

**Seuil de sortie** — promouvoir à n≥3 dont **au moins un contrefactuel** : une passe où l'on sait aussi ce qu'aurait donné le lot en bloc. Supprimer si un découpage en incréments laisse passer autant de défauts non vérifiés qu'une passe en bloc.

## 2. Le contexte est du code — 2026-07-30

**Appliquée une fois, concluante.** Le test ajouté a attrapé **7 défauts réels le jour même**.

**Seuil de sortie** — promouvoir à n≥3 artefacts dont le test ajouté a attrapé un défaut réel. Supprimer si le test ne rend que des faux positifs, ou s'il coûte plus cher à écrire que le défaut qu'il attrape.

## 3. Capitaliser la leçon avant la fin de session — 2026-07-30

**Appliquée une fois, tenue.** Aucun chiffre relevé — c'est la plus faiblement étayée des cinq, et celle dont la promotion demandera une observation neuve.

**Seuil de sortie** — promouvoir à n≥3 leçons descendues dans un artefact **qu'une session ultérieure a effectivement rechargé** : c'est la seule preuve que la capitalisation a servi. Supprimer si les artefacts produits ne sont jamais rechargés — ce serait de l'archivage, pas de la capitalisation.

## 4. Une instruction dupliquée s'élimine — 2026-07-31

**n=1, deux défauts du même jour :**

- Un sous-agent a **sauté un skill** au motif que la règle résiduelle suffisait — la couche partielle qui a l'air complète supprime le chargement de l'autre.
- Un **conflit d'ordre** entre une règle et le template d'un skill n'est apparu qu'à l'exécution, invisible à la relecture des deux fichiers séparément.

Le second cas est le plus instructif : relire les deux copies ne révèle pas la divergence, parce qu'aucune des deux n'est fausse isolément.

**Seuil de sortie** — promouvoir à n≥3 découpages où la couche permanente, déclarée délibérément partielle, n'a pas empêché le chargement de l'autre. Supprimer si un « délibérément partiel » se fait sauter quand même : ce serait le défaut d'origine sous un autre nom, et la pratique ne le corrigerait pas.

## 5. Charger le journal avant de répondre sur le passé — 2026-08-05

**n=1, et c'est un échec.** À la question « où en sommes-nous sur la config agentique », réponse rendue : aucune trace d'audit n'existe. Elle était dans le log du **31 juillet**.

La règle existait déjà sous une autre forme et n'a pas suffi — c'est la raison pour laquelle elle est descendue dans le banc d'essai plutôt que de rester dans `rules/`.

**Seuil de sortie, différent des autres** — promouvoir à n≥3 questions sur le passé où le journal a été chargé avant de répondre. Mais un **second échec la supprime** au lieu de prolonger le test : deux formulations successives restées sans effet montrent que le défaut n'est pas adressable par une règle de prose, et il faut alors chercher un mécanisme déterministe ou renoncer.

---

## Écartées du banc d'essai

Décision du harnais, consignée ici : ces quatre pratiques ne sont **pas chargées**. Critère commun — une pratique qu'une règle ne peut pas exercer dilue les autres sans rien gagner. Le vault peut les porter comme matière de réflexion ; ça ne les remet pas au banc.

- **Spécialiser le modèle par fonction** et **cross-review inter-modèles** → décisions d'orchestration humaine, l'agent ne les prend pas. La forme utile de la seconde est un skill de vérification déléguée, pas une règle.
- **Chaîne spec → plan → décomposition** → déjà couverte par `workflow.md` et les skills AIDD ; la recharger créerait un doublon, donc une dérive.
- **Reconstruire le contexte plutôt que rattraper une dérive** → déclencheur non fiable : il exige de repérer soi-même sa propre dérive. À retenter si un signal observable émerge.
