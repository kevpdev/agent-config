# Références — `rules/reasoning.md`

Les cas mesurés qui fondent les règles de `reasoning.md`. Même contrat que `ref-workflow.md` : jamais chargé automatiquement, l'instruction et son pourquoi restent dans la règle, seule l'anecdote chiffrée descend ici.

---

## Ne jamais affirmer sans vérifier — le rejeu de VW3-3256 (2026-08-04)

**Ce qu'une mesure tue, un argument ne le tue pas.**

Sur les **14 affirmations fausses** relevées au rejeu du ticket :

- **12 sont tombées sur une mesure** — une commande, un `grep`, un `ls`.
- **2 seulement sur un arbitrage**, c'est-à-dire sur de la discussion.

**Trois d'entre elles tenaient à un `ls` jamais lancé**, et leur coût a été **757 lignes de raisonnement à détruire**.

**La leçon** : une heure d'analyse juste, posée sur une prémisse non testée, ne vaut rien. Et démolir coûte une seconde fois — d'où l'interdit qui porte sur la prémisse, pas seulement sur la conclusion.

## Un comptage qui rend « zéro » — les 1 019 points-virgules

Zéro point-virgule fautif annoncé sur six corpus. Faux deux fois, le même jour, sur le même fait, pour deux raisons qui se cumulaient :

- **Le corpus mentait.** Le plus propre des six avait été nettoyé sur demande. Il ne mesurait donc que ce qui avait survécu à la correction, jamais la propension qui l'avait produit — et une correction faite en cours de rédaction ne laisse aucune trace dans git.
- **L'instrument était aveugle.** La regex exigeait `mot; mot` et ignorait la typographie française `mot ; mot`.

**Comptage réel après calibrage : 1 019 occurrences.**

**La leçon** : un détecteur non calibré ne distingue pas l'absence du défaut de son incapacité à le voir, et il rend le même « zéro » dans les deux cas. D'où les deux gestes de la règle — un corpus témoin que personne ne relit, et un calibrage sur un cas positif exhibé à la main.
