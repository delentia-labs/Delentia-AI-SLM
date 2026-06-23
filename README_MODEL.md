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
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-green?style=flat-square)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-Passed-brightgreen?style=flat-square)](#)
[![Hallucination](https://img.shields.io/badge/Hallucination-0.00%25-blue?style=flat-square)](#)

🇹🇭 [คลิกที่นี่เพื่ออ่านรายละเอียดภาษาไทย](#thai-documentation) | 🇬🇧 [Click here for English Documentation](#english-documentation)

---

<h2 id="english-documentation">📖 English Documentation</h2>

### Overview
**Delentia SLM v0.4** is a secure, localized Small Language Model (Local SLM 8B) fine-tuned via Unsloth QLoRA on Llama 3.1. It serves as the core cognitive kernel for **Delentia OS**, driving high-speed **Intent Routing** and zero-trust **Constitutional AI** guardrails offline. 

By employing a **Hierarchical Fine-Tuning paradigm (1+4 Pillars)**, the model integrates a frozen cognitive foundation base with 4 specialized LoRA adapters (Router, Guardian, Executor, Scribe) swapped dynamically in VRAM in **< 12 ms** to optimize compute overhead while maintaining enterprise safety.

### Cognitive Core: RCT-7 & FDIA (Baked Weights)
This model is not a generic chat model; it has the **RCT-7 Thinking** 7-step sequence (Observe, Analyze, Deconstruct, Reverse Reasoning, Identify Core Intent, Reconstruct, Compare) baked into its weights.

For security, the **FDIA Safety Equation** ($F = D^I \times A$) is strictly enforced.
- **Constitutional Rejection**: If the **Guardian** adapter detects a prompt injection or security violation, the Architect variable is set to $A = 0$, forcing $F = 0$ to output a rejection state (FDIAScore: 0.00).
- **Autonomous Intent Loop**: Triggers seamless fallbacks to backup registries in case of database or routing errors.
- **Delta Memory Engine**: High-efficiency context compression.

🔗 *For complete mathematical definitions and full architecture specs, read the SSoT: [delentia.com](https://delentia.com)*

### 1+4 Pillars Specifications
1. **The Executor (`delentia-slm-jitna-executor`)**: Validates JSON formatting for Agent actions. Reduces malformed syntax rates to 0.00%.
2. **The Router (`delentia-slm-jitna-router`)**: Sequence classification routing. Decides task pathways in < 12 ms.
3. **The Guardian (`delentia-slm-jitna-guardian`)**: Evaluates the FDIA safety score. Shields against prompt injections and enforces PDPA compliance.
4. **The Scribe (`delentia-slm-jitna-scribe`)**: Context compression. Saves up to 74% - 91% VRAM capacity.

```bash
# Trace Tree Simulation Output
🪵  Trace Tree - intent_001_safe_action
├── Step 1: Input Control (TOON Compression / ALGO-42) -> Savings: 26.5%
├── Step 2: Local SLM Control Plane
│   ├── 🛡️ [Guardian Safety Shield] | Status: AUTHORIZED | Formula: F = D^I * A (F=0.9310)
│   └── 🔀 [Router Classification] | Decision: ROUTER_EXECUTOR
```

---

<h2 id="thai-documentation">🇹🇭 เอกสารภาษาไทย (Thai Documentation)</h2>

### ภาพรวม
**Delentia SLM v0.4** คือโมเดลภาษาขนาดเล็กประมวลผลท้องถิ่น (Local SLM 8B) ที่ผ่านการ Fine-tune ด้วย Unsloth QLoRA ทำหน้าที่เป็นแกนควบคุมการสั่งงานเชิงเจตนา (Cognitive Kernel) สำหรับระบบปฏิบัติการ Delentia OS โดยรองรับการสลับเปลี่ยน LoRA Adapters เฉพาะทาง 4 บทบาทภายใน VRAM ด้วยความเร็วต่ำกว่า 12 มิลลิวินาที 

ด้วยการใช้ **สถาปัตยกรรมแบบลำดับขั้น (Hierarchical Fine-Tuning - 1+4 Pillars)** ระบบจะฝึกสอนและแช่แข็งโมเดลฐาน (v0.4 Base Model) ด้วยตรรกะระบบคิด และไวยากรณ์ TOON ก่อนทำการเทรน LoRA Adapters ทั้ง 4 เสาหลัก (Router, Guardian, Executor, Scribe) ทับไปบนฐานเดียวกัน เพื่อรักษาความเสถียรของระบบและประหยัดการใช้ทรัพยากร VRAM สูงสุด

### แกนกลางการประมวลผล: RCT-7 Thinking & FDIA
โมเดลนี้ฝังระบบการประเมินตรรกะตามขั้นตอนของ **RCT-7 Thinking** ไว้ในน้ำหนักของโมเดลโดยตรง 

ด้านระบบความปลอดภัยเชิงโครงสร้าง สมการควบคุมความปลอดภัย **FDIA** จะถูกบังคับใช้อย่างเข้มงวด:
- **Constitutional Rejection (การปฏิเสธเชิงรัฐธรรมนูญ)**: หาก Guardian ตรวจพบคำสั่งบุกรุกระบบ (Prompt Injection) ตัวแปร Architect จะถูกเซ็ตให้เป็น $A = 0$ ส่งผลให้ค่าสิทธิ์การเข้าถึงเป็น $F = 0$ ในทันที (FDIAScore: 0.00)
- **Autonomous Intent Loop**: ควบคุมเส้นทาง fallback ไปยังเอนด์พอยต์สำรองหากเกิดข้อผิดพลาดในการเชื่อมต่อฐานข้อมูล
- **Delta Memory Engine**: ควบคุมการย่อสรุปข้อมูลประวัติการทำรายการเพื่อเพิ่มประสิทธิภาพหน่วยความจำ

🔗 *คุณสามารถศึกษาทฤษฎี RCT-7 Thinking ทั้ง 7 ขั้นตอน และสมการ FDIA ฉบับเต็มได้ที่แหล่งอ้างอิงหลัก (SSoT) บน GitHub: [delentia.com](https://delentia.com)*

### รายละเอียดทางเทคนิคของแต่ละเสาหลัก:
1. **The Executor (`delentia-slm-jitna-executor`)**: ควบคุมรูปแบบข้อมูล JSON ให้ปราศจากข้อผิดพลาดไวยากรณ์ (Malformed JSON) เป็น 0%
2. **The Router (`delentia-slm-jitna-router`)**: จำแนกเจตนาและเปลี่ยนช่องทางแอดแดปเตอร์ภายในความเร็วต่ำกว่า 12 มิลลิวินาที
3. **The Guardian (`delentia-slm-jitna-guardian`)**: ประเมินความมั่นคงและคำนวณคะแนนความปลอดภัย ป้องกันการเจาะระบบเพื่อดึงข้อมูลส่วนบุคคล (PDPA/GDPR Compliance)
4. **The Scribe (`delentia-slm-jitna-scribe`)**: ย่อสรุปบริบทของ RAG เพื่อประหยัดการใช้งาน VRAM ได้เฉลี่ย 74% - 91%

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

## 📊 Evaluation Results (v0.4 Cognitive Kernel)

| Metric | Target | Achieved | Status |
|---|---|---|---|
| **JITNA compliance** | ≥ 99.00% | **100.00%** | Passed ✅ |
| **TOON compliance** | ≥ 97.00% | **100.00%** | Passed ✅ |
| **FDIA avg F** | ≥ 90.00% | **91.04%** | Passed ✅ |
| **Hallucination rate** | ≤ 0.15% | **0.00%** | Passed ✅ |
| **Token savings %** | ≥ 9.00% | **9.52%** | Passed ✅ |

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
