import datetime as dt

from content_radar.chat import build_chat_prompt, relevant_items
from content_radar.models import Item


def _item(id_, title, score=10, text=""):
    return Item(source="hackernews", id=id_, title=title, url=f"http://x/{id_}",
                text=text, score=score)


def test_relevant_items_ranks_by_keyword_overlap():
    nvidia = _item("1", "NVIDIA releases open GPU kernels", score=5)
    rag = _item("2", "A guide to RAG pipelines", score=99)
    items = [rag, nvidia]
    # despite lower score, the NVIDIA item must win for an NVIDIA question
    top = relevant_items(items, "what is new with nvidia gpu?", k=1)
    assert top == [nvidia]


def test_relevant_items_falls_back_to_score_when_no_terms_match():
    a = _item("1", "Cats", score=5)
    b = _item("2", "Dogs", score=50)
    top = relevant_items([a, b], "the and for", k=1)  # only stopwords
    assert top == [b]


def test_build_chat_prompt_includes_question_and_sources():
    items = [_item("1", "NVIDIA news", text="kernels open sourced")]
    prompt = build_chat_prompt("nvidia?", items, "DIGEST TEXT HERE")
    assert "nvidia?" in prompt
    assert "NVIDIA news" in prompt
    assert "DIGEST TEXT HERE" in prompt
    assert "http://x/1" in prompt


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
    assert "Never invent" in prompt


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
