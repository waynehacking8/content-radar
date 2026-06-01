import datetime as dt

from content_radar.models import Item
from content_radar.synthesize import _extract_json, build_prompt, write_drafts


def test_extract_json_handles_fenced_blocks():
    raw = '```json\n[{"title": "a", "body": "b"}]\n```'
    out = _extract_json(raw)
    assert out == [{"title": "a", "body": "b"}]


def test_extract_json_ignores_surrounding_prose():
    raw = 'Here are your drafts:\n[{"title": "x"}]\nHope that helps!'
    assert _extract_json(raw) == [{"title": "x"}]


def test_build_prompt_includes_items_and_count():
    items = [Item(source="hackernews", id="1", title="Cool LLM thing", url="http://u", score=99)]
    prompt = build_prompt(items, n_drafts=3, item_limit=10)
    assert "Cool LLM thing" in prompt
    assert "Produce 3 drafts" in prompt


def test_write_drafts_emits_review_ready_files(tmp_path):
    drafts = [
        {"title": "My Hook", "angle": "opinionated-take", "body": "Body text.",
         "tags": ["LLM", "AI"], "source_urls": ["http://u"]},
    ]
    paths = write_drafts(drafts, tmp_path, dt.date(2026, 6, 1))
    assert len(paths) == 1
    content = paths[0].read_text()
    assert "status: draft" in content          # never auto-approved
    assert "platform: linkedin" in content
    assert "publish_date: 2026-06-01" in content
    assert "Body text." in content
