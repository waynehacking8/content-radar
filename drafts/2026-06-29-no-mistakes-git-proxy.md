---
id: no-mistakes-git-proxy
platform: linkedin
status: draft
publish_date: 2026-06-29
title: "no-mistakes-git-proxy"
angle: tool-spotlight
tags:
  - GitWorkflow
  - DeveloperExperience
  - AITools
  - CodeQuality
  - SoftwareEngineering
sources:
  - https://github.com/kunchenguid/no-mistakes
---

A git proxy that runs an AI review before your push reaches origin. That's the whole pitch for no-mistakes, and it's a genuinely clever place to put a quality gate.

The flow: you push to a local no-mistakes remote instead of origin. It spins up a disposable worktree, runs a validation pipeline, and only forwards the push if the code passes. Fail locally — before anything hits your team's repo.

What I like is the level of intervention. Pre-commit hooks are easy to skip. CI catches issues late and wastes pipeline time. This sits in between: on your machine, before the push, opt-in per repo. The disposable worktree also means it tests a clean copy — not your working directory with stray debug logs still in.

Early project, rough edges, but the architecture reflects a real insight: put quality enforcement where the cost of failure is lowest. That principle applies well beyond git workflows.

#gitworkflow #developerexperience #aitools #codequality #softwareengineering
