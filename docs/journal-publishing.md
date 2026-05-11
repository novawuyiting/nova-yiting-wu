# Journal Publishing

Use GitHub Issues as the daily writing entry point.

## Daily Flow

1. Open the repository on GitHub.
2. Go to Issues.
3. Choose `New journal entry`.
4. Fill in the Chinese title, English title, summaries, topics, Chinese body, English body, and optional references.
5. Submit the issue.
6. GitHub Actions publishes the journal files to `main`.
7. GitHub Pages updates the public site after the Pages build finishes.

This does not call an AI translator or spend AI credits. The English version is a field you can write, paste, or improve later.

## Reference Format

Use one reference per line:

```text
Creator | Title | URL | Publisher/platform | Year | Why it matters
```

Example:

```text
Andy Weir | Project Hail Mary | https://openlibrary.org/books/OL33833935M/Project_Hail_Mary | Ballantine Books | 2021 | The collaboration idea came from this novel.
```

## What Gets Updated

The workflow creates or updates:

- `content/YYYY-MM-DD-slug.md`
- `journal/YYYY-MM-DD-slug.html`
- `index.html`
- `agent-index.json`
- `rss.xml`
- `sitemap.xml`

## When To Use Codex

Use the issue workflow for daily publishing. Use Codex when you want to change the site format, design, analytics, automation, or a published article that needs careful editing.
