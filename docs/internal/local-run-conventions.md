# Local Run Conventions

This note captures recurring local development patterns across the repos in `~/projects`.

## Common Python App Pattern

Small local web apps often use one of these run styles:

```bash
python app.py
```

or:

```bash
python -m <package-or-module>
```

Common examples:

- `cluster-home`: `python app.py`
- `cluster-lite-wiki`: `python app.py`
- `cluster-query-router`: `python app.py`
- `overlord`: `python app.py`
- `space-cadet`: `python -m space_cadet.app`

## Virtualenv Pattern

Python repos frequently assume a local virtualenv and minimal dependency install:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Some newer repos use editable installs:

```bash
pip install -e .[dev]
```

Some MCP-specific repos use `uv`:

```bash
uv sync
uv run server.py
```

## Browser-First Pattern

Toy/game repos often run directly from static files or a simple Python static server:

```bash
python3 -m http.server 8080
```

or just open `index.html` in a browser.

## Localhost Bias

Most local apps default to loopback and simple ports rather than network exposure.

- `127.0.0.1:8080` is a common default
- local-only tools are usually optimized for fast iteration, not production parity

## Verification Pattern

Common lightweight checks:

- direct local app run
- syntax checks like `python -m py_compile`
- `pytest` or `unittest` when tests exist
- `helm template` when chart changes are involved

The general pattern is: prefer the smallest honest verification step that matches the change.
