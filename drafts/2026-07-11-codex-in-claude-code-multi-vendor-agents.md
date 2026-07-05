---
id: codex-in-claude-code-multi-vendor-agents
platform: linkedin
status: draft
publish_date: 2026-07-11
title: "Codex-in-Claude-Code: multi-vendor agents"
angle: opinionated-take
tags:
  - AIagents
  - AIArchitecture
  - ClaudeCode
  - MultiModel
sources:
  - https://github.com/openai/codex-plugin-cc
---

OpenAI just shipped a plugin that lets you call Codex from inside Claude Code — get a second opinion on a review, or delegate a task to a different model, without leaving your existing workflow. Coming from OpenAI, aimed at Claude Code users, that's notable.

It's a small integration, but it's a signal worth paying attention to. The assumption a lot of teams still build on — pick one AI vendor, standardize your workflow around it — is quietly breaking down. The more useful pattern emerging is treating models as interchangeable workers behind a workflow you control, not a workflow bolted onto one vendor's tool.

For anyone architecting AI systems for a client or a team, this matters beyond convenience. It's an argument for designing the orchestration layer — the harness, the agent definitions, the review process — as the durable asset, and treating "which model does this step" as a swappable detail underneath it. Vendor lock-in at the model layer is becoming a choice, not a default, and that changes how you should be building.

#aiagents #aiarchitecture #claudecode #multimodel
