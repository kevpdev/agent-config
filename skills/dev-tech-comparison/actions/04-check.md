# 04 - Contrôler

Fait passer le fichier au lint de prose, à l'auto-relecture, et en mode strict à un relecteur qui ne l'a pas écrit.

## Input

Le chemin du fichier écrit par `write`, la liste des sources de `research`, et le mode choisi dans `frame`.

## Output

Le fichier corrigé, plus un compte rendu qui nomme le mode joué, la sortie du lint lancé sur le fichier livré et les défauts restants s'il en reste.

## Process

Le lint se lance par `python3 "$(readlink -f ~/.claude/skills)/../wrappers/claude/scripts/lint-html-prose.py" <fichier>`. *Pourquoi un chemin absolu : le skill est global et écrit dans le dossier courant, donc le run part presque toujours d'un autre repo que `agent-config`.*

**Toute correction du fichier est suivie d'un lint**, quelle que soit l'étape qui l'a demandée. Un lint rouge après une correction renvoie à `write` sur ses interdits, et cette boucle-là compte dans la limite de l'étape 1.

1. **Linter.** Lancer le lint sur le fichier.
   - Code 1, retourner à `write` avec les lignes « interdit », puis relancer le lint. 3 retours à `write` au plus sur des interdits, sur tout le contrôle. *Pourquoi 3 : un script rend le même verdict partout, donc la borne de la [convention des skills](../../skill-craft/references/skill-authoring-fr.md), section « Frame–Deliver–Checker », suffit.*
   - Limite atteinte et lint encore rouge, continuer et garder les interdits restants pour le compte rendu.
   - Code 2, le fichier est illisible, arrêter et le dire.
2. **Relire soi-même**, dans les deux modes. Jouer les étapes de [`../references/controles-redaction.md`](../references/controles-redaction.md) dans une passe séparée de la rédaction, en relisant depuis le titre comme un lecteur qui découvre le sujet. Appliquer les corrections en une seule passe, puis relancer le lint.
3. **Faire relire par un sous-agent**, en mode strict seulement. Le sous-agent est générique et neuf. Il ne reçoit que le chemin du fichier, le chemin de la référence, la liste des sources et les lignes « à trier » du dernier lint, plus ses interdits restants s'il y en a. Ni la conversation, ni les intentions de rédaction.
   > Sous-agent : « Lis `<chemin de controles-redaction.md>`, puis relis `<fichier>` en entier, comme un lecteur qui découvre le sujet. Vérifie les chiffres contre ces sources : `<sources>`. Juge ces lignes relevées par le lint : `<lignes à trier>`. Ne modifie pas le fichier. Rends le rapport au format de la section « Format du rapport », verdict en dernière ligne. »
   - Sur « à corriger », appliquer le rapport par `write`, relancer le lint, puis relancer un sous-agent neuf pour confirmer. 2 relectures au plus.
   - Après la 2e relecture, les lignes restantes vont au compte rendu sans nouvelle correction.
   - *Pourquoi une relecture de confirmation : l'exigence de départ est « applique les corrections, puis relance le relecteur une seule fois pour confirmer ». Pourquoi un contexte neuf : un relecteur qui repart de zéro ne partage pas les angles morts de celui qui a rédigé.*
4. **Imprimer.** Produire un PDF de test par `google-chrome --headless --print-to-pdf` ou `chromium`, à défaut par Playwright, dans un dossier temporaire et jamais à côté du fichier livré, puis vérifier page par page qu'aucune figure, aucun tableau ni aucun encadré n'est coupé.
   - Une coupure se corrige par `write`, une fois, puis le lint se relance. Une coupure qui résiste va au compte rendu.
   - Sans aucun des trois outils, déclarer l'étape non jouée.
5. **Livrer.** Rendre le compte rendu, qui nomme le mode joué et reprend la sortie du dernier lint.
   - En mode standard, écrire « relu par l'auteur, sans relecture indépendante ». *Pourquoi : se relire soi-même attrape moins qu'un regard extérieur, et le lecteur doit savoir quel contrôle a eu lieu.*

## Test

| Cas | Preuve |
| --- | --- |
| comparer, dans le transcript d'un run, la dernière écriture du fichier et le dernier lint | le lint vient après, donc il porte sur le fichier livré |
| compter les retours à `write` motivés par un lint rouge | trois au plus |
| un run en mode standard | aucun sous-agent de relecture lancé, et le compte rendu porte « relu par l'auteur, sans relecture indépendante » |
| un run en mode strict | un ou deux sous-agents de relecture lancés, jamais plus, et leur brief ne porte ni la conversation ni les intentions de rédaction |
