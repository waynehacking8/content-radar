"""Send the daily digest by email over Gmail SMTP.

Reuses the same free Gmail App Password as the IMAP collector (GMAIL_USER +
GMAIL_APP_PASSWORD) — no paid API. Builds a multipart message (plain-text +
a light HTML rendering of the Markdown) so it reads well in any mail client.
"""
from __future__ import annotations

import re
import smtplib
import ssl
from email.message import EmailMessage

from . import config

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465  # implicit TLS (SMTPS)


def configured() -> bool:
    return bool(config.gmail_user() and config.gmail_app_password())


def _md_to_html(markdown: str) -> str:
    """Tiny, dependency-free Markdown -> HTML for headings/links/lists.

    Intentionally minimal: the digest uses only #/##/### headings, `[t](url)`
    links, `> quote`, `- ` bullets and blank-line paragraphs.
    """
    html_lines: list[str] = []
    in_list = False
    for raw in markdown.splitlines():
        line = raw.rstrip()
        # inline links [text](url) -> <a>
        line_html = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', line)
        # bare <url> angle links -> <a>
        line_html = re.sub(r"&lt;(https?://[^&]+)&gt;", r'<a href="\1">\1</a>', line_html)

        heading = re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            level = len(heading.group(1))
            html_lines.append(f"<h{level}>{heading.group(2)}</h{level}>")
            continue
        if line.startswith("- "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            html_lines.append(f"<li>{line_html[2:]}</li>")
            continue
        if in_list:
            html_lines.append("</ul>")
            in_list = False
        if not line:
            continue
        if line.startswith("> "):
            html_lines.append(f"<blockquote>{line_html[2:]}</blockquote>")
        else:
            html_lines.append(f"<p>{line_html}</p>")
    if in_list:
        html_lines.append("</ul>")
    body = "\n".join(html_lines)
    return (
        '<div style="font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,'
        'sans-serif;max-width:680px;margin:0 auto;line-height:1.6;color:#1a1a1a">'
        f"{body}</div>"
    )


def build_message(subject: str, markdown: str, to_addr: str, from_addr: str) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.set_content(markdown)  # plain-text fallback
    msg.add_alternative(_md_to_html(markdown), subtype="html")
    return msg


def send_markdown_email(subject: str, markdown: str, to_addr: str | None = None) -> str:
    """Send a Markdown digest as an email. Returns the recipient on success."""
    user, password = config.gmail_user(), config.gmail_app_password()
    if not user or not password:
        raise RuntimeError(
            "email needs GMAIL_USER + GMAIL_APP_PASSWORD (the same Gmail App "
            "Password the IMAP collector uses)."
        )
    to_addr = to_addr or config.digest_email_to()
    msg = build_message(subject, markdown, to_addr=to_addr, from_addr=user)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
        server.login(user, password)
        server.send_message(msg)
    return to_addr
