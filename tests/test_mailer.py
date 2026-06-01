from content_radar import mailer


def test_md_to_html_renders_headings_links_and_lists():
    md = "# Title\n\n> lede line\n\n## Themes\n\n- [Anthropic ships](http://x/1) news\n- plain item"
    html = mailer._md_to_html(md)
    assert "<h1>Title</h1>" in html
    assert "<h2>Themes</h2>" in html
    assert "<blockquote>lede line</blockquote>" in html
    assert '<a href="http://x/1">Anthropic ships</a>' in html
    assert "<ul>" in html and "<li>plain item</li>" in html and "</ul>" in html


def test_md_to_html_renders_bold_italic_and_rules():
    md = "**Opus 4.8** landed\n\n*5 月 30 日*\n\n---\n\n### #### sub"
    html = mailer._md_to_html(md)
    assert "<strong>Opus 4.8</strong>" in html
    assert "<em>5 月 30 日</em>" in html
    assert "<hr>" in html
    # literal asterisks must not survive into the HTML body
    assert "**" not in html
    # bold inside a heading is converted too
    h = mailer._md_to_html("## **重點** 章節")
    assert "<h2><strong>重點</strong> 章節</h2>" in h


def test_build_message_is_multipart_plain_and_html():
    msg = mailer.build_message("Subj", "# Hi\n\nbody", to_addr="a@b.com", from_addr="c@d.com")
    assert msg["Subject"] == "Subj"
    assert msg["To"] == "a@b.com"
    assert msg["From"] == "c@d.com"
    types = {part.get_content_type() for part in msg.walk()}
    assert "text/plain" in types
    assert "text/html" in types


def test_send_markdown_email_requires_credentials(monkeypatch):
    monkeypatch.setattr(mailer.config, "gmail_user", lambda: None)
    monkeypatch.setattr(mailer.config, "gmail_app_password", lambda: None)
    try:
        mailer.send_markdown_email("s", "b")
        assert False, "expected RuntimeError when credentials are missing"
    except RuntimeError as exc:
        assert "GMAIL_USER" in str(exc)


def test_send_markdown_email_logs_in_and_sends(monkeypatch):
    sent = {}

    class FakeSMTP:
        def __init__(self, host, port, context=None):
            sent["host"], sent["port"] = host, port

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def login(self, user, password):
            sent["login"] = (user, password)

        def send_message(self, msg):
            sent["to"] = msg["To"]
            sent["from"] = msg["From"]

    monkeypatch.setattr(mailer.config, "gmail_user", lambda: "me@gmail.com")
    monkeypatch.setattr(mailer.config, "gmail_app_password", lambda: "app-pw")
    monkeypatch.setattr(mailer.smtplib, "SMTP_SSL", FakeSMTP)

    to = mailer.send_markdown_email("Subj", "# body", to_addr="you@gmail.com")
    assert to == "you@gmail.com"
    assert sent["login"] == ("me@gmail.com", "app-pw")
    assert sent["to"] == "you@gmail.com"
    assert sent["from"] == "me@gmail.com"
    assert sent["host"] == mailer.SMTP_HOST
