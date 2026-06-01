"""Industry-standard (2026) retrieval: contextual chunks + hybrid search + rerank.

Pipeline, per current best practice:
  1. Chunk long docs (chunk.py), no overlap.
  2. Contextual Retrieval (Anthropic): prepend the parent's source/date/title to
     each chunk before embedding — a free, deterministic form that captures the
     chunk's situational context (who/when/what).
  3. Hybrid index: dense multilingual vectors (e5-large) + sparse BM25, fused
     with Reciprocal Rank Fusion in Qdrant.
  4. Cross-encoder rerank (bge-reranker-v2-m3, multilingual) for precision.
Embeddings + rerank run locally via fastembed (no API key); vectors live in
Qdrant Cloud. Falls back to local SQLite FTS (kb.py) when Qdrant isn't set.
"""
from __future__ import annotations

import os
import uuid

from .chunk import chunk_text
from .models import Item

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


def search(query: str, limit: int = 12, prefetch: int = 40, per_parent: int = 3) -> list[Item]:
    """Hybrid retrieve -> cross-encoder rerank -> diversified top-k chunks."""
    hits = _client().query(collection_name=COLLECTION, query_text=query, limit=prefetch)
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
