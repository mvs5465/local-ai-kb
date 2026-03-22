# Repo Dependency Map

This note captures high-value repo relationships that show up repeatedly in guidance and README files.

## Cluster Core Relationships

### `local-k8s-argocd` -> `local-k8s-apps`

- `local-k8s-argocd` owns bootstrap, shared ArgoCD config, and AppProject policy
- `local-k8s-apps` owns routine child `Application` manifests
- If an application sources its chart from a git repo, `local-k8s-argocd` must whitelist that repo URL in `manifests/config/appproject.yaml`

### `local-k8s-apps` -> service repos

Service repos often contain the actual app/chart source, while `local-k8s-apps` points ArgoCD at them.

Examples:

- `cluster-home`
- `cluster-lite-wiki`
- `cluster-query-router`
- `loki-mcp-server`

### Cluster docs coupling

If cluster workflows, services, routes, or user-facing behavior change, seeded docs in `cluster-lite-wiki` often need a companion update.

## MCP and AI Tooling Relationships

### `cluster-query-router` -> MCP services

`cluster-query-router` depends conceptually on MCP services such as Loki and Prometheus endpoints and uses a small local model only for summarization.

### `loki-mcp-server` -> `local-k8s-apps`

`loki-mcp-server` ships the MCP server and chart, while the ArgoCD app wiring lives in `local-k8s-apps`.

### `local-ai-kb` -> local knowledge sources

`local-ai-kb` is a personal knowledge layer that indexes source files from `~/projects` plus local curated memory.

## Pattern To Remember

In the cluster ecosystem, changing one repo often implies a check in at least one adjacent repo:

- bootstrap/policy question -> `local-k8s-argocd`
- app wiring / sync-wave / values question -> `local-k8s-apps`
- app implementation question -> service repo
- docs/update onboarding question -> `cluster-lite-wiki`
