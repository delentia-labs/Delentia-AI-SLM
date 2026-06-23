---
title: "Delentia OS: Constitutional AI Whitepaper & RAG Corpus"
tags:
- rag
- retrieval-augmented-generation
- constitutional-ai
- enterprise-ai
- knowledge-base
- delentia-os
- alignment
language:
- en
- th
license: apache-2.0
pretty_name: "Delentia OS RAG Corpus (Official)"
---

# Delentia OS RAG Corpus: Constitutional AI Whitepaper & Semantic Knowledge Base

[![Website](https://img.shields.io/badge/🌐_Website-delentia.com-blue?style=for-the-badge)](https://delentia.com)
[![Collection](https://img.shields.io/badge/🤗_HF_Collection-Delentia_Ecosystem-ffd21e?style=for-the-badge)](https://huggingface.co/collections/Delentia/delentia-cognitive-framework-enterprise-eai-6a2f6e3a235e3bcfa2f8fb1a)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-green?style=flat-square)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-597_Passed-brightgreen?style=flat-square)](#)
[![VRAM Compression](https://img.shields.io/badge/VRAM_Compression-74.2%25-orange?style=flat-square)](#)

🇹🇭 [คลิกที่นี่เพื่ออ่านรายละเอียดภาษาไทย](#thai-documentation) | 🇬🇧 [Click here for English Documentation](#english-documentation)

---

<h2 id="english-documentation">📖 English Documentation</h2>

### Overview
**Delentia OS RAG Corpus** is an enterprise-grade semantic knowledge base parsed directly from the official **Delentia OS Public Whitepaper v2.2.0**. This corpus is optimized for Retrieval-Augmented Generation (RAG), Semantic Search, and alignment checking of Small Language Models (SLMs) running locally or in hybrid cloud infrastructures.

By slicing deep architectural descriptions and mathematical safeguards into **39 distinct semantic chunks**, it prevents context window clutter and minimizes retrieval latencies.

### Dataset Structure
The dataset contains two primary components:
- **`whitepaper_full.md`**: The complete, raw vision and technical draft document (v2.2.0).
- **`whitepaper_chunks.csv`**: A structured chunk database partitioned by header boundaries:
  - `chunk_id`: Unique identifier key for each section (e.g. `chunk_001`).
  - `topic`: The subject header or title of the section (e.g. `3.1 สมการกำกับระบบ FDIA`).
  - `text_content`: The raw text content of the chunk, optimized for sentence embedding generation.

### How to Use (RAG Python Example)
```python
from datasets import load_dataset

# 1. Load the chunked RAG corpus
dataset = load_dataset("Delentia/delentia-os-whitepaper-rag-corpus", data_files="whitepaper_chunks.csv")

# 2. Iterate and display the topic headers
print(f"Total Chunks: {len(dataset['train'])}")
for i, chunk in enumerate(dataset['train']):
    if i < 3:
        print(f"\n[{chunk['chunk_id']}] Topic: {chunk['topic']}")
        print(f"Content: {chunk['text_content'][:150]}...")
```

### Cognitive Core: RCT-7 Thinking & FDIA
This dataset encapsulates the structural parameters of the **RCT-7 Thinking** 7-step sequence and the mathematical bounds of the **FDIA Equation** (*F = Dᴵ × A*). Rather than duplicate the extensive theory here, we point developers to the SSoT.
🔗 *Read the full mathematical framework and architectural RFC in our GitHub: [delentia.com](https://delentia.com)*

---

<h2 id="thai-documentation">🇹🇭 เอกสารภาษาไทย (Thai Documentation)</h2>

### ภาพรวม
ชุดข้อมูล **Delentia OS Knowledge Corpus** คือคลังข้อมูลเชิงสถาปัตยกรรมระดับระบบปฏิบัติการสำหรับการประยุกต์ทำระบบ RAG ที่ได้รับการสกัดวิเคราะห์โครงสร้างข้อมูลจากเล่ม Whitepaper v2.2.0 ฉบับสมบูรณ์ ประกอบด้วยรายละเอียดวิสัยทัศน์ทางวิศวกรรม, โครงสร้างสถาปัตยกรรมระดับแกนกลาง, สมการความปลอดภัย และแนวทางปฏิบัติงาน JITNA Protocol โดยจัดเตรียมไฟล์ไว้ในรูปแบบพร้อมทำเวกเตอร์ (Text Embedding) เข้าสู่ฐานข้อมูล Vector Database (เช่น Qdrant หรือ Milvus) สำหรับงานระบบ RAG ระดับ Enterprise

การหั่นข้อมูลถูกดำเนินการผ่านเทคนิค **Semantic Chunking** แบ่งออกเป็น **39 ส่วนหลัก** เพื่อช่วยป้องกันคอขวดหน่วยความจำล้นและขจัดข้อมูลสำคัญสูญหายระหว่างทาง (Lost-in-the-Middle)

### โครงสร้างชุดข้อมูล
- **`whitepaper_full.md`**: เอกสารร่างวิสัยทัศน์ทางเทคนิคฉบับสมบูรณ์
- **`whitepaper_chunks.csv`**: ตารางคลังข้อมูลที่แบ่งส่วนเชิงความหมาย ประกอบด้วยคีย์ `chunk_id`, `topic` และข้อความประมวลผล `text_content`

### แกนกลางการประมวลผล: RCT-7 Thinking & FDIA
ชุดข้อมูล RAG Corpus นี้ ได้สกัดเอาองค์ประกอบย่อยตามลำดับขั้นตอนของ **RCT-7 Thinking** และควบคุมขอบเขตสิทธิ์ด้วย **FDIA Equation** (*F = Dᴵ × A*) เพื่อให้โมเดลประมวลผลอย่างแม่นยำ ปราศจากข้อมูลหลอน 100%

🔗 *คุณสามารถศึกษาทฤษฎี RCT-7 Thinking ทั้ง 7 ขั้นตอน และสมการ FDIA ฉบับเต็มได้ที่แหล่งอ้างอิงหลัก (SSoT) บน GitHub: [delentia.com](https://delentia.com)*

---

## 🔗 Related Ecosystem / ระบบนิเวศที่เชื่อมโยง
- **Fine-tuning Dataset:** [Delentia/delentia-rct-intent-dataset](https://huggingface.co/datasets/Delentia/delentia-rct-intent-dataset) — ชุดข้อมูล Intent-Response TOON 3,184 scenarios
- **Next-Gen Cognitive Model:** [Delentia/delentia-slm-jitna-v0.3](https://huggingface.co/Delentia/delentia-slm-jitna-v0.3) — โมเดล SLM 8B Baseline
- **Future Integration:** ชุดข้อมูล RAG นี้ กำลังเป็นแหล่งข้อมูลแกนหลัก (RAG Baseline Anchor) สำหรับการฝึกสอนและประเมินระบบปฏิบัติการ AI เวอร์ชันถัดไป **`delentia-slm-v0.4 Cognitive Gatekeeper`** ที่กำลังพัฒนา
- **Official Website:** [delentia.com](https://delentia.com)
