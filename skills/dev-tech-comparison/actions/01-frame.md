# 01 - Cadrer

Fixe le mode de contrôle et les entrées du comparatif avant toute recherche.

## Input

Le texte passé après `/dev-tech-comparison`, et ce que la conversation en dit déjà.

## Output

Le mode choisi et le bloc d'entrées rempli, affichés dans le chat, plus le chemin du fichier à écrire.

## Process

1. **Choisir le mode.** Afficher exactement : « Mode de contrôle : tape 0 pour standard (lint et auto-relecture, rapide), 1 pour strict (standard plus une relecture par un sous-agent neuf, plus coûteux en temps et en tokens). »
   - **Garde.** Attendre la réponse avant toute autre étape. Une réponse autre que 0 ou 1 repose la question une fois, puis prend 0.
2. **Extraire.** Remplir les huit entrées depuis la demande, sans rien inventer.

   | Entrée | Exemple |
   | --- | --- |
   | sujet | Mistral OCR 3 contre OCR 4.1 pour les factures de consommables |
   | options | 2 ou 3, chacune avec son identifiant exact et sa version |
   | cas d'usage réel | ce que le système doit faire, avec un exemple du domaine |
   | contexte technique | stack, hébergement, RGPD, volumes, équipe |
   | questions à trancher | 3 à 6 questions auxquelles le document répond |
   | lecteurs | CTO, développeurs, product owners |
   | sources imposées | des liens, ou « aucune » |
   | dossier de sortie | le dossier courant par défaut |

3. **Compléter.** Une entrée secondaire absente (lecteurs, contexte, sources) prend l'hypothèse la plus défendable, marquée « supposé » dans le bloc.
   - **Garde.** Moins de 2 options identifiées avec leur version, ou moins de 3 questions à trancher, arrête le flux. Plus de 3 options ou plus de 6 questions aussi, avec une demande de réduire. Poser une seule question qui demande ce qui manque, et ne pas lancer `research`. *Pourquoi : sans versions, la recherche compare des produits flous, et sans questions, la grille de décision n'a rien à trancher.*
4. **Nommer le fichier.** Dériver un slug en kebab-case du sujet, et fixer `<dossier>/<slug>.html`.
   - Si le fichier existe déjà, demander s'il faut l'écraser. Sur un refus, demander un autre nom de fichier une seule fois, sans rien écrire. Si ce nom existe aussi, lui ajouter la date du jour en suffixe.
5. **Afficher.** Rendre le mode choisi et le bloc d'entrées dans le chat, hypothèses marquées, puis enchaîner sur `research` sans attendre de validation.

## Test

| Cas | Preuve |
| --- | --- |
| un run lancé avec un sujet complet | le flux s'arrête d'abord sur la question du mode, avant toute recherche web |
| la réponse « 2 » deux fois à la question du mode | le bloc affiché porte le mode standard |
| un run lancé avec une seule option | le flux s'arrête sur une question, aucun appel de recherche web n'est parti |
| un run complet | le bloc affiché porte les huit entrées, et chaque hypothèse est marquée « supposé » |
