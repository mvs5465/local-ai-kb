# Which Repo To Edit

This note is a practical routing guide for choosing the right repo before making changes.

## Cluster Changes

Edit `local-k8s-argocd` when the change is about:

- ArgoCD bootstrap
- root applications
- AppProject policy
- allowed source repos
- cluster-wide bootstrap behavior

Edit `local-k8s-apps` when the change is about:

- child `Application` manifests
- sync-wave placement
- app wiring
- cluster-facing Helm overrides
- enabling or disabling a deployed service

Edit the service repo itself when the change is about:

- application behavior
- UI
- backend logic
- chart defaults owned by the service
- MCP tool behavior

Common service repos:

- `cluster-home`
- `cluster-lite-wiki`
- `cluster-query-router`
- `loki-mcp-server`
- `overlord`

## Docs Changes

Edit `cluster-lite-wiki` seeded docs when:

- cluster routes or user-facing services changed
- a workflow that new users depend on changed
- a cluster behavior change should be reflected in first-boot docs

## Local Tooling And Research

Edit `prompt-tuning` or `phi4-tool-calling-analysis` when the work is about:

- model behavior experiments
- tool-calling reliability
- prompt evaluation harnesses
- model comparison rather than product behavior

Edit `local-ai-kb` when the work is about:

- local knowledge ingestion
- personal durable memory
- MCP search over your own docs and notes

## Quick Rule

Before editing:

1. decide whether the change is bootstrap, wiring, implementation, or docs
2. pick the repo that owns that layer
3. check adjacent repos only if the change crosses boundaries
