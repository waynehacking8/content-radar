import datetime as dt

from content_radar.digest import pick_best_digest
from content_radar.enrich import _should_enrich
from content_radar.models import Item


def _item(url="https://example.com/a", text="", source="hackernews"):
    return Item(source=source, id="1", title="t", url=url, text=text, score=10)


def test_should_enrich_skips_items_with_long_text():
    assert _should_enrich(_item(text="x" * 700)) is False
    assert _should_enrich(_item(text="short")) is True


def test_should_enrich_skips_listing_hosts_and_empty_urls():
    assert _should_enrich(_item(url="https://news.ycombinator.com/item?id=1")) is False
    assert _should_enrich(_item(url="")) is False
    assert _should_enrich(_item(url="https://a-real-article.com/post")) is True


def test_pick_best_with_single_candidate_skips_the_judge():
    only = {"headline": "h", "themes": []}
    # one candidate must short-circuit (no model call)
    assert pick_best_digest([only], model="sonnet") is only
