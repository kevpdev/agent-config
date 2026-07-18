# Observabilité

Les 3 piliers : **logs + métriques + traces**.

- **Logs** : structurés (JSON), niveau explicite (INFO/WARN/ERROR), pas de données sensibles
- **Métriques** : Prometheus + Grafana, alertes sur SLO (pas sur des seuils arbitraires)
- **Traces** : OpenTelemetry pour les systèmes distribués

Alertes pertinentes (alerter sur les symptômes, pas les causes) :
```
✅ "Taux d'erreur 5xx > 1% pendant 5 min"
❌ "CPU > 80%" (cause, pas symptôme)
```
