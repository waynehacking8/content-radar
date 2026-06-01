import os

from content_radar import rag


def test_point_id_is_deterministic_and_uuid():
    a = rag.point_id("hackernews:123")
    b = rag.point_id("hackernews:123")
    assert a == b
    assert rag.point_id("hackernews:124") != a
    assert len(a) == 36 and a.count("-") == 4  # uuid format


def test_configured_reflects_env(monkeypatch):
    monkeypatch.delenv("QDRANT_URL", raising=False)
    monkeypatch.delenv("QDRANT_API_KEY", raising=False)
    assert rag.configured() is False
    monkeypatch.setenv("QDRANT_URL", "https://x.qdrant.io")
    monkeypatch.setenv("QDRANT_API_KEY", "k")
    assert rag.configured() is True


def test_index_items_noop_without_config(monkeypatch):
    monkeypatch.delenv("QDRANT_URL", raising=False)
    monkeypatch.delenv("QDRANT_API_KEY", raising=False)
    # must not raise or require qdrant-client when unconfigured
    assert rag.index_items([]) == 0
