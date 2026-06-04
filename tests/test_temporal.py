import datetime as dt

from content_radar.temporal import TemporalIntent, TemporalTier, detect_temporal_intent

NOW = dt.datetime(2026, 6, 4, 10, 0, 0, tzinfo=dt.timezone.utc)


def test_explicit_today_chinese():
    intent = detect_temporal_intent("今天的AI新聞", now=NOW)
    assert intent.tier == TemporalTier.EXPLICIT
    assert intent.date_from == dt.datetime(2026, 6, 4, 0, 0, tzinfo=dt.timezone.utc)
    assert intent.date_to == NOW


def test_explicit_today_english():
    intent = detect_temporal_intent("what's today's AI news?", now=NOW)
    assert intent.tier == TemporalTier.EXPLICIT
    assert intent.date_from.day == 4


def test_explicit_yesterday():
    intent = detect_temporal_intent("昨天有什麼新聞", now=NOW)
    assert intent.tier == TemporalTier.EXPLICIT
    assert intent.date_from == dt.datetime(2026, 6, 3, 0, 0, tzinfo=dt.timezone.utc)


def test_explicit_this_week():
    intent = detect_temporal_intent("this week in AI", now=NOW)
    assert intent.tier == TemporalTier.EXPLICIT
    assert intent.date_from == dt.datetime(2026, 5, 28, 0, 0, tzinfo=dt.timezone.utc)


def test_implicit_latest():
    intent = detect_temporal_intent("latest trends in AI agents", now=NOW)
    assert intent.tier == TemporalTier.IMPLICIT
    assert intent.date_from is not None


def test_implicit_chinese():
    intent = detect_temporal_intent("最新的LLM消息", now=NOW)
    assert intent.tier == TemporalTier.IMPLICIT


def test_none_for_explanatory():
    intent = detect_temporal_intent("explain transformer architecture", now=NOW)
    assert intent.tier == TemporalTier.NONE
    assert intent.date_from is None
    assert intent.date_to is None


def test_none_for_topical():
    intent = detect_temporal_intent("what is CUDA", now=NOW)
    assert intent.tier == TemporalTier.NONE


def test_explicit_takes_precedence_over_implicit():
    intent = detect_temporal_intent("today's latest AI news", now=NOW)
    assert intent.tier == TemporalTier.EXPLICIT


def test_case_insensitive():
    intent = detect_temporal_intent("TODAY in AI", now=NOW)
    assert intent.tier == TemporalTier.EXPLICIT


def test_whitespace_normalization():
    intent = detect_temporal_intent("  今天   的新聞  ", now=NOW)
    assert intent.tier == TemporalTier.EXPLICIT
