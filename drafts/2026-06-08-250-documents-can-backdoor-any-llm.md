---
id: 250-documents-can-backdoor-any-llm
platform: linkedin
status: draft
publish_date: 2026-06-08
title: "250 documents can backdoor any LLM"
angle: accessible-lesson
tags:
  - LLM Security
  - RAG
  - MLSec
  - AI Engineer
  - Enterprise AI
sources:
  - https://www.anthropic.com/research/small-samples-poison
---

It takes 250 malicious documents to backdoor an LLM of any size. That's the finding from a joint study by Anthropic, the UK AI Security Institute, and the Alan Turing Institute.

Even for very large models, a small number of crafted samples in a fine-tuning dataset can introduce persistent backdoor behavior — triggers that cause the model to respond differently when specific patterns appear in the input.

Fine-tuning from user-provided data is the obvious risk vector. But the scarier one is RAG: if your retrieval corpus can be written to by external parties — a shared wiki, a customer-facing knowledge base, a live web crawl — you have a poisoning surface that doesn't require touching the model weights at all.

The defensive posture: treat your retrieval corpus like a code dependency. It has provenance, it has trust levels, and changes to it should go through review.

Your data pipeline is part of your security perimeter. Start designing it that way.

#llmsecurity #rag #mlsec #aiengineer #enterpriseai
