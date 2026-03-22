PYTHON ?= python3
VENV := .venv
PIP := $(VENV)/bin/pip

.PHONY: run index stop setup eval

run:
	./scripts/run_ollama.sh
	./scripts/run_qdrant.sh
	./scripts/run_mcp.sh

index:
	./scripts/run_ollama.sh
	./scripts/run_qdrant.sh
	./scripts/setup_venv.sh
	PYTHONPATH=src $(VENV)/bin/python -m local_ai_kb.index_docs

stop:
	./scripts/stop.sh

setup:
	./scripts/setup_venv.sh

eval:
	./scripts/run_ollama.sh
	./scripts/run_qdrant.sh
	./scripts/setup_venv.sh
	PYTHONPATH=src $(VENV)/bin/python -m local_ai_kb.eval_search
