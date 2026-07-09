---
id: would-you-install-a-skill-without-reading-its-pe
platform: linkedin
status: draft
publish_date: 2026-07-13
title: "Would you install a skill without reading its permissions?"
angle: tool-spotlight
tags:
  - AI
  - AgentSecurity
  - AppSec
  - LLM
  - DevTools
sources:
  - https://github.com/NVIDIA/SkillSpector
---

Browser extensions taught us to check permissions before installing. Agent skills need the same instinct, and most people aren't doing it yet.

Skills, plugins, and MCP tools for coding agents are just files — instructions and sometimes executable code — that your agent reads and trusts. If one contains a malicious pattern (data exfiltration instructions, prompt injection payloads, quiet permission escalation), your agent may follow it exactly as written, with whatever access it already has. NVIDIA's SkillSpector is a scanner built specifically to catch this before install: it looks for vulnerabilities and malicious patterns in agent skills the same way we'd scan a new npm package.

What I like about this is it treats agent tooling as a supply chain, because that's what it is. If you're the one an org trusts to bring AI agents into production, this kind of due diligence isn't optional — it's the difference between a useful capability and a new attack surface nobody scoped.
