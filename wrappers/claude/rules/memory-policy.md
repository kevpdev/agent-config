## Auto-memory — ce qui n'y entre pas

**RÈGLE D'ÉCRITURE** : ne pas y écrire de fait projet dans un dépôt git ou quand un vault assure le récap. La hiérarchie de la mémoire de `rules/aidd.md` donne alors son home à la couche projet. L'auto-memory ne la reprend que hors des deux, et rien n'en est migré.

**CE QU'ELLE GARDE** : profil user, config et environnement perso, référence Claude, feedback parent-only. Autrement dit ce qui n'a pas d'autre home.

**POURQUOI** : un fait projet volatil (config, clé, run, état) devient faux, et l'auto-memory ne s'auto-purge pas. La copie périmée survit jusqu'à ce qu'une session la corrige. Fermer la porte à la couche projet évite d'avoir à purger. Un doublon de règle **statique** (style, méthodo) est en revanche bénin : il ne dérive pas.

**CE QUI DOIT TRAVERSER UN SOUS-AGENT** va dans `rules/` ou `CLAUDE.md`, jamais dans le vault ni en auto-memory, parce qu'un sous-agent ne lit ni l'un ni l'autre. Les rules user globales sont bien injectées, vérifié le 2026-07-20 par sondage d'un sous-agent general-purpose sans aucune lecture disque, et celles à frontmatter `paths:` suivent leur scope.
