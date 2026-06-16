---
id: llm-poisoning-250-docs
platform: linkedin
status: draft
publish_date: 2026-06-18
title: "llm-poisoning-250-docs"
angle: accessible-lesson
tags:
  - llmsecurity
  - aiengineering
  - mlsecurity
  - datasecurity
sources:
  - https://www.anthropic.com/research/small-samples-poison
---

250 malicious documents is all it takes to backdoor an LLM — and bigger models do not make you safer.

Anthropic published research with the UK AI Security Institute and the Alan Turing Institute showing that fine-tuning on as few as 250 poisoned samples can embed a persistent backdoor into a model of any size. The model behaves normally most of the time, but when it encounters a specific trigger pattern, its behavior flips: it might leak data, generate harmful content, or take unintended actions.

The attack surface this opens is the training data pipeline, not the model weights themselves. If you are fine-tuning on user-generated data, scraping training sets from the open web, or accepting third-party datasets, you are implicitly trusting a supply chain you may not be auditing.

For practitioners: data provenance and integrity checks deserve the same rigor you already apply to code dependencies. The threat model for LLMs is not just adversarial prompts at inference time — it starts much earlier.
