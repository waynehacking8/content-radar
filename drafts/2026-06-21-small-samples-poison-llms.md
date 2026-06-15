---
id: small-samples-poison-llms
platform: linkedin
status: draft
publish_date: 2026-06-21
title: "small-samples-poison-llms"
angle: accessible-lesson
tags:
  - llmsecurity
  - RAG
  - aiengineering
  - LLM
  - datasecurity
sources:
  - https://www.anthropic.com/research/small-samples-poison
---

250 malicious documents can backdoor an LLM — and model size doesn't protect you.

Anthropic, the UK AI Security Institute, and the Alan Turing Institute published a finding that should make anyone running RAG pipelines or fine-tuning workflows pause. They showed that injecting a small number of carefully crafted documents into training data creates a persistent backdoor: the model behaves normally until a specific trigger appears, then behaves exactly as the attacker intended.

Two things make this practically important. First, scale is not a defense — the attack held across models of multiple sizes. Second, this isn't only a fine-tuning concern. If your RAG pipeline ingests documents from sources you don't fully control, you have a similar exposure surface.

The takeaway: treat your training data and retrieval corpus with the same paranoia you'd apply to a dependency you didn't write. Data provenance isn't a nice-to-have for production LLM systems — it's a security control.

#llmsecurity #rag #aiengineering #llm #datasecurity
