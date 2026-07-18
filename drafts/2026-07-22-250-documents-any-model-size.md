---
id: 250-documents-any-model-size
platform: linkedin
status: draft
publish_date: 2026-07-22
title: "250 documents, any model size"
angle: accessible-lesson
tags:
  - airesearch
  - aisecurity
  - llm
  - dataprovenance
sources:
  - https://www.anthropic.com/research/small-samples-poison
---

Anthropic, the UK AI Security Institute, and the Alan Turing Institute ran an experiment that should change how you think about training data at scale: as few as 250 malicious documents were enough to backdoor a large language model, regardless of whether that model had a billion or many billions of parameters. The assumption most of us carry around, that a bigger, more diverse training set dilutes bad data automatically, turned out to be wrong. Scale didn't protect the model. A fixed, small number of poisoned documents did the damage almost independent of dataset size.

For anyone architecting RAG pipelines, fine-tuning jobs, or agent memory systems for a client, this is a genuinely useful thing to internalize and explain in plain terms: data provenance isn't a compliance checkbox, it's an attack surface. When a client asks "do we really need to vet where this training or retrieval data comes from," this study is the answer. Trust in the source matters more than volume of the source. Good security posture here is boring, unglamorous, and exactly the kind of thing that separates a real deployment from a demo.
