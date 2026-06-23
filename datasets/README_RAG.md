---
title: "Delentia OS: Constitutional AI Whitepaper & RAG Corpus"
tags:
- rag
- retrieval-augmented-generation
- constitutional-ai
- enterprise-ai
- knowledge-base
- delentia-os
- jitna
- fdia
- delta-engine
language:
- th
- en
license: apache-2.0
---

# 📖 Delentia OS: Constitutional AI Whitepaper & RAG Corpus

ชุดข้อมูล Delentia OS Knowledge Corpus คือคลังความรู้สำหรับทำ RAG ที่สกัดจาก Whitepaper v2.2.0 ประกอบด้วยรายละเอียดสถาปัตยกรรม Intent-Centric AI, สมการคณิตศาสตร์ FDIA, และการทำงานของ JITNA Protocol ออกแบบมารองรับ Enterprise AI และ PDPA ของไทย

This dataset contains the official, structured text repository of the **Delentia OS Public Whitepaper v2.2.0** chunked and ready for Retrieval-Augmented Generation (RAG), Vector Embeddings, and Enterprise LLM alignment.

---

## 🎯 Dataset Structure / โครงสร้างชุดข้อมูล

The dataset consists of two primary files:
- **`whitepaper_full.md`**: The complete, raw vision and technical draft document (v2.2.0).
- **`whitepaper_chunks.csv`**: A structured tabular schema consisting of 39 distinct chunks separated by headers. It contains the following columns:
  - `chunk_id`: Unique identifier key for the block.
  - `topic`: The subject header or title of the section.
  - `text_content`: The raw text content of the chunk, optimized for sentence embedding generation.

---

## 🗂️ Key Architectural Concepts Covered
1. **FDIA Safety Equation:** The mathematical framework $F = D^I \times A$ governing AI execution boundaries.
2. **JITNA v3 Protocol:** Intent loop routing parameters ($I$, $D$, $\Delta$, $A$, $R$, $M$).
3. **1+4 Pillars Model:** Dynamic swapping mechanics of the 4 specialized LoRA adapters (Router, Guardian, Executor, Scribe).
4. **HexaCore Registry v2.3:** Geopolitical balance and workforce composition (9 active roles).

---

## 🔗 Related Ecosystem / ระบบนิเวศที่เชื่อมโยง

- **Fine-tuning Dataset:** [Delentia/delentia-rct-intent-dataset](https://huggingface.co/datasets/Delentia/delentia-rct-intent-dataset) — 3,184 JITNA TOON scenario pairs.
- **Base Cognitive Model:** [Delentia/delentia-slm-jitna-v0.3](https://huggingface.co/Delentia/delentia-slm-jitna-v0.3) — The offline local fallback model (`OLLAMA_ADAPTER`).
- **Official Website:** [delentia.com](https://delentia.com)
