import datetime as dt

import content_radar.chat as chat_mod
from content_radar.chat import _filter_by_date, build_chat_prompt, recent_digests
from content_radar.models import Item
from content_radar.temporal import TemporalIntent, TemporalTier


def test_recent_digests_prefers_live_http(monkeypatch, tmp_path):
    # local disk has an OLD digest; HTTP returns today's -> HTTP wins
    (tmp_path / "digest-2026-05-01.md").write_text("OLD LOCAL", encoding="utf-8")
    monkeypatch.setattr(chat_mod, "_fetch_url",
                        lambda url, timeout=4: "LIVE TODAY" if "2026-06-01" in url else None)
    out = recent_digests(tmp_path, n=2, raw_base="http://repo/digests",
                         today=dt.date(2026, 6, 1))
    assert "LIVE TODAY" in out
    assert "OLD LOCAL" not in out


def test_recent_digests_falls_back_to_disk_when_http_unreachable(monkeypatch, tmp_path):
    (tmp_path / "digest-2026-06-01.md").write_text("DISK COPY", encoding="utf-8")
    monkeypatch.setattr(chat_mod, "_fetch_url", lambda url, timeout=4: None)  # all 404/offline
    out = recent_digests(tmp_path, n=2, raw_base="http://repo/digests",
                         today=dt.date(2026, 6, 1))
    assert out == "DISK COPY"


def test_recent_digests_uses_disk_when_raw_base_disabled(tmp_path):
    (tmp_path / "digest-2026-06-01.md").write_text("DISK ONLY", encoding="utf-8")
    out = recent_digests(tmp_path, n=1, raw_base="")  # HTTP disabled
    assert out == "DISK ONLY"


def _item(id_, title, score=10, text=""):
    return Item(source="hackernews", id=id_, title=title, url=f"http://x/{id_}",
                text=text, score=score)


def test_build_chat_prompt_includes_question_and_sources():
    items = [_item("1", "NVIDIA news", text="kernels open sourced")]
    prompt = build_chat_prompt("nvidia?", items, "DIGEST TEXT HERE",
                               today=dt.date(2026, 6, 4))
    assert "nvidia?" in prompt
    assert "NVIDIA news" in prompt
    assert "DIGEST TEXT HERE" in prompt
    assert "http://x/1" in prompt


def test_build_chat_prompt_injects_today_date():
    prompt = build_chat_prompt("q", [], "", today=dt.date(2026, 6, 4))
    assert "Today is 2026-06-04 (UTC)" in prompt


def test_build_chat_prompt_kb_only_does_not_invite_web_search():
    items = [_item("1", "NVIDIA news", text="kernels")]
    prompt = build_chat_prompt("nvidia?", items, "DIGEST", web_fallback=False)
    assert "WebSearch" not in prompt
    assert "say so rather than guessing" in prompt


def test_build_chat_prompt_web_fallback_invites_web_search_with_attribution():
    items = [_item("1", "NVIDIA news", text="kernels")]
    prompt = build_chat_prompt("nvidia?", items, "DIGEST", web_fallback=True)
    # prefers KB but allows the tool, and demands sourced facts (no invention)
    assert "WebSearch" in prompt
    assert "Prefer the retrieved context" in prompt
    assert "never state a fact you cannot source" in prompt


def test_answer_passes_websearch_tool_only_when_web_fallback(monkeypatch):
    import content_radar.chat as chat_mod

    captured = {}

    def fake_run(prompt, model, timeout=300, allowed_tools=None):
        captured["timeout"] = timeout
        captured["allowed_tools"] = allowed_tools
        return "ok"

    monkeypatch.setattr(chat_mod, "run_claude_cli", fake_run)
    monkeypatch.setattr(chat_mod.rag, "configured", lambda: False)
    monkeypatch.setattr(chat_mod.kb, "get_index", lambda _d: object())
    monkeypatch.setattr(chat_mod.kb, "search", lambda _i, _q, limit=12: [])
    monkeypatch.setattr(chat_mod, "recent_digests", lambda _d, n=2: "")

    chat_mod.answer("q", web_fallback=True)
    assert captured["allowed_tools"] == ["WebSearch"]
    assert captured["timeout"] == 420

    chat_mod.answer("q", web_fallback=False)
    assert captured["allowed_tools"] is None
    assert captured["timeout"] == 300


def test_answer_passes_temporal_intent_to_rag(monkeypatch):
    captured = {}

    def fake_rag_search(query, limit=12, temporal_intent=None, **kw):
        captured["temporal_intent"] = temporal_intent
        return []

    monkeypatch.setattr(chat_mod, "run_claude_cli",
                        lambda p, m, timeout=300, allowed_tools=None: "ok")
    monkeypatch.setattr(chat_mod.rag, "configured", lambda: True)
    monkeypatch.setattr(chat_mod.rag, "search", fake_rag_search)
    monkeypatch.setattr(chat_mod, "recent_digests", lambda _d, n=2: "")

    chat_mod.answer("今天的AI新聞", web_fallback=False)
    intent = captured["temporal_intent"]
    assert intent is not None
    assert intent.tier == TemporalTier.EXPLICIT


def test_filter_by_date_keeps_matching_items():
    today_item = _item("1", "Today news", text="fresh")
    today_item = Item(**{**today_item.to_dict(), "created": "2026-06-06T10:00:00Z"})
    old_item = _item("2", "Old news", text="stale")
    old_item = Item(**{**old_item.to_dict(), "created": "2026-06-03T10:00:00Z"})

    intent = TemporalIntent(
        tier=TemporalTier.EXPLICIT,
        date_from=dt.datetime(2026, 6, 6, 0, 0, tzinfo=dt.timezone.utc),
        date_to=dt.datetime(2026, 6, 6, 23, 59, tzinfo=dt.timezone.utc),
    )
    filtered = _filter_by_date([today_item, old_item], intent)
    assert len(filtered) == 1
    assert filtered[0].title == "Today news"


def test_filter_by_date_drops_items_without_created():
    no_date = _item("1", "No date", text="missing")
    intent = TemporalIntent(
        tier=TemporalTier.EXPLICIT,
        date_from=dt.datetime(2026, 6, 6, 0, 0, tzinfo=dt.timezone.utc),
        date_to=dt.datetime(2026, 6, 6, 23, 59, tzinfo=dt.timezone.utc),
    )
    filtered = _filter_by_date([no_date], intent)
    assert len(filtered) == 0


def test_answer_kb_path_filters_by_date(monkeypatch):
    captured = {}

    old_item = Item(source="hn", id="1", title="Old", url="http://x/1",
                    text="old stuff", score=99, created="2026-06-01T10:00:00Z")

    def fake_run(prompt, model, timeout=300, allowed_tools=None):
        captured["prompt"] = prompt
        return "ok"

    monkeypatch.setattr(chat_mod, "run_claude_cli", fake_run)
    monkeypatch.setattr(chat_mod.rag, "configured", lambda: False)
    monkeypatch.setattr(chat_mod.kb, "get_index", lambda _d: object())
    monkeypatch.setattr(chat_mod.kb, "search", lambda _i, _q, limit=12: [old_item])
    monkeypatch.setattr(chat_mod, "recent_digests", lambda _d, n=2: "")

    chat_mod.answer("今天的AI新聞", web_fallback=False)
    assert "Old" not in captured["prompt"]
    assert "CRITICAL DATE CONSTRAINT" in captured["prompt"]


def test_build_chat_prompt_explicit_temporal_no_items():
    intent = TemporalIntent(
        tier=TemporalTier.EXPLICIT,
        date_from=dt.datetime(2026, 6, 6, 0, 0, tzinfo=dt.timezone.utc),
    )
    prompt = build_chat_prompt("今日AI新聞?", [], "old digest content",
                               today=dt.date(2026, 6, 6), temporal_intent=intent)
    assert "CRITICAL DATE CONSTRAINT" in prompt
    assert "2026-06-06" in prompt
    assert "RECENT DIGEST" in prompt
    assert "TODAY'S DIGEST" not in prompt


def test_build_chat_prompt_explicit_temporal_with_items():
    intent = TemporalIntent(
        tier=TemporalTier.EXPLICIT,
        date_from=dt.datetime(2026, 6, 6, 0, 0, tzinfo=dt.timezone.utc),
    )
    items = [_item("1", "Fresh news", text="breaking")]
    prompt = build_chat_prompt("今日AI新聞?", items, "digest",
                               today=dt.date(2026, 6, 6), temporal_intent=intent)
    assert "DATE CONSTRAINT" in prompt
    assert "ONLY discuss items whose date tag matches" in prompt
