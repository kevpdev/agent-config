---
name: audit-harnais
description: >-
  Stratégie d'exécution d'un audit du harnais (la config agentique de ce poste) contre la grille
  audits/grille-harnais.md du repo agent-config : fige le contrat sur un sous-domaine, découpe les
  fichiers en instructions, fait descendre chaque instruction dans la cascade de la grille avec
  mesures batchées, et rend un rapport horodaté immuable. Utiliser quand l'utilisateur dit "audite le harnais", "audit
  agent-config", "passe la grille", "audite les règles / le contexte permanent", "rejoue l'audit
  sur <domaine>" (vault, projets), ou "/audit-harnais". NE PAS utiliser pour auditer une codebase
  applicative (→ aidd-dev:04-audit), reviewer un diff (→ aidd-dev:05-review), ni réviser la grille
  elle-même (révision humaine, entre deux audits).
---

# audit-harnais

Protocole d'exécution d'un audit du harnais contre `audits/grille-harnais.md` (repo `agent-config`).

> [!note] Pourquoi ce skill existe
> Deux audits ont divergé sur la même grille (2026-08-10) : tranches horizontales par critère, verdicts au fichier, C1/C4 jugés de mémoire dans l'un. Les critères CX évaluent, ils n'exécutent pas — ce skill porte la stratégie d'exécution qui manquait.

## Le flux

```
domaine demandé → 01-cadrer → 02-cribler → 03-consolider → rapport immuable
```

Ordre strict : pas de verdict avant l'inventaire, pas de rapport avant la cascade complète.

## Actions

| Étape | Fichier | Rôle |
|---|---|---|
| Cadrage | `actions/01-cadrer.md` | contrat figé sur un sous-domaine, commit de la grille relevé, inventaire, découpage des fichiers en instructions |
| Criblage | `actions/02-cribler.md` | mesures batchées, cascade par instruction (sortie au premier critère disqualifiant), formulation sur chaque survivante, cohérence par fichier |
| Consolidation | `actions/03-consolider.md` | budget global (une somme, jamais par instruction), rédaction du rapport horodaté |

## Règles transverses

- **La grille fait foi, ce skill est délibérément partiel.** Les définitions des critères C1–C7, l'ordre des domaines, les invariants du rapport (nom horodaté, immutabilité, traçabilité, remesure des chiffres repris) vivent dans la grille, section Méthode. Les actions les citent, ne les recopient jamais. *Pourquoi : un critère recopié ici diverge au premier edit de la grille — c'est le constat C4 de l'audit qui a motivé ce skill.*
- **L'unité de travail est l'instruction**, jamais le fichier ni le critère. Un fichier de règles porte plusieurs instructions aux sorts différents ; un verdict au fichier les écrase. *Pourquoi : c'est la divergence mesurée entre les deux premiers rapports.*
- **Le protocole ne se corrige pas dans la passe qui l'observe.** Un défaut de ce skill relevé pendant une passe se verse en ajout dans `audits/axes-protocole.md`, et s'y applique plus tard, par l'humain via `skill-craft`. Aucune action n'appelle `skill-craft` toute seule. Ce que le registre porte de **conventions figées** se lit en revanche au cadrage et s'applique tel quel. *Pourquoi la coupe entre les deux : `rules/reasoning.md` pose qu'une mesure vient de dehors, Huang et al. 2023 à l'appui — l'auto-correction sans retour externe dégrade le raisonnement. Une passe qui corrige l'instrument avec lequel elle vient de juger n'a aucun bras de contrôle. La porte du registre, elle, est un comptage.*
- **La grille ne se touche pas pendant l'audit.** Une révision se propose dans le rapport et se décide entre deux audits, par l'humain. *Pourquoi : réviser le référentiel en cours de mesure invalide les verdicts déjà rendus.*
- **Mesurer avant de juger.** Tout test exécutable tourne en lot avant le premier verdict de cascade. *Pourquoi : un verdict rendu avant sa mesure se rationalise au lieu de se vérifier (`rules/reasoning.md`).*
- **Une étape qui ne peut pas conclure échoue fermé.** Rendre le partiel avec son état (verdicts rendus, restantes listées), jamais improviser la suite — chaque action porte son bloc « Si ça casse ». *Pourquoi : un audit qui continue sur une étape ratée produit des verdicts invérifiables, pires qu'un partiel honnête — même exigence que pour un mécanisme déterministe, cf. les contraintes de **C2** dans la grille.*
