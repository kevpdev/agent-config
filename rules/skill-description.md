# Description d'un skill — quoi et quand, sans chevron

**DÉCLENCHEUR** : je crée, modifie ou **planifie la modification** d'un `SKILL.md`, dans n'importe quel repo, skill AIDD compris.

**POURQUOI global et non scopé par `paths:`** : un `paths:` se déclenche à l'édition, et la planification vient avant. Constaté le 2026-10-15 : un plan d'extension de `video-brief` a été écrit sans que cette règle soit chargée, rattrapée seulement parce que l'utilisateur l'a citée. La règle est courte, la charger toujours coûte presque rien.

**La `description` dit ce que fait le skill et quand l'utiliser.** Troisième personne, le cas d'usage principal en premier, les mots que l'utilisateur dira pour le déclencher. Ni forme d'appel, ni syntaxe d'arguments : ils vont dans `argument-hint`, en `[crochets]` (`[issue-number]`, `[filename] [format]`).

**Pas de `<` ni de `>` dans la `description`.** La doc de la plateforme interdit les balises XML dans ce champ (1 024 caractères au plus). Claude Code échappe les chevrons en `&lt;` `&gt;` dans la liste des skills (constaté en 2.1.300), donc écrire `URL` et non `<url>`.

**POURQUOI, mesuré le 2026-10-15** : `/capture-video <url>` dans une `description` sortait en `&lt;url&gt;` dans la liste des skills. La doc range les arguments dans `argument-hint`, qui s'affiche à l'autocomplétion. Je ne sais pas si cette autocomplétion montre aussi la `description` : non mesuré.

**Sources** : `platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices` (section « Writing effective descriptions ») et `code.claude.com/docs/en/skills` (champs `description` et `argument-hint`).

**TEST** : `grep -rn '^description:.*[<>]' --include=SKILL.md .` ne renvoie rien. Une description en bloc YAML (`>-`) se lit sur ses lignes suivantes, le `grep` ne les couvre pas.
