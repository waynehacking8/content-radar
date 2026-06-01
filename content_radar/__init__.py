"""content-radar — collect trending AI/dev signal and synthesize post drafts.

Pipeline: collectors (Hacker News, arXiv, GitHub Trending, Reddit, X) -> dated
JSON store with dedup -> Claude synthesis -> review-ready Markdown drafts.
"""

__version__ = "0.1.0"
