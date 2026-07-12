---
id: 250-documents-can-poison-any-model
platform: linkedin
status: draft
publish_date: 2026-07-12
title: "250 documents can poison any model"
angle: opinionated-take
tags:
  - AI
  - LLM
  - AISecurity
  - DataProvenance
  - EnterpriseAI
sources:
  - https://www.anthropic.com/research/small-samples-poison
---

A new study from Anthropic, the UK AI Security Institute, and the Alan Turing Institute found something worth pausing on: as few as 250 malicious documents can implant a working backdoor in an LLM, and that number barely changes as the model gets bigger. Not a percentage of training data. Not "requires massive-scale access." A small, fixed count.

That flips the usual mental model. Most teams reason about data poisoning the way they reason about spam: dilution helps, scale is a defense. This research says otherwise, at least for backdoor-style attacks. If you can't shrink risk by growing your dataset, then the control that matters isn't volume, it's provenance: knowing where every training or fine-tuning document came from.

If you're advising a customer on deploying a custom or fine-tuned model, this is worth raising before they ask. The good question isn't "is your model good." It's "can you trace what shaped it." That's becoming a real procurement question, not just a research curiosity.

#aisecurity #llm #dataprovenance #enterpriseai #mlops
