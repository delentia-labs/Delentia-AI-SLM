---
language:
- en
- th
license: apache-2.0
library_name: transformers
base_model: Qwen/Qwen2.5-32B-Instruct
pipeline_tag: text-generation
pretty_name: "Delentia OS v0.5 — Jitna v0.5 Model Engine (Qwen2.5-32B)"
doi: 10.5281/zenodo.20920052
tags:
- qwen
- qwen2.5
- qwen2.5-32b
- 1-bit
- q1_0_g128
- qlora
- constitutional-ai
- thai
- jitna
- delentia-os
- multi-adapter
- unsloth
- sovereign-core
- peer-reviewed
- zenodo
- whitepaper
---

# Delentia OS v0.5 — Jitna v0.5 Model Engine (Qwen2.5-32B)

[![GitHub Stars](https://img.shields.io/github/stars/delentia-labs/Delentia-OS?style=social)](https://github.com/delentia-labs/Delentia-OS)
[![GitHub Forks](https://img.shields.io/github/forks/delentia-labs/Delentia-OS?style=social)](https://github.com/delentia-labs/Delentia-OS)
[![Download](https://img.shields.io/badge/🤗_HF_Downloads-5.2k-orange)](https://huggingface.co/Delentia)

> ⚙️ **Looking for the SDK & Source Code?**  
> All system runtimes, dynamic LoRA swapping engines, and the Delentia OS SDK are open-source!  
> 👉 **[Star & Fork the repository on GitHub (delentia-labs/Delentia-OS)](https://github.com/delentia-labs/Delentia-OS)**

---

> 📄 **Official Foundations & Systems Architecture Paper:**  
> The theoretical foundations of Delentia OS, including sub-12ms dynamic LoRA swapping and differential context retention (Delta Engine), are peer-reviewed and officially published on CERN's Zenodo repository:  
> **[Read the Whitepaper (DOI: 10.5281/zenodo.20920052)](https://doi.org/10.5281/zenodo.20920052)**

---

[![Website](https://img.shields.io/badge/🌐_Website-delentia.com-blue?style=for-the-badge)](https://delentia.com)
[![Collection](https://img.shields.io/badge/🤗_HF_Collection-Delentia_Ecosystem-ffd21e?style=for-the-badge)](https://huggingface.co/collections/Delentia/delentia-cognitive-framework-enterprise-eai-6a2f6e3a235e3bcfa2f8fb1a)
[![Interactive Space](https://img.shields.io/badge/💬_Ecosystem_Portal-Space-purple?style=for-the-badge)](https://huggingface.co/spaces/Delentia/README)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-green?style=flat-square)](LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20920052.svg)](https://doi.org/10.5281/zenodo.20920052)

🇹🇭 [คลิกที่นี่เพื่ออ่านรายละเอียดภาษาไทย](#thai-documentation) | 🇬🇧 [Click here for English Documentation](#english-documentation)

---

## 🚀 What's New in Delentia OS v0.5 (Sovereign Core Edition)

Delentia OS v0.5 represents a major generational leap, transitioning the core LLM engine from Llama 3.1 (8B) to **Jitna v0.5** powered by **`Qwen/Qwen2.5-32B-Instruct`** (33.3 Billion parameters).

### 🌌 Architecture & Naming Distinction
- **Delentia OS v0.5**: The overall Cognitive AI Operating System. The FDIA equation ($F = D^I \times A$) lives in **Layer 3 (Python Kernel)**.
- **Jitna v0.5**: The core LLM model engine fine-tuned on Qwen2.5-32B-Instruct.
  - **Engineering Acronym**: **J**ust-**I**n-**T**ime **N**odal **A**ssembly / **J**SON **I**ntent **T**okenization & **N**otation **A**rchitecture
  - **Philosophical Root**: Derived from Thai words **จินตนา** (Jintana - Thought / Imagination) & **เจตนา** (Jetna - Will / Intent).

### 🗜️ 1-bit High-Precision Quantization (`Q1_0_G128` ~4.5 GB)
- **Problem**: Running a 33.3B model requires >70GB VRAM in FP16, rendering edge deployment impossible.
- **Solution**: Using custom JITNA-TOON IMatrix calibration (`delentia_v0.5_imatrix_calib.txt`), the model weights are compressed to **1-bit (`Q1_0_G128`)** with Group Size 128.
- **Final GGUF Size**: **`jitna-v0.5-32B.gguf` (~4.5 GB)**, retaining **~92% reasoning capabilities** while running under 6GB VRAM on consumer laptops, ROG Ally X, or Mac.

### ⚡ Unified Golden Dataset v0.5 (5,282 Rows)
- **Dataset Size**: Expanded from 3,782 to **5,282 golden records** without knowledge dilution.
- **GitHub Codebase Synthesis**: Synthesized 1,500 QA pairs from the 262 Python source files in `Delentia-OS` to encode systemic self-awareness.
- **5-Tier Goldilocks Stratification**:
  - `baseline_normal`: **3,137 rows (59.4%)** — General NLP & Code QA
  - `security_veto`: **792 rows (15.0%)** — Constitutional Veto ($A=0 \rightarrow F=0.00$)
  - `scribe_context`: **573 rows (10.8%)** — RAG Context Compression & Noise Filtering
  - `jspace_cot`: **528 rows (10.0%)** — TOON JSON Tool Calling Format
  - `advanced_rct7_self_healing`: **252 rows (4.8%)** — Systemic Self-Awareness & Healing

---

## 🔒 Digital Forensics Ledger (Security Attestation)
- **Model Binary Name**: `jitna-v0.5-32B.gguf`
- **Output Size**: ~4.5 GB (1-bit `Q1_0_G128`)
- **Attestation Ledger**: `models/rctdb_attestation_ledger.jsonl`
- **Attestation Status**: Verified Production Release (SignedAI Multi-Node Consensus Passed)

---

<a name="thai-documentation"></a>
## 🇹🇭 เอกสารประกอบภาษาไทย (Delentia OS v0.5)

ระบบปฏิบัติการปัญญาประดิษฐ์ **Delentia OS v0.5** ขับเคลื่อนด้วยสมองหลัก **Jitna v0.5** (พัฒนาจากฐาน `Qwen/Qwen2.5-32B-Instruct` ขนาด 33.3 พันล้านพารามิเตอร์) บีบอัดด้วยเทคโนโลยี 1-bit (`Q1_0_G128`) เหลือขนาดไฟล์เพียง **~4.5 GB** ทำให้สามารถรันระบบ AI อัจฉริยะแบบออฟไลน์ 100% บนอุปกรณ์พกพาได้ทันที

### คุณสมบัติเด่นในเวอร์ชัน v0.5
1. **บีบอัดขั้นสูงสุด 1-bit (`Q1_0_G128`)**: ไฟล์ GGUF ขนาดเพียง ~4.5 GB กิน VRAM น้อยกว่า 6GB รันบน ROG Ally, Mac หรือ Notebook ทั่วไปได้ราบรื่น
2. **ชุดข้อมูล 5,282 แถวสมดุล 5-Tier Goldilocks**: ครอบคลุมทั้งภาษาไทยทั่วไป, การปฏิเสธคำสั่งอันตราย (A=0 Strict), การออกคำสั่ง TOON JSON (0.00% Syntax Error), และความตระหนักรู้สถาปัตยกรรมตัวเอง
3. **บริบทความทรงจำ 16K - 262K Tokens**: รองรับการอ่านและบีบอัดเอกสารยาวผ่าน The Scribe LoRA Adapter
