from content_radar import config, watch
from content_radar.collectors import gmail_imap
from content_radar.models import Item


def _newsletter(**over) -> Item:
    base = dict(
        source="gmail",
        id="<ainews-20260602@mail.example.com>",
        title="[AINews] Big model day",
        url="",
        text="AINews <news@smol.ai>: today's recap ...",
        created="Tue, 02 Jun 2026 04:12:00 +0000",
        extra={"newsletter": True},
    )
    base.update(over)
    return Item(**base)


def test_find_unforwarded_returns_the_newest_match(monkeypatch):
    item = _newsletter()
    calls = {}

    def fake_fetch(query, limit, max_chars):
        calls.update(query=query, limit=limit, max_chars=max_chars)
        return [item]

    monkeypatch.setattr(watch.gmail_imap, "fetch", fake_fetch)
    found = watch.find_unforwarded()
    assert found is item
    # only the newest one, fetched in FULL (faithful translation needs the whole body)
    assert calls["limit"] == 1
    assert calls["max_chars"] == gmail_imap.FULL_CHARS
    # the default query is the dedup-aware watch query
    assert calls["query"] == config.ainews_watch_query()


def test_find_unforwarded_returns_none_when_nothing_fresh(monkeypatch):
    monkeypatch.setattr(watch.gmail_imap, "fetch", lambda *a, **k: [])
    assert watch.find_unforwarded() is None


def test_find_unforwarded_honours_query_override(monkeypatch):
    seen = {}
    monkeypatch.setattr(watch.gmail_imap, "fetch",
                        lambda query, limit, max_chars: seen.update(query=query) or [])
    watch.find_unforwarded(query="from:other@list.com newer_than:2d")
    assert seen["query"] == "from:other@list.com newer_than:2d"


def test_pending_count_uses_the_watch_query(monkeypatch):
    seen = {}

    def fake_count(query):
        seen["query"] = query
        return 2

    monkeypatch.setattr(watch.gmail_imap, "search_count", fake_count)
    assert watch.pending_count() == 2
    assert seen["query"] == config.ainews_watch_query()


def test_mark_forwarded_labels_the_original_message(monkeypatch):
    labelled = {}

    def fake_add_label(message_id, label):
        labelled[message_id] = label
        return True

    monkeypatch.setattr(watch.gmail_imap, "add_label", fake_add_label)
    item = _newsletter()
    assert watch.mark_forwarded(item) is True
    assert labelled == {item.id: config.ainews_forwarded_label()}


def test_mark_forwarded_reports_failure(monkeypatch):
    monkeypatch.setattr(watch.gmail_imap, "add_label", lambda *a: False)
    assert watch.mark_forwarded(_newsletter()) is False
