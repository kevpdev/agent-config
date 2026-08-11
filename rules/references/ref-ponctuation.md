# Références — `rules/ponctuation.md`

Les mesures qui fondent la règle. Jamais chargé automatiquement.

---

## Pourquoi un dosage ne marche pas (2026-08-05)

La consigne en vigueur avant cette date demandait de « limiter le `;` » et de « préférer `:` ». Comptage sur la prose du vault pro, tirets de titre et de tableau exclus :

| Corpus | Points-virgules / 1 000 mots | Tirets de prose / 1 000 mots |
|---|---|---|
| `scripts/logs/sessions/` | 5,25 | 2,30 |
| `2_PROJECTS/` | 2,80 | — |
| Vault perso, même règle scopée | **1,09** | — |

Le vault perso sert de cible parce que la règle y était déjà écrite en substitutions et non en dosage.

## Le corpus qui portait les règles était le pire (2026-08-11)

Comptage sur la couche chargée de `agent-config` : `rules/*.md` non scopés, `wrappers/claude/rules/*.md`, l'output style actif. Prose seule, 3 235 mots.

| | Mesure | Rapport à la cible de 1,09 |
|---|---|---|
| Points-virgules | **7,11** / 1 000 mots | 6,5× |
| Tirets de prose | **10,82** / 1 000 mots | pas de cible chiffrée |

**Six jours sans mouvement.** La session du 2026-08-05 avait déjà compté ce dossier précis : 23 points-virgules et 38 tirets, soit 61 substitutions dues. Le 2026-08-11 : 23 et 35, alors que la couche avait été réécrite de fond en comble dans la journée, passant de 4 869 à 2 840 mots. La ponctuation survit à une réécriture complète, ce qui montre qu'elle ne se corrige pas comme effet de bord d'un autre chantier.

**Cause du non-mouvement, mesurée** : la règle vivait dans `$OBSIDIAN_VAULT_PRO/.agents/rules/ponctuation.md`, avec un frontmatter `paths:` ne listant que des dossiers du vault. Elle se chargeait bien en session vault, par le `.claude/rules/` du projet qui est un symlink vers `.agents/`. Elle ne se chargeait jamais en session `agent-config`. D'où le déplacement du 2026-08-11 vers la couche globale, sans `paths:`.

## Commande de comptage, et son calibrage

```bash
P=$(cat rules/*.md wrappers/claude/rules/*.md wrappers/claude/output-styles/*.md \
    | grep -v '^#' | grep -v '^|' | grep -v '^---')
W=$(printf "%s" "$P" | wc -w)
SC=$(printf "%s" "$P" | grep -o ' ; ' | wc -l)
EM=$(printf "%s" "$P" | grep -o ' — ' | wc -l)
LAB=$(printf "%s" "$P" | grep -oE '\*\* — ' | wc -l)   # séparateurs label/définition
# tirets de prose = EM - LAB
```

**Calibré sur le contre-exemple de la règle** avant tout comptage, conformément au trigger « zéro » de `reasoning.md` : « Le score baisse — probablement à cause du bruit — donc on le recalibre ; le seuil actuel n'est plus fiable. » rend 2 tirets et 1 point-virgule. L'instrument voit le positif.

**Ce que la commande ne sait pas exclure** : un tiret de séparateur label sans gras, et un tiret dans un item de liste. Le chiffre des tirets de prose est donc un majorant, jamais un exact.
