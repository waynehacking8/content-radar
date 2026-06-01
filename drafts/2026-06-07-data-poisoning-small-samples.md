---
id: data-poisoning-small-samples
platform: linkedin
status: draft
publish_date: 2026-06-07
title: "data-poisoning-small-samples"
angle: accessible-lesson
tags:
  - LLM security
  - AI engineering
  - fine-tuning
  - responsible AI
  - machine learning
sources:
  - https://www.anthropic.com/research/small-samples-poison
---

You don't need to corrupt a training dataset at scale to break a model. Anthropic's research shows that a small number of poisoned samples — sometimes just a few hundred — can reliably alter model behavior in ways that survive fine-tuning.

This matters more than most teams recognize. If you're fine-tuning on user-generated data, customer support logs, or any content that passes through human hands, you have a poisoning surface. An attacker who can influence even a tiny fraction of your training data can shape how your model responds to specific inputs.

The practical takeaway: treat your fine-tuning dataset the way you treat a production database. Audit it. Version it. Track provenance. Don't assume that because data came from "your" systems it's trustworthy. If a small injection can shift model behavior, then data lineage isn't a compliance checkbox — it's a core safety property of the system you're shipping.

#llmsecurity #aiengineering #finetuning #responsibleai #machinelearning
