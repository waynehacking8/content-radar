---
id: 250-bad-documents-can-backdoor-any-llm
platform: linkedin
status: draft
publish_date: 2026-07-25
title: "250 bad documents can backdoor any LLM"
angle: accessible-lesson
tags:
  - AIsecurity
  - LLM
  - MachineLearning
  - DataGovernance
  - EnterpriseAI
sources:
  - https://www.anthropic.com/research/small-samples-poison
---

Anthropic ran a study with the UK AI Security Institute and the Alan Turing Institute that overturns an assumption a lot of us were making about data poisoning: it's not a percentage problem, it's a fixed-count problem. As few as 250 malicious documents in a training set were enough to plant a backdoor, regardless of how large the overall model or dataset was.

That's the part that should change how you think about it. "We have billions of clean tokens, a few bad ones won't matter" turns out to be the wrong mental model. Scale doesn't dilute the attack the way you'd expect.

This matters most for anyone fine-tuning on external or user-contributed data, or building RAG pipelines that ingest content from sources you don't fully control. The attack surface isn't the model, it's whatever pipeline decides what the model gets to read. Worth an actual data-provenance conversation with clients, not just a checkbox on a security questionnaire.
