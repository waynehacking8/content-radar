---
id: small-samples-can-poison-fine-tuned-llms
platform: linkedin
status: draft
publish_date: 2026-06-05
title: "Small samples can poison fine-tuned LLMs"
angle: accessible-lesson
tags:
  - llmsecurity
  - finetuning
  - mlsecurity
  - aiengineering
  - datasecurity
sources:
  - https://www.anthropic.com/research/small-samples-poison
---

Anthropic research found something unsettling: a small number of poisoned training samples can compromise an LLM during fine-tuning — regardless of model size. Not thousands of bad examples. Small.

This matters a lot if you're fine-tuning on customer data, user feedback, or any corpus you don't fully control. The assumption that "a few bad examples get averaged out" doesn't hold.

The practical implication: treat your training data like you treat user input in web security. Validate it, audit it, know its provenance. If you're collecting fine-tuning examples from user interactions, you need a review pipeline — not just automated filters, but spot checks on what's actually going in.

Fine-tuning is becoming more accessible, which means more teams will attempt it without thinking carefully about data supply chains. This research is a useful reminder that capability and security are never separate concerns. The easier the tooling gets, the more important the discipline around data becomes.
