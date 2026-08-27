---
name: <nom-du-skill>
description: <ce qu'il produit>. Utiliser quand l'utilisateur veut <intentions>. NE PAS utiliser pour <X> (→ <frère>).
argument-hint: <ce que l'utilisateur apporte : ses cas, ou l'artefact consommé>
disable-model-invocation: true # <OPTIONNEL. Garder si le skill a un effet de bord ET que seul l'humain l'ouvre. Supprimer la ligne sinon, y compris quand un skill ou un orchestrateur l'appelle : R13 l'interdit alors, et exige un garde nommé.>
---

# <Nom du skill>

<Une phrase de portée : ce que le skill couvre, et sur quoi il rend la main.>

```mermaid
flowchart TD
  <le parcours : les slugs enchaînés, un nœud d'entrée par cas, une arête retour par boucle, un nœud terminal par issue>
```

## Actions

<ALTERNATIF:forme. Le skill porte un dossier `actions/`. Une ligne par fichier d'action, dans l'ordre d'exécution.>

Dérouler le flux. Ne lire que la prochaine action.

| Action | Fait |
| --- | --- |
| <slug nu, sans backticks ni numéro> | <demi-ligne impérative en minuscules, sans point final> |

## Process

<ALTERNATIF:forme. Le skill est mono-fichier : sa méthode vit ici, à la place de la table d'actions.>

1. **<Label>.** <Étape impérative, une phrase. Sous-puce pour un cas, une branche, une garde ou un retour de boucle.>

## Transversal rules

<OBLIGATOIRE. Les règles qu'aucune action ni référence ne possède. Une règle dite ici ne se redit nulle part.>

- <règle>

## References

<OPTIONNEL. Omis quand le skill n'a pas de dossier `references/`.>

- `references/<fichier>.md` — <son rôle, en une ligne>

## Assets

<OPTIONNEL. Omis quand le skill n'a pas de dossier `assets/`.>

- `assets/<fichier>.md` — <ce qu'il sert à écrire>

## Test

<OBLIGATOIRE. Première ligne : le mode de vérification, jouable seul ou relecture humaine. Puis la table, ou le geste manuel en une phrase.>

| Cas | Preuve |
| --- | --- |
| <ce qui est lancé> | <le résultat observable qu'il rend> |

> Remplir chaque `<...>` et supprimer cette ligne. Un chevron resté dans le fichier écrit est un bug.
