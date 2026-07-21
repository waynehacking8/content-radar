# content-radar

> **Automation status (2026-07-21).** AINews forwarding runs once daily in
> GitHub Actions. The broader radar and Telegram bot workflows remain paused.

Collect trending **AI / dev** signal from multiple sources, build a **vector
knowledge base** from it, and serve three things off that KB: an AINews-style
daily **digest**, review-ready post **drafts**, and a **Traditional-Chinese chat
bot** — all synthesised with Claude on your subscription (no API key).

```
                                            ┌──▶ daily thematic digest (.md)
collectors ──▶ dated JSON store (dedup) ──▶ │
 HN·arXiv·GitHub·Reddit·X·Gmail(AINews)     ├──▶ post drafts (.md, status: draft)
        │                                   │
        └──▶ enrich (full text) ──▶ Qdrant  ├──▶ Telegram chat bot (繁中, RAG + WebSearch)
             vector KB (e5 + BM25 + rerank) │
                                            └──▶ AINews → 繁中 email + 本期摘要 (daily at 18:00 Taipei)
```

Two model layers: **retrieval runs locally for free** (fastembed: e5-large dense +
BM25 sparse + jina cross-encoder rerank, vectors in Qdrant Cloud); **all generation
runs on Claude Sonnet** via the `claude` CLI subscription. Nothing is ever
auto-published — posts are **drafts** (`status: draft`) for a human to approve.

AINews issues are embedded and upserted into the KB by the daily forwarding
workflow. Re-runs are idempotent (deterministic point IDs dedup). The broader
radar collector remains paused, so its other sources do not update by themselves.

## Why these sources

For an LLM-infra / agentic-AI niche, the highest-signal trends surface first on
**Hacker News, arXiv, GitHub Trending, and Reddit** — all free, with clean APIs.
**X** is added as an *optional, paid* layer via [twitterapi.io](https://twitterapi.io)
(~$0.15 / 1,000 tweets, no monthly fee) — deliberately **not** the official API
($0.005/read) and **not** self-scraping (fragile + account-ban risk).

## Install

```bash
python3 -m pip install -r requirements.txt
cp .env.example .env     # generation uses your `claude` CLI login — no API key.
                         # add QDRANT_URL/_API_KEY for the KB, GMAIL_* for AINews + email.
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

## Chat bot — ask your radar (中文問答範例)

A Telegram bot (`content_radar/telegram_bot.py`) answers questions grounded in the
knowledge base (413+ dated AINews issues 2024–2026 + HN/arXiv/GitHub), retrieved
with **hybrid search + cross-encoder rerank**. Answers are in **Traditional Chinese**,
cite sources with dates, and are **not truncated**. When the KB doesn't cover a
question, it falls back to **WebSearch** and attributes the web sources.

可以問的問題類型(實際回答節錄,皆為機器人真實輸出):

| 類型 | 範例問題 |
|---|---|
| 📅 時間軸 / 歷史 | 「Anthropic 從 2024 到 2026 完成哪幾輪融資?各輪金額大約多少?」 |
| 🏢 公司 / 模型 | 「Claude Opus 4.8 跟前一代相比有哪些重點改進?」 |
| 🔬 技術概念 | 「Contextual Retrieval 是什麼?它如何改善 RAG 效果?」 |
| ⚙️ 工程實作 | 「推測解碼(Speculative Decoding)如何加速大模型推理?」 |
| 🌐 KB 沒有 → 自動上網 | 「NVIDIA H100 跟 H200 的規格主要差在哪?」 |

<details>
<summary><b>Q:</b> Contextual Retrieval 是什麼?它如何改善 RAG 效果?</summary>

> **Contextual Retrieval** 是 Anthropic 提出的 RAG 改良技術,核心是在把文件切成 chunks 存入向量庫前,先為每個 chunk 加上「情境說明」,讓每段文字知道自己在整份文件中的位置與意義。
>
> 根據 Anthropic 研究(2024-09),它結合 **Contextual Embedding** 與 **Contextual BM25**,搭配 reranking 後,前 20 個 chunk 的**檢索失誤率從 5.7% 降至 1.9%(降幅 67%)**;並用 prompt caching 降低為每個 chunk 生成情境說明的成本。
>
> 來源:[AINews] Anthropic Contextual Retrieval(2024-09-21)、[AINews] cde-small-v1(2024-10-05)

</details>

<details>
<summary><b>Q:</b> Anthropic 從 2024 到 2026 完成哪幾輪融資?(時間軸題)</summary>

> | 時間 | 輪次 | 金額／估值 |
> |------|------|-----------|
> | 2024 末 | Amazon 策略投資 | $40 億 |
> | 2025-03 | Series E | 估值 $615 億 |
> | 2026-02 | 未具名 | 估值 $3,800 億(ARR $140 億) |
> | 2026-05-29 | Series H | 募資 $650 億,post-money 估值 $9,650 億(ARR $470 億) |
>
> 每筆都附對應的 AINews 期數與日期連結。

</details>

<details>
<summary><b>Q:</b> NVIDIA H100 跟 H200 的規格主要差在哪?(KB 沒有 → WebSearch)</summary>

> H200 是 H100 的**記憶體升級版**,同一塊 Hopper(GH100)晶片,差異集中在記憶體:
>
> | 規格 | H100 SXM | H200 SXM |
> |------|----------|----------|
> | 記憶體 | 80 GB HBM3 | **141 GB HBM3e**(+76%) |
> | 頻寬 | 3.35 TB/s | **4.8 TB/s**(+43%) |
>
> 因為大模型推論是記憶體頻寬瓶頸,H200 在 MLPerf Llama2-70B 吞吐量提升約 +37～42%。
>
> Sources(WebSearch 自動附上):NVIDIA H200 官方頁、Databasemart、Spheron 等。

</details>

> 完整問答(含 Opus 4.8、Speculative Decoding 等)直接 DM 機器人即可;每題回答都帶日期與來源,KB 不足時自動補網路來源。

## Automation

Automation uses GitHub Actions only and authenticates with **your subscription**,
not an API key:

- **`.github/workflows/radar.yml`** — retained collect → enrich → index → digest →
  drafts pipeline; paused with no schedule.
- **`.github/workflows/ainews-watch.yml`** — active once daily at 18:00 Taipei.
  It checks for a fresh AINews issue, translates and forwards it, then indexes it.
  Dedup lives in Gmail via the `radar-forwarded` label. Empty checks stop before
  installing the heavy dependencies.

Setup:

1. Locally: `claude setup-token` → copies a 1-year subscription token (works on
   monthly Pro/Max).
2. Repo → Settings → Secrets and variables → Actions → add `CLAUDE_CODE_OAUTH_TOKEN`
   (and optionally `TWITTERAPI_IO_KEY`, `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`).
3. Use `workflow_dispatch` from the Actions tab only when a manual retry is needed.

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
  config.py            # interests + secrets + synth_model / web_fallback / email toggles
  collectors/
    hackernews.py      # Algolia API (free)
    arxiv.py           # export API (free)
    github_trending.py # trending page parse (free)
    reddit.py          # OAuth or public JSON (free)
    x_twitterapi.py    # twitterapi.io: keyword search + curated account timelines (opt-in)
    discord_collector.py # official Bot REST API (opt-in; no self-bots)
    gmail_imap.py      # fold AINews (& other newsletters) from your inbox via IMAP
  enrich.py            # fetch + attach linked-article text (detailed KB)
  chunk.py             # sentence-aware chunking, no overlap
  temporal.py           # query analyzer: EXPLICIT/IMPLICIT/NONE temporal intent → date filters
  rag.py               # KB: contextual chunks + hybrid (e5 dense + BM25) + jina rerank → Qdrant
  kb.py                # local SQLite FTS fallback when Qdrant isn't configured
  digest.py            # thematic clustering + best-of-N pick; full 繁中 translation + 本期摘要 TL;DR
  synthesize.py        # claude CLI backend (subscription; tools off by default)
  chat.py              # RAG chat: retrieve → answer in 繁中, WebSearch fallback on KB gaps
  telegram_bot.py      # long-poll Telegram bot over chat.py (serverless, no own host)
  mailer.py            # Gmail SMTP: 繁中 AINews edition
  watch.py             # daily AINews watcher, dedup via Gmail label
  eval_qa.py           # LLM-as-judge QA harness (generate questions, score answers)
  cli.py               # collect / show / enrich / index / import / digest / synthesize / check-ainews / email-digest / eval
tests/                 # 95 tests (python -m pytest)
```

### How it matches AINews

| AINews technique | content-radar |
|---|---|
| Breadth: Twitter accounts + Reddit + Discord | `x_accounts` timelines, Reddit OAuth, Discord bot |
| Click through links and summarise them | `enrich.py` (full article text) |
| Cluster into themes with attribution | `digest.py` |
| Run N pipelines, pick the best | `--best-of N` |
| Searchable archive of every past issue | **Qdrant vector KB** (`rag.py`) — every day's signal auto-indexed |
| Ask it anything, grounded | **繁中 chat bot** (`chat.py` + `telegram_bot.py`), RAG + WebSearch fallback |
| Automation | GitHub Actions only; broader radar and bot workflows remain paused |
| AINews forwarding | Daily at 18:00 Taipei; Gmail-label dedup makes retries idempotent |

## Design notes

- **Collectors never raise.** A dead source logs a warning and returns what it
  has; one broken feed can't take down a run.
- **Idempotent store.** Re-collecting the same day dedups by `source:id` and
  keeps the higher score.
- **Human in the loop by construction.** Synthesis only ever writes `draft`s.
- **The KB can grow incrementally.** Each explicit run embeds that day's signal (incl. the
  day's AINews) into Qdrant; deterministic point IDs make re-indexing idempotent.
- **Two cost layers.** Retrieval (fastembed + Qdrant free tier) is local and free;
  only Claude generation uses your subscription. No per-token API billing.
- **Tools off by default.** Generation calls run with no agent tools so they can't
  touch the filesystem; only the chat bot's KB-gap path opts into WebSearch.

## License

MIT
