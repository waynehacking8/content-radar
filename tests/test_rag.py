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
