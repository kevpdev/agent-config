# INSTALL.md : installer le kit

Fichier pour l'humain, non lu par l'agent pendant une tâche (B4). Le kit est un seul dossier de fichiers Markdown, sans variante par outil : on le copie, on le symlinke ou on le zippe tel quel.

## Statut des informations

Trois points sont **doc-vérifiés le 2026-10-02** sur la page « Agent Skills » de la documentation d'Anthropic (platform.claude.com, overview). Ils sont marqués ✔ ci-dessous. Tout le reste vient de la synthèse de conception et reste **à vérifier** dans la documentation de chaque outil.

- ✔ `name` : 64 caractères au plus, minuscules, chiffres et tirets. `description` : 1 024 caractères au plus.
- ✔ Les skills ne se synchronisent pas entre claude.ai, l'API et Claude Code. Chaque surface s'installe séparément.
- ✔ Sur l'API, un skill tourne sans accès réseau. Sur claude.ai, l'accès réseau dépend des réglages. Sur Claude Code, l'accès réseau est celui de la machine.

## Environnements

| Environnement | Installation | Conséquences pour le kit |
|---|---|---|
| Claude Code | source unique dans `agent-config/skills/research-kit/`, et lien `~/.claude/skills/research-kit` vers ce dossier | tout fonctionne, y compris `check_claims.py --en-ligne` |
| claude.ai (web) | envoi d'un zip du dossier dans les réglages, exécution de code activée ✔ | `--en-ligne` dépend des réglages réseau. Sans réseau, « sources : à la main » |
| API | envoi par l'API des skills ✔ | ni recherche web ni `--en-ligne` ✔ : le kit dégrade tout en *Non vérifié* et le déclare |
| App mobile Claude | déclenchement des skills non confirmé. Plan B : coller `lite.md` dans les instructions d'un projet | à tester |
| Codex | `~/.agents/skills/` ou `.agents/skills/`, plus un pointeur de quelques lignes dans le fichier d'instructions personnel | emplacement à vérifier selon la version |
| Grok Build | skills et fichier d'instructions pris en charge | emplacement à vérifier avec la commande d'inspection de l'outil |

## Principe de maintenance

Une seule source de vérité, `agent-config/skills/research-kit/`, versionnée avec le reste du dépôt. Chaque outil y pointe par lien symbolique quand il lit le disque, ou reçoit un zip du dossier quand il ne le lit pas. Après une modification, rejouer :

```bash
python3 scripts/tests/test_check_claims.py            # 21 cas hors ligne
python3 scripts/tests/test_check_claims.py --reseau   # + 3 cas en ligne
```

Les sous-agents et les hooks diffèrent d'un outil à l'autre : le kit n'en dépend pas, et ne les utilise que s'ils existent.

## Après l'installation

1. Vérifier que le déclenchement fonctionne : poser une question de recherche et contrôler que l'agent lit `guardrails.md` et annonce un niveau de garantie.
2. Passer la batterie de `tests-adverses.md` et remplir la matrice de conformité.
3. Noter ses questions réelles pendant une à deux semaines, les classer par verbe et par domaine pour vérifier le « 80 % » visé, puis ajouter des lentilles ou des profils selon l'usage.
