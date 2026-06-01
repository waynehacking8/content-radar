"""Industry-standard vector retrieval: local fastembed vectors + Qdrant vector DB.

Embeddings are computed locally with fastembed (BAAI/bge-small, no API key);
vectors live in Qdrant Cloud (free tier, persistent). Dedup/upsert by a stable
UUID derived from the item key, so daily indexing is idempotent. Falls back to
the local SQLite FTS index (kb.py) when Qdrant isn't configured.
"""
from __future__ import annotations

import os
import uuid

from .models import Item

COLLECTION = "radar"
# Multilingual so Traditional-Chinese questions retrieve English sources
# (cross-lingual). Local, free, CI-friendly (ONNX).
EMBED_MODEL = "intfloat/multilingual-e5-large"
_NAMESPACE = uuid.UUID("6f9619ff-8b86-d011-b42d-00cf4fc964ff")


def _creds() -> tuple[str | None, str | None]:
    return os.environ.get("QDRANT_URL"), os.environ.get("QDRANT_API_KEY")


def configured() -> bool:
    url, key = _creds()
    return bool(url and key)


def point_id(key: str) -> str:
    """Stable Qdrant point id from an item key (so re-indexing upserts)."""
    return str(uuid.uuid5(_NAMESPACE, key))


def _client():
    from qdrant_client import QdrantClient

    url, key = _creds()
    client = QdrantClient(url=url, api_key=key)
    client.set_model(EMBED_MODEL)  # fastembed runs locally; only vectors go to cloud
    return client


def index_items(items: list[Item]) -> int:
    if not items or not configured():
        return 0
    docs, metas, ids = [], [], []
    for it in items:
        body = f"{it.title}\n{it.text}".strip()
        if not body:
            continue
        docs.append(body)
        metas.append({
            "key": it.key, "source": it.source, "title": it.title, "url": it.url,
            "score": it.score, "created": it.created, "text": (it.text or "")[:2000],
        })
        ids.append(point_id(it.key))
    if not docs:
        return 0
    _client().add(collection_name=COLLECTION, documents=docs, metadata=metas, ids=ids)
    return len(docs)


def search(query: str, limit: int = 25) -> list[Item]:
    hits = _client().query(collection_name=COLLECTION, query_text=query, limit=limit)
    out: list[Item] = []
    for h in hits:
        m = getattr(h, "metadata", None) or {}
        out.append(Item(
            source=m.get("source", ""),
            id=str(m.get("key", "")).split(":", 1)[-1],
            title=m.get("title", ""),
            url=m.get("url", ""),
            text=m.get("text", ""),
            score=int(m.get("score") or 0),
            created=m.get("created", ""),
        ))
    return out
