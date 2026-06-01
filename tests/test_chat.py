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
