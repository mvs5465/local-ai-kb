# Ports And Endpoints

This note captures recurring local ports and endpoint conventions visible across the project set.

## Common Local App Port

`127.0.0.1:8080` is a very common local default for Python web apps and localhost-first tools.

Examples include:

- `cluster-home`
- `cluster-lite-wiki`
- `cluster-query-router`
- `overlord`
- `space-cadet`
- some static-server workflows like `rocket-sim`

## MCP Endpoints

MCP-style services commonly expose streamable HTTP at `/mcp`.

Known local examples:

- `local-ai-kb`: `http://127.0.0.1:8090/mcp`
- `loki-mcp-server`: local default described as streamable HTTP at `/mcp`

## Ollama

The local Ollama default endpoint is:

```text
http://127.0.0.1:11434
```

This is treated as a normal local dependency in model- or embedding-related repos.

## Qdrant

The local AI KB uses native Qdrant with:

- HTTP: `127.0.0.1:6333`
- gRPC: `127.0.0.1:6334`

## Cluster Entry Pattern

The local cluster commonly uses `.lan` hostnames exposed through ingress and local port-forwarding.

A recurring user-facing entrypoint pattern is:

- start the ingress port-forward
- map `127.0.0.1 *.lan` in `/etc/hosts`
- browse to service hostnames like `http://home.lan`

## Heuristic

When uncertain, check for:

- local web UIs on `127.0.0.1:8080`
- MCP endpoints on `/mcp`
- Ollama on `11434`
- cluster app entry through `.lan` hosts
