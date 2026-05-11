#!/usr/bin/env python3
import json
import os
import re
import sys
import textwrap
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import format_datetime
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE_TITLE = "Nova Yiting Wu"
SITE_TAGLINE = "Exchange Ideas & Beyond"


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

    cleaned = {}
    for key, value in fields.items():
        cleaned[key] = re.sub(r"\n_No response_\s*$", "", value).strip()
        cleaned[key] = cleaned[key].replace("_No response_", "").strip()
    return cleaned


def value(fields, label, required=True):
    result = fields.get(label, "").strip()
    if required and not result:
        fail(f"Missing required field: {label}")
    return result


def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "journal-entry"


def normalize_slug(date, raw_slug, title_en):
    slug = slugify(raw_slug) if raw_slug else f"{date}-{slugify(title_en)}"
    if not slug.startswith(f"{date}-"):
        slug = f"{date}-{slug}"
    return slug


def parse_topics(raw):
    topics = [item.strip() for item in raw.split(",") if item.strip()]
    if not topics:
        fail("At least one topic is required.")
    return topics


def split_paragraphs(text):
    return [part.strip() for part in re.split(r"\n\s*\n", text.strip()) if part.strip()]


def html_paragraphs(text):
    return "\n".join(f"        <p>{escape(part)}</p>" for part in split_paragraphs(text))


def markdown_paragraphs(text):
    return "\n\n".join(split_paragraphs(text))


def parse_references(raw):
    refs = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = [part.strip() for part in line.split("|")]
        while len(parts) < 6:
            parts.append("")
        creator, title, url, publisher, year, note = parts[:6]
        refs.append({
            "creator": creator,
            "title": title,
            "url": url,
            "publisher": publisher,
            "year": year,
            "note": note,
        })
    return refs


def reference_html(refs):
    if not refs:
        return ""

    items = []
    for ref in refs:
        title = escape(ref["title"] or "Reference")
        title_html = f"<cite>{title}</cite>"
        if ref["url"]:
            title_html = (
                f'<a href="{escape(ref["url"], quote=True)}" target="_blank" rel="noreferrer">'
                f"{title_html}</a>"
            )

        prefix = f'{escape(ref["creator"])}, ' if ref["creator"] else ""
        publisher = f', {escape(ref["publisher"])}' if ref["publisher"] else ""
        year = f', {escape(ref["year"])}' if ref["year"] else ""
        note = f' {escape(ref["note"])}' if ref["note"] else ""
        items.append(f"            <li>{prefix}{title_html}{publisher}{year}.{note}</li>")

    return "\n".join([
        '        <section class="article-references" aria-labelledby="references-title">',
        '          <h2 id="references-title">Appendix / References</h2>',
        "          <ol>",
        *items,
        "          </ol>",
        "        </section>",
    ])


def reference_markdown(refs):
    if not refs:
        return ""

    lines = ["## Appendix / References", ""]
    for index, ref in enumerate(refs, start=1):
        title = ref["title"] or "Reference"
        title_md = f"[*{title}*]({ref['url']})" if ref["url"] else f"*{title}*"
        prefix = f"{ref['creator']}, " if ref["creator"] else ""
        publisher = f", {ref['publisher']}" if ref["publisher"] else ""
        year = f", {ref['year']}" if ref["year"] else ""
        note = f" {ref['note']}" if ref["note"] else ""
        lines.append(f"{index}. {prefix}{title_md}{publisher}{year}.{note}")
    return "\n".join(lines)


def yaml_list(items):
    return "\n".join(f"  - {item}" for item in items)


def topic_meta(topics):
    return " / ".join(topics)


def format_display_date(value):
    dt = datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return dt.strftime("%b %-d, %Y")


def rss_date(value):
    dt = datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return format_datetime(dt)


def build_markdown(data):
    refs_md = reference_markdown(data["references"])
    refs_md_en = refs_md
    if refs_md_en:
        refs_md_en = refs_md_en.replace("## Appendix / References", "## Appendix / References", 1)

    return f"""---
title: {data["title_zh"]}
title_en: {data["title_en"]}
date: {data["date"]}
topics:
{yaml_list(data["topics"])}
summary: {data["summary_zh"]}
summary_en: {data["summary_en"]}
metrics:
  page_view: 0
  share: 0
  agent_use: 0
language_modes:
  - zh-Hans
  - en
agent_prompt: Continue the conversation in a flowing format. Reply with a thoughtful response, one continuation, or one concrete next experiment.
source_issue: {data["issue_url"]}
---

# {data["title_zh"]}

{data["summary_zh"]}

{markdown_paragraphs(data["body_zh"])}

{refs_md}

## English translation

{data["summary_en"]}

{markdown_paragraphs(data["body_en"])}

{refs_md_en}

## Conversation

Future replies can continue here in a flowing format. People and agents are welcome to add a thoughtful response, a continuation, or one concrete next experiment.
"""


def optional_reply_html(data):
    if not data["first_reply_zh"] and not data["first_reply_en"]:
        return ""

    zh_reply = html_paragraphs(data["first_reply_zh"] or "回应待补充。")
    en_reply = html_paragraphs(data["first_reply_en"] or "Reply to be added.")
    return f"""
        <article class="reply-card" id="first-reply">
          <p class="reply-meta">Nova Yiting Wu · {format_display_date(data["date"])}</p>
          <h3 data-lang="zh">第一条回应</h3>
          <h3 data-lang="en" hidden>First reply</h3>
          <div data-lang="zh">
{zh_reply}
          </div>
          <div data-lang="en" hidden>
{en_reply}
          </div>

          <div class="share-panel" data-share-url="#first-reply" data-share-title="Reply to {escape(data["title_zh"], quote=True)}">
            <span>Share this reply</span>
            <button type="button" data-share-action="copy">Link</button>
            <button type="button" data-share-action="email">Email</button>
            <button type="button" data-share-action="qr">QR code</button>
            <output aria-live="polite"></output>
          </div>
        </article>
"""


def build_html(data):
    refs_zh = reference_html(data["references"])
    refs_en = refs_zh.replace('aria-labelledby="references-title"', 'aria-labelledby="references-title-en"', 1)
    refs_en = refs_en.replace('id="references-title"', 'id="references-title-en"', 1)
    reply = optional_reply_html(data)
    display_date = format_display_date(data["date"])
    topics = topic_meta(data["topics"])

    return f"""<!doctype html>
<html lang="zh-Hans">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{escape(data["title_zh"])} · {SITE_TITLE}</title>
    <meta name="description" content="{escape(data["summary_zh"], quote=True)}" />
    <link rel="alternate" type="application/rss+xml" title="{SITE_TITLE} RSS" href="../rss.xml" />
    <link rel="stylesheet" href="../styles.css" />
  </head>
  <body>
    <header class="site-header">
      <a class="brand" href="../index.html" aria-label="{SITE_TITLE} home">
        <span class="brand-mark" aria-hidden="true"></span>
        <span>{SITE_TITLE}</span>
      </a>
      <nav class="nav" aria-label="Primary navigation">
        <a href="../index.html#journal">Journal</a>
        <a href="../index.html#topics">Topics</a>
        <a href="../agent-index.json">Agent Index</a>
        <a href="../index.html#about">About</a>
        <span class="language-switch nav-language-switch" aria-label="Choose reading language">
          <button class="language-option is-active" type="button" data-language-choice="zh" aria-pressed="true">中文原文</button>
          <button class="language-option" type="button" data-language-choice="en" aria-pressed="false">English</button>
        </span>
      </nav>
    </header>

    <main class="article-body" data-article-slug="{data["slug"]}">
      <p class="article-meta">{display_date} · {escape(topics)}</p>

      <h1 data-lang="zh">{escape(data["title_zh"])}</h1>
      <h1 data-lang="en" hidden>{escape(data["title_en"])}</h1>
      <p class="lede" data-lang="zh">{escape(data["summary_zh"])}</p>
      <p class="lede" data-lang="en" hidden>{escape(data["summary_en"])}</p>

      <section class="original-article" id="journal-entry" aria-labelledby="original-title" data-lang="zh">
        <h2 id="original-title">Original Chinese</h2>
{html_paragraphs(data["body_zh"])}

{refs_zh}

        <div class="article-metrics content-metrics" aria-label="Article metrics" data-slug="{data["slug"]}">
          <span>Page View <strong data-metric="pageViews">0</strong></span>
          <span>Share <strong data-metric="shares">0</strong></span>
          <span>Agent Use <strong data-metric="agentUse">0</strong></span>
        </div>

        <div class="share-panel" data-share-url="#journal-entry" data-share-title="{escape(data["title_zh"], quote=True)}">
          <span>Share this journal</span>
          <button type="button" data-share-action="copy">Link</button>
          <button type="button" data-share-action="email">Email</button>
          <button type="button" data-share-action="qr">QR code</button>
          <output aria-live="polite"></output>
        </div>
      </section>

      <section class="translation-box" id="journal-entry-en" aria-labelledby="english-title" data-lang="en" hidden>
        <h2 id="english-title">English translation</h2>
{html_paragraphs(data["body_en"])}

{refs_en}

        <div class="article-metrics content-metrics" aria-label="Article metrics" data-slug="{data["slug"]}">
          <span>Page View <strong data-metric="pageViews">0</strong></span>
          <span>Share <strong data-metric="shares">0</strong></span>
          <span>Agent Use <strong data-metric="agentUse">0</strong></span>
        </div>

        <div class="share-panel" data-share-url="#journal-entry-en" data-share-title="{escape(data["title_en"], quote=True)}">
          <span>Share this journal</span>
          <button type="button" data-share-action="copy">Link</button>
          <button type="button" data-share-action="email">Email</button>
          <button type="button" data-share-action="qr">QR code</button>
          <output aria-live="polite"></output>
        </div>
      </section>

      <section class="conversation-thread" aria-labelledby="conversation-title">
        <div class="conversation-heading">
          <h2 id="conversation-title">Conversation</h2>
          <p data-lang="zh">欢迎朋友和 AI agents 顺着这篇文章继续回应、补充、质疑和延展。</p>
          <p data-lang="en" hidden>Friends and AI agents are welcome to continue this thread with responses, additions, challenges, and extensions.</p>
        </div>
{reply}
        <div class="reply-invite">
          <h3>Continue the thread</h3>
          <p data-lang="zh">未来的回复可以作为新的卡片继续添加在这里。朋友可以用散文式回应；agents 可以留下简短确认、延展，或一个具体的下一步实验。</p>
          <p data-lang="en" hidden>Future replies can be added as new cards here. People can respond in prose; agents can respond with a short acknowledgement, a continuation, or a concrete next experiment.</p>
        </div>
      </section>

      <div class="article-actions">
        <a class="button" href="../index.html">Back to journal</a>
        <button class="share-button" type="button" data-share-title="{escape(data["title_zh"], quote=True)}">Share</button>
        <a class="text-link" href="../content/{data["slug"]}.md">View source note</a>
      </div>

      <div class="qr-modal" id="qr-modal" hidden role="dialog" aria-modal="true" aria-labelledby="qr-title">
        <div class="qr-card">
          <button class="qr-close" type="button" aria-label="Close QR code">×</button>
          <h2 id="qr-title">QR code</h2>
          <img alt="QR code for shared section" />
          <p class="qr-url"></p>
        </div>
      </div>
    </main>

    <script src="../analytics.js"></script>
    <script src="../language.js"></script>
    <script src="../share.js"></script>
  </body>
</html>
"""


def update_index(data):
    path = ROOT / "index.html"
    text = path.read_text()
    match = re.search(r'(<script id="posts-data" type="application/json">\s*)(.*?)(\s*</script>)', text, re.S)
    if not match:
        fail("Could not find posts-data JSON in index.html")

    posts = json.loads(match.group(2))
    post = {
        "slug": data["slug"],
        "title": data["title_zh"],
        "titleEn": data["title_en"],
        "date": data["date"],
        "summary": data["summary_zh"],
        "summaryEn": data["summary_en"],
        "topics": data["topics"],
        "url": f"journal/{data['slug']}.html",
        "metrics": {"pageViews": 0, "shares": 0, "agentUse": 0},
        "conversationPrompt": "Continue the thread with a thoughtful response, one continuation, or one concrete next experiment.",
    }
    posts = [item for item in posts if item.get("slug") != data["slug"]]
    posts.insert(0, post)

    replacement = match.group(1) + textwrap.indent(json.dumps(posts, ensure_ascii=False, indent=2), "      ") + match.group(3)
    path.write_text(text[:match.start()] + replacement + text[match.end():])


def update_agent_index(data):
    path = ROOT / "agent-index.json"
    doc = json.loads(path.read_text())
    article = {
        "slug": data["slug"],
        "title": data["title_zh"],
        "title_en": data["title_en"],
        "date": data["date"],
        "url": f"journal/{data['slug']}.html",
        "source": f"content/{data['slug']}.md",
        "topics": data["topics"],
        "summary": data["summary_zh"],
        "summary_en": data["summary_en"],
        "language_modes": ["zh-Hans", "en"],
        "metrics": {"page_view": 0, "share": 0, "agent_use": 0},
        "references": [
            {key: ref[key] for key in ["creator", "title", "url", "publisher", "year", "note"]}
            for ref in data["references"]
        ],
        "conversation": {
            "format": "flowing thread",
            "invitation": "People and AI agents are welcome to continue the conversation with replies, continuations, or concrete next experiments.",
        },
        "agent_prompt": "Continue the conversation in a flowing format. Reply with a thoughtful response, one continuation, or one concrete next experiment.",
    }
    doc["articles"] = [item for item in doc["articles"] if item.get("slug") != data["slug"]]
    doc["articles"].insert(0, article)
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")


def update_rss(data):
    path = ROOT / "rss.xml"
    tree = ET.parse(path)
    channel = tree.getroot().find("channel")
    channel.find("lastBuildDate").text = rss_date(data["date"])
    link = f"/journal/{data['slug']}.html"

    for item in list(channel.findall("item")):
        guid = item.findtext("guid")
        if guid == link:
            channel.remove(item)

    item = ET.Element("item")
    ET.SubElement(item, "title").text = data["title_zh"]
    ET.SubElement(item, "link").text = link
    ET.SubElement(item, "guid").text = link
    ET.SubElement(item, "pubDate").text = rss_date(data["date"])
    ET.SubElement(item, "description").text = data["summary_zh"]
    channel.insert(4, item)
    ET.indent(tree, space="  ")
    tree.write(path, encoding="unicode", xml_declaration=True)


def update_sitemap(data):
    path = ROOT / "sitemap.xml"
    ET.register_namespace("", "http://www.sitemaps.org/schemas/sitemap/0.9")
    tree = ET.parse(path)
    root = tree.getroot()
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    loc = f"/journal/{data['slug']}.html"

    for url in list(root.findall("sm:url", ns)):
        if url.findtext("sm:loc", namespaces=ns) == loc:
            root.remove(url)

    url = ET.Element("{http://www.sitemaps.org/schemas/sitemap/0.9}url")
    ET.SubElement(url, "{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text = loc
    ET.SubElement(url, "{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod").text = data["date"]
    root.insert(1, url)
    ET.indent(tree, space="  ")
    tree.write(path, encoding="unicode", xml_declaration=True)


def main():
    fields = parse_issue_form(os.environ.get("ISSUE_BODY", ""))
    date = value(fields, "Date")
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        fail("Date must be YYYY-MM-DD.")

    data = {
        "date": date,
        "title_zh": value(fields, "Chinese title"),
        "title_en": value(fields, "English title"),
        "summary_zh": value(fields, "Chinese summary"),
        "summary_en": value(fields, "English summary"),
        "topics": parse_topics(value(fields, "Topics")),
        "body_zh": value(fields, "Chinese body"),
        "body_en": value(fields, "English body"),
        "references": parse_references(value(fields, "References", required=False)),
        "first_reply_zh": value(fields, "First reply in Chinese", required=False),
        "first_reply_en": value(fields, "First reply in English", required=False),
        "issue_url": os.environ.get("ISSUE_URL", ""),
    }
    data["slug"] = normalize_slug(date, value(fields, "Slug", required=False), data["title_en"])

    content_path = ROOT / "content" / f"{data['slug']}.md"
    html_path = ROOT / "journal" / f"{data['slug']}.html"
    content_path.write_text(build_markdown(data))
    html_path.write_text(build_html(data))

    update_index(data)
    update_agent_index(data)
    update_rss(data)
    update_sitemap(data)

    print(f"Published journal: {data['slug']}")


if __name__ == "__main__":
    main()
