---
id: no-mistakes-git-proxy
platform: linkedin
status: draft
publish_date: 2026-06-29
title: "no-mistakes-git-proxy"
angle: tool-spotlight
tags:
  - aiengineering
  - devtools
  - gitworkflow
  - agentdrivendevelopment
sources:
  - https://github.com/kunchenguid/no-mistakes
---

Here's a pattern I hadn't seen before: a git proxy that sits between your local machine and your actual remote.

You push to `no-mistakes` instead of `origin`. It spins up a disposable worktree, runs an AI-driven validation pipeline over your changes, and only forwards the push if it passes. If something's wrong, the push fails locally — before your CI queue ever sees it.

The project is open source and the goal is catching AI-generated slop before it becomes a PR for humans to review.

What I find interesting isn't the specific tool — it's the architectural instinct. As AI coding assistants generate more of our commits, the review surface shifts. You can't rely on "a human wrote this, so it's probably intentional." Pre-push gates that actually understand code are going to become standard tooling.

This is one early version of what that looks like. The principle — interpose an AI quality check between generation and publication — will show up everywhere.
