---
id: llm-inevitabilism-evaluation-trap
platform: linkedin
status: draft
publish_date: 2026-06-13
title: "llm-inevitabilism-evaluation-trap"
angle: opinionated-take
tags:
  - llm
  - ai
  - aiengineering
  - productenginering
  - criticalthinking
sources:
  - https://tomrenner.com/posts/llm-inevitabilism/
---

There's a rhetorical move that happens every time someone critiques an AI system: "But it'll get better." Tom Renner calls this LLM inevitabilism, and naming it is genuinely useful.

The pattern: point out a real failure — hallucinations, unreliable reasoning, poor performance on edge cases — and the response is that future models will fix it. It's technically unfalsifiable. There's no current failure that can't be dismissed this way.

The problem isn't optimism. Real progress has happened. The problem is that inevitabilism short-circuits honest evaluation. It turns "is this model reliable enough for my use case today" into "will this eventually be fine" — a much weaker standard that can justify almost anything.

When you're advising on whether to use an LLM for a production workflow, the question that matters is current reliability against your specific requirements and failure tolerance. Not the trajectory. Not what next year's model might do.

Evaluate what's in front of you. Ship when it's good enough. Revisit when the landscape changes.
