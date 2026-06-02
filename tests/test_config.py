import pytest

from content_radar import config


@pytest.mark.parametrize("value", ["1", "true", "yes", "on", "TRUE", "anything"])
def test_web_fallback_enabled_when_truthy(monkeypatch, value):
    monkeypatch.setenv("WEB_FALLBACK", value)
    assert config.web_fallback_enabled() is True


@pytest.mark.parametrize("value", ["0", "false", "no", "FALSE", "  ", ""])
def test_web_fallback_disabled_when_falsy_or_blank(monkeypatch, value):
    monkeypatch.setenv("WEB_FALLBACK", value)
    assert config.web_fallback_enabled() is False


def test_web_fallback_defaults_on_when_unset(monkeypatch):
    monkeypatch.delenv("WEB_FALLBACK", raising=False)
    assert config.web_fallback_enabled() is True


# ── AINews watcher config ────────────────────────────────────────────────────

def test_ainews_watch_query_is_fresh_and_dedup_aware_by_default(monkeypatch):
    monkeypatch.delenv("AINEWS_WATCH_QUERY", raising=False)
    monkeypatch.delenv("AINEWS_FORWARDED_LABEL", raising=False)
    q = config.ainews_watch_query()
    assert "subject:AINews" in q
    assert "newer_than:1d" in q                       # only today's issue, never a stale one
    assert f"-label:{config.DEFAULT_AINEWS_FORWARDED_LABEL}" in q  # skip already-forwarded


def test_ainews_watch_query_env_override(monkeypatch):
    monkeypatch.setenv("AINEWS_WATCH_QUERY", "from:news@other.com newer_than:2d")
    assert config.ainews_watch_query() == "from:news@other.com newer_than:2d"


def test_ainews_forwarded_label_env_override(monkeypatch):
    monkeypatch.setenv("AINEWS_FORWARDED_LABEL", "my-label")
    assert config.ainews_forwarded_label() == "my-label"
    monkeypatch.delenv("AINEWS_FORWARDED_LABEL", raising=False)
    assert config.ainews_forwarded_label() == config.DEFAULT_AINEWS_FORWARDED_LABEL


def test_forwarded_subject_appends_the_chinese_suffix():
    assert config.forwarded_subject("[AINews] X") == f"[AINews] X{config.ZH_SUBJECT_SUFFIX}"
