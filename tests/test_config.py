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
