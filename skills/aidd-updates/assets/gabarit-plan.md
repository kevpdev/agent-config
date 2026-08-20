# Montée AIDD — <N> plugin(s) en attente

<!--
Gabarit du corps du plan, injecté par l'action 02 dans le fichier d'état.
Le front-matter n'est PAS ici : il appartient au détecteur, seul écrivain.
Ordre imposé : les plugins cassants d'abord, puis les autres, puis ce qui ne nous touche pas.
Pourquoi cet ordre : le lecteur arrive à froid et décide en lisant la première section.
-->

## Ce qui casse chez nous

### <plugin> <version installée> vers <version cible> — CASSANT

<Ce que dit le changelog, en une ou deux phrases, sans recopier la prose upstream.>

| Fichier | Ligne | Remplacer | Par |
|---|---|---|---|
| `skills/…/….md` | 45 | `aidd-refine:04-shadow-areas` | `aidd-refine:03-shadow-areas` |

<!-- Une ligne par occurrence réellement trouvée par grep. Aucune entrée « à vérifier ». -->

## Ce qui monte sans nous toucher

| Plugin | De | Vers | Ce que ça apporte |
|---|---|---|---|
| `aidd-vcs` | 2.2.1 | 2.3.1 | <une ligne> |

## Ce qui reste à décider par l'humain

<Omettre cette section s'il n'y a rien. Jamais de « aucun » en placeholder.>

- <la question, et pourquoi elle ne se tranche pas par une mesure>

## Commandes de la montée

```bash
claude plugin marketplace update aidd-framework
claude plugin update <plugin>@aidd-framework   # une fois par plugin en retard
# puis redémarrer la session : les skills et agents ne sont pas rechargés à chaud
```
