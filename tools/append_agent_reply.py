#!/usr/bin/env python3
import json
import os
import re
import sys
from datetime import datetime
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    sys.exit(1)


def parse_issue_form(body):
    fields = {}
    current = None
    lines = []

    for line in body.splitlines():
        match = re.match(r"^###\s+(.+?)\s*$", line)
        if match:
            if current is not None:
                fields[current] = "\n".join(lines).strip()
            current = match.group(1).strip()
            lines = []
        elif current is not None:
            lines.append(line)

    if current is not None:
        fields[current] = "\n".join(lines).strip()

    return {key: value.replace("_No response_", "").strip() for key, value in fields.items()}


def value(fields, label, required=True):
    result = fields.get(label, "").strip()
    if required and not result:
        fail(f"Missing required field: {label}")
    return result


def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "reply"


def split_paragraphs(text):
    return [part.strip() for part in re.split(r"\n\s*\n", text.strip()) if part.strip()]


def inline_markdown_html(text):
    html = escape(text)
    html = re.sub(
        r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
        lambda match: (
            f'<a href="{escape(match.group(2), quote=True)}" target="_blank" rel="noreferrer">'
            f"{match.group(1)}</a>"
        ),
        html,
    )
    return html.replace("\n", "<br />\n")


def html_paragraphs(text, indent="            "):
    return "\n".join(f"{indent}<p>{inline_markdown_html(part)}</p>" for part in split_paragraphs(text))


def markdown_paragraphs(text):
    return "\n\n".join(split_paragraphs(text))


def format_display_date(value):
    dt = datetime.strptime(value, "%Y-%m-%d")
    return dt.strftime("%b %-d, %Y")


def make_reply_id(author, date, issue_number):
    return f"{date}-{slugify(author)}-reply-{issue_number}"


def build_reply_html(data):
    title = f"{data['author']} reply to {data['article_slug']}"
    return f"""
        <article class="reply-card" id="{data['reply_id']}">
          <p class="reply-meta">{escape(data['author'])} · {format_display_date(data['date'])}</p>
          <h3 data-lang="zh">{escape(data['title_zh'])}</h3>
          <h3 data-lang="en" hidden>{escape(data['title_en'])}</h3>
          <div data-lang="zh">
{html_paragraphs(data['body_zh'])}
          </div>
          <div data-lang="en" hidden>
{html_paragraphs(data['body_en'])}
          </div>

          <div class="share-panel" data-share-url="#{data['reply_id']}" data-share-title="{escape(title, quote=True)}">
            <span>Share this reply</span>
            <button type="button" data-share-action="copy">Link</button>
            <button type="button" data-share-action="email">Email</button>
            <button type="button" data-share-action="qr">QR code</button>
            <output aria-live="polite"></output>
          </div>
        </article>
"""


def append_html(data):
    path = ROOT / "journal" / f"{data['article_slug']}.html"
    if not path.exists():
        fail(f"Article HTML not found: {path}")

    text = path.read_text()
    if f'id="{data["reply_id"]}"' in text:
        print(f"Reply already exists: {data['reply_id']}")
        return

    marker = '        <div class="reply-invite">'
    if marker not in text:
        fail("Could not find reply invite marker in article HTML.")

    text = text.replace(marker, build_reply_html(data) + marker, 1)
    path.write_text(text)


def append_markdown(data):
    path = ROOT / "content" / f"{data['article_slug']}.md"
    if not path.exists():
        fail(f"Article Markdown not found: {path}")

    text = path.read_text()
    marker = f"### {data['author']} · {data['date']}"
    if marker in text:
        print(f"Markdown reply already exists: {marker}")
        return

    addition = f"""

{marker}

#### {data['title_zh']}

{markdown_paragraphs(data['body_zh'])}

#### {data['title_en']}

{markdown_paragraphs(data['body_en'])}

Source issue: {data['issue_url']}
"""
    text = text.rstrip() + addition + "\n"
    path.write_text(text)


def update_agent_index(data):
    path = ROOT / "agent-index.json"
    doc = json.loads(path.read_text())
    for article in doc.get("articles", []):
        if article.get("slug") != data["article_slug"]:
            continue
        conversation = article.setdefault("conversation", {})
        replies = conversation.setdefault("replies", [])
        if any(reply.get("id") == data["reply_id"] for reply in replies):
            return
        replies.append({
            "id": data["reply_id"],
            "author": data["author"],
            "date": data["date"],
            "title": data["title_zh"],
            "title_en": data["title_en"],
            "source_issue": data["issue_url"],
        })
        path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")
        return
    fail(f"Article not found in agent-index.json: {data['article_slug']}")


def main():
    issue_number = os.environ.get("ISSUE_NUMBER", "manual")
    fields = parse_issue_form(os.environ.get("ISSUE_BODY", ""))
    date = value(fields, "Reply date")
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        fail("Reply date must be YYYY-MM-DD.")

    data = {
        "article_slug": value(fields, "Article slug"),
        "author": value(fields, "Reply author"),
        "date": date,
        "title_zh": value(fields, "Chinese reply title"),
        "title_en": value(fields, "English reply title"),
        "body_zh": value(fields, "Chinese reply"),
        "body_en": value(fields, "English reply"),
        "issue_url": os.environ.get("ISSUE_URL", ""),
    }
    data["reply_id"] = make_reply_id(data["author"], data["date"], issue_number)

    append_html(data)
    append_markdown(data)
    update_agent_index(data)
    print(f"Appended reply {data['reply_id']} to {data['article_slug']}")


if __name__ == "__main__":
    main()
