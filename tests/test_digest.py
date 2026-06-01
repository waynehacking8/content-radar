import datetime as dt

from content_radar.digest import (
    build_digest_prompt,
    extract_json_object,
    render_digest_markdown,
    write_digest,
)
from content_radar.models import Item


def test_extract_json_object_handles_fences_and_prose():
    raw = 'Here you go:\n```json\n{"headline": "h", "themes": []}\n```\nthanks'
    assert extract_json_object(raw) == {"headline": "h", "themes": []}


def test_build_digest_prompt_includes_items_and_theme_cap():
    items = [Item(source="hackernews", id="1", title="NVIDIA kernels", url="http://u", score=2410)]
    prompt = build_digest_prompt(items, max_themes=4, item_limit=10)
    assert "NVIDIA kernels" in prompt
    assert "4 or fewer THEMES" in prompt


def test_render_digest_markdown_has_themes_and_top_sections():
    data = {
        "headline": "Open weights kept closing the gap.",
        "themes": [
            {"title": "Local MoE releases",
             "narrative": "StepFun shipped a flash MoE; quants kept shrinking VRAM.",
             "sources": ["http://a", "http://b"]},
        ],
        "top_by_engagement": [
            {"title": "Zai ZCube networking", "url": "http://z", "source": "reddit", "score": 716},
        ],
    }
    md = render_digest_markdown(data, dt.date(2026, 6, 1), {"hackernews": 175, "github": 21})
    assert "# AI Radar — 2026-06-01" in md
    assert "Open weights kept closing the gap." in md
    assert "### Local MoE releases" in md
    assert "Checked github(21), hackernews(175) — 196 items." in md
    assert "## Top by engagement" in md
    assert "[Zai ZCube networking](http://z) — reddit · 716" in md


def test_write_digest_creates_dated_file(tmp_path):
    path = write_digest("# hi", tmp_path, dt.date(2026, 6, 1))
    assert path.name == "digest-2026-06-01.md"
    assert path.read_text() == "# hi"
