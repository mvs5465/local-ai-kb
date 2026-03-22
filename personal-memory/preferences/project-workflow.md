# Project Workflow Preferences

This note captures stable workflow preferences inferred from global and repo-local guidance.

## Repo Discovery

- Start in `~/projects` by default for "our repos" or "my projects".
- Prioritize the cluster repos first for infrastructure and cluster questions.

## Git and PR Behavior

- Prefer `gh` for GitHub operations.
- Use Conventional Commits for commit messages and PR titles.
- Default to feature branches and PRs.
- Do not merge or push to protected/default branches without explicit approval, unless the user has explicitly changed that expectation for the current repo or task.

## How To Work In Repos

- Read repo-local `AGENTS.md` or `CLAUDE.md` before major work.
- Prefer direct repo inspection over assumptions.
- Prefer `rg` for search.
- Avoid heavy build tooling or unnecessary dependencies in small apps.
- Keep changes small and pragmatic.

## Local-App Bias

- Prefer localhost-first operation.
- Prefer simple local run paths.
- Prefer server-rendered UI and file- or SQLite-backed persistence unless there is a strong reason not to.

## Cluster-Specific Bias

- Treat `local-k8s-argocd` as the bootstrap/policy repo.
- Treat `local-k8s-apps` as the routine application-definition repo.
- Prefer explicit, deterministic behavior over opaque agent behavior in cluster tooling and MCP surfaces.
