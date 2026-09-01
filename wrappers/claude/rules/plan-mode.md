# Sortie d'analyse — passer par le plan mode

Quand la conclusion d'une analyse appellera des modifications, appeler `EnterPlanMode` avant d'éditer, au lieu d'enchaîner.

Ni le mode **bypass**, ni une demande précise et détaillée ne valent accord sur une **approche** : les deux couvrent l'exécution, jamais le choix de ce qu'on va faire. La description de l'outil autorise à sauter le plan dans le second cas. Ici, non.

**POURQUOI** : en plan mode l'édition devient impossible, pas seulement déconseillée. Une décision à prendre une fois, au lieu d'une retenue à tenir sur toute la durée de la session.

## Dire la reco avant d'appeler l'outil

**DÉCLENCHEUR** : je viens de conclure, et mon prochain geste serait `EnterPlanMode`.

**À LA PLACE d'** appeler l'outil directement, écrire la reco et sa ligne de pourquoi, puis finir sur « je pars sur ça ? ». L'appel n'a lieu qu'après un accord explicite.

**POURQUOI** : le plan mode masque la conversation à l'écran. Un verdict qui n'a jamais été dit part avec elle, donc il n'est pas lu. Écrit avant l'appel, il reste dans l'historique visible.

**POURQUOI cette demande ne double pas celle de l'outil** : la description d'`EnterPlanMode` dit qu'il exige le consentement de l'utilisateur. Constaté à l'usage, cette invite n'apparaît pas, et `wrappers/claude/settings.json` ne porte aucun bloc `permissions` qui la rétablirait. La porte n'existe donc plus qu'ici.

**Ce que la demande ne rouvre pas** : une réponse « oui » vaut accord sur l'approche, pas sur l'exécution. Le plan mode reste le lieu où le plan se rédige et se valide.

## EXCEPTION — quand un skill du framework AIDD possède le flux

Ne pas appeler `EnterPlanMode` quand le travail est piloté par un skill AIDD, que ce soit `/aidd-orchestrator:01-sdlc` ou un `/aidd-dev:*` lancé à la main. Ces skills portent leurs propres portes de validation, et le plan mode arrête le flux à son premier edit.

**Ce que l'exception ne couvre pas** : le travail que je pilote moi-même dans un repo AIDD. Une analyse de ticket, une refacto à la main, une lecture de code qui conclut sur des modifications. La règle s'applique alors entière, que le repo porte un `aidd_docs/` ou non.

**POURQUOI, mesuré le 2026-08-19** : le corps de `aidd-orchestrator:01-sdlc` dit « decide and act without confirmation », quand cette page dit qu'aucune demande détaillée ne vaut accord sur une approche. Les deux textes se contredisent mot pour mot, et une instruction utilisateur passe devant celle d'un skill. Sans cette exception, le harnais refuse structurellement d'héberger un SDLC autonome.

**POURQUOI la condition ne rouvre pas la décision** : « un skill AIDD pilote-t-il ? » se tranche au premier tour et ne se rejoue pas ensuite. C'est la même forme que la règle au-dessus, pas une vigilance à tenir sur la durée.

**POURQUOI ce n'est pas un `paths:`** : le scope `paths:` porte sur le fichier édité, jamais sur le repo (`back-spring.md` sur `**/*.java`, `front-react.md` sur `**/*.{ts,tsx}`). Un repo AIDD mêlant Java et TypeScript matcherait les deux, donc aucun glob n'exprime cette exception.
