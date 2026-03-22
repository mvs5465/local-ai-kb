from __future__ import annotations

from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path
from typing import Iterable

import yaml

from local_ai_kb.config import ROOT_DIR, SOURCES_CONFIG


@dataclass(frozen=True)
class SourceFile:
    path: Path
    source_name: str
    source_type: str


def _expand_path(pattern: str) -> Iterable[Path]:
    if pattern.startswith("~/"):
        path_pattern = Path(pattern).expanduser()
    elif pattern.startswith("/"):
        path_pattern = Path(pattern)
    else:
        path_pattern = ROOT_DIR / pattern

    if any(char in str(path_pattern) for char in "*?[]"):
        yield from sorted(Path("/").glob(str(path_pattern).lstrip("/")))
        return

    if path_pattern.exists():
        yield path_pattern


def _normalize_pattern(pattern: str) -> str:
    if pattern.startswith("~/"):
        return str(Path(pattern).expanduser())
    if pattern.startswith("/"):
        return pattern
    return str((ROOT_DIR / pattern).resolve())


def _matches_any(path: Path, patterns: list[str]) -> bool:
    resolved = str(path.resolve())
    return any(fnmatch(resolved, _normalize_pattern(pattern)) for pattern in patterns)


def iter_source_files() -> list[SourceFile]:
    config = yaml.safe_load(SOURCES_CONFIG.read_text(encoding="utf-8")) or {}
    results: list[SourceFile] = []
    seen: set[Path] = set()

    for source in config.get("sources", []):
        source_name = source["name"]
        source_type = source["source_type"]
        exclude_paths = source.get("exclude_paths", [])
        for pattern in source.get("paths", []):
            for path in _expand_path(pattern):
                resolved_path = path.resolve()
                if (
                    resolved_path.is_dir()
                    or resolved_path.suffix.lower() != ".md"
                    or resolved_path in seen
                    or _matches_any(resolved_path, exclude_paths)
                ):
                    continue
                seen.add(resolved_path)
                results.append(
                    SourceFile(
                        path=resolved_path,
                        source_name=source_name,
                        source_type=source_type,
                    )
                )

    return results
