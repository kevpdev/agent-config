---
paths:
  - "**/SKILL.md"
---

# Description d'un skill — la forme d'appel y figure, sans chevron

**DÉCLENCHEUR** : je crée ou modifie un `SKILL.md`, dans n'importe quel repo, skill AIDD compris.

**À LA PLACE de** ranger les arguments dans `argument-hint` seul, ouvrir la `description` sur la forme d'appel : `Call /nom URL [--option].` Les arguments obligatoires sont en majuscules, les facultatifs entre crochets, puis vient le reste de la description.

**Pas de `<`, `>` ni `->` dans la `description`.** Écrire `URL` et non `<url>`, `(voir x)` et non `(-> x)`. `argument-hint` peut garder ses chevrons.

**POURQUOI, mesuré le 2026-10-15** : le menu `/` affiche la `description` en entier et n'affiche pas `argument-hint`. Les chevrons y sortaient en `&lt;url&gt;`, et les options n'étaient visibles nulle part. La `description` est donc le seul endroit où celui qui tape `/` voit comment appeler le skill.

**TEST** : `grep -rn '^description:.*[<>]' --include=SKILL.md .` ne renvoie rien. Une description en bloc YAML (`>-`) se lit sur ses lignes suivantes, le `grep` ne les couvre pas.
