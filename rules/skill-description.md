# Description d'un skill — quoi et quand, sans chevron

**DÉCLENCHEUR** : je crée, modifie ou **planifie la modification** d'un `SKILL.md`, dans n'importe quel repo, skill AIDD compris.

**La `description` dit ce que fait le skill et quand l'utiliser.** Troisième personne, le cas d'usage principal en premier, les mots que l'utilisateur dira pour le déclencher. Ni forme d'appel, ni syntaxe d'arguments : ils vont dans `argument-hint`, en `[crochets]` (`[issue-number]`, `[filename] [format]`).

**Pas de `<` ni de `>` dans la `description`.** La doc de la plateforme interdit les balises XML dans ce champ (1 024 caractères au plus). Claude Code échappe les chevrons en `&lt;` `&gt;` dans la liste des skills (constaté en 2.1.300), donc écrire `URL` et non `<url>`.

**TEST** : `grep -rn '^description:.*[<>]' --include=SKILL.md .` ne renvoie rien. Une description en bloc YAML (`>-`) se lit sur ses lignes suivantes, le `grep` ne les couvre pas.

Mesure, sources et raison de rangement → `rules/references/ref-skill-description.md`.
