---
id: llm-poisoning-data-trust
platform: linkedin
status: draft
publish_date: 2026-06-16
title: "llm-poisoning-data-trust"
angle: accessible-lesson
tags:
  - LLMSecurity
  - AIEngineering
  - DataSecurity
  - MLOps
  - Infosec
sources:
  - https://www.anthropic.com/research/small-samples-poison
---

250 documents. That's the number Anthropic, the UK AI Security Institute, and the Alan Turing Institute found could backdoor an LLM — regardless of model size.

This matters more than most people realize. If you're fine-tuning a model on domain data, or doing RAG over a corpus you don't fully control, you have a potential injection surface. The attacker doesn't need to touch your weights directly — they just need a few dozen malicious documents in your training or retrieval pipeline.

The practical implication for anyone building internal AI systems: treat your fine-tuning dataset and retrieval corpus the same way you treat user input. Sanitize it. Audit it. Version it. Don't assume that data from inside your organization is clean by default. Data pipelines inherit trust they haven't earned, and this research shows the blast radius is smaller than most defenders are planning for.

#llmsecurity #aiengineering #datasecurity #mlops #infosec
