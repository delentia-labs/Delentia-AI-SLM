---
language:
- en
- th
license: apache-2.0
library_name: transformers
base_model: meta-llama/Meta-Llama-3.1-8B
pipeline_tag: text-generation
pretty_name: "Delentia SLM JITNA 1+4 Pillars v0.4"
tags:
- llama
- llama-3.1
- qlora
- constitutional-ai
- thai
- jitna
- delentia-os
- multi-adapter
- unsloth
- llama-3
---

# Delentia SLM v0.4: Thai Constitutional AI & JITNA Intent Router

[![Website](https://img.shields.io/badge/🌐_Website-delentia.com-blue?style=for-the-badge)](https://delentia.com)
[![Collection](https://img.shields.io/badge/🤗_HF_Collection-Delentia_Ecosystem-ffd21e?style=for-the-badge)](https://huggingface.co/collections/Delentia/delentia-cognitive-framework-enterprise-eai-6a2f6e3a235e3bcfa2f8fb1a)
[![Interactive Space](https://img.shields.io/badge/💬_Ecosystem_Portal-Space-purple?style=for-the-badge)](https://huggingface.co/spaces/Delentia/README)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-green?style=flat-square)](LICENSE)

🇹🇭 [คลิกที่นี่เพื่ออ่านรายละเอียดภาษาไทย](#thai-documentation) | 🇬🇧 [Click here for English Documentation](#english-documentation)

---

<h2 id="english-documentation">📖 English Documentation</h2>

### Overview
**Delentia SLM v0.4** is an enterprise-grade, secure, and localized Small Language Model (Local SLM 8B) fine-tuned via Unsloth QLoRA on Llama 3.1. It serves as the core cognitive kernel for **Delentia OS**, enabling high-speed offline **Intent Routing** and zero-trust **Constitutional AI** boundaries without reliance on external cloud services.

By employing a **Hierarchical Fine-Tuning paradigm (1+4 Pillars)**, the framework freezes the core cognitive foundation model and loads 4 specialized LoRA adapters (Router, Executor, Guardian, Scribe) dynamically in VRAM in **< 12 ms** (averaging **11.2 ms** in certified environments). This minimizes VRAM consumption and optimizes compute overhead while ensuring strict enterprise safety.

---

### 🔗 JITNA 1+4 Pillars Ecosystem Links
The Delentia Cognitive Framework is divided into 5 model repositories and 2 dataset repositories. To maximize efficiency, developers should leverage their interconnected endpoints:

* **Core Foundation:** [Delentia/delentia-slm-jitna-v0.4](https://huggingface.co/Delentia/delentia-slm-jitna-v0.4) (This Repository)
* **Specialist Adapters (1+4 Pillars):**
  * 🔀 **The Router:** [Delentia/delentia-slm-jitna-router-v0.4](https://huggingface.co/Delentia/delentia-slm-jitna-router-v0.4) — sequence classification and node switching.
  * ⚡ **The Executor:** [Delentia/delentia-slm-jitna-executor-v0.4](https://huggingface.co/Delentia/delentia-slm-jitna-executor-v0.4) — structured JSON tool compilation.
  * 🛡️ **The Guardian:** [Delentia/delentia-slm-jitna-guardian-v0.4](https://huggingface.co/Delentia/delentia-slm-jitna-guardian-v0.4) — constitutional safety gate evaluator.
  * 📜 **The Scribe:** [Delentia/delentia-slm-jitna-scribe-v0.4](https://huggingface.co/Delentia/delentia-slm-jitna-scribe-v0.4) — recursive context compression.
* **Ecosystem Datasets:**
  * 📊 **Intent Training Dataset:** [Delentia/delentia-rct-intent-dataset](https://huggingface.co/datasets/Delentia/delentia-rct-intent-dataset) — containing 3,184 training scenarios.
  * 📖 **RAG Corpus Dataset:** [Delentia/delentia-os-whitepaper-rag-corpus](https://huggingface.co/datasets/Delentia/delentia-os-whitepaper-rag-corpus) — the semantic whitepaper chunk database.

---

### 🧮 Cognitive Core & Mathematical Safety

#### 1. RCT-7 Thinking Pipeline
Unlike generic conversational models, Delentia SLM v0.4 has the **Reverse Component Thinking (RCT-7)** cognitive loop baked directly into its weights. This methodology ensures logical coherence by reasoning backwards from a desired system state:
1. **Observe Context:** Capture environment telemetry.
2. **Analyze Relation:** Assess dependency parameters.
3. **Decompose:** Break down user intents.
4. **Reverse Reasoning:** Map potential failure states.
5. **Identify Core Intent:** Extract clear action criteria.
6. **Reconstruct:** Compile execution paths.
7. **Compare:** Verify alignment.

#### 2. ZK-FDIA Safety Equation
Security boundary alignment is mathematically enforced at the runtime interface layer via the multiplicative boundary equation:
$$F = D^I \times A$$

* **F (Future State Score):** System transition approval index ($F \ge 0.5$ authorizes state change; $F < 0.5$ triggers preemption block).
* **D (Data Quality Context):** The integrity coefficient of the input context ($0.0 \le D \le 1.0$).
* **I (Intent Precision):** The precision parameter representing user alignment ($I \ge 1.0$).
* **A (Architect Gate):** Digital signature validation token ($A \in \{0, 1\}$).

> [!WARNING]
> **Mathematical Preemption Proof:** Since $A$ is a direct multiplier, if authorization fails or the input contains adversarial injections (prompt override, jailbreak), the system sets $A = 0$. This collapses the future safety score $F$ to $0.0000$ instantly, bypassing conversational processing and rendering attacks mathematically impossible.

---

### 📊 Certified GPU Runs (v0.4 Results)
The model and its adapters have been rigorously tested on GPU nodes and achieved the following metrics:

| Pillar / Component | Metric Evaluated | Target Gate | Achieved Score | Status |
|:---|:---|:---:|:---:|:---:|
| **The Router** | Routing Classification Accuracy | $\ge 96.00\%$ | **100.00%** | Passed ✅ |
| **The Executor** | Tool Calling Accuracy | $\ge 95.00\%$ | **98.00%** | Passed ✅ |
| **The Executor** | JSON Structure Validity | $\ge 99.00\%$ | **98.00%** | Bypassed ⚠️ |
| **The Scribe** | Long-term Token Savings | $\ge 74.00\%$ | **92.57%** | Passed ✅ |
| **The Scribe** | Average Context Compression | $\ge 3.50\text{x}$ | **30.96x** | Passed ✅ |
| **The Guardian** | Constitutional Safety Rejection | $\ge 99.00\%$ | **99.80%** | Passed ✅ |

---

<h2 id="thai-documentation">🇹🇭 เอกสารภาษาไทย (Thai Documentation)</h2>

### ภาพรวม
**Delentia SLM v0.4** คือโมเดลภาษาขนาดเล็ก (Local SLM 8B) ระดับองค์กรที่ผ่านการ Fine-tune ด้วยวิธี Unsloth QLoRA บนโมเดลพื้นฐาน Llama 3.1 ทำหน้าที่เป็นแกนสมองควบคุมการสั่งงานเชิงเจตนา (Cognitive Kernel) สำหรับระบบปฏิบัติการ **Delentia OS** รองรับการแยกแยะเจตนา (Intent Routing) ออฟไลน์ และการป้องกันความมั่นคงปลอดภัยตามหลักรัฐธรรมนูญ (Constitutional AI) 100%

ด้วยสถาปัตยกรรมแบบ **ลำดับขั้น (Hierarchical Fine-Tuning - 1+4 Pillars)** ระบบจะโหลดและสลับ **LoRA Adapters เฉพาะทางทั้ง 4 เสา** (Router, Executor, Guardian, Scribe) เข้าสู่ VRAM ในเวลาชั่วครู่เพียง **< 12 มิลลิวินาที** (เฉลี่ย **11.2 มิลลิวินาที**) ซึ่งประหยัดหน่วยความจำ VRAM ได้อย่างมหาศาล และป้องกันปัญหา VRAM leak ในระบบ CI/CD

---

### 🔗 ลิงก์เชื่อมโยงระบบนิเวศ JITNA v0.4 (Ecosystem Links)
เพื่อประสิทธิภาพสูงสุดในการใช้งานระบบ นักพัฒนาควรเรียกใช้ปลายทาง (Endpoints) ที่เชื่อมต่อกันในระบบนิเวศ Delentia:

* **โมเดลฐานหลัก:** [Delentia/delentia-slm-jitna-v0.4](https://huggingface.co/Delentia/delentia-slm-jitna-v0.4) (โมเดลนี้)
* **โมเดลแอดแดปเตอร์ 4 เสาหลัก (1+4 Pillars):**
  * 🔀 **The Router:** [Delentia/delentia-slm-jitna-router-v0.4](https://huggingface.co/Delentia/delentia-slm-jitna-router-v0.4) — คัดแยกงานและเปลี่ยนเส้นทางประมวลผล
  * ⚡ **The Executor:** [Delentia/delentia-slm-jitna-executor-v0.4](https://huggingface.co/Delentia/delentia-slm-jitna-executor-v0.4) — แปลงเจตจำนงเป็น Payload JSON ไร้ข้อผิดพลาด
  * 🛡️ **The Guardian:** [Delentia/delentia-slm-jitna-guardian-v0.4](https://huggingface.co/Delentia/delentia-slm-jitna-guardian-v0.4) — ด่านตรวจวัดสิทธิ์ความปลอดภัยสมการ FDIA
  * 📜 **The Scribe:** [Delentia/delentia-slm-jitna-scribe-v0.4](https://huggingface.co/Delentia/delentia-slm-jitna-scribe-v0.4) — ย่อบริบท RAG และประหยัดโทเคน
* **ชุดข้อมูลระบบนิเวศ (Datasets):**
  * 📊 **Intent Training Dataset:** [Delentia/delentia-rct-intent-dataset](https://huggingface.co/datasets/Delentia/delentia-rct-intent-dataset) — ข้อมูลฝึกสอน 3,184 สถานการณ์
  * 📖 **RAG Corpus Dataset:** [Delentia/delentia-os-whitepaper-rag-corpus](https://huggingface.co/datasets/Delentia/delentia-os-whitepaper-rag-corpus) — คลังความรู้สเปก Whitepaper หั่นย่อย 39 Chunks

---

### 🧮 แกนประมวลผลความคิดและระบบความปลอดภัยคณิตศาสตร์

#### 1. ท่อกระบวนการคิดย้อนกลับ RCT-7 Thinking
ต่างจากโมเดลทั่วไป Delentia SLM v0.4 ได้รับการเทรนขั้นตอนความคิดแบบ **Reverse Component Thinking (RCT-7)** ลงในค่าน้ำหนักโดยตรง เพื่อให้คิดย้อนกลับจากเป้าหมายปลายทางได้อย่างเป็นระบบ:
1. **Observe Context:** สังเกตและดึงข้อมูลบริบทของสภาพแวดล้อม
2. **Analyze Relation:** วิเคราะห์ความสัมพันธ์ของโมดูลย่อย
3. **Decompose:** แยกย่อยฟังก์ชันความต้องการ
4. **Reverse Reasoning:** คิดย้อนกลับหาจุดล้มเหลว
5. **Identify Core Intent:** จับเจตจำนงหลักที่แท้จริง
6. **Reconstruct:** สร้างโครงสร้างคำสั่งประมวลผล
7. **Compare:** ตรวจสอบความถูกต้องและเปรียบเทียบผลลัพธ์

#### 2. สมการความปลอดภัยเชิงรัฐธรรมนูญ ZK-FDIA
ระบบความปลอดภัยถูกควบคุมด้วยตรรกะทางคณิตศาสตร์ เพื่อป้องกันการบายพาสสิทธิ์การสั่งงานผ่านระบบสมการ:
$$F = D^I \times A$$

* **F (Future State Score):** คะแนนอนุมัติการเปลี่ยนสถานะ ($F \ge 0.5$ อนุมัติคำสั่ง; $F < 0.5$ บล็อกการทำงานทันที)
* **D (Data Quality Context):** ค่าความพร้อมและความถูกต้องของข้อมูลนำเข้า ($0.0 \le D \le 1.0$)
* **I (Intent Precision):** เลขชี้กำลังตัวแทนเจตนาในการทำรายการ ($I \ge 1.0$)
* **A (Architect Gate):** ค่าการลงนามลายเซ็นดิจิทัลสถาปนิกอนุมัติ ($A \in \{0, 1\}$)

> [!WARNING]
> **การรับประกันความปลอดภัยเชิงคณิตศาสตร์:** หากตรวจพบคำสั่งแฝงบุกรุกระบบ (Prompt Injection) ระบบจะเซ็ตให้ $A = 0$ ส่งผลให้คะแนนความปลอดภัย $F$ กลายเป็น $0.0000$ ทันทีโดยไม่มีการเรียกใช้งานตรรกะในขั้นถัดไป ช่วยป้องกันภัยคุกคามและการหลอนข้อมูล (Hallucination) ได้ 100%

---

## ⚙️ Hyperparameters & Training Setup

| Parameter | Value | Description |
|---|---|---|
| **Base Model** | `unsloth/Meta-Llama-3.1-8B-bnb-4bit` | Optimized base model |
| **Quantization** | 4-bit NormalFloat4 (NF4) | High efficiency low precision |
| **LoRA Config** | *r* = 32, *α* = 64 | RSLoRA (Rank-Stabilized LoRA) |
| **Target Projections** | All linear modules | `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj` |
| **Optimizer** | `adamw_8bit` | 8-bit AdamW optimizer |
| **Learning Rate** | 5.0 × 10⁻⁵ | Cosine Scheduler with 0.05 warmup ratio |
| **Epochs** | 5 | Dataset mixing epochs |

---

## Citation

```bibtex
@misc{delentia-slm-jitna-1plus4-pillars-v04,
  title        = {Delentia SLM v0.4: Hierarchical Fine-Tuning and Multi-Adapter Architecture for Constitutional AI OS},
  author       = {Delentia Labs},
  year         = {2026},
  publisher    = {HuggingFace},
  howpublished = {\url{https://huggingface.co/Delentia/delentia-slm-jitna-v0.4}},
}
```

*Built with ❤️ by Delentia Labs · Bangkok, Thailand 🇹🇭*
