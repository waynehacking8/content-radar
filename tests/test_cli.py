from content_radar import cli
from content_radar.models import Item


def _newsletter() -> Item:
    return Item(
        source="gmail",
        id="<ainews-20260602@mail.example.com>",
        title="[AINews] Big model day",
        url="",
        text="AINews <news@smol.ai>: today's full recap body",
        created="Tue, 02 Jun 2026 04:12:00 +0000",
        extra={"newsletter": True},
    )


# ── check-ainews ─────────────────────────────────────────────────────────────

def test_check_ainews_writes_found_true_to_github_output(monkeypatch, tmp_path, capsys):
    gh_out = tmp_path / "github_output"
    monkeypatch.setenv("GITHUB_OUTPUT", str(gh_out))
    monkeypatch.setattr("content_radar.watch.pending_count", lambda query=None: 1)

    cli.main(["check-ainews"])

    assert "found=true" in gh_out.read_text(encoding="utf-8")
    assert "found=true" in capsys.readouterr().out


def test_check_ainews_writes_found_false_when_nothing_pending(monkeypatch, tmp_path, capsys):
    gh_out = tmp_path / "github_output"
    monkeypatch.setenv("GITHUB_OUTPUT", str(gh_out))
    monkeypatch.setattr("content_radar.watch.pending_count", lambda query=None: 0)

    cli.main(["check-ainews"])

    assert "found=false" in gh_out.read_text(encoding="utf-8")
    assert "found=false" in capsys.readouterr().out


def test_check_ainews_works_without_github_output(monkeypatch, capsys):
    monkeypatch.delenv("GITHUB_OUTPUT", raising=False)
    monkeypatch.setattr("content_radar.watch.pending_count", lambda query=None: 1)

    cli.main(["check-ainews"])  # must not raise

    assert "found=true" in capsys.readouterr().out


# ── email-digest --if-new ────────────────────────────────────────────────────

def _allow_sending(monkeypatch):
    monkeypatch.setattr("content_radar.mailer.configured", lambda: True)


def test_email_digest_if_new_exits_quietly_when_nothing_new(monkeypatch, capsys):
    _allow_sending(monkeypatch)
    monkeypatch.setattr("content_radar.watch.find_unforwarded", lambda query=None, max_chars=None: None)
    sent = []
    monkeypatch.setattr("content_radar.mailer.send_markdown_email",
                        lambda *a, **k: sent.append(a))

    cli.main(["email-digest", "--if-new"])  # exit 0, no SystemExit

    assert sent == []
    assert "nothing to do" in capsys.readouterr().out


def test_email_digest_if_new_translates_sends_marks_and_indexes(monkeypatch, capsys):
    _allow_sending(monkeypatch)
    item = _newsletter()
    events = []

    monkeypatch.setattr("content_radar.watch.find_unforwarded", lambda query=None, max_chars=None: item)
    monkeypatch.setattr("content_radar.digest.chinese_newsletter_markdown",
                        lambda body, model: events.append("translate") or "# 中文內容")
    monkeypatch.setattr("content_radar.mailer.send_markdown_email",
                        lambda subject, md, to_addr=None: events.append(("send", subject)) or "to@x.com")
    monkeypatch.setattr("content_radar.watch.mark_forwarded",
                        lambda it: events.append("mark") or True)
    monkeypatch.setattr("content_radar.rag.configured", lambda: True)
    monkeypatch.setattr("content_radar.rag.ensure_datetime_index", lambda: None)
    monkeypatch.setattr("content_radar.rag.index_items",
                        lambda items: events.append(("index", [it.id for it in items])) or 3)

    cli.main(["email-digest", "--if-new", "--index"])

    from content_radar import config
    assert events[0] == "translate"
    assert events[1] == ("send", config.forwarded_subject(item.title))
    # dedup label is applied only AFTER a successful send
    assert events[2] == "mark"
    assert events[3] == ("index", [item.id])


def test_email_digest_if_new_does_not_mark_when_send_fails(monkeypatch):
    """The dedup label must only be applied AFTER a successful send, so a failed
    run is retried by the next poll instead of being silently swallowed."""
    _allow_sending(monkeypatch)
    item = _newsletter()

    monkeypatch.setattr("content_radar.watch.find_unforwarded",
                        lambda query=None, max_chars=None: item)
    monkeypatch.setattr("content_radar.digest.chinese_newsletter_markdown",
                        lambda body, model: "# 中文內容")

    def smtp_blows_up(subject, md, to_addr=None):
        raise RuntimeError("SMTP connection refused")

    monkeypatch.setattr("content_radar.mailer.send_markdown_email", smtp_blows_up)
    monkeypatch.setattr("content_radar.watch.mark_forwarded",
                        lambda it: (_ for _ in ()).throw(
                            AssertionError("must NOT label when the send failed")))

    import pytest
    with pytest.raises(RuntimeError, match="SMTP"):
        cli.main(["email-digest", "--if-new"])


def test_email_digest_if_new_skips_index_when_qdrant_unconfigured(monkeypatch, capsys):
    _allow_sending(monkeypatch)
    item = _newsletter()

    monkeypatch.setattr("content_radar.watch.find_unforwarded", lambda query=None, max_chars=None: item)
    monkeypatch.setattr("content_radar.digest.chinese_newsletter_markdown",
                        lambda body, model: "# 中文內容")
    monkeypatch.setattr("content_radar.mailer.send_markdown_email",
                        lambda subject, md, to_addr=None: "to@x.com")
    monkeypatch.setattr("content_radar.watch.mark_forwarded", lambda it: True)
    monkeypatch.setattr("content_radar.rag.configured", lambda: False)
    monkeypatch.setattr("content_radar.rag.index_items",
                        lambda items: (_ for _ in ()).throw(AssertionError("must not index")))

    cli.main(["email-digest", "--if-new", "--index"])  # must not raise

    assert "skipping index" in capsys.readouterr().out


def test_email_digest_plain_mode_still_works(monkeypatch, capsys):
    """Backward compat: without --if-new, behaviour is unchanged (no dedup, no label)."""
    _allow_sending(monkeypatch)
    item = _newsletter()

    monkeypatch.setattr("content_radar.collectors.gmail_imap.fetch",
                        lambda query, limit, max_chars: [item])
    monkeypatch.setattr("content_radar.digest.chinese_newsletter_markdown",
                        lambda body, model: "# 中文內容")
    sent = {}
    monkeypatch.setattr("content_radar.mailer.send_markdown_email",
                        lambda subject, md, to_addr=None: sent.setdefault("subject", subject) or "to@x.com")
    monkeypatch.setattr("content_radar.watch.mark_forwarded",
                        lambda it: (_ for _ in ()).throw(AssertionError("plain mode must not label")))

    cli.main(["email-digest"])

    from content_radar import config
    assert sent["subject"] == config.forwarded_subject(item.title)
