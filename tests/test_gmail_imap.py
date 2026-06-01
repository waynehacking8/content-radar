from email.message import EmailMessage

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
