"""Configuration: what to watch and where secrets come from.

Topic interests live here as data (no magic values scattered in logic). Secrets
are only ever read from the environment / a git-ignored .env file.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
STORE_DIR = ROOT / "store"
DIGESTS_DIR = ROOT / "digests"
ENV_FILE = ROOT / ".env"

# Trusted senders for swyx's AINews newsletter. Requiring a sender prevents
# unrelated messages such as Apps Script failure summaries (whose subjects can
# also contain "AINews") from entering the collector or forwarding pipeline.
DEFAULT_AINEWS_SENDERS = (
    "swyx+ainews@substack.com",
    "news@smol.ai",
)
DEFAULT_AINEWS_QUERY = (
    "{" + " ".join(f"from:{sender}" for sender in DEFAULT_AINEWS_SENDERS) + "} "
    "subject:AINews"
)


def load_env() -> None:
    load_dotenv(ENV_FILE)


@dataclass(frozen=True)
class Interests:
    """The niche this radar watches. Tune freely — these are the defaults."""

    keywords: tuple[str, ...] = (
        "LLM", "inference", "agent", "RAG", "vLLM", "TensorRT", "NVIDIA",
        "quantization", "fine-tuning", "GPU", "CUDA", "evaluation",
    )
    arxiv_categories: tuple[str, ...] = ("cs.CL", "cs.LG", "cs.DC", "cs.AI")
    subreddits: tuple[str, ...] = ("LocalLLaMA", "MachineLearning")
    github_languages: tuple[str, ...] = ("python", "cuda", "")  # "" = all langs
    x_queries: tuple[str, ...] = (
        "LLM inference", "agentic RAG", "vLLM OR TensorRT-LLM",
    )
    # Curated X accounts to monitor (the AINews "544 twitters" pattern). A small,
    # high-signal starter set — extend freely.
    x_accounts: tuple[str, ...] = (
        "swyx", "karpathy", "_philschmid", "jeremyphoward", "ClementDelangue",
        "vllm_project", "ggerganov", "scaling01", "omarsar0", "reach_vb",
    )
    # Discord channel IDs to read (needs DISCORD_BOT_TOKEN + a bot in those
    # servers). Empty by default — opt in.
    discord_channels: tuple[str, ...] = ()
    # Gmail search (Gmail syntax) for AI-news newsletters to fold in. Needs
    # GMAIL_USER + GMAIL_APP_PASSWORD. Targets swyx's AINews (smol.ai) — the
    # gold-standard expert-curated AI digest. Add more senders as needed.
    gmail_query: str = f"{DEFAULT_AINEWS_QUERY} newer_than:4d"
    # Minimum score to keep an item (per-source floors).
    min_score: dict[str, int] = field(
        default_factory=lambda: {
            "hackernews": 20, "reddit": 50, "github": 25, "arxiv": 0,
            "x": 10, "discord": 0,
        }
    )


DEFAULT_INTERESTS = Interests()


def twitterapi_io_key() -> str | None:
    return os.environ.get("TWITTERAPI_IO_KEY") or None


def discord_bot_token() -> str | None:
    return os.environ.get("DISCORD_BOT_TOKEN") or None


def anthropic_api_key() -> str | None:
    return os.environ.get("ANTHROPIC_API_KEY") or None


def gmail_user() -> str | None:
    return os.environ.get("GMAIL_USER") or None


def gmail_app_password() -> str | None:
    return os.environ.get("GMAIL_APP_PASSWORD") or None


# Where the daily Traditional-Chinese digest email is delivered. Reuses the
# Gmail SMTP sender above; override the recipient with DIGEST_EMAIL_TO.
DEFAULT_DIGEST_EMAIL_TO = "waynehacking8@gmail.com"


def digest_email_to() -> str:
    return os.environ.get("DIGEST_EMAIL_TO", DEFAULT_DIGEST_EMAIL_TO).strip() or DEFAULT_DIGEST_EMAIL_TO


# ── AINews watcher ───────────────────────────────────────────────────────────
# A daily GitHub Actions workflow (.github/workflows/ainews-watch.yml) checks
# after the newsletter's usual arrival window. Dedup state lives in Gmail itself:
# a successful forward labels the original mail, and the watch query excludes
# that label — every poll is idempotent, no state files.
DEFAULT_AINEWS_FORWARDED_LABEL = "radar-forwarded"

# Subject suffix for the forwarded Traditional-Chinese edition.
ZH_SUBJECT_SUFFIX = " — 中文版"

# How far back the watcher looks for an unforwarded issue. Wider than 1 day so
# a delayed or failed daily run can catch up the next day — the radar-forwarded
# label, not this window, prevents re-sends.
AINEWS_FRESH_WINDOW = "2d"


def ainews_forwarded_label() -> str:
    return (os.environ.get("AINEWS_FORWARDED_LABEL", DEFAULT_AINEWS_FORWARDED_LABEL).strip()
            or DEFAULT_AINEWS_FORWARDED_LABEL)


def ainews_watch_query() -> str:
    """Gmail search for 'a fresh AINews that has not been forwarded yet'."""
    default = (f"{DEFAULT_AINEWS_QUERY} newer_than:{AINEWS_FRESH_WINDOW} "
               f"-label:{ainews_forwarded_label()}")
    return os.environ.get("AINEWS_WATCH_QUERY", default).strip() or default


def forwarded_subject(title: str) -> str:
    """Subject line of the forwarded Chinese edition."""
    return f"{title}{ZH_SUBJECT_SUFFIX}"


# Where the chat bot reads the latest digest from. Fetching over HTTP (raw
# GitHub) makes "today's digest" live — the bot sees a new digest within the
# CDN cache window (~5 min) instead of waiting for its next 6-hourly restart to
# re-checkout the repo. Set DIGEST_RAW_BASE="" to force the local-disk path.
DEFAULT_DIGEST_RAW_BASE = "https://raw.githubusercontent.com/waynehacking8/content-radar/main/digests"


def digest_raw_base() -> str:
    return os.environ.get("DIGEST_RAW_BASE", DEFAULT_DIGEST_RAW_BASE).strip()


# Synthesis model. Alias ("sonnet"/"opus"/"haiku") is most portable for the
# `claude` CLI; override with SYNTH_MODEL for a specific version.
def synth_model() -> str:
    return os.environ.get("SYNTH_MODEL", "sonnet")


# Agentic web-search fallback: when the local knowledge base doesn't cover a
# question (niche specs, exact figures, fast-moving vertical news), let the
# answering model fill the gap from the live web. On by default; set
# WEB_FALLBACK=0 for a pure, KB-only (and faster) answer path.
def web_fallback_enabled() -> bool:
    return os.environ.get("WEB_FALLBACK", "1").strip().lower() not in {"0", "false", "no", ""}
