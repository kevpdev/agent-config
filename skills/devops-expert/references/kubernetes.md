# Kubernetes

Manifestes minimaux mais complets :

```yaml
# Deployment — éléments critiques
resources:
  requests: { cpu: "100m", memory: "128Mi" }  # toujours définir
  limits:   { cpu: "500m", memory: "512Mi" }
readinessProbe:
  httpGet: { path: /health, port: 3000 }
  initialDelaySeconds: 5
livenessProbe:
  httpGet: { path: /health, port: 3000 }
  initialDelaySeconds: 15
```

Anti-patterns K8s :
- Pas de `latest` comme tag d'image (non-déterministe)
- Pas de `requests` = éviction en cas de pression mémoire
- Pas de `readinessProbe` = traffic envoyé avant que l'app soit prête
- Secrets K8s en base64 ≠ chiffrés — utiliser Sealed Secrets ou External Secrets
