# Engineering Patterns

This note captures recurring engineering and repo-management patterns inferred from the project set and repo guidance files.

## Workflow Style

- Prefer direct implementation over long planning.
- Keep repos easy to run locally with simple commands and minimal setup.
- Favor small, scoped changes over broad rewrites.
- Use Conventional Commits consistently.
- Default to feature branch plus PR, but direct pushes to `main` happen when explicitly approved.

## Tech and Architecture Preferences

- Localhost-first defaults are common.
- Python is heavily used for utilities, dashboards, and local services.
- Flask and FastAPI are common for small web apps.
- Server-rendered HTML is preferred over heavy frontend build systems unless there is a clear need.
- Dependencies are usually kept intentionally light.
- SQLite or file-backed persistence is preferred for local tools.
- MCP-related repos prefer deterministic behavior and stable tool contracts.

## Documentation and Repo Contracts

- `README.md` usually explains what the project is, how to run it locally, and current scope.
- `AGENTS.md` usually contains the stricter engineering contract.
- Repo-local guidance often matters more than generic global guidance.
- Stable repo contracts are treated seriously:
  - MCP tool names and parameter shapes should stay stable
  - chart defaults should remain generic
  - cluster-specific overrides should live in deployment repos rather than app repos

## Deployment and Release Patterns

- Cluster-managed services often ship with Helm charts in the app repo.
- Chart changes usually imply version bumps in `chart/Chart.yaml`.
- ArgoCD repos separate bootstrap/policy from app definitions.
- Changes that affect user-facing cluster behavior should usually be reflected in seeded wiki docs.

## High-Value Heuristics

- For implementation truth, inspect the repo directly.
- For operational conventions, check `AGENTS.md`.
- For cluster work, think in terms of cross-repo coordination rather than isolated repo changes.
