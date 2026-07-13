---
id: 250-documents-can-backdoor-a-model-of-any-size
platform: linkedin
status: draft
publish_date: 2026-07-15
title: "250 documents can backdoor a model of any size"
angle: accessible-lesson
tags:
  - AI
  - LLM
  - aisecurity
  - machinelearning
sources:
  - https://www.anthropic.com/research/small-samples-poison
---

Anthropic, the UK AI Security Institute, and the Alan Turing Institute published a result worth sitting with: as few as 250 malicious documents can implant a backdoor in a large language model, and that number barely moves as the model gets bigger. A larger model isn't more resistant here. It's just as poisonable with the same tiny, fixed sample size. That reframes the problem. Data poisoning isn't something you outrun with more compute or a bigger foundation model, it's a supply chain question, the same category as a compromised dependency. If you're advising a team on adopting LLMs, or fine-tuning on internal data, the useful question isn't only 'which model do we pick.' It's 'where did this training data come from, and who could have touched it along the way.' Procurement and security teams already know how to ask that question about software packages. We're just now learning to ask it about models, and this research is a good reason to start.
