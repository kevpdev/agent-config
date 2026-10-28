# Sortie d'analyse — passer par le plan mode

Quand la conclusion d'une analyse appellera des modifications, appeler `EnterPlanMode` avant d'éditer, au lieu d'enchaîner.

Ni le mode **bypass**, ni une demande précise et détaillée ne valent accord sur une **approche** : les deux couvrent l'exécution, jamais le choix de ce qu'on va faire. La description de l'outil autorise à sauter le plan dans le second cas. Ici, non.

**POURQUOI** : en plan mode l'édition devient impossible, pas seulement déconseillée. Une décision à prendre une fois, au lieu d'une retenue à tenir sur toute la durée de la session.

## Dire la reco avant d'appeler l'outil

**DÉCLENCHEUR** : je viens de conclure, et mon prochain geste serait `EnterPlanMode`.

**À LA PLACE d'** appeler l'outil directement, écrire la reco et sa ligne de pourquoi, puis finir sur « je pars sur ça ? ». L'appel n'a lieu qu'après un accord explicite.

**POURQUOI** : le plan mode masque la conversation à l'écran. Un verdict qui n'a jamais été dit part avec elle, donc il n'est pas lu. Écrit avant l'appel, il reste dans l'historique visible.

**Ce que la demande ne rouvre pas** : une réponse « oui » vaut accord sur l'approche, pas sur l'exécution. Le plan mode reste le lieu où le plan se rédige et se valide.

## EXCEPTION — quand un skill du framework AIDD possède le flux

Ne pas appeler `EnterPlanMode` quand le travail est piloté par un skill AIDD, que ce soit `/aidd-orchestrator:01-sdlc` ou un `/aidd-dev:*` lancé à la main. Ces skills portent leurs propres portes de validation, et le plan mode arrête le flux à son premier edit.

**Ce que l'exception ne couvre pas** : le travail que je pilote moi-même dans un repo AIDD. Une analyse de ticket, une refacto à la main, une lecture de code qui conclut sur des modifications. La règle s'applique alors entière, que le repo porte un `aidd_docs/` ou non.

**POURQUOI** : le corps de `aidd-orchestrator:01-sdlc` dit « decide and act without confirmation ». Sans cette exception, le harnais ne peut pas héberger un SDLC autonome.

**Ce que l'exception autorise aussi** : commit, push et PR draft pendant le run, voir la section « Git pendant un run AIDD » de `rules/aidd.md`.

Récits et raisons de rangement de cette page → `rules/references/ref-plan-mode.md`.
