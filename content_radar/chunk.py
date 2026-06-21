"""Document chunking for retrieval.

Long documents (newsletters like AINews) embed poorly as one vector and lose
detail when truncated, so we split them into sentence-aware passages — each gets
its own embedding, with a small ~10-15% overlap (CHUNK_OVERLAP) so a fact split
across a passage boundary still lands whole in at least one chunk. The parent's
title + date are prepended at index time (rag.py) as a cheap, free form of
Anthropic's Contextual Retrieval.
"""
from __future__ import annotations

CHUNK_SIZE = 1200      # ~300 tokens — fits e5-large's 512-token window with contextual prefix
CHUNK_OVERLAP = 150    # ~10-15% overlap to preserve context across boundaries


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    text = " ".join((text or "").split())
    if not text:
        return []
    if len(text) <= size:
        return [text]
    chunks: list[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + size, n)
        if end < n:
            # prefer a sentence boundary, else a word boundary, in the back half
            dot = text.rfind(". ", start + size // 2, end)
            brk = dot + 1 if dot != -1 else text.rfind(" ", start + size // 2, end)
            if brk != -1 and brk > start:
                end = brk
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= n:
            break
        start = max(end - overlap, start + 1)
    return chunks
