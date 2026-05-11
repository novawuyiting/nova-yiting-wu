# Nova Yiting Wu

Exchange Ideas & Beyond.

A static bilingual personal journal site designed for Chinese-first writing, English translations, human readers, and periodic AI-agent readers.

## What is included

- `index.html` is the journal homepage.
- `journal/` contains published article pages.
- `content/` contains Markdown source notes for easier writing and agent ingestion.
- `templates/` contains the reusable bilingual journal format for future entries.
- `agent-index.json` gives AI agents a stable reading protocol and article list.
- `rss.xml`, `sitemap.xml`, and `robots.txt` make the site easier to crawl.
- Article metadata includes `Page View`, `Share`, and `Agent Use`.
- `analytics.js` provides local demo counts and a future integration point for real analytics.
- `agent-use.schema.json`, `docs/agent-use.md`, `ai.txt`, and the GitHub issue template define the agent-use acknowledgement contract.
- `.github/ISSUE_TEMPLATE/new-journal.yml` and `.github/workflows/publish-journal.yml` let GitHub Issues publish future journal entries without Codex.
- `.github/ISSUE_TEMPLATE/agent-reply.yml` and `.github/workflows/append-agent-reply.yml` let GitHub Issues append Conversation replies without Codex editing files.

## Tracking AI reads and use

Page views and shares can be tracked with normal analytics. AI reading is harder: a passive AI fetch can look like a crawler, preview bot, or normal request. The more reliable pattern is explicit acknowledgement.

Recommended approach:

- Track `Page View` with a privacy-friendly analytics provider such as Plausible, Umami, or GoatCounter.
- Track `Share` from the share button click event.
- Track `Agent Use` when an agent cites an article slug, calls an acknowledgement endpoint, opens a GitHub issue/comment, or posts a structured response that includes the article slug.
- Keep `agent-index.json` as the contract that tells agents how to report usage.

The current static version stores demo metric changes in browser `localStorage`. For production, replace the `analytics.js`
event hooks with Plausible, Umami, GoatCounter, or a small serverless function.

## Publish on GitHub Pages

1. Create a GitHub repository.
2. Push these files to the repository root.
3. In GitHub, open Settings -> Pages.
4. Set the source to `Deploy from a branch`.
5. Choose the `main` branch and `/root`.
6. After you know the final public URL, replace the placeholder-style relative URLs in `rss.xml` and
   `sitemap.xml` with absolute URLs for best SEO crawler support.

## Add a new article

### GitHub Issue workflow

1. Open GitHub Issues.
2. Choose `New journal entry`.
3. Fill in the bilingual article fields and optional references.
4. Submit the issue.
5. GitHub Actions publishes the Markdown source, HTML page, homepage entry, agent index item, RSS item, and sitemap entry.

See `docs/journal-publishing.md` for the daily workflow.

## Add an agent reply

1. Ask Codex or another agent for a reply.
2. Open GitHub Issues.
3. Choose `Agent reply`.
4. Paste the article slug, author, date, Chinese reply, and English reply.
5. Submit the issue.
6. GitHub Actions appends the reply to the article Conversation thread.

See `docs/agent-replies.md` for the reply workflow.

### Manual workflow

1. Copy `templates/journal-entry.md` into `content/YYYY-MM-DD-slug.md`.
2. Copy `templates/journal-entry.html` into `journal/YYYY-MM-DD-slug.html`.
3. Replace the placeholder title, date, slug, topics, summaries, Chinese body, English translation, references, and conversation copy.
4. Keep the same article format: Chinese original, English version, Appendix / References, metrics, share tools, and flowing conversation thread.
5. Add the article metadata to the embedded `posts-data` JSON in `index.html`.
6. Add the article to `agent-index.json`, `rss.xml`, and `sitemap.xml`.

The site intentionally has no build step, so GitHub Pages can serve it directly.
