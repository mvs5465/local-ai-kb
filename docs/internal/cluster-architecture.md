# Cluster Architecture

This note summarizes the recurring local cluster architecture described across the cluster repos.

## Core Split

The cluster is organized around a two-repo control model:

- `local-k8s-argocd`: bootstrap, shared ArgoCD config, AppProject policy, and source repo allowlists
- `local-k8s-apps`: generated child `Application` inputs, organized by sync wave

This split exists to keep bootstrap and policy separate from routine application iteration.

## Sync-Wave Model

`local-k8s-apps` groups applications by wave:

- `wave-0`: foundational ingress and earliest prerequisites
- `wave-1`: platform services like secrets and observability backends
- `wave-2`: higher-level services and user-facing apps

App manifests should not set their own sync-wave annotation because the ApplicationSet derives that from the folder.

## Common Cluster Baseline

The local baseline repeatedly referenced in guidance is:

```bash
colima start --kubernetes --cpu 4 --memory 6 \
  --mount ~/clusterstorage:w \
  --mount ~/.secrets:/mnt/secrets:ro
```

Global durable guidance also mentions a common variant with `--memory 8`.

## Cross-Repo Rules

- If an app sources its chart from a git repo, whitelist that repo in `local-k8s-argocd/manifests/config/appproject.yaml`.
- Do not manually apply child `Application` manifests; ArgoCD generates them from the source repo.
- If cluster workflows or user-facing services change, update `cluster-lite-wiki` seeded docs in the same PR series when practical.

## Core Service Pattern

A common stack appears across the cluster repos:

- ingress
- external secrets
- Grafana / Prometheus / Mimir / Loki / Tempo
- cluster-specific services like `cluster-home`, `cluster-lite-wiki`, `cluster-query-router`, and MCP-backed tools

This is a homelab-style platform with observability and AI/tooling services treated as first-class citizens.
