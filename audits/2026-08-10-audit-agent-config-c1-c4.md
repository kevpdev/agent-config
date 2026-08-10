# Audit agent-config — passe C1 + C4 (session vierge)

**Date** : 2026-08-10.
**Grille** : `audits/grille-harnais.md` au commit `2c9fc31`, avec modifications locales non commitées (2 insertions, 2 suppressions — `git diff --stat`).
**Conditions** : session vierge du rapport précédent — ni `audits/2026-08-10-audit-agent-config.md` ni la note d'inbox du vault n'ont été lus. Rapport indépendant, à confronter au premier.
**Contrat** : C1 (inférable ?) et C4 (unique ?) uniquement. Hors contrat : C2, C3, C5, C6, le vault, les repos projets. Les découvertes hors contrat sont capturées en fin de rapport, non creusées.

**Verdict** : le socle passe bien C1 — une seule règle largement inférable (`commit-convention.md`, mesuré). C4 rend **un seul doublon volatil** à corriger : la liste des types de commit, dupliquée entre la règle et le guard.

---

## Inventaire du domaine

Mesure : `ls`, `find wrappers -type f` (2026-08-10).

- `rules/` : 11 fichiers, dont 2 scopés par frontmatter `paths:` (`back-spring.md`, `front-react.md` — vérifié par lecture des lignes 1–5).
- `wrappers/claude/` : `rules/memory-policy.md`, `output-styles/chat-style.md`, `settings.json`, `agents/doc-writer.md`, 2 hooks (`guard-no-claude-in-commit.sh`, `guard-no-remote-write.py`), 3 scripts.
- `skills/` : 26 skills.
- Pas de `checks/`, pas de `CLAUDE.md` racine.
- Memory auto du projet : `MEMORY.md` **absent** (`cat` → absent) — rien à auditer sur ce sous-domaine.

---

## C1 — Inférable ?

### Test de la grille, exécuté sur le candidat le plus suspect

Un sous-agent en contexte neuf, sommé d'ignorer ses instructions injectées et de ne lire ni `rules/commit-convention.md` ni `audits/`, a retrouvé la convention de commit **complète** — structure, 8 types, langue EN, exception vault (date en scope, sujet FR toléré), interdit de mention Claude/co-authorship, fail-open du guard — en **4 appels d'outil** (git log, 2 find/grep, 1 read du guard). Source finale : `wrappers/claude/scripts/hooks/guard-no-claude-in-commit.sh:96,228-241`.

4 appels > seuil de 3 → **inférable à coût élevé, info stable** → action de la grille : **synthèse courte**. La règle actuelle l'est déjà en grande partie, mais sa section « What is enforced, and what is not » décrit le contenu du guard, lisible en 1 read une fois localisé → réductible en pointeur.

**Réserve méthodologique (approximé)** : un sous-agent hérite des règles globales injectées (vérifié le 2026-07-20, cf. `wrappers/claude/rules/memory-policy.md`). Le test C1 « contexte neuf » de la grille n'est donc jamais propre pour une règle globale — il repose sur l'instruction « ignore ton contexte », que rien ne garantit. Résultat à lire comme approximation, et point de grille à réviser entre deux audits.

### Verdicts par fichier

Jugés sur pièce (contenu injecté en session ou lu — `back-spring.md`, `front-react.md` lus intégralement).

| Fichier | Verdict C1 | Base |
|---|---|---|
| `tooling.md` | **Garder** — deux pièges d'environnement (JAVA_HOME absent hors shell login, `mvnw` mode 644), dont un à panne **silencieuse** (heredoc imbriqué) : la récupération naturelle d'un modèle qui échoue serait la mauvaise (`chmod +x`), et la panne silencieuse ne déclenche aucune découverte | jugé sur pièce |
| `reasoning.md` | **Garder** — décisions comportementales, non-inférables | jugé sur pièce |
| `workflow.md` | **Garder** — décisions (go-ahead, pré-vol, échec fermé, délégation), non-inférables | jugé sur pièce |
| `style.md`, `profil.md`, `chat-style.md` | **Garder** — préférences de l'opérateur, non-inférables par construction | jugé sur pièce |
| `mermaid.md` | **Garder** — décision (vertical, zéro croisement) | jugé sur pièce |
| `memory-policy.md` | **Garder** — décision de rangement | jugé sur pièce |
| `ai-principles.md`, `ai-practices.md` | **Garder au titre de C1** — doctrine et banc d'essai, non-inférables (leur volume relève de C3/C6, hors contrat) | jugé sur pièce |
| `commit-convention.md` | **Réduire** — inférable à coût élevé (4 appels, mesuré ci-dessus), info stable → synthèse courte + pointeur vers le guard | mesuré |
| `back-spring.md`, `front-react.md` | **Garder** — majoritairement des décisions que le code ne montre pas uniformément (pas de DDD tactique, mock I/O uniquement, outside-in). Marginal : les lignes de stack (JUnit 5 + Mockito, Vitest + RTL) sont inférables en 1 lecture de pom.xml/package.json — supposé, non testé sur un repo Winggy (hors domaine) | lu + supposé |
| `settings.json` | Config, pas d'instruction — hors crible | lu |

---

## C4 — Unique ?

Mesure : greps des motifs centraux sur `rules/`, `skills/`, `wrappers/`, grille incluse, rapport du jour et inbox exclus (2026-08-10).

### Doublon volatil — le seul à corriger

**Liste des 8 types de commit** : `rules/commit-convention.md` (section Format) **et** `guard-no-claude-in-commit.sh:231,236` (regex + message d'erreur). La règle assume la duplication par écrit (« It carries the same type list as this file, so a new type has to be added in both places ») — c'est la hiérarchisation que C4 interdit : le doublon diverge au premier type ajouté d'un seul côté.

**Reco** : le guard fait foi (c'est lui qui refuse), la règle garde une ligne de pointeur. Se combine avec le verdict C1 du même fichier.

### Doublons statiques — bénins selon la grille, notés

- « Une instruction dupliquée s'élimine, elle ne se hiérarchise pas » : quasi-verbatim dans `rules/ai-practices.md:51` (§4) et `audits/grille-harnais.md` (critère C4). La grille se dit « consolidée » des règles mais restate au lieu de pointer.
- Les 3 contraintes d'échec fermé (`workflow.md`) restatées dans la grille C2, avec pointeur (« de workflow.md, non renégociables »).

Statiques tous deux → bénins tant qu'ils ne bougent pas ; à trancher à la prochaine révision de grille.

### Conformes exemplaires — vérifiés sur pièce

- `mermaid.md` ↔ `skills/mermaid-craft/SKILL.md:23` : le skill **refuse explicitement** de redire les deux non-négociables (« Ne pas les redire ici et ne pas en écrire de variante »). Modèle du pattern C4.
- `style.md` ↔ `chat-style.md` : l'output style se déclare **delta**, le noyau pointé vers `rules/style.md`.
- `profil.md` ↔ `chat-style.md` : scission déclarée besoin/protocole de ré-ancrage.
- `skills/backend-architect/assets/decision-template.md:3` : applique « verdict d'abord » avec pointeur « cf. `rules/style.md` ».
- `skills/aidd-pilot` (`SKILL.md:56`, `references/governor.md:35`) : **suspend** la gate « demander avant d'implémenter » in-scope en la référençant, sans la copier. Une exception déclarée n'est pas un doublon.

### Faux positifs écartés

- « contrat figé » dans `skills/aidd-pilot/actions/02-pipeline.md:28` : autre concept (contrat back verrouillé d'un pipeline), pas la règle de `reasoning.md`.
- `bash -lc` dans les 7 skills vault : commandes d'application (sourcer `$OBSIDIAN_VAULT_PRO`), pas un restatement de `tooling.md`.
- « verdict en tête » dans les gabarits aidd-pilot (`04-doc-ship.md:31`, `governor.md:45`) : application locale du style à un livrable, sans copie du critère.

---

## Captures hors contrat (non creusées)

- L'en-tête d'`ai-principles.md` (« le vault reste la source ») contredit la décision source-de-vérité du 2026-08-10 — déjà relevé dans la grille elle-même.
- Le test C1 de la grille est structurellement approximé pour les règles globales (héritage des règles par les sous-agents) — à réviser entre deux audits.
- `MEMORY.md` auto absent pour ce projet : le sous-domaine « memory auto » est vide, pas défaillant.
- La grille auditée porte des modifications locales non commitées : le prochain rapport devrait tourner contre une grille commitée.
