from email.message import EmailMessage

import pytest

from content_radar.collectors import gmail_imap


def test_normalize_preserves_paragraphs_and_collapses_blank_runs():
    raw = "  Title \n\n\n\n  Section A  \nitem 1\nitem 2\n\n\nSection B  "
    out = gmail_imap._normalize(raw)
    # lines trimmed, 3+ blank lines collapsed to one blank line, structure kept
    assert out == "Title\n\nSection A\nitem 1\nitem 2\n\nSection B"


def test_body_text_keeps_newsletter_section_structure():
    msg = EmailMessage()
    html = (
        "<h2>AI Twitter Recap</h2>"
        "<p>Opus 4.8 landed.</p>"
        "<h2>AI Reddit Recap</h2>"
        "<p>StepFun released a MoE.</p>"
        "<script>tracking()</script>"
    )
    msg.set_content("plain fallback")
    msg.add_alternative(html, subtype="html")
    text = gmail_imap._body_text(msg)
    # sections survive as separate lines (not flattened into one blob); script gone
    assert "AI Twitter Recap" in text
    assert "AI Reddit Recap" in text
    assert "tracking()" not in text
    assert "\n" in text  # structure preserved, not space-collapsed


# ── search_count / add_label (the watcher's Gmail-side dedup) ────────────────

class FakeIMAP:
    """Minimal imaplib.IMAP4_SSL stand-in recording calls."""

    # message ids the fake "server" returns for searches; tests override per-case
    search_result: bytes = b"1 2"
    instances: list["FakeIMAP"] = []

    def __init__(self, host):
        self.host = host
        self.calls: list[tuple] = []
        FakeIMAP.instances.append(self)

    def login(self, user, password):
        self.calls.append(("login", user))
        return "OK", [b"Logged in"]

    def select(self, mailbox="INBOX", readonly=False):
        self.calls.append(("select", mailbox, readonly))
        return "OK", [b"1"]

    def search(self, charset, *criteria):
        self.calls.append(("search", charset, *criteria))
        return "OK", [type(self).search_result]

    def store(self, num, command, flags):
        self.calls.append(("store", num, command, flags))
        return "OK", [b""]

    def logout(self):
        self.calls.append(("logout",))
        return "BYE", [b""]


@pytest.fixture
def fake_imap(monkeypatch):
    monkeypatch.setenv("GMAIL_USER", "u@example.com")
    monkeypatch.setenv("GMAIL_APP_PASSWORD", "app-password")
    FakeIMAP.instances = []
    FakeIMAP.search_result = b"1 2"
    monkeypatch.setattr(gmail_imap.imaplib, "IMAP4_SSL", FakeIMAP)
    return FakeIMAP


def test_search_count_counts_matches_without_fetching_bodies(fake_imap):
    fake_imap.search_result = b"4 8 15"
    assert gmail_imap.search_count("subject:AINews newer_than:1d") == 3
    conn = fake_imap.instances[0]
    # gmail-syntax query goes through X-GM-RAW; nothing is fetched
    assert any(c[0] == "search" and "X-GM-RAW" in c for c in conn.calls)
    assert not any(c[0] == "fetch" for c in conn.calls)
    assert conn.calls[-1] == ("logout",)


def test_search_count_returns_zero_when_no_match(fake_imap):
    fake_imap.search_result = b""
    assert gmail_imap.search_count("subject:AINews") == 0


def test_search_count_returns_zero_without_credentials(monkeypatch):
    monkeypatch.delenv("GMAIL_USER", raising=False)
    monkeypatch.delenv("GMAIL_APP_PASSWORD", raising=False)
    assert gmail_imap.search_count("subject:AINews") == 0


def test_add_label_stores_gmail_label_on_matching_message(fake_imap):
    fake_imap.search_result = b"7"
    ok = gmail_imap.add_label("<ainews@mail.example.com>", "radar-forwarded")
    assert ok is True
    conn = fake_imap.instances[0]
    # found via the Message-ID header, then labelled with the Gmail extension
    assert ("search", None, "HEADER", "Message-ID", '"<ainews@mail.example.com>"') in conn.calls
    assert ("store", b"7", "+X-GM-LABELS", '("radar-forwarded")') in conn.calls


def test_add_label_returns_false_when_message_not_found(fake_imap):
    fake_imap.search_result = b""
    assert gmail_imap.add_label("<missing@mail.example.com>", "radar-forwarded") is False
    conn = fake_imap.instances[0]
    assert not any(c[0] == "store" for c in conn.calls)


def test_add_label_returns_false_when_store_is_rejected(fake_imap, monkeypatch):
    """A rejected STORE means the dedup marker is NOT in place — must report False."""
    fake_imap.search_result = b"7"
    monkeypatch.setattr(FakeIMAP, "store",
                        lambda self, num, cmd, flags: ("NO", [b"label rejected"]))
    assert gmail_imap.add_label("<ainews@mail.example.com>", "radar-forwarded") is False


def test_connection_is_closed_even_when_search_raises(fake_imap, monkeypatch):
    def boom(self, charset, *criteria):
        raise OSError("network dropped")

    monkeypatch.setattr(FakeIMAP, "search", boom)
    assert gmail_imap.search_count("subject:AINews") == 0
    conn = fake_imap.instances[0]
    assert conn.calls[-1] == ("logout",)  # _session always logs out


def test_add_label_returns_false_without_credentials(monkeypatch):
    monkeypatch.delenv("GMAIL_USER", raising=False)
    monkeypatch.delenv("GMAIL_APP_PASSWORD", raising=False)
    assert gmail_imap.add_label("<x@y>", "radar-forwarded") is False
