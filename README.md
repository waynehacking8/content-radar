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

# 3a) AINews-style thematic digest of the day (clusters signal into themes)
python -m content_radar.cli digest --out ./digests --themes 5

# 3b) or draft individual posts from the signal
python -m content_radar.cli synthesize --out ./drafts --n 5
```

Synthesis runs on the **local `claude` CLI (your Claude subscription)** by default
— no API key. For automated runs with your laptop off, see **Automation** below.

The `digest` command produces an AINews-style brief: a one-line headline, a handful
of **themes** (each a short narrative that synthesises the day's items with inline
source links), and a **Top by engagement** list.

## Automation (runs with your laptop off)

`.github/workflows/radar.yml` runs daily on GitHub's servers and commits the digest
+ drafts back to the repo for review. It authenticates with **your subscription**,
not an API key:

1. Locally: `claude setup-token` → copies a 1-year subscription token (works on
   monthly Pro/Max).
2. Repo → Settings → Secrets and variables → Actions → add `CLAUDE_CODE_OAUTH_TOKEN`
   (and optionally `TWITTERAPI_IO_KEY`, `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`).
3. Trigger it from the Actions tab, or wait for the daily schedule.

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
  config.py            # interests (keywords, x_accounts, subreddits...) + secrets
  collectors/
    hackernews.py      # Algolia API (free)
    arxiv.py           # export API (free)
    github_trending.py # trending page parse (free)
    reddit.py          # OAuth or public JSON (free)
    x_twitterapi.py    # twitterapi.io: keyword search + curated account timelines
    discord_collector.py # official Bot REST API (opt-in; no self-bots)
  enrich.py            # Phase 3: fetch + attach linked-article text
  digest.py            # Phase 2/4: thematic clustering + best-of-N editorial pick
  synthesize.py        # Claude backend (subscription CLI) -> draft posts
  cli.py               # collect / show / digest / synthesize
tests/                 # 16 tests; gate, store, digest, enrich (python -m pytest)
```

### How it matches AINews

| AINews technique | content-radar |
|---|---|
| Breadth: Twitter accounts + Reddit + Discord | `x_accounts` timelines, Reddit OAuth, Discord bot |
| Click through links and summarise them | `enrich.py` (Phase 3) |
| Cluster into themes with attribution | `digest.py` (Phase 2) |
| Run N pipelines, pick the best | `--best-of N` (Phase 4) |
| Daily, automated | GitHub Actions on your subscription |

## Design notes

- **Collectors never raise.** A dead source logs a warning and returns what it
  has; one broken feed can't take down a run.
- **Idempotent store.** Re-collecting the same day dedups by `source:id` and
  keeps the higher score.
- **Human in the loop by construction.** Synthesis only ever writes `draft`s.

## License

MIT
