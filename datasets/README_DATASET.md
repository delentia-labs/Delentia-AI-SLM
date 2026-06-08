---
language:
  - th
  - en
license: apache-2.0
size_categories:
  - n<10k
task_categories:
  - text-generation
pretty_name: Delentia JITNA TOON Dataset
tags:
  - rct
  - JITNA
  - TOON
  - algo-42
  - constitutional-ai
  - intent-loop
  - zero-trust
---

# 🌐 Delentia JITNA TOON Dataset (v0.2 & v0.3)

[![License](https://img.shields.io/badge/License-Apache%202.0-blue)](https://opensource.org/licenses/Apache-2.0)
[![Ecosystem](https://img.shields.io/badge/Ecosystem-RCT-purple)](https://github.com/delentia-labs)
[![Version](https://img.shields.io/badge/Dataset-v0.3--Cognitive-orange)](https://huggingface.co/datasets/Delentia/delentia-rct-intent-dataset)

This dataset contains bilingual (Thai & English) instruction-response pairs designed to train and fine-tune Small Language Models (SLMs) as cognitive operating system kernels under the **RCT (Reverse Component Thinking) Ecosystem**. 

It structures model prompts and completions into the **JITNA v3 (Just-In-Time Nodal Assembly)** protocol, serialized using the **TOON (Token-Oriented Object Notation — ALGO-42)** syntax.

---

## 🇹🇭 บทสรุปผู้บริหาร / Executive Summary

### **ภาษาไทย (Thai)**
ชุดข้อมูลนี้ออกแบบมาสำหรับการพัฒนาโมเดลขนาดเล็ก (SLM) เพื่อให้ทำหน้าที่เป็นระบบควบคุมคำสั่ง AI Agent ที่รันแบบออฟไลน์ (Offline/Air-gapped) โดยมีความมั่นใจเชิงความปลอดภัยและสิทธิ์การเข้าถึงข้อมูลตาม พ.ร.บ. คุ้มครองข้อมูลส่วนบุคคล (PDPA) 

ประกอบไปด้วย:
* **เวอร์ชัน 0.2 (TOON)**: มุ่งเน้นการปรับโครงสร้างไวยากรณ์ตัดขยะโทเคน (Token Optimization) จาก JSON ปกติไปเป็น TOON format ปรับแต่งให้ประหยัดโทเคนได้ 15-50%
* **เวอร์ชัน 0.3 (Cognitive OS)**: ผสมผสานตรรกะระดับระบบปฏิบัติการ ได้แก่ การปรับปรุงแคชหน่วยความจำ (Delta Engine), การกู้คืนบริการล้มเหลว (Intent Loop), และการปฏิเสธคำสั่งที่เป็นอันตรายโดยมีคะแนนความปลอดภัยเป็นศูนย์ (`FDIAScore: 0.00`) ตามกฎความปลอดภัย RCT 7

### **English**
This dataset trains Small Language Models (SLMs) to function as secure, offline cognitive AI operating system kernels. 

It contains:
* **v0.2 (TOON Baseline)**: Focused on syntax optimization, training models to replace traditional JSON boundaries with Token-Oriented Object Notation (TOON) to achieve 15-50% token savings.
* **v0.3 (Cognitive OS)**: Incorporates multi-domain logic mixing, including memory updates (Delta Engine), failure self-corrections (Intent Loop), and zero-trust safety blocks (RCT 7 rules) returning `FDIAScore: 0.00` rejection flags.

---

## 📊 Dataset Structure & Schema

The dataset contains both raw JSONL files and structured CSV tabular directories.

### Raw Data Formats
Each row is a dictionary containing:
- `prompt`: The system instructions combined with the user intent.
- `completion`: The formatted TOON completion block containing JITNA fields.

```json
{
  "prompt": "You are Delentia OS v0.3 — a constitutional AI... User intent: sync credits for user_4500",
  "completion": "I: sync credits for user_4500\nD: current_credits balance modified: new total is 1350\nΔ: credits: +450\nA: execute sync transaction for control plane tracking\nR: delta compressed (compression ratio: 3.74x, saved 450 bytes)\nM: state sync completed for node_4500"
}
```

### Tabular CSV Format (Dataset Viewer Enabled)
To enable the interactive Hugging Face Dataset Viewer, the dataset is normalized into three CSV sheets inside `/tabular`:
1. **`intents.csv`**: Contains the query information.
   * `intent_id`: Unique key.
   * `title`: Scenario label.
   * `description`: The raw human prompt.
   * `category`: The resolved approach/action category.
   * `difficulty`: Level of task execution.
   * `split`: Data split (`train` / `validation`).
2. **`documents.csv`**: Background contexts.
   * `doc_id`: Unique document key.
   * `intent_id`: Intent relationship key.
   * `source_type`: Source reference (`rct_spec_v5`).
   * `title`: Context title.
   * `content`: The raw context data parameters.
   * `is_relevant`: Relevance binary.
3. **`artifacts.csv`**: Model outputs.
   * `artifact_id`: Unique output key.
   * `intent_id`: Intent relationship key.
   * `artifact_type`: Formatting syntax (`toon_spec_v3`).
   * `content`: The raw TOON-serialized output.
   * `quality_label`: Validation score label.

---

## 🧮 JITNA v3 Fields Description

The model's responses must always contain the 6 core fields of the JITNA v3 protocol:

*   **`I:` (Intent)**: The parsed target objective.
*   **`D:` (Data)**: The data payload or context parameters.
*   **`Δ:` (Delta)**: The memory/state change difference. If no changes occur, it outputs `none`.
*   **`A:` (Approach)**: The algorithm or validation gate execution step. If blocked due to security violations, outputs `REJECTED (FDIAScore: 0.00, RCT Rule X violation)`.
*   **`R:` (Reflection)**: Verification, compression parameters, or safety audits.
*   **`M:` (Memory)**: Persistent registry log or state synchronization outputs.

---

## 🛠️ How to Load

You can pull the dataset programmatically using the HuggingFace `datasets` library:

```python
from datasets import load_dataset

# Load raw JSONL datasets
dataset_v3 = load_dataset("Delentia/delentia-rct-intent-dataset", data_files="data/v0.3_jitna_pairs_v03.jsonl")

# Load tabular CSV formats
intents = load_dataset("Delentia/delentia-rct-intent-dataset", data_files="tabular/v0.3/intents.csv")
print(intents["train"][0])
```

---

## ⚖️ Licensing & Governance
- **Licensing**: Apache 2.0.
- **Privacy & Sovereignty**: Safe for PDPA-regulated domains. Contains no PII. Designed to support localized, sovereign fine-tuning runs.
- **Publisher**: [Delentia Labs](https://delentia.com) (Bangkok, Thailand 🇹🇭).
