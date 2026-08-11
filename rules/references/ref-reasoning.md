# Références — `rules/reasoning.md`

Les cas mesurés qui fondent les règles de `reasoning.md`. Jamais chargé automatiquement : l'instruction et son pourquoi restent dans la règle, seule l'anecdote chiffrée descend ici.

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

## Le pourquoi quand il porte une information — deux prescriptions de doc en apparence opposées (2026-08-11)

La règle disait « **toujours** le pourquoi ». Deux pages de doc du même éditeur, fetchées le même jour, tranchent plus finement — et leur contradiction apparente est le cœur du sujet.

**Page *Prompting best practices*, section « Add context to improve performance »** — partie explicitement valable pour tous les modèles courants :

> *Providing context or motivation behind your instructions, such as explaining to Claude why such behavior is important, can help Claude better understand your goals and deliver more targeted responses.*

Son exemple : `NEVER use ellipses` (moins efficace) → *« Your response will be read aloud by a text-to-speech engine, so never use ellipses since the text-to-speech engine will not know how to pronounce them »* (plus efficace). Suivi de : *« Claude is smart enough to generalize from the explanation. »* **Le pourquoi apporte ici un fait de l'environnement de l'auteur, indevinable.**

**Page *Skill authoring best practices*** — 22 items de checklist, **aucun** sur le pourquoi, et la prescription inverse :

> *Default assumption: Claude is already very smart. Only add context Claude doesn't already have. Challenge each piece of information: « Does Claude really need this explanation? » […] « Does this paragraph justify its token cost? »*

> *Review for conciseness: Check that Claude A hasn't added unnecessary explanations. Ask: « Remove the explanation about what win rate means — Claude already knows that. »*

**Ce qui réconcilie les deux** : le critère n'est pas la présence d'une raison, c'est son **contenu informationnel**. Une raison qui transmet un fait de l'environnement, une mesure ou un piège vécu se donne ; une raison qui explique au modèle ce qu'il sait déjà se coupe. La même page applique exactement cette ligne aux constantes — *« Configuration parameters should also be justified […] to avoid "voodoo constants". If you don't know the right value, how will Claude determine it? »* : justifier est obligatoire là où la valeur est arbitraire, jamais partout.

**Pourquoi la structure ne le porte pas nativement** : la doc affirme que le format des skills est déjà connu du modèle — *« Claude models understand the Skill format and structure natively. You don't need […] a "writing skills" skill »*. Ce qui est natif est le **gabarit** ; la présence d'un bloc pourquoi dépend du contenu, pas du gabarit, donc aucun gabarit ne peut la décider.

**Non vérifié, et ça reste un trou** : les skills livrés par le harnais ne sont pas sur le disque — le binaire ne contient que leurs noms (5 occurrences de `artifact-design`, zéro pour leur corps), leur texte est servi côté serveur. Leur structure réelle n'a donc pas pu être mesurée ; seuls les exemples de la doc l'ont été, et aucun ne porte de bloc pourquoi.
