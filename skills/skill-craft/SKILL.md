---
name: skill-craft
description: Fabrique et vérifie mes skills perso en français, selon la convention de rédaction (`references/skill-authoring-fr.md`). Prend une intention de skill (nom, domaine, but, actions pressenties) et produit un skill au format routeur AIDD — SKILL.md pur + actions à l'anatomie + références. Vérifie aussi un skill existant : relance le `## Test` de chaque action et lint les dérives R1/R6/R4 que rien d'autre n'attrape. Autonome, sans dépendance au framework AIDD, sortie 100 % française. Utiliser quand l'utilisateur dit "crée un skill perso", "refonds ce skill", "valide ce skill", "lint ce skill", ou "/skill-craft". NE PAS utiliser pour un skill d'équipe destiné au partage anglophone (→ aidd-context:04-skill-generate), ni pour piloter un workflow de dev (→ aidd-pilot).
---

# skill-craft

Fabrique de skills perso. Il applique **ma** convention de rédaction (`references/skill-authoring-fr.md`, fork FR des règles AIDD) au lieu de dépendre du plugin AIDD. Deux gestes : **échafauder** un skill neuf, **vérifier** un skill existant.

> [!note] Pourquoi un skill et pas juste la convention
> Un document ne sert que s'il est chargé en contexte. Un skill est invocable et se suffit à lui-même, donc il atteint un contexte neuf, même un sous-agent. C'est ce qui fait mordre la convention au lieu d'espérer qu'elle soit sous les yeux.

## Le flux

```
intention → 01-scaffold → 02-validate → skill prêt
                              ↑
        skill existant ───────┘  (02 tourne aussi seul)
```

- **Échafauder puis vérifier** pour un skill neuf : `01-scaffold` pose l'arborescence, `02-validate` la contrôle avant de rendre la main.
- **Vérifier seul** pour un skill déjà écrit (refonte, audit) : entrer direct dans `02-validate` avec le chemin du skill.

## Actions

| Étape | Fichier | Rôle |
|---|---|---|
| Échafaudage | `actions/01-scaffold.md` | de l'intention au squelette : nom, check de collision, SKILL.md routeur, actions à l'anatomie, en français |
| Vérification | `actions/02-validate.md` | relance le `## Test` de chaque action + lint R1 (routeur pur), R4 (<500 lignes), R6 (doublon) |

## Règles transverses

- **La convention est l'unique source.** Les règles R1–R12, l'anatomie d'action, le nommage vivent dans `references/skill-authoring-fr.md`. Les actions la citent, ne la recopient pas (R6). *Pourquoi : un fait à deux endroits dérive.*
- **Français partout.** Frontmatter, corps, actions, références en français. Seuls les en-têtes d'anatomie (`Input`/`Output`/`Process`/`Test`) restent en anglais, ce sont des repères de structure. *Pourquoi : mes skills perso sont pour moi, pas pour du partage anglophone — c'est le R10 modifié.*
- **Sans dépendance AIDD.** Ce skill ne compose pas `04-skill-generate` et ne suppose aucun plugin installé. Il porte sa propre convention. *Pourquoi : un skill perso doit se créer n'importe où, même sans le framework AIDD, et sans repasser par une traduction depuis l'anglais.*
- **R1 et R6 ne se vérifient qu'ici.** Aucun autre outil ne détecte un routeur qui regonfle en logique métier ni un fait recopié. C'est le lint de `02-validate` qui bouche ce trou. *Pourquoi : ce sont les deux dérives les plus fréquentes.*
