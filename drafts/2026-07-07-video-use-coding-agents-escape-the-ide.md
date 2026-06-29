---
id: video-use-coding-agents-escape-the-ide
platform: linkedin
status: draft
publish_date: 2026-07-07
title: "video-use — coding agents escape the IDE"
angle: opinionated-take
tags:
  - claudecode
  - aiengineering
  - codingagents
  - automation
  - agenticai
sources:
  - https://github.com/browser-use/video-use
---

I didn't expect 'edit videos with Claude Code' to be the thing that changed how I think about agentic AI.

video-use is a new open-source project: drop raw footage in a folder, describe the edit you want in plain text, get final.mp4 back. The agent writes ffmpeg commands, reviews the output, and iterates until it's done.

What this made clear is that the assumption coding agents belong inside an IDE was always a constraint of imagination, not technology. The agent doesn't know it's 'editing a video' — it knows it can run shell commands and inspect output.

The actual capability is: write code, execute it, observe results, correct. That loop works for video editing the same way it works for refactoring a function.

The surface area of what's automatable here is much larger than most teams are currently building for. Anywhere there's a CLI tool and a feedback loop, there's a potential agent workflow.
