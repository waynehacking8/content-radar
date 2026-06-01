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


def _inline(text: str) -> str:
    """Inline Markdown -> HTML: links, then **bold** and *italic*."""
    # [text](url) -> <a>, and bare <url> angle links -> <a>
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"&lt;(https?://[^&]+)&gt;", r'<a href="\1">\1</a>', text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)  # bold before italic
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", text)
    return text


def _md_to_html(markdown: str) -> str:
    """Tiny, dependency-free Markdown -> HTML for the newsletter shape:
    #..###### headings, `---` rules, `[t](url)`/`<url>` links, **bold**, *italic*,
    `> quote`, `- ` bullets, and blank-line paragraphs.
    """
    html_lines: list[str] = []
    in_list = False
    for raw in markdown.splitlines():
        line = raw.rstrip()

        heading = re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            level = len(heading.group(1))
            html_lines.append(f"<h{level}>{_inline(heading.group(2))}</h{level}>")
            continue
        if re.fullmatch(r"-{3,}|\*{3,}|_{3,}", line.strip()):  # horizontal rule
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append("<hr>")
            continue
        if line.startswith("- "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            html_lines.append(f"<li>{_inline(line[2:])}</li>")
            continue
        if in_list:
            html_lines.append("</ul>")
            in_list = False
        if not line:
            continue
        if line.startswith("> "):
            html_lines.append(f"<blockquote>{_inline(line[2:])}</blockquote>")
        else:
            html_lines.append(f"<p>{_inline(line)}</p>")
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
