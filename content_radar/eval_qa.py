"""Offline QA evaluation: run questions through the bot brain and LLM-judge each.

`generate` asks Claude for a diverse question set; `run` answers each via the
real retrieval pipeline and scores it (grounded, complete, not truncated,
Traditional Chinese) with an LLM-as-judge. Used to verify answer quality at scale.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from . import config
from .chat import answer
from .synthesize import run_claude_cli

GEN_PROMPT = """Generate {n} diverse questions (in Traditional Chinese) that a
practitioner would ask an AI-news assistant whose knowledge base is ~600 days of
AINews newsletters plus Hacker News / GitHub / arXiv signal (2024-2026). Cover a
mix: company news (Anthropic, OpenAI, Google, NVIDIA), funding, model releases,
agents & safety, RAG/retrieval, open-source models, GPU/inference, and some
date-specific "what happened around <month>" questions. Vary specificity.
Return ONLY a JSON array of question strings."""

JUDGE_PROMPT = """You are grading an AI-news assistant. Given the QUESTION and the
ANSWER, score the ANSWER 1-5:
5 = grounded, specific, complete, well-structured, NOT truncated, in Traditional Chinese.
3 = partially useful but thin, or missing specifics/dates the question asked for.
1 = wrong, empty, truncated, or wrong language.
An honest "the knowledge base doesn't cover this" is acceptable (score 4) ONLY if
the topic is genuinely niche. Return ONLY JSON:
{"score": <1-5>, "pass": <true if score>=4>, "issue": "<short reason>"}"""


def _extract_array(text: str) -> list:
    text = re.sub(r"^```[a-zA-Z]*\n?|\n?```$", "", text.strip())
    s, e = text.find("["), text.rfind("]")
    return json.loads(text[s:e + 1])


def _extract_obj(text: str) -> dict:
    text = re.sub(r"^```[a-zA-Z]*\n?|\n?```$", "", text.strip())
    s, e = text.find("{"), text.rfind("}")
    return json.loads(text[s:e + 1])


def generate_questions(n: int, model: str) -> list[str]:
    out = run_claude_cli(GEN_PROMPT.replace("{n}", str(n)), model)
    return _extract_array(out)


def judge(question: str, ans: str, model: str) -> dict:
    out = run_claude_cli(f"{JUDGE_PROMPT}\n\nQUESTION:\n{question}\n\nANSWER:\n{ans}", model)
    try:
        return _extract_obj(out)
    except (ValueError, json.JSONDecodeError):
        return {"score": 0, "pass": False, "issue": "judge parse error"}


def run(questions: list[str], model: str | None = None, out_path: str | None = None) -> dict:
    model = model or config.synth_model()
    results = []
    for i, q in enumerate(questions, 1):
        try:
            ans = answer(q)
            verdict = judge(q, ans, model)
        except Exception as exc:  # noqa: BLE001
            ans, verdict = "", {"score": 0, "pass": False, "issue": f"error: {exc}"}
        results.append({"q": q, "score": verdict.get("score", 0),
                        "pass": bool(verdict.get("pass")), "issue": verdict.get("issue", ""),
                        "answer": ans})
        print(f"[{i}/{len(questions)}] {verdict.get('score', 0)}/5 "
              f"{'PASS' if verdict.get('pass') else 'FAIL'}  {q[:42]}", flush=True)
    passed = sum(r["pass"] for r in results)
    avg = sum(r["score"] for r in results) / max(len(results), 1)
    summary = {"total": len(results), "passed": passed, "avg_score": round(avg, 2),
               "results": results}
    print(f"\n=== {passed}/{len(results)} passed (score>=4), avg {avg:.2f}/5 ===")
    if out_path:
        Path(out_path).write_text(json.dumps(summary, ensure_ascii=False, indent=2),
                                  encoding="utf-8")
    return summary
