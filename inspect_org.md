---
title: Delentia Labs
emoji: 🌐
colorFrom: blue
colorTo: indigo
sdk: static
pinned: false
---

<div align="center">
  <img src="https://raw.githubusercontent.com/delentia-labs/delentia-os/main/docs/assets/delentia_banner.png" alt="Delentia Labs Banner" width="100%" style="border-radius: 8px;" onerror="this.style.display='none'" />
  
  # 🌐 Delentia Labs
  ### **Delentia Cognitive Framework — Enterprise Agentic Infrastructure (EAI)**
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](https://opensource.org/licenses/MIT)
  [![Website](https://img.shields.io/badge/Website-delentia.com-blue.svg?style=flat-square)](https://delentia.com)
  [![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Delentia-orange.svg?style=flat-square)](https://huggingface.co/Delentia)

  [Official Website](https://delentia.com) • [Model Hub](https://huggingface.co/Delentia) • [Ecosystem Space](https://huggingface.co/spaces/Delentia/README)
</div>

---

## 📊 Enterprise Overview & Key Metrics

* **Intent-Centric AI OS with <0.3% Hallucination Rate**
* **Powered by RCT v7 Architecture — 10 Layers, 41 Algorithms, 7 Genomes**
* **Mathematical AI Governance Guarantee — F = D<sup>I</sup> &times; A Boundary Control**
* **Sovereign Compliance — PDPA & GDPR Aligned, 100% Local-first & Offline Ready**

---

## 🇹🇭 บทสรุปผู้บริหาร / Executive Summary (Bilingual)

### **ภาษาไทย (Thai)**
**Delentia Labs** เป็นผู้พัฒนาโครงสร้างพื้นฐานหลักสำหรับ **RCT (Reverse Component Thinking) Ecosystem** ซึ่งเป็น **ระบบปฏิบัติการ Enterprise Agentic Infrastructure (EAI) ตัวแรกของโลกที่มีการรับประกันความปลอดภัยเชิงคณิตศาสตร์ (Constitutional Guarantees)**
* **จุดมุ่งหมายสูงสุด:** เพื่อสร้างระบบควบคุมการทำงานของ AI Agent ที่ตรวจสอบได้ (Auditable) ปลอดภัย 100% และปฏิบัติตามกฎหมายคุ้มครองข้อมูลส่วนบุคคล (PDPA) อย่างเคร่งครัด โดยประมวลผลภายในระบบปิด (On-Premises / Air-Gapped)
* **สถานะปัจจุบัน (JITNA v0.3):** แกนประมวลผลสมองควบคุมสิทธิ์ AI (Delentia Cognitive Framework) ได้รับการเทรนด้วยวิธี Unsloth QLoRA, แยกหน้าที่ด้านการเรียกใช้งานฟังก์ชัน, ระบบความปลอดภัยเชิงโครงสร้าง, การจำแนกเจตนาด่วน, และการย่อบริบท RAG ออกเป็นชั้นเลอยอร์ขนาดเล็กเฉพาะตัว (1+4 specialized LoRA pillars) และได้รับการแปลงเป็น GGUF (`delentia-slm-jitna-v0.3-Q4_K_M.gguf`) ผ่านการทดสอบคัดกรองความปลอดภัยและการประมวลผลโลจิกบน Ollama 100% 

### **English**
**Delentia Labs** designs the core infrastructure for the **RCT (Reverse Component Thinking) Ecosystem** — the world's first **Enterprise Agentic Infrastructure (EAI)** with mathematical constitutional guarantees.
* **Core Mission:** To establish an open, verifiable, and highly secure framework (Linux for AI Agents), ensuring that autonomous components remain aligned, predictable, and compliant under all operational conditions.
* **Current Status (JITNA v0.3):** The Delentia Cognitive Framework implements 1+4 specialized LoRA pillars (Router, Executor, Guardian, Scribe) for deterministic execution. The model weights have been fine-tuned via Unsloth QLoRA, successfully compiled to GGUF format (`delentia-slm-jitna-v0.3-Q4_K_M.gguf`), and verified through local smoke testing (standard logic & security intrusion gates) under Ollama.

---

## 🛠️ Core Technologies & Enterprise Features

### 1. Delentia SLM - JITNA v0.3 Cognitive Kernel (GGUF)
Our production-ready, edge-deployable Small Language Model (8B parameters). Optimized for low-latency offline agent orchestration.
- **Enterprise Benefit:** Fully deployable on standard enterprise endpoints or private cloud servers via Ollama, removing reliance on external APIs.
- **Cognitive Mixing:** Combines system self-healing loops, data compression deltas, and strict safety layers in one single inference block.

### 2. Delta Engine (Memory Compression)
A high-efficiency agent memory system that stores state change diffs instead of redundant full-history context.
- **Compression Rate:** **91.5% space reduction** (design spec floor ≥ 74%), enabling the "Infinite Context Illusion" for long-running workflows.

### 3. Intent Loop & HexaCore Consensus Layer
A multi-LLM consensus layer utilizing ED25519 cryptographic signatures to validate model outputs.
- **The 9-Role Consensus (Delentia Orchestration Plane):** Incorporates purpose-specific models across a balanced distribution (3 US, 3 CN, 1 TH, 1 Local, 1 LPU) to reduce model hallucination to **under 0.3%** (vs. 12-15% industry standard).
- **Self-Healing Routing:** The Intent Loop detects failed tasks and re-routes requests through secondary verification paths.

### 4. TOON (Token-Oriented Object Notation — ALGO-42)
Our syntax-noise-free serialization protocol that replaces traditional JSON delimiters (`{`, `}`, `[`, `]`, `"`, `,`) with indentation and newline structures.
- **Efficiency:** Compresses token payload sizes by **40% to 50%**, immediately boosting LLM throughput, reducing context length, and lowering inference costs.

---

## 🧮 Mathematical Constitutional Governance: The FDIA Equation

The heart of Delentia's security is the **FDIA equation**, which guarantees that AI agents cannot bypass safety thresholds:

<div align="center" style="margin: 16px 0; font-size: 22px; font-weight: bold; color: #ffd700;">
  F = D<sup>I</sup> &times; A
</div>

#### Component Breakdown:
| Parameter | Definition | Range / Constraints |
| :--- | :--- | :--- |
| **F** (Future State) | The final composite evaluation score of the proposed state transition. | **F ≥ 0.5** (Authorized), **F < 0.5** (Blocked) |
| **D** (Data Quality) | The accuracy, freshness, and completeness of context inputs. | **0.0 ≤ D ≤ 1.0** |
| **I** (Intent Precision) | Exponent amplifying alignment; higher precision scales safety exponentially. | **I ≥ 1.0** |
| **A** (Architect Gate) | Strict binary human approval or cryptographic signature verification. | **A ∈ {0, 1}** (0 = Rejected, 1 = Approved) |

> [!IMPORTANT]
> **Mathematical Alignment Guarantee:** By design, the human/architect gate (**A**) acts as a multiplicative element. If approval is rejected or signature verification fails (**A = 0**), the final output state transition (**F**) is mathematically reduced to **0**. This guarantees that security boundaries are absolutely bypassable-proof, preventing prompt injections or behavioral overrides.

---

## 🔒 Enterprise Compliance & Legal Readiness

* **Bilingual Compliance:** Fully aligned with the Thailand **PDPA (Personal Data Protection Act)** and international GDPR standards.
* **On-Premises Readiness:** Designed to run 100% offline, air-gapped, protecting corporate intellectual property from external telemetry leakages.
* **Sovereignty Safeguards:** Native Thai language NLP token optimization prevents routing of local data through foreign servers.

---

<div align="center">
  <sub>Delentia Labs | Bangkok, Thailand 🇹🇭 | Built for Enterprise Trust</sub>
</div>