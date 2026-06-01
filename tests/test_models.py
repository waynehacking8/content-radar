from content_radar.models import Item


def test_key_is_source_plus_id():
    assert Item(source="x", id="123", title="t", url="u").key == "x:123"


def test_dict_roundtrip_preserves_fields():
    item = Item(source="hackernews", id="7", title="Title", url="http://u",
                text="body", score=42, author="me", created="2026-06-01",
                extra={"comments": 3})
    again = Item.from_dict(item.to_dict())
    assert again == item
