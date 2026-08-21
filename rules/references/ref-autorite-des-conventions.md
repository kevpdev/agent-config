# Références — `rules/autorite-des-conventions.md`

Les cas mesurés qui fondent la hiérarchie. Jamais chargé automatiquement : la règle garde l'impératif, le déclencheur et une ligne de pourquoi, seule la preuve descend ici. Extrait le 2026-08-21, passe d'audit `rules/`, cinq blocs au-dessus de l'alerte C7.

---

## Pourquoi la règle existe — le run du 2026-08-19

Sur un run réel de `aidd-orchestrator:01-sdlc`, l'agent s'est **arrêté pour demander** si les 40 tests existants d'une classe devaient migrer au format de `back-spring.md`.

La règle donnait le format sans donner sa **portée**, donc la question se rouvrait à chaque run. Pire, sur un repo à plusieurs développeurs sans convention écrite, elle n'a même pas de bonne réponse : l'hétérogénéité n'est pas un signal, c'est du bruit.

**La leçon** : une convention sans portée déclarée produit une question, et une question qui se rouvre à chaque run coûte plus que la convention ne rapporte.

## La coupe forme/fond — le cas `front-react.md`

`front-react.md` fait la démonstration en le disant lui-même. Le PascalCase d'un composant et le préfixe `use` d'un hook « ne sont pas des conventions **cosmétiques** mais des **contrats outillés** » :

- la **casse** signale à React qu'il ne s'agit pas d'une balise HTML,
- **`use`** déclenche la vérification des règles des hooks par le linter.

Ils relèvent donc du **fond**, et aucun repo ne les rouvre. La colocalisation du fichier de test, elle, reste de la **forme**.

**La leçon** : le test « ça change ce qui est vrai, ou seulement à quoi ça ressemble » ne se devine pas au ressenti. Deux conventions qui se ressemblent (nommer un composant, ranger son test) tombent de part et d'autre de la coupe.

## Pourquoi le repo passe devant mon harnais

Une convention de forme sert la **cohésion**. Une convention « meilleure » appliquée à 5 % d'un repo vaut moins qu'une convention médiocre appliquée à 100 %.

Imposer mon format personnel à une base partagée produit exactement l'hétérogénéité que la convention devait supprimer. C'est l'inverse de la précédence habituelle, où mon harnais gagne, et c'est voulu.

## Le niveau 0 n'est pas théorique — `vcs.md` contre le garde

`Winggy-v3/aidd_docs/memory/vcs.md` déclare **dix** types de commit, dont `style` et `revert`. `wrappers/claude/scripts/hooks/guard-no-claude-in-commit.sh` n'accepte que `feat|fix|refactor|docs|test|chore|perf|ci`.

Un `style(...)` y est **refusé à l'appel**, quoi que dise la mémoire du repo.

**La leçon** : une hiérarchie qui commencerait au niveau 1 promettrait le contraire de ce qui se passe. Le garde déterministe n'arbitre pas, il coupe.

## Pourquoi la portée s'arrête au neuf

Une convention adoptée après le code laisse forcément des fichiers mixtes, et c'est son état transitoire **normal**.

Migrer l'existant dans le même run gonfle le diff et mélange deux intentions. Cette migration est un `refactor` séparé, que l'humain demande.

## Trou connu, non comblé

La hiérarchie ne porte **aucun niveau pour le défaut d'un framework installé**. Cas mesuré le 2026-08-21 : `rules/mermaid.md` impose `TD`/`TB` quand `aidd-context:09-mermaid` déclare `LR` par défaut dans sa propre référence. Ni le niveau 1 (le repo ne déclare rien) ni le niveau 2 (les deux sources sont extérieures au repo) ne le rangent.

Résolu au cas par cas pour l'instant : la règle nomme le skill qu'elle écrase. Versé à `audits/2026-08-21-audit-agent-config-rules.md`, section « À réviser entre deux audits ».
