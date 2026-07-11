---
id: why-every-engineer-should-build-one-agent
platform: linkedin
status: draft
publish_date: 2026-07-17
title: "Why every engineer should build one agent"
angle: accessible-lesson
tags:
  - aiagents
  - buildinpublic
  - softwareengineering
  - llm
sources:
  - https://fly.io/blog/everyone-write-an-agent/
---

Thomas Ptacek's advice is simple: if you want to actually understand agents, stop reading about them and write one. Not a wrapper around a chat API, an actual loop: a model, a set of tools it can call, and a way to feed results back in. It takes an afternoon, and it teaches you more than any framework's documentation will. You see immediately why prompt engineering is really just context engineering, why tool schemas matter more than clever prompting, and why the failure modes are almost always about the scaffolding around the model, not the model itself. This is the same reason I'd tell anyone moving into solutions or forward-deployed engineering to build the smallest possible agent before touting any platform's agent framework. You can't evaluate whether a tool is doing something hard for you until you've felt how hard that thing actually is. The gap between 'I've used an agent' and 'I've built one' is bigger than it looks.
