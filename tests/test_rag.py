import datetime as dt
import os

from content_radar import rag
from content_radar.temporal import TemporalIntent, TemporalTier


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


def test_build_query_filter_none_for_non_temporal():
    intent = TemporalIntent(tier=TemporalTier.NONE)
    assert rag._build_query_filter(intent) is None


def test_build_query_filter_explicit_has_gte():
    start = dt.datetime(2026, 6, 4, 0, 0, tzinfo=dt.timezone.utc)
    end = dt.datetime(2026, 6, 4, 10, 0, tzinfo=dt.timezone.utc)
    intent = TemporalIntent(tier=TemporalTier.EXPLICIT, date_from=start, date_to=end)
    qf = rag._build_query_filter(intent)
    assert qf is not None
    assert len(qf.must) == 2
    assert "2026-06-04" in str(qf.must[0].range.gte)


def test_build_query_filter_implicit_has_range():
    start = dt.datetime(2026, 6, 1, 0, 0, tzinfo=dt.timezone.utc)
    end = dt.datetime(2026, 6, 4, 10, 0, tzinfo=dt.timezone.utc)
    intent = TemporalIntent(tier=TemporalTier.IMPLICIT, date_from=start, date_to=end)
    qf = rag._build_query_filter(intent)
    assert qf is not None
    assert len(qf.must) == 2


def test_ensure_datetime_index_noop_without_config(monkeypatch):
    monkeypatch.delenv("QDRANT_URL", raising=False)
    monkeypatch.delenv("QDRANT_API_KEY", raising=False)
    rag.ensure_datetime_index()  # must not raise


def _make_fake_client(call_count):
    class FakeHit:
        metadata = {"chunk": "stuff", "key": "hn:1", "title": "Item",
                     "source": "hackernews", "url": "", "score": 10,
                     "created": "2026-06-01", "chunk_idx": 0}

    class FakeClient:
        def query(self, collection_name, query_text, query_filter=None, limit=10):
            call_count["n"] += 1
            if query_filter is not None:
                return []
            return [FakeHit()] * 5

    return FakeClient()


def test_explicit_temporal_does_not_fallback_to_unfiltered(monkeypatch):
    """When user asks 'today's news' but nothing was collected today,
    the search must return empty — NOT silently serve stale items."""
    call_count = {"n": 0}
    monkeypatch.setenv("QDRANT_URL", "https://x.qdrant.io")
    monkeypatch.setenv("QDRANT_API_KEY", "k")
    monkeypatch.setattr(rag, "_client", lambda: _make_fake_client(call_count))
    monkeypatch.setattr(rag, "_rerank", lambda q, texts: list(range(len(texts))))

    start = dt.datetime(2026, 6, 4, 0, 0, tzinfo=dt.timezone.utc)
    end = dt.datetime(2026, 6, 4, 10, 0, tzinfo=dt.timezone.utc)
    explicit = TemporalIntent(tier=TemporalTier.EXPLICIT, date_from=start, date_to=end)
    result = rag.search("AI news", temporal_intent=explicit)

    assert result == []
    assert call_count["n"] == 1  # only the filtered call, no fallback


def test_implicit_temporal_falls_back_when_few_results(monkeypatch):
    """IMPLICIT queries ('latest') should fallback to unfiltered if too few results."""
    call_count = {"n": 0}
    monkeypatch.setenv("QDRANT_URL", "https://x.qdrant.io")
    monkeypatch.setenv("QDRANT_API_KEY", "k")
    monkeypatch.setattr(rag, "_client", lambda: _make_fake_client(call_count))
    monkeypatch.setattr(rag, "_rerank", lambda q, texts: list(range(len(texts))))

    start = dt.datetime(2026, 6, 1, 0, 0, tzinfo=dt.timezone.utc)
    end = dt.datetime(2026, 6, 4, 10, 0, tzinfo=dt.timezone.utc)
    implicit = TemporalIntent(tier=TemporalTier.IMPLICIT, date_from=start, date_to=end)
    result = rag.search("AI news", temporal_intent=implicit)

    assert len(result) > 0
    assert call_count["n"] == 2  # filtered + fallback
