# Projects Landscape

This note summarizes the recurring structure visible under `~/projects` as of March 22, 2026.

## Main Repo Groups

### Cluster and homelab

These repos work together as the main local-cluster stack:

- `local-k8s-argocd`: ArgoCD bootstrap, shared policy, and AppProject allowlists
- `local-k8s-apps`: day-to-day ArgoCD `Application` manifests grouped by sync wave
- `cluster-home`: lightweight cluster homepage
- `cluster-lite-wiki`: lightweight seeded wiki for cluster docs
- `cluster-query-router`: deterministic router that maps cluster questions to MCP tools
- `loki-mcp-server`: Loki-backed MCP server for cluster log analysis
- `github-pr-slack-notifier`: GitHub PR to Slack reconciliation service

The cluster repos are the most interconnected and highest-signal group in `~/projects`.

### Localhost-first utilities and experiments

These repos skew toward small, local, fast-iteration tools:

- `macdash-tui`
- `overlord`
- `prompt-tuning`
- `phi4-tool-calling-analysis`
- `spotify-music-dj`
- `space-cadet`

### Browser games and visual sandboxes

These repos are usually plain HTML/JS or lightweight app stacks with direct local runs:

- `rocket-sim`
- `a-game-about-plants`
- `cosmic-simulator`
- `platformer`
- `tgw-simulator`

## Recurring Repo Shapes

- Small single-purpose app repos are common.
- README files usually describe current scope, local run commands, and next targets.
- `AGENTS.md` often carries the real behavioral contract for the repo.
- Cluster-facing service repos often include a `chart/` directory for Helm deployment.
- Localhost-first apps commonly default to `127.0.0.1:8080`.

## Working Assumption

When a task refers to "our repos" or "my projects", start in `~/projects` and prioritize the cluster repos first unless the request clearly points elsewhere.
