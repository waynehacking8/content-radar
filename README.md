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
