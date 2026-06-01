import datetime as dt

from content_radar.models import Item
from content_radar.store import load_day, merge, save_day


def _item(source, id_, score):
    return Item(source=source, id=id_, title=f"{source}-{id_}", url="http://x", score=score)


def test_merge_dedups_by_key_keeping_higher_score():
    a = _item("hackernews", "1", 10)
    a_better = _item("hackernews", "1", 50)
    b = _item("arxiv", "2", 0)
    merged = merge([a, b], [a_better])
    assert len(merged) == 2
    hn = next(i for i in merged if i.key == "hackernews:1")
    assert hn.score == 50


def test_merge_sorts_by_score_desc():
    merged = merge([], [_item("a", "1", 5), _item("b", "2", 99), _item("c", "3", 50)])
    assert [i.score for i in merged] == [99, 50, 5]


def test_save_and_load_roundtrip_is_idempotent(tmp_path):
    day = dt.date(2026, 6, 1)
    save_day(tmp_path, day, [_item("hackernews", "1", 10), _item("reddit", "9", 80)])
    # re-running the same day must not duplicate
    save_day(tmp_path, day, [_item("hackernews", "1", 10)])
    loaded = load_day(tmp_path, day)
    assert len(loaded) == 2
    assert {i.key for i in loaded} == {"hackernews:1", "reddit:9"}
