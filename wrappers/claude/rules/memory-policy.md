## Auto-memory — ce qui n'y entre pas

**RÈGLE D'ÉCRITURE** : ne pas y écrire de fait projet dès que le repo porte un `aidd_docs/` ou qu'un vault assure le récap. Ces deux-là sont les homes de la couche projet, chacun avec son propre système. L'auto-memory ne la reprend que si aucun des deux n'existe.

**CE QU'ELLE GARDE** : profil user, config et environnement perso, référence Claude, feedback parent-only. Autrement dit ce qui n'a pas d'autre home.

**POURQUOI** : un fait projet volatil (config, clé, run, état) devient faux, et l'auto-memory ne s'auto-purge pas. La copie périmée survit jusqu'à ce qu'une session la corrige, donc le même fait rangé à deux endroits finit par diverger. Ne pas laisser entrer la couche projet empêche le stock périmé de se reconstituer, sans purge manuelle récurrente. Un doublon de règle **statique** (style, méthodo) est en revanche bénin, puisqu'il ne dérive pas, et ne justifie aucune purge.

**CE QUI DOIT TRAVERSER UN SOUS-AGENT** va dans `rules/` ou `CLAUDE.md`, jamais dans le vault ni en auto-memory, parce qu'un sous-agent ne lit ni l'un ni l'autre. Les rules user globales sont bien injectées, vérifié le 2026-07-20 par sondage d'un sous-agent general-purpose sans aucune lecture disque, et celles à frontmatter `paths:` suivent leur scope.
