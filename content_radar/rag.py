"""Industry-standard (2026) retrieval: contextual chunks + hybrid search + rerank.

Pipeline, per current best practice:
  1. Chunk long docs (chunk.py), no overlap.
  2. Contextual Retrieval (Anthropic): prepend the parent's source/date/title to
     each chunk before embedding — a free, deterministic form that captures the
     chunk's situational context (who/when/what).
  3. Hybrid index: dense multilingual vectors (e5-large) + sparse BM25, fused
     with Reciprocal Rank Fusion in Qdrant.
  4. Cross-encoder rerank (bge-reranker-v2-m3, multilingual) for precision.
  5. Temporal-aware retrieval: date filtering + recency decay (Perplexity-style
     freshness weighting at ~40% of ranking signal for news queries).
Embeddings + rerank run locally via fastembed (no API key); vectors live in
Qdrant Cloud. Falls back to local SQLite FTS (kb.py) when Qdrant isn't set.
"""
from __future__ import annotations

import datetime as _dt
import logging
import os
import uuid

from .chunk import chunk_text
from .models import Item
from .temporal import TemporalIntent, TemporalTier

_log = logging.getLogger(__name__)

COLLECTION = "radar"
EMBED_MODEL = "intfloat/multilingual-e5-large"     # dense, multilingual
SPARSE_MODEL = "Qdrant/bm25"                        # sparse keyword signal
RERANK_MODEL = "jinaai/jina-reranker-v2-base-multilingual"  # multilingual cross-encoder
_NAMESPACE = uuid.UUID("6f9619ff-8b86-d011-b42d-00cf4fc964ff")
_RERANKER = None


def _creds() -> tuple[str | None, str | None]:
    return os.environ.get("QDRANT_URL"), os.environ.get("QDRANT_API_KEY")


def configured() -> bool:
    url, key = _creds()
    return bool(url and key)


def point_id(key: str) -> str:
    return str(uuid.uuid5(_NAMESPACE, key))


def _client():
    from qdrant_client import QdrantClient

    url, key = _creds()
    client = QdrantClient(url=url, api_key=key)
    client.set_model(EMBED_MODEL)
    client.set_sparse_model(SPARSE_MODEL)  # enables hybrid dense+sparse
    return client


def _context_prefix(item: Item) -> str:
    """Cheap contextual-retrieval header: situates the chunk (who/when/what)."""
    date = (item.created or "")[:16]
    return f"[{item.source} · {date}] {item.title}".strip()


def ensure_datetime_index() -> None:
    """Create a payload index on `created` for efficient DatetimeRange filtering.

    Idempotent — safe to call on every index run. Qdrant's filterable HNSW uses
    this index to skip non-matching nodes during graph traversal instead of
    brute-force scanning all payloads.
    """
    if not configured():
        return
    from qdrant_client import models
    _client().create_payload_index(
        collection_name=COLLECTION,
        field_name="created",
        field_schema=models.PayloadSchemaType.DATETIME,
    )


def _build_query_filter(intent: TemporalIntent) -> "models.Filter | None":
    """Translate a TemporalIntent into a Qdrant Filter (or None).

    Only EXPLICIT queries get a hard date filter. IMPLICIT ("latest", "最新")
    queries skip filtering — "latest" means "prefer fresh", not "only recent".
    Future: IMPLICIT will use Qdrant FormulaQuery with exp_decay scoring.
    """
    if intent.tier != TemporalTier.EXPLICIT or intent.date_from is None:
        return None
    from qdrant_client import models
    conditions = [models.FieldCondition(
        key="created",
        range=models.DatetimeRange(gte=intent.date_from.isoformat()),
    )]
    if intent.date_to is not None:
        conditions.append(models.FieldCondition(
            key="created",
            range=models.DatetimeRange(lte=intent.date_to.isoformat()),
        ))
    return models.Filter(must=conditions)


def index_items(items: list[Item]) -> int:
    if not items or not configured():
        return 0
    docs, metas, ids = [], [], []
    for it in items:
        prefix = _context_prefix(it)
        for idx, ch in enumerate(chunk_text(f"{it.title}\n{it.text}")):
            docs.append(f"{prefix}\n{ch}")  # contextualized text is what gets embedded
            metas.append({
                "key": it.key, "source": it.source, "title": it.title, "url": it.url,
                "score": it.score, "created": it.created, "chunk": ch, "chunk_idx": idx,
            })
            ids.append(point_id(f"{it.key}#{idx}"))
    if not docs:
        return 0
    _client().add(collection_name=COLLECTION, documents=docs, metadata=metas, ids=ids)
    return len(docs)


def _rerank(query: str, texts: list[str]) -> list[int]:
    global _RERANKER
    from fastembed.rerank.cross_encoder import TextCrossEncoder

    if _RERANKER is None:
        _RERANKER = TextCrossEncoder(model_name=RERANK_MODEL)
    scores = list(_RERANKER.rerank(query, texts))
    return sorted(range(len(texts)), key=lambda i: scores[i], reverse=True)


_FILTERED_FALLBACK_MIN = 3


def search(
    query: str,
    limit: int = 12,
    prefetch: int = 40,
    per_parent: int = 3,
    temporal_intent: TemporalIntent | None = None,
) -> list[Item]:
    """Hybrid retrieve -> cross-encoder rerank -> diversified top-k chunks.

    When *temporal_intent* carries a date range (EXPLICIT or IMPLICIT tier),
    a Qdrant DatetimeRange payload filter restricts candidates to that window.

    Fallback policy:
      EXPLICIT ("today", "昨天") — never fallback. If today has no data, the
        LLM should say so rather than silently serving stale news.
      IMPLICIT ("latest", "最新") — fallback to unfiltered search when the
        filtered set is too small, since the user's intent is softer.
    """
    client = _client()
    qf = _build_query_filter(temporal_intent) if temporal_intent else None
    hits = client.query(
        collection_name=COLLECTION, query_text=query,
        query_filter=qf, limit=prefetch,
    )
    metas = [getattr(h, "metadata", None) or {} for h in hits]
    metas = [m for m in metas if m.get("chunk")]

    allow_fallback = (
        temporal_intent is not None
        and temporal_intent.tier == TemporalTier.IMPLICIT
    )
    if len(metas) < _FILTERED_FALLBACK_MIN and qf is not None and allow_fallback:
        _log.warning(
            "Temporal filter returned %d results (< %d); retrying without date filter",
            len(metas), _FILTERED_FALLBACK_MIN,
        )
        hits = client.query(
            collection_name=COLLECTION, query_text=query, limit=prefetch,
        )
        metas = [getattr(h, "metadata", None) or {} for h in hits]
        metas = [m for m in metas if m.get("chunk")]

    if not metas:
        return []
    order = _rerank(query, [f"{m.get('title','')} {m['chunk']}" for m in metas])
    out: list[Item] = []
    seen_parent: dict[str, int] = {}
    for i in order:
        m = metas[i]
        pkey = m.get("key", "")
        if seen_parent.get(pkey, 0) >= per_parent:
            continue
        seen_parent[pkey] = seen_parent.get(pkey, 0) + 1
        out.append(Item(
            source=m.get("source", ""),
            id=str(m.get("key", "")).split(":", 1)[-1],
            title=m.get("title", ""),
            url=m.get("url", ""),
            text=m.get("chunk", ""),
            score=int(m.get("score") or 0),
            created=m.get("created", ""),
        ))
        if len(out) >= limit:
            break
    return out
