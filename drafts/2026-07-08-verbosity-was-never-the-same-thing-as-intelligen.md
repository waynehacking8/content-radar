---
id: verbosity-was-never-the-same-thing-as-intelligen
platform: linkedin
status: draft
publish_date: 2026-07-08
title: "Verbosity was never the same thing as intelligence"
angle: accessible-lesson
tags:
  - LLM
  - promptengineering
  - AIagents
  - costoptimization
  - AI
sources:
  - https://github.com/JuliusBrussee/caveman
---

There's a genuinely funny new Claude Code skill called "caveman" that makes your agent answer in short, blunt sentences — "why use many token when few token do trick" — and it cuts output tokens by roughly 65% with no loss in correctness.

The joke is doing real work. Most of what an LLM writes in a normal response isn't reasoning, it's padding: restating the question, hedging, explaining what it's about to do before doing it. None of that changes whether the answer is correct, but all of it costs tokens, latency, and money at scale. If you're running agents in a loop — coding agents especially — that overhead compounds fast across a session.

You don't need to make your agent talk like a caveman to benefit from the lesson. Tightening system prompts to demand terse, direct output is a free performance and cost win most teams haven't bothered to claim yet. Sometimes the silliest projects make the sharpest point.
