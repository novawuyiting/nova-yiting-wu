# Agent Use Tracking

`Page View` and `Share` can be counted through normal web analytics. `Agent Use` needs an explicit acknowledgement because a passive AI fetch is difficult to distinguish from a crawler, link preview, or normal request.

Recommended signal:

```json
{
  "article_slug": "2026-05-10-building-a-thinking-garden",
  "agent_name": "example-agent",
  "used_for": "Generated three follow-up experiments from the article.",
  "response_type": "extension",
  "generated_ideas": ["Turn open questions into recurring prompts."],
  "source_url": "https://example.com/journal/2026-05-10-building-a-thinking-garden.html",
  "created_at": "2026-05-10T00:00:00Z"
}
```

For a static GitHub Pages site, practical options are:

- Ask agents to cite the article slug in their replies.
- Ask agents to open a GitHub issue with the `Agent Use acknowledgement` template.
- Later, replace this with a small serverless endpoint that accepts the same JSON schema.
