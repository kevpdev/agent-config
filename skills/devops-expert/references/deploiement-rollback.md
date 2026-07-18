# Déploiement & rollback

| Stratégie | Quand | Risque |
|---|---|---|
| Rolling update | Default K8s, zéro downtime | Version mixte pendant déploiement |
| Blue-Green | Prod critique, rollback instantané | Double infra coût |
| Canary | Validation progressive sur % trafic | Complexité routing |
| Recreate | Dev/staging, downtime acceptable | Interruption de service |

**Rollback** : toujours tester le rollback avant la mise en prod. `kubectl rollout undo` fonctionne si l'image précédente est toujours dans le registry.
