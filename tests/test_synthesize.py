import datetime as dt

from content_radar.models import Item
from content_radar import synthesize
from content_radar.synthesize import _extract_json, _result_text, build_prompt, write_drafts


def test_run_claude_cli_always_constrains_tools(monkeypatch):
    captured = {}

    class FakeProc:
        returncode = 0
        stdout = '{"result": "ok"}'
        stderr = ""

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd
        return FakeProc()

    monkeypatch.setattr(synthesize.subprocess, "run", fake_run)

    # no tools requested -> still passes --allowedTools with an empty value
    synthesize.run_claude_cli("hi", "sonnet")
    cmd = captured["cmd"]
    assert "--allowedTools" in cmd
    assert cmd[cmd.index("--allowedTools") + 1] == ""

    # WebSearch requested -> passes it through
    synthesize.run_claude_cli("hi", "sonnet", allowed_tools=["WebSearch"])
    cmd = captured["cmd"]
    assert cmd[cmd.index("--allowedTools") + 1] == "WebSearch"


def test_result_text_recovers_result_from_stream_json():
    # if the CLI ever emits stream-json (one object per line), still recover result
    stream = '{"type":"assistant","message":{}}\n{"type":"result","result":"final answer"}'
    assert _result_text(stream) == "final answer"


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
