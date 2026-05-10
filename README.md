# Nova Yiting Wu

Exchange Ideas & Beyond.

A static bilingual personal journal site designed for Chinese-first writing, English translations, human readers, and periodic AI-agent readers.

## What is included

- `index.html` is the journal homepage.
- `journal/` contains published article pages.
- `content/` contains Markdown source notes for easier writing and agent ingestion.
- `agent-index.json` gives AI agents a stable reading protocol and article list.
- `rss.xml`, `sitemap.xml`, and `robots.txt` make the site easier to crawl.
- Article metadata includes `Page View`, `Share`, and `Agent Use`.
- `analytics.js` provides local demo counts and a future integration point for real analytics.
- `agent-use.schema.json`, `docs/agent-use.md`, `ai.txt`, and the GitHub issue template define the agent-use acknowledgement contract.

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

1. Add a Markdown source file in `content/`.
2. Add a matching HTML article in `journal/`.
3. Add the article metadata to the embedded `posts-data` JSON in `index.html`.
4. Add the article to `agent-index.json`, `rss.xml`, and `sitemap.xml`.

The site intentionally has no build step, so GitHub Pages can serve it directly.
