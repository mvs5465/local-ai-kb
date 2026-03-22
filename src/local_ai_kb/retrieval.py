from __future__ import annotations

import math
import re
from dataclasses import dataclass
from datetime import datetime, timezone


TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9-]+")
CAMEL_RE_1 = re.compile(r"([a-z0-9])([A-Z])")
CAMEL_RE_2 = re.compile(r"([A-Z]+)([A-Z][a-z])")
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "do",
    "for",
    "from",
    "how",
    "i",
    "in",
    "is",
    "it",
    "local",
    "my",
    "of",
    "on",
    "or",
    "repo",
    "should",
    "that",
    "the",
    "to",
    "usually",
    "what",
    "which",
}

SOURCE_TYPE_BOOSTS = {
    "personal_memory": 0.16,
    "internal_guidance": 0.12,
    "internal_docs": 0.06,
    "external_reference": 0.0,
}


@dataclass(frozen=True)
class RankedResult:
    score: float
    raw_score: float
    path: str
    source_type: str
    source_name: str
    heading: str
    text: str
    confidence: float
    canonical: bool
    modified_at: str


def _tokenize(text: str) -> set[str]:
    text = CAMEL_RE_2.sub(r"\1 \2", text)
    text = CAMEL_RE_1.sub(r"\1 \2", text)
    text = text.replace("_", " ").replace("/", " ").replace(".", " ")
    return {
        token
        for token in TOKEN_RE.findall(text.lower())
        if token not in STOPWORDS and len(token) > 1
    }


def _overlap_score(query_tokens: set[str], value: str, weight: float) -> float:
    if not query_tokens:
        return 0.0
    tokens = _tokenize(value)
    if not tokens:
        return 0.0
    overlap = len(query_tokens & tokens) / len(query_tokens)
    return overlap * weight


def _curation_boost(path: str, source_type: str) -> float:
    if source_type == "personal_memory":
        return 0.12
    if path.startswith("projects/local-ai-kb/docs/internal/"):
        return 0.18
    if path.startswith("projects/local-ai-kb/personal-memory/"):
        return 0.22
    return 0.0


def _freshness_boost(modified_at: str) -> float:
    if not modified_at:
        return 0.0
    try:
        modified = datetime.fromisoformat(modified_at)
    except ValueError:
        return 0.0
    if modified.tzinfo is None:
        modified = modified.replace(tzinfo=timezone.utc)
    age_days = max((datetime.now(timezone.utc) - modified).days, 0)
    if age_days <= 14:
        return 0.08
    if age_days <= 60:
        return 0.04
    if age_days <= 180:
        return 0.02
    return 0.0


def _query_shape_boost(query_tokens: set[str], path: str, heading: str) -> float:
    joined = f"{path} {heading}".lower()
    boost = 0.0
    if {"repo", "edit"} & query_tokens and "which-repo-to-edit" in joined:
        boost += 0.18
    if {"port", "endpoint", "endpoints"} & query_tokens and "ports-and-endpoints" in joined:
        boost += 0.18
    if {"workflow", "preferences"} & query_tokens and "project-workflow" in joined:
        boost += 0.18
    if {"landscape", "groups"} & query_tokens and "projects-landscape" in joined:
        boost += 0.18
    if {"architecture", "argocd", "wave"} & query_tokens and "cluster-architecture" in joined:
        boost += 0.18
    if {"run", "locally"} & query_tokens and "local-run-conventions" in joined:
        boost += 0.18
    if {"dependency", "dependencies", "related"} & query_tokens and "repo-dependency-map" in joined:
        boost += 0.18
    if {"appproject", "source", "repos"} <= query_tokens and (
        "cluster-architecture" in joined or "which-repo-to-edit" in joined
    ):
        boost += 0.22
    if {"sync", "wave"} <= query_tokens and (
        "cluster-architecture" in joined or "which-repo-to-edit" in joined
    ):
        boost += 0.18
    return boost


def rerank_results(query: str, hits: list[dict], limit: int) -> list[RankedResult]:
    query_tokens = _tokenize(query)
    ranked: list[RankedResult] = []

    for hit in hits:
        raw_score = float(hit["score"])
        score = raw_score
        score += SOURCE_TYPE_BOOSTS.get(hit["source_type"], 0.0)
        score += min(max(float(hit.get("confidence", 0.7)) - 0.7, 0.0), 0.3) * 0.4
        score += 0.05 if hit.get("canonical", False) else 0.0
        score += _freshness_boost(hit.get("modified_at", ""))
        score += _curation_boost(hit["path"], hit["source_type"])
        score += _overlap_score(query_tokens, hit["heading"], 0.32)
        score += _overlap_score(query_tokens, hit["path"], 0.22)
        score += _overlap_score(query_tokens, hit["text"][:800], 0.18)
        score += _query_shape_boost(query_tokens, hit["path"], hit["heading"])

        ranked.append(
            RankedResult(
                score=score,
                raw_score=raw_score,
                path=hit["path"],
                source_type=hit["source_type"],
                source_name=hit.get("source_name", ""),
                heading=hit["heading"],
                text=hit["text"],
                confidence=float(hit.get("confidence", 0.7)),
                canonical=bool(hit.get("canonical", False)),
                modified_at=hit.get("modified_at", ""),
            )
        )

    ranked.sort(
        key=lambda item: (
            item.score,
            item.raw_score,
            -math.log(max(len(item.text), 50)),
        ),
        reverse=True,
    )

    selected: list[RankedResult] = []
    seen_pairs: set[tuple[str, str]] = set()
    seen_paths: set[str] = set()
    for item in ranked:
        pair = (item.path, item.heading)
        if pair in seen_pairs:
            continue
        if item.path in seen_paths:
            continue
        seen_pairs.add(pair)
        seen_paths.add(item.path)
        selected.append(item)
        if len(selected) >= limit:
            break

    return selected


def format_snippet(text: str, limit: int = 320) -> str:
    collapsed = " ".join(text.split())
    if len(collapsed) <= limit:
        return collapsed
    return collapsed[: limit - 3].rstrip() + "..."
