"""Collector contract + shared HTTP helper.

Every collector exposes `collect(interests) -> list[Item]` and must never raise:
a failing source logs a warning and returns whatever it got (often nothing), so
one dead source never takes down a run.
"""
from __future__ import annotations

import sys

import requests

USER_AGENT = "content-radar/0.1 (+https://github.com/)"
TIMEOUT = 20


def get(url: str, *, params: dict | None = None, headers: dict | None = None):
    h = {"User-Agent": USER_AGENT}
    if headers:
        h.update(headers)
    return requests.get(url, params=params, headers=h, timeout=TIMEOUT)


def warn(source: str, exc: Exception) -> None:
    print(f"[content-radar] {source} collector failed: {exc}", file=sys.stderr)
