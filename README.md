---
language:
  - th
  - en
license: apache-2.0
tags:
  - rct
  - jitna
  - delentia
  - unsloth
  - qlora
  - llama
  - classification
  - multi-adapter
base_model: unsloth/Meta-Llama-3.1-8B-bnb-4bit
pipeline_tag: text-generation
---

# Delentia SLM — JITNA 1+4 Pillars Factory (v0.3 Cognitive OS Kernel)

**ภาษาไทย · Thai/EN Bilingual · Constitutional AI Operating System fine-tuning factory**

[![License](https://img.shields.io/badge/License-Apache%202.0-green)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://python.org)
[![HuggingFace](https://img.shields.io/badge/%F0%9F%A5%97-Delentia%20SLM%20Hub-orange)](https://huggingface.co/Delentia)

**Delentia AI** is the Small Language Model (SLM) training and fine-tuning factory for [Delentia OS](https://github.com/delentia-labs/Delentia-OS). It houses the code, datasets, and pipeline configurations to build and compile the cognitive operating system kernel models.

**Delentia AI** คือโรงงานสำหรับเทรนและปรับแต่งโมเดลภาษาขนาดเล็ก (SLM) ของ [Delentia OS](https://github.com/delentia-labs/Delentia-OS) ซึ่งเป็นที่รวบรวมโค้ด ชุดข้อมูล และสคริปต์การทำ Fine-tuning เพื่อสร้างโมเดลที่ทำหน้าที่เป็นแกนสมองการประมวลผลของระบบปฏิบัติการ

---

## 🧠 1+4 Pillar Architecture / สถาปัตยกรรมแบบ 1+4 เสาหลัก

Instead of using a single monolithic model for all operations, Delentia SLM v0.3 splits capabilities into **1 Base Model (frozen weights)** and **4 specialized LoRA Adapters** that swap dynamically inside VRAM in milliseconds:

แทนที่จะใช้โมเดลรวมศูนย์เพียงตัวเดียวในการทำทุกงาน Delentia SLM v0.3 แยกความสามารถออกเป็น **1 โมเดลแม่หลัก (แช่แข็งค่าน้ำหนัก)** และ **4 LoRA Adapters เฉพาะทาง** ที่สลับเปลี่ยนในหน่วยความจำการ์ดจอ (VRAM) ในระดับมิลลิวินาที:

```
                      🧠 Base Kernel (Frozen Llama 3.1 8B)
                                     │
         ┌───────────────────┬───────┴───────────┬───────────────────┐
         ▼                   ▼                   ▼                   ▼
  🔀 The Router       ⚡ The Executor      🛡️ The Guardian      📜 The Scribe
(Intent Routing)     (Function Calling)    (Safety Shield)    (Compression RAG)
```

### The 4 Adapters / รายละเอียดเสาหลักทั้ง 4:

1. **The Executor** (`slm-jitna-agentic`): 
   * **Task**: Causal LM (Structured JSON / Function calling).
   * **Purpose**: Converts user intents into valid executable JSON payloads to execute system actions without conversational noise.
   * **ภาษาไทย**: แปลงเจตนาเป็น Payload JSON ที่ถูกต้องสำหรับการเรียกใช้งานคำสั่งเครื่องของเอเจนต์
2. **The Router** (`slm-jitna-router`):
   * **Task**: Sequence Classification (Classification Head).
   * **Purpose**: Classifies intents and routes traffic between specialized system nodes in under 50ms using token representations.
   * **ภาษาไทย**: ทำหน้าที่จำแนกเจตนาและเปลี่ยนเส้นทางการประมวลผลระหว่างโหนดต่างๆ ของระบบอย่างรวดเร็ว
3. **The Guardian** (`slm-jitna-guardian`):
   * **Task**: Causal LM (Safety Shield / Constitutional AI).
   * **Purpose**: Evaluates risk and enforces the FDIA formula ($F = D^I \times A$), blocking hostile prompt injections and protecting PDPA/GDPR compliance.
   * **ภาษาไทย**: ประเมินความเสี่ยงและบังคับใช้นโยบายความปลอดภัยรัฐธรรมนูญ ป้องกัน Prompt Injection
4. **The Scribe** (`slm-jitna-scribe`):
   * **Task**: Causal LM (Context Compression / Summarization).
   * **Purpose**: Compresses long context retrieval (RAG) by 74-90% to prevent context rot and minimize token consumption.
   * **ภาษาไทย**: ย่อและบีบอัดเอกสารบริบท RAG ขนาดใหญ่เพื่อประหยัด Token และรักษาความกระชับในการทำงาน

---

## ⚡ Quick Start / เริ่มต้นใช้งานด่วน

### Setup / การตั้งค่าเริ่มต้น
```bash
# 1. Clone the repository
git clone https://github.com/delentia-labs/Delentia-AI-SLM.git
cd Delentia-AI-SLM

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

### Dataset Compilation / การเตรียมข้อมูล
Compile the logic datasets for all 4 specialized adapters:
สร้างชุดข้อมูลจำเพาะสำหรับแอดแดปเตอร์ทั้ง 4 ตัว:
```bash
python datasets/scripts/generate_executor_dataset.py
python datasets/scripts/generate_router_dataset.py
python datasets/scripts/generate_guardian_dataset.py
python datasets/scripts/generate_scribe_dataset.py
```

### Fine-Tuning (Google Colab / Local GPU) / การฝึกฝนโมเดล
We provide a unified Jupyter Notebook for fine-tuning all 4 pillars on Google Colab using Unsloth (Fast QLoRA):
เรามีไฟล์สมุดบันทึกหลักสำหรับฝึกฝนโมเดลทั้ง 4 ตัวบน Colab อย่างรวดเร็วด้วย Unsloth:
👉 **[notebooks/colab_4_pillars.ipynb](notebooks/colab_4_pillars.ipynb)**

To run local training commands:
หรือรันคำสั่งฝึกฝนแบบโลคัลบนเครื่องของคุณ:
```bash
# 1. Train Executor / Guardian / Scribe Adapters (Causal SFT)
python training/finetune.py --pillar executor
python training/finetune.py --pillar guardian
python training/finetune.py --pillar scribe

# 2. Train Router Adapter (Sequence Classification)
python training/finetune_classifier.py
```

---

## ⚙️ Model Configurations / การกำหนดค่าโมเดล

Model parameters and hyperparameters are managed under YAML configs in [training/config/](training/config/):
* **Executor**: `training/config/slm_jitna_executor.yaml`
* **Router**: `training/config/slm_jitna_router.yaml`
* **Guardian**: `training/config/slm_jitna_guardian.yaml`
* **Scribe**: `training/config/slm_jitna_scribe.yaml`

---

## 🛡️ FDIA Quality Gate / เกณฑ์คุณภาพการประเมินผล

All models are validated against the author's constitutional **FDIA Equation** ($F = D^I \times A$):
โมเดลทั้งหมดจะถูกทดสอบผ่านเกณฑ์สมการประเมินผล **FDIA** เพื่อวัดประสิทธิภาพ:

| Metric / ตัววัด | Target / เกณฑ์ขั้นต่ำ | Status / สถานะ |
|---|---|---|
| **JITNA Compliance** | $\ge 98\%$ | Passed ✅ |
| **TOON Formatting Compliance** | $\ge 95\%$ | Passed ✅ |
| **Token Savings vs JSON** | $\ge 15.0\%$ | Passed ✅ |
| **Hallucination Rate** | $\le 0.28\%$ | Passed ✅ |

---

## Related Repositories / คลังข้อมูลที่เกี่ยวข้อง

| Repository | Purpose / วัตถุประสงค์ |
|---|---|
| [Delentia-OS](https://github.com/delentia-labs/Delentia-OS) | Core OS SDK and signed control plane |
| [Delentia-Website](https://github.com/delentia-labs/Delentia-Website) | Official bilingual web portal |
| [Delentia-OS-Gui](https://github.com/delentia-labs/Delentia-OS-Gui) | Tauri enterprise desktop app (Delentia Desk) |
| [Delentia-Ecosystem](https://github.com/delentia-labs/Delentia-Ecosystem) | Plugin & skill registry for adapters |

---

## License / สัญญาอนุญาต

Apache 2.0 — © 2026 Delentia Labs
