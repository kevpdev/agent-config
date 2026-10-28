# Références — `wrappers/claude/rules/plan-mode.md`

Les raisons de rangement et les récits datés de la règle. Jamais chargé automatiquement : la règle garde le déclencheur et un fait par pourquoi. Sortis de la règle le 2026-10-28 (issue #66), texte d'origine.

---

## Pourquoi la reco ne double pas l'invite de l'outil

**POURQUOI cette demande ne double pas celle de l'outil** : la description d'`EnterPlanMode` dit qu'il exige le consentement de l'utilisateur. Constaté à l'usage, cette invite n'apparaît pas, et `wrappers/claude/settings.json` ne porte aucun bloc `permissions` qui la rétablirait. La porte n'existe donc plus qu'ici.

## Le conflit avec `aidd-orchestrator:01-sdlc` (2026-08-19)

**POURQUOI, mesuré le 2026-08-19** : le corps de `aidd-orchestrator:01-sdlc` dit « decide and act without confirmation », quand cette page dit qu'aucune demande détaillée ne vaut accord sur une approche. Les deux textes se contredisent mot pour mot, et une instruction utilisateur passe devant celle d'un skill. Sans cette exception, le harnais refuse structurellement d'héberger un SDLC autonome.

## Pourquoi l'exception ne rouvre pas la décision

**POURQUOI la condition ne rouvre pas la décision** : « un skill AIDD pilote-t-il ? » se tranche au premier tour et ne se rejoue pas ensuite. C'est la même forme que la règle au-dessus, pas une vigilance à tenir sur la durée.

## Pourquoi l'exception n'est pas un `paths:`

**POURQUOI ce n'est pas un `paths:`** : le scope `paths:` porte sur le fichier édité, jamais sur le repo (`back-spring.md` sur `**/*.java`, `front-react.md` sur `**/*.{ts,tsx}`). Un repo AIDD mêlant Java et TypeScript matcherait les deux, donc aucun glob n'exprime cette exception.
