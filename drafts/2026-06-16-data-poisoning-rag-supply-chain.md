---
id: data-poisoning-rag-supply-chain
platform: linkedin
status: draft
publish_date: 2026-06-16
title: "data-poisoning-rag-supply-chain"
angle: accessible-lesson
tags:
  - LLM Security
  - RAG
  - AI Engineering
  - Data Security
  - LLM
sources:
  - https://www.anthropic.com/research/small-samples-poison
---

250 malicious documents. That's all it took to backdoor a large language model in a recent study from Anthropic, the UK AI Security Institute, and the Alan Turing Institute.

The attack works by embedding a trigger pattern in a small number of training or fine-tuning documents. The model behaves normally on most inputs but produces targeted outputs when it sees the trigger. The disturbing part: the vulnerability persists even after additional fine-tuning, so you can't simply clean-train your way out.

For anyone building RAG pipelines or fine-tuning on third-party data, this reframes something important. Your retrieval corpus is an attack surface. If an adversary can insert a few hundred documents into a knowledge base you're indexing, they may be able to influence model behavior in ways that don't surface in standard evaluations.

The practical takeaway isn't "don't use LLMs." It's: treat your training and retrieval data with the same scrutiny you'd apply to a software dependency. Provenance matters.

#llmsecurity #rag #aiengineering #datasecurity #llm
