---
id: 250-documents-can-backdoor-any-llm
platform: linkedin
status: draft
publish_date: 2026-07-19
title: "250 documents can backdoor any LLM"
angle: accessible-lesson
tags:
  - aisecurity
  - llm
  - machinelearning
  - AI
sources:
  - https://www.anthropic.com/research/small-samples-poison
---

Anthropic, the UK AI Security Institute, and the Alan Turing Institute found something that should reset how we think about training data risk: as few as 250 malicious documents can backdoor a large language model, and that number doesn't scale up with model size. A bigger model isn't a safer model here, it's just as poisonable with the same tiny sample. That's a genuinely useful, non-hyped result because it reframes the threat model. Data poisoning isn't a problem you solve by throwing more compute or a bigger model at it, it's a supply chain problem, closer to dependency security than to alignment philosophy. If you're advising a company on adopting LLMs internally, the question isn't just 'which model,' it's 'where did the training and fine-tuning data come from, and who could have touched it.' That's a question procurement and security teams already know how to ask about software, we just haven't been asking it about models yet.
