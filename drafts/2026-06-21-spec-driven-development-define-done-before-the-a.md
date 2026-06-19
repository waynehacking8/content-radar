---
id: spec-driven-development-define-done-before-the-a
platform: linkedin
status: draft
publish_date: 2026-06-21
title: "spec-driven development: define done before the agent starts"
angle: opinionated-take
tags:
  - agentdev
  - softwareengineering
  - aiworkflows
  - productengineering
sources:
  - https://github.com/github/spec-kit
---

Hot take: the biggest problem with AI-generated code isn't hallucination — it's building the wrong thing faster.

GitHub's spec-kit introduces Spec-Driven Development: write a product spec first, defining which scenarios should work and what outcomes count as success, then use that spec to guide and validate what the agent generates. The deliverable becomes verifiable before a single line of code is written.

This maps to something I see constantly in solutions engineering work: the gap isn't between "code that runs" and "code that doesn't." It's between "code that runs" and "code that solves the actual problem." Vibe coding closes the first gap fast. Spec-driven approaches try to close the second.

The toolkit is open source and early-stage, but the methodology is the real point. If you're deploying AI agents in any production workflow, forcing yourself to define done before the agent starts is just good practice — regardless of what tools you use. Garbage-in, garbage-out applies to requirements as much as it applies to data.
