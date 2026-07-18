# CI/CD

Pipeline en 3 phases : **build → test → deploy**. Chaque phase doit être indépendante et cacheable.

Bonnes pratiques :
- Fail fast : lint + typecheck avant les tests lourds
- Cache agressif : dépendances, layers Docker, artefacts de build
- Secrets jamais dans le code — variables CI protégées ou vault
- Un pipeline par environnement (dev/staging/prod), pas de `if branch == main`
- Artifacts versionnés : tag = version, jamais `latest` en prod

```yaml
# GitLab CI — structure type
stages: [lint, test, build, deploy]

lint:
  stage: lint
  cache:
    key: $CI_COMMIT_REF_SLUG
    paths: [node_modules/]
  script: [npm ci, npm run lint, npm run typecheck]

build:
  stage: build
  script: [docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .]
  only: [main, tags]
```
