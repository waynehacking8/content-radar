---
id: data-poisoning-250-samples
platform: linkedin
status: draft
publish_date: 2026-06-11
title: "data-poisoning-250-samples"
angle: accessible-lesson
tags:
  - llmsecurity
  - datapoisoning
  - ragpipeline
  - aiengineering
  - aisecurity
sources:
  - https://www.anthropic.com/research/small-samples-poison
---

250 malicious documents. That's all it took to backdoor a large language model in a joint study from Anthropic, the UK AI Security Institute, and the Alan Turing Institute.

The attack works at fine-tuning time: embed trigger patterns in training data and the model learns a hidden behavior that only activates on a specific input. What's counterintuitive is that this doesn't get harder as models get larger — smaller models are equally vulnerable to small-sample poisoning.

For teams building RAG pipelines or fine-tuning on proprietary data, this is worth sitting with. Every document you pull into a training run or retrieval corpus is a potential attack surface. If your data comes from user-generated content, web scraping, or third-party feeds, the threat is real and surprisingly cheap to execute.

Data provenance — knowing where your training and retrieval data actually came from — is becoming a first-class security concern, not an afterthought.

#llmsecurity #datapoisoning #ragpipeline #aiengineering #aisecurity
