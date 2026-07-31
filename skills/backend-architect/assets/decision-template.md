# Template — Décision d'architecture

> L'ordre compte : la recommandation ouvre le rapport, les options la justifient ensuite. Un lecteur qui s'arrête après trois lignes doit déjà connaître la décision — cf. `rules/style.md`, « verdict d'abord ». Ne pas restaurer un catalogue en tête sous prétexte d'exposer le raisonnement.

```markdown
## Recommandation

**Go with <Option X>** parce que <raison load-bearing — le critère qui fait pencher la balance>.

**Trade-off accepté :** <inconvénient principal de l'option choisie, explicitement reconnu>.

**Contexte assumé :** <contraintes retenues — charge, équipe, deadline, stack existante> · **Incertitude :** <ce qui n'est pas clair et ferait basculer la décision>.

---

## Options écartées

### 1. **<Option A>** — <résumé en une ligne>

**Pros :**
- <avantage concret>

**Cons :**
- <inconvénient concret>
- <coût ou risque — dont celui qui l'a fait écarter>

### 2. **<Option B>** — <résumé en une ligne>

**Pros :**
- …

**Cons :**
- …

### 3. **<Option C>** *(optionnelle)*
- …

---

## Signal de prématurité *(si applicable)*

"Tu n'as pas besoin de <pattern> parce que <signal concret>.
Reviens à cette question quand <seuil mesurable>."

---

## Validation

Cette décision est correcte si dans 3-6 mois :
- [ ] <Signal mesurable 1>
- [ ] <Signal mesurable 2>
```
