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
ENV_FILE = ROOT / ".env"


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
    # Minimum score to keep an item (per-source floors).
    min_score: dict[str, int] = field(
        default_factory=lambda: {
            "hackernews": 20, "reddit": 50, "github": 25, "arxiv": 0, "x": 10,
        }
    )


DEFAULT_INTERESTS = Interests()


def twitterapi_io_key() -> str | None:
    return os.environ.get("TWITTERAPI_IO_KEY") or None


def anthropic_api_key() -> str | None:
    return os.environ.get("ANTHROPIC_API_KEY") or None


# Synthesis model. Override with SYNTH_MODEL if you want a cheaper/bigger one.
def synth_model() -> str:
    return os.environ.get("SYNTH_MODEL", "claude-sonnet-4-6")
