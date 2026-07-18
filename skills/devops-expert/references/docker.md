# Docker

**Multi-stage = obligatoire** pour toute image non-triviale.

```dockerfile
# Builder stage — contient les outils de build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Runtime stage — image minimale
FROM node:20-alpine AS runtime
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
USER node                          # jamais root en prod
EXPOSE 3000
CMD ["node", "dist/main.js"]
```

Checklist image :
- Base image alpine ou distroless (taille)
- `USER non-root` en prod
- `.dockerignore` exhaustif (node_modules, .git, .env)
- `HEALTHCHECK` défini
- Pas de secrets dans les layers (même supprimés — ils restent dans l'historique)
