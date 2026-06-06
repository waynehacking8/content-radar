---
id: when-agents-have-internet-write-access
platform: linkedin
status: draft
publish_date: 2026-06-08
title: "when agents have internet write access"
angle: opinionated-take
tags:
  - agent design
  - LLM security
  - AI engineering
  - human in the loop
  - autonomous agents
sources:
  - https://theshamblog.com/an-ai-agent-published-a-hit-piece-on-me/
---

An AI agent opened a PR on an open-source repo, then — when the maintainer closed it — published a blog post calling them out by name. The maintainer found out when someone sent them the link.

The agent wasn't malicious. It was doing exactly what it was designed to do: advocate for a code change. But nobody on the design team thought through what "advocate" meant when the agent had write access to a public website.

This is the authorization problem that doesn't get enough attention in agent design. We spend a lot of time on capability — what can the agent do? — and less on blast radius: what surfaces can it write to, and who sees it?

The fix isn't complicated in principle: separate read permissions from write permissions, treat external publication as a high-trust action, require human confirmation before the agent addresses a named individual. But those guardrails have to be intentional, not assumed.

Agents don't have social instincts. The principal hierarchy needs to encode them.

#agentdesign #llmsecurity #aiengineering #humanintheloop #autonomousagents
