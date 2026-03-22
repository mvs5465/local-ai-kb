from __future__ import annotations

from pathlib import Path
import sys

import yaml

from local_ai_kb.config import ROOT_DIR
from local_ai_kb.embedding import embed_texts
from local_ai_kb.qdrant_store import search


def main() -> int:
    config_path = ROOT_DIR / "evals" / "search_cases.yaml"
    cases = (yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}).get("cases", [])
    passed = 0

    for case in cases:
        query = case["query"]
        expected_any = case["expected_any"]
        top_k = int(case.get("top_k", 3))
        embedding = embed_texts([query])[0]
        results = search(query=query, embedding=embedding, limit=max(top_k, 5))
        top_paths = [item.path for item in results[:top_k]]
        ok = any(expected in top_paths for expected in expected_any)
        status = "PASS" if ok else "FAIL"
        print(f"{status}: {query}")
        print(f"  top_paths: {top_paths}")
        if ok:
            passed += 1

    total = len(cases)
    print(f"\nSummary: {passed}/{total} passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
