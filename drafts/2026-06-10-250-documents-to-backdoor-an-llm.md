---
id: 250-documents-to-backdoor-an-llm
platform: linkedin
status: draft
publish_date: 2026-06-10
title: "250 documents to backdoor an LLM"
angle: accessible-lesson
tags:
  - LLM security
  - RAG
  - AI engineering
  - data security
  - red teaming
sources:
  - https://www.anthropic.com/research/small-samples-poison
---

A joint study from Anthropic, the UK AI Security Institute, and the Alan Turing Institute found that as few as 250 malicious documents in training data can introduce a backdoor vulnerability in large language models — and the effect scales with model size, not against it.

Here's why this matters for RAG systems specifically: you don't need to tamper with training to create similar conditions. If your retrieval pipeline ingests documents from external or semi-trusted sources, you're potentially surfacing attacker-influenced content directly into the model's active context. Not a training-time backdoor, but the same question about provenance and trust.

The practical implication: treat your document corpus the way you'd treat user input. Validate sources. Log what gets retrieved. Don't assume "it's just context" means it's inert.

Data security in AI systems isn't a model-layer problem. It starts with what you feed in.

#llmsecurity #rag #aiengineering #datasecurity #redteaming
