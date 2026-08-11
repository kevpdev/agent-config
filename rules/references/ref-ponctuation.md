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

**Ce que la commande ne sait pas exclure**, mesuré en payant la dette le 2026-08-11 :

- un tiret de séparateur label **quand le label contient une parenthèse** (`**Vertical par défaut** (`TD`/`TB`) — horizontal…`) ou **quand le tiret est à l'intérieur du gras** (`**TRIGGER concret — un comptage…**`). Le filtre `\*\* — ` les rate tous les deux.
- un tic **cité comme contre-exemple**. Les 2 tirets et le point-virgule de la ligne ❌ de `rules/ponctuation.md` sont comptés comme des défauts alors qu'ils sont la démonstration. Un compteur ne distingue pas l'illustration de l'infraction.

Le chiffre des tirets de prose est donc un majorant, jamais un exact.

## Dette payée sur la couche chargée (2026-08-11)

| | Avant | Après |
|---|---|---|
| Prose mesurée | 3 411 mots | 2 761 mots |
| Points-virgules / 1 000 mots | **7,04** | **0,36** |
| Tirets de prose / 1 000 mots | **10,85** | **2,17** |
| `=` pour « est » en prose | 4 | **0** |

La cible de 1,09 point-virgule est tenue avec un facteur 3. Les deux résidus sont des faux positifs de l'instrument, listés juste au-dessus.

**Deux substitutions n'ont pas été traitées, et c'est un choix** :

- la flèche de l'idiome `**À LA PLACE de** X → Y`, présente dans tout le harnais. La règle range la flèche dans les exceptions de code, de diagramme et d'index, ce qui ne couvre pas cet usage. La retirer partout est une décision de forme à part entière, pas un nettoyage de ponctuation.
- la flèche de mapping de `tooling.md` (`` `java` → `bash -lc …` ``), qui est une table de correspondance déguisée en liste. Exception d'index, gardée.

**Hors périmètre de cette passe** : `back-spring.md` et `front-react.md`, scopés par `paths:` donc absents de la couche chargée. Ils portaient 9 et 4 occurrences au comptage du 2026-08-11.
