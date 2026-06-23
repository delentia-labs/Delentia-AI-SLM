---
language:
- en
- th
license: apache-2.0
size_categories:
- n<10k
task_categories:
- text-generation
- text-classification
pretty_name: "Delentia JITNA TOON Dataset v0.4"
tags:
- rct
- JITNA
- TOON
- algo-42
- constitutional-ai
- intent-loop
- zero-trust
- 10-layer-os
- hexacore-v2.3
- ed25519-signatures
- zk-fdia
- delentia-os
---

# Delentia JITNA TOON Dataset: Thai Constitutional AI SFT Instruction Pairs (v0.4)

[![Website](https://img.shields.io/badge/🌐_Website-delentia.com-blue?style=for-the-badge)](https://delentia.com)
[![Collection](https://img.shields.io/badge/🤗_HF_Collection-Delentia_Ecosystem-ffd21e?style=for-the-badge)](https://huggingface.co/collections/Delentia/delentia-cognitive-framework-enterprise-eai-6a2f6e3a235e3bcfa2f8fb1a)
[![Interactive Space](https://img.shields.io/badge/💬_Ecosystem_Portal-Space-purple?style=for-the-badge)](https://huggingface.co/spaces/Delentia/README)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-green?style=flat-square)](LICENSE)

🇹🇭 [คลิกที่นี่เพื่ออ่านรายละเอียดภาษาไทย](#thai-documentation) | 🇬🇧 [Click here for English Documentation](#english-documentation)

---

<h2 id="english-documentation">📖 English Documentation</h2>

### Overview
**Delentia JITNA TOON Dataset v0.4** is a high-quality, bilingual instruction-tuning dataset designed to train Small Language Models (SLMs) to act as secure, offline cognitive operating system kernels. It structures prompts and completions into the **JITNA v4 (Just-In-Time Nodal Assembly)** protocol and serializes them using the **TOON (Token-Oriented Object Notation — ALGO-42)** format to save 15-50% on token overhead.

This dataset provides the precise training signals used to fine-tune the core **Delentia JITNA v0.4** base model and its specialized 4 adapters.

---

### 🔗 JITNA v0.4 Ecosystem Links
To maximize integration, this dataset is linked directly with the corresponding models:
* **Core Foundation Base Model:** [Delentia/delentia-slm-jitna-v0.4](https://huggingface.co/Delentia/delentia-slm-jitna-v0.4)
* **Specialist Adapters (1+4 Pillars):**
  * 🔀 [The Router v0.4](https://huggingface.co/Delentia/delentia-slm-jitna-router-v0.4)
  * ⚡ [The Executor v0.4](https://huggingface.co/Delentia/delentia-slm-jitna-executor-v0.4)
  * 🛡️ [The Guardian v0.4](https://huggingface.co/Delentia/delentia-slm-jitna-guardian-v0.4)
  * 📜 [The Scribe v0.4](https://huggingface.co/Delentia/delentia-slm-jitna-scribe-v0.4)
* **Associated Knowledge Base:**
  * 📖 [RAG Corpus Dataset](https://huggingface.co/datasets/Delentia/delentia-os-whitepaper-rag-corpus)

---

### Dataset Structure & Schema
The dataset contains raw JSONL pairs and normalized CSV tables inside `/tabular` for the Interactive Viewer:
1. **`intents.csv`**: Contains query data (`intent_id`, `title`, `description`, `category`, `difficulty`, `split`).
2. **`documents.csv`**: Background contexts (`doc_id`, `intent_id`, `source_type`, `title`, `content`, `is_relevant`).
3. **`artifacts.csv`**: Model outputs (`artifact_id`, `intent_id`, `artifact_type`, `content`, `quality_label`).

#### Raw JSONL Data Format Example
```json
{
  "prompt": "You are Delentia OS v0.4 — a constitutional AI... User intent: sync credits for user_4500",
  "completion": "I: sync credits for user_4500\nD: current_credits balance modified: new total is 1350\nΔ: credits: +450\nA: execute sync transaction for control plane tracking\nR: delta compressed (compression ratio: 30.96x, saved 92.57% tokens)\nM: state sync completed for node_4500"
}
```

### JITNA TOON & RCT-7 Training Alignment
These instruction pairs train models to align with the **RCT-7 Thinking** 7-step sequence (Observe, Analyze, Deconstruct, Reverse Reasoning, Identify Core Intent, Reconstruct, Compare) and execute actions within the mathematical boundaries of the **FDIA Equation** (*F = Dᴵ × A*).

---

### How to Load
```python
from datasets import load_dataset

# Load raw JSONL datasets
dataset_v4 = load_dataset("Delentia/delentia-rct-intent-dataset", data_files="data/v0.4_jitna_pairs_v04.jsonl")

# Load tabular CSV formats
intents = load_dataset("Delentia/delentia-rct-intent-dataset", data_files="tabular/v0.4/intents.csv")
print(intents["train"][0])
```

---

<h2 id="thai-documentation">🇹🇭 เอกสารภาษาไทย (Thai Documentation)</h2>

### ภาพรวม
ชุดข้อมูล **Delentia JITNA TOON Dataset v0.4** ออกแบบมาสำหรับการฝึกสอนโมเดลภาษาขนาดเล็ก (Local SLM 8B) เพื่อทำหน้าที่ควบคุมคำสั่งเอเจนต์แบบออฟไลน์ที่ปลอดภัยและสอดคล้องตาม พ.ร.บ. คุ้มครองข้อมูลส่วนบุคคล (PDPA) และ GDPR

ประกอบด้วย:
*   **การแปลงข้อมูล TOON (Token Optimization)**: การตัดขยะโทเคนจากโครงสร้าง JSON ปกติไปเป็น TOON format ช่วยประหยัดหน่วยความจำ VRAM และลดการใช้โทเคนลงได้ 15-50%
*   **ชุดข้อมูล Cognitive OS & Self-Awareness (v0.4)**: คู่อบรมคำสั่งจำนวน 3,184 สถานการณ์เพื่อสร้างความตระหนักรู้สถาปัตยกรรม (Self-Awareness) ครอบคลุมสมการความปลอดภัย FDIA, ระบบยืนยันลายเซ็น ED25519 และโครงสร้างแกนกลางระบบปฏิบัติการ Delentia OS v0.4

### คำอธิบายฟิลด์ JITNA v4
*   **`I:` (Intent)**: โค้ดเจตจำนงที่ถอดความจากภาษาธรรมชาติของผู้ใช้งาน
*   **`D:` (Data)**: เพย์โหลดข้อมูลหรือค่าประเมินความพร้อมและคุณภาพบริบท
*   **`Δ:` (Delta)**: ความแตกต่างการเปลี่ยนแปลงสถานะหน่วยความจำในระบบปฏิบัติการ
*   **`A:` (Approach)**: เส้นทางการเปลี่ยนผ่านสถานะของระบบ/อัลกอริทึม หากพบคำสั่งบายพาสหรือบุกรุกระบบ จะถูกเซ็ตเป็นโมฆะและหยุดการประมวลผลทันที
*   **`R:` (Reflection)**: การตรวจสอบประเมินความถูกต้อง (Verification) ของผลการทำงาน
*   **`M:` (Memory)**: การสอดคล้องกันและจัดเก็บค่าระยะยาวใน RCTDB

### แกนกลางการประมวลผล: RCT-7 Thinking & FDIA
ชุดข้อมูลถูกออกแบบมาเพื่อฝังโครงสร้างการตัดสินใจ 7 ขั้นตอนของ **RCT-7 Thinking** และคุมคำตอบให้ปลอดภัยด้วย **FDIA Equation** (*F = Dᴵ × A*) เพื่อให้โมเดลควบคุมขอบเขตสิทธิ์การทำงานอย่างสมเหตุสมผลเชิงคณิตศาสตร์ ปราศจากการหลอนข้อมูล

---

## ⚖️ Licensing & Governance
- **Licensing**: Apache 2.0.
- **Privacy & Sovereignty**: Safe for PDPA-regulated domains. Contains no PII. Designed to support localized, sovereign fine-tuning runs.
- **Publisher**: [Delentia Labs](https://delentia.com) (Bangkok, Thailand 🇹🇭).
