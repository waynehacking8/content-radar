# content-radar

Collect trending **AI / dev** signal from multiple sources, then synthesize
**review-ready post drafts** with Claude. Built for practitioners who want their
posts to ride current topics without hand-trawling five feeds every morning.

```
collectors ──▶ dated JSON store (dedup) ──▶ Claude synthesis ──▶ draft .md files
 HN · arXiv · GitHub Trending · Reddit · X                         (you review & post)
```

Nothing is ever auto-published. The output is **drafts** (`status: draft`) for a
human to approve — pairs naturally with a review-gated posting queue.

## Why these sources

For an LLM-infra / agentic-AI niche, the highest-signal trends surface first on
**Hacker News, arXiv, GitHub Trending, and Reddit** — all free, with clean APIs.
**X** is added as an *optional, paid* layer via [twitterapi.io](https://twitterapi.io)
(~$0.15 / 1,000 tweets, no monthly fee) — deliberately **not** the official API
($0.005/read) and **not** self-scraping (fragile + account-ban risk).

## Install

```bash
python3 -m pip install -r requirements.txt
cp .env.example .env     # add ANTHROPIC_API_KEY (and optionally TWITTERAPI_IO_KEY)
```

## Use

```bash
# 1) collect today's signal (free sources need no keys)
python -m content_radar.cli collect
python -m content_radar.cli collect --sources hackernews arxiv   # subset

# 2) see what came in
python -m content_radar.cli show --top 25

# 3) draft posts from it (needs ANTHROPIC_API_KEY)
python -m content_radar.cli synthesize --out ./drafts --n 5
```

Each draft is a Markdown file with YAML front matter:

```yaml
---
id: stop-asking-which-llm-server-is-faster
platform: linkedin
status: draft
publish_date: 2026-06-02
title: "..."
angle: opinionated-take
tags: [LLM, MLOps]
sources:
  - https://news.ycombinator.com/item?id=...
---

The post body, ready to review and paste.
```

## Configure what it watches

Interests are data, not magic values — edit `content_radar/config.py`:

```python
keywords         = ("LLM", "inference", "agent", "RAG", "vLLM", ...)
arxiv_categories = ("cs.CL", "cs.LG", "cs.DC", "cs.AI")
subreddits       = ("LocalLLaMA", "MachineLearning")
x_queries        = ("LLM inference", "agentic RAG", ...)
min_score        = {"hackernews": 20, "reddit": 50, "github": 25, ...}
```

## Layout

```
content_radar/
  models.py            # immutable Item
  store.py             # dated JSON store + dedup (idempotent re-runs)
  config.py            # interests + secret loading (.env, nothing hard-coded)
  collectors/
    hackernews.py      # Algolia API (free)
    arxiv.py           # export API (free)
    github_trending.py # trending page parse (free)
    reddit.py          # public JSON (free)
    x_twitterapi.py    # twitterapi.io (optional, paid; off unless key set)
  synthesize.py        # Claude -> draft .md files
  cli.py               # collect / show / synthesize
tests/                 # store, models, synthesis (run: python -m pytest)
```

## Design notes

- **Collectors never raise.** A dead source logs a warning and returns what it
  has; one broken feed can't take down a run.
- **Idempotent store.** Re-collecting the same day dedups by `source:id` and
  keeps the higher score.
- **Human in the loop by construction.** Synthesis only ever writes `draft`s.

## License

MIT
