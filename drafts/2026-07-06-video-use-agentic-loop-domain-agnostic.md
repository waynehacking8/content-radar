---
id: video-use-agentic-loop-domain-agnostic
platform: linkedin
status: draft
publish_date: 2026-07-06
title: "video-use-agentic-loop-domain-agnostic"
angle: building-in-public
tags:
  - ClaudeCode
  - AIAgents
  - BuildingInPublic
  - AgenticAI
  - LLM
sources:
  - https://github.com/browser-use/video-use
---

Someone just used Claude Code to edit video — not to write a Python script that calls ffmpeg, but to actually direct the edit: what to cut, what order, what transitions.

The project is called video-use. Drop raw footage in a folder, describe what you want, get final.mp4 back. Fully open source.

What's interesting beyond the demo is the architectural point. Claude Code was built for software development, but the underlying capability — reading files, reasoning about structure, executing shell commands, iterating on output — transfers to any domain where work can be expressed as operations on files.

The boundary between coding tool and domain tool is collapsing. Not because the tools are becoming magical, but because the agentic loop is domain-agnostic when you frame tasks the right way.

Video editing was not on my short list of workflows that would get claimed by this approach. It probably should have been.

#claudecode #aiagents #buildinginpublic #agenticai #llm
