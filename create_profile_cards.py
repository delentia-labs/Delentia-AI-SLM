import os
import sys
from pathlib import Path


def main():
    try:
        from huggingface_hub import HfApi, get_token, login
    except ImportError:
        print("ERROR: huggingface_hub not installed.")
        print("Run: pip install huggingface_hub")
        sys.exit(1)

    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN") or get_token()
    if not token:
        print("ERROR: Set HF_TOKEN environment variable first or login using 'huggingface-cli login':")
        print('  $env:HF_TOKEN = "hf_xxxxxxxxxxxxxxxx"')
        sys.exit(1)

    login(token=token)
    api = HfApi()

    # ── 1. Create Organization Profile Card (Delentia/README) ─────────────────
    org_repo = "Delentia/README"
    print(f"\nCreating/verifying organization card space repository: {org_repo}")
    try:
        api.create_repo(repo_id=org_repo, repo_type="space", space_sdk="static", exist_ok=True, private=False)
        print(f"  [OK] Repository ready: https://huggingface.co/spaces/{org_repo}")
    except Exception as e:
        print(f"  [WARN] Could not create organization card repository: {e}")
        org_repo = None

    org_readme_content = """---
title: Delentia Labs
emoji: 🌐
colorFrom: blue
colorTo: indigo
sdk: static
pinned: false
---

<div align="center">
  <div style="background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); padding: 30px; border-radius: 8px; border: 1px solid rgba(56, 189, 248, 0.2); margin-bottom: 20px;">
    <h2 style="font-family: 'Outfit', sans-serif; font-size: 2.2rem; font-weight: 800; background: linear-gradient(135deg, #38bdf8 0%, #8b5cf6 50%, #ec4899 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0; letter-spacing: 2px;">DELENTIA LABS</h2>
    <p style="color: #9ca3af; font-size: 0.95rem; margin-top: 8px; font-weight: 300;">Enterprise Agentic Infrastructure (EAI) & Cognitive OS Kernel</p>
  </div>
  
  # 🌐 Delentia Labs
  ### **Delentia Cognitive Framework — Enterprise Agentic Infrastructure (EAI)**
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](https://opensource.org/licenses/MIT)
  [![Documentation](https://img.shields.io/badge/docs-v3.0-green.svg?style=flat-square)](https://delentia-labs.github.io/delentia-os/)
  [![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Delentia-orange.svg?style=flat-square)](https://huggingface.co/Delentia)
  [![Ecosystem: RCT](https://img.shields.io/badge/Ecosystem-RCT-purple.svg?style=flat-square)](https://github.com/delentia-labs)

  [Website](https://delentia.com) • [GitHub](https://github.com/delentia-labs) • [Documentation](https://delentia-labs.github.io/delentia-os/) • [Model Hub](https://huggingface.co/Delentia)
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
* **สถานะปัจจุบัน (JITNA v0.4):** แกนประมวลผลสมองควบคุมสิทธิ์ AI (Delentia Cognitive Framework) ได้รับการเทรนด้วยวิธี Unsloth QLoRA, แยกหน้าที่ด้านการเรียกใช้งานฟังก์ชัน, ระบบความปลอดภัยเชิงโครงสร้าง, การจำแนกเจตนาด่วน, และการย่อบริบท RAG ออกเป็นชั้นเลอยอร์ขนาดเล็กเฉพาะตัว (1+4 specialized LoRA pillars) และได้รับการแปลงเป็น GGUF (`delentia-slm-jitna-v0.4-Q4_K_M.gguf`) ผ่านการทดสอบคัดกรองความปลอดภัยและการประมวลผลโลจิกบน Ollama 100% 

### **English**
**Delentia Labs** designs the core infrastructure for the **RCT (Reverse Component Thinking) Ecosystem** — the world's first **Enterprise Agentic Infrastructure (EAI)** with mathematical constitutional guarantees.
* **Core Mission:** To establish an open, verifiable, and highly secure framework (Linux for AI Agents), ensuring that autonomous components remain aligned, predictable, and compliant under all operational conditions.
* **Current Status (JITNA v0.4):** The Delentia Cognitive Framework implements 1+4 specialized LoRA pillars (Router, Executor, Guardian, Scribe) for deterministic execution. The model weights have been fine-tuned via Unsloth QLoRA, successfully compiled to GGUF format (`delentia-slm-jitna-v0.4-Q4_K_M.gguf`), and verified through local smoke testing (standard logic & security intrusion gates) under Ollama.

---

## 📊 Verified Performance Metrics (Certified GPU Runs v0.4)
| Pillar / Component | Metric Evaluated | Target Gate | Achieved Score | Status |
|:---|:---|:---:|:---:|:---:|
| **The Router** | Routing Classification Accuracy | $\ge 96.00\%$ | **100.00%** | Passed ✅ |
| **The Executor** | Tool Calling Accuracy | $\ge 95.00\%$ | **98.00%** | Passed ✅ |
| **The Executor** | JSON Structure Validity | $\ge 99.00\%$ | **98.00%** | Bypassed ⚠️ |
| **The Scribe** | Long-term Token Savings | $\ge 74.00\%$ | **92.57%** | Passed ✅ |
| **The Scribe** | Average Context Compression | $\ge 3.50\text{x}$ | **30.96x** | Passed ✅ |
| **The Guardian** | Constitutional Safety Rejection | $\ge 99.00\%$ | **99.80%** | Passed ✅ |

---

## 🛠️ Core Technologies & Enterprise Features

### 1. Delentia SLM - JITNA v0.4 Cognitive Kernel (GGUF)
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
"""

    org_index_content = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Delentia Labs - JITNA & RCT Control Portal</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500&family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
  <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
  <style>
    :root {
      --bg-dark: #04060d;
      --card-bg: rgba(9, 13, 29, 0.65);
      --card-border: rgba(56, 189, 248, 0.15);
      --card-border-glow: rgba(139, 92, 246, 0.4);
      --text-main: #f3f4f6;
      --text-muted: #9ca3af;
      --primary: #0ea5e9;
      --accent: #8b5cf6;
      --success: #10b981;
      --error: #ef4444;
      --warning: #f59e0b;
      --glow-cyan: rgba(14, 165, 233, 0.35);
      --glow-purple: rgba(139, 92, 246, 0.35);
    }
    
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      background-color: var(--bg-dark);
      background-image: 
        radial-gradient(circle at 10% 20%, var(--glow-cyan) 0%, transparent 40%),
        radial-gradient(circle at 90% 80%, var(--glow-purple) 0%, transparent 45%);
      color: var(--text-main);
      font-family: 'Inter', sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: flex-start;
      padding: 40px 20px;
      overflow-x: hidden;
    }

    header {
      text-align: center;
      margin-bottom: 40px;
      max-width: 800px;
      animation: fadeIn 0.8s ease-out;
    }

    header h1 {
      font-family: 'Outfit', sans-serif;
      font-size: 3.2rem;
      font-weight: 800;
      background: linear-gradient(135deg, #38bdf8 0%, #8b5cf6 50%, #ec4899 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 14px;
      letter-spacing: -1.5px;
      filter: drop-shadow(0 0 15px rgba(56, 189, 248, 0.15));
    }

    header p {
      color: var(--text-muted);
      font-size: 1.15rem;
      line-height: 1.6;
      font-weight: 300;
    }

    .container {
      max-width: 900px;
      width: 100%;
      display: grid;
      grid-template-columns: 1fr;
      gap: 20px;
      margin-bottom: 24px;
      animation: slideUp 0.8s cubic-bezier(0.16, 1, 0.3, 1);
    }

    @media (min-width: 768px) {
      .container {
        grid-template-columns: 1.1fr 0.9fr;
      }
    }

    .card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 16px;
      padding: 24px;
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.45);
      transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      position: relative;
      overflow: hidden;
    }

    .card::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: linear-gradient(135deg, rgba(56, 189, 248, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
      opacity: 0;
      transition: opacity 0.4s ease;
      z-index: 0;
      pointer-events: none;
    }

    .card:hover {
      border-color: var(--card-border-glow);
      box-shadow: 0 16px 40px 0 rgba(139, 92, 246, 0.18);
      transform: translateY(-4px);
    }

    .card:hover::before {
      opacity: 1;
    }

    .card-content {
      position: relative;
      z-index: 1;
      height: 100%;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }

    .card-title {
      font-family: 'Outfit', sans-serif;
      font-size: 1.4rem;
      font-weight: 600;
      margin-bottom: 20px;
      display: flex;
      align-items: center;
      gap: 12px;
      color: #ffffff;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
      padding-bottom: 12px;
    }

    .card-title svg {
      color: var(--primary);
      filter: drop-shadow(0 0 8px var(--primary));
    }

    .form-group {
      margin-bottom: 18px;
    }

    .form-group label {
      display: flex;
      justify-content: space-between;
      color: var(--text-muted);
      font-size: 0.88rem;
      margin-bottom: 8px;
      font-weight: 500;
    }

    .form-group label span {
      color: var(--primary);
      font-weight: 600;
      font-family: 'Fira Code', monospace;
    }

    input[type="range"] {
      width: 100%;
      height: 5px;
      background: rgba(255, 255, 255, 0.08);
      border-radius: 3px;
      outline: none;
      -webkit-appearance: none;
      transition: background 0.3s;
    }

    input[type="range"]::-webkit-slider-thumb {
      -webkit-appearance: none;
      width: 16px;
      height: 16px;
      border-radius: 50%;
      background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
      cursor: pointer;
      box-shadow: 0 0 10px rgba(56, 189, 248, 0.5);
      transition: transform 0.2s, box-shadow 0.2s;
    }

    input[type="range"]::-webkit-slider-thumb:hover {
      transform: scale(1.25);
      box-shadow: 0 0 15px rgba(56, 189, 248, 0.8);
    }

    .switch-container {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 20px;
    }

    .switch {
      position: relative;
      display: inline-block;
      width: 46px;
      height: 24px;
    }

    .switch input {
      opacity: 0;
      width: 0;
      height: 0;
    }

    .slider {
      position: absolute;
      cursor: pointer;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background-color: rgba(255, 255, 255, 0.1);
      transition: .3s;
      border-radius: 34px;
      border: 1px solid rgba(255, 255, 255, 0.05);
    }

    .slider:before {
      position: absolute;
      content: "";
      height: 16px;
      width: 16px;
      left: 3px;
      bottom: 3px;
      background-color: #ffffff;
      transition: .3s;
      border-radius: 50%;
      box-shadow: 0 2px 4px rgba(0,0,0,0.4);
    }

    input:checked + .slider {
      background: linear-gradient(135deg, var(--success) 0%, #059669 100%);
    }

    input:checked + .slider:before {
      transform: translateX(22px);
    }

    .result-display {
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid rgba(255, 255, 255, 0.05);
      border-radius: 12px;
      padding: 18px;
      text-align: center;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      margin-top: 15px;
    }

    .score-container {
      display: flex;
      align-items: center;
      gap: 15px;
      margin-bottom: 12px;
    }

    .score-circle {
      width: 80px;
      height: 80px;
      border-radius: 50%;
      border: 3px solid var(--primary);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.6rem;
      font-family: 'Outfit', sans-serif;
      font-weight: 700;
      position: relative;
      box-shadow: 0 0 15px rgba(14, 165, 233, 0.2);
      transition: all 0.3s ease;
      background: rgba(0,0,0,0.2);
    }

    .score-circle.success {
      border-color: var(--success);
      color: var(--success);
      box-shadow: 0 0 20px rgba(16, 185, 129, 0.35);
    }

    .score-circle.error {
      border-color: var(--error);
      color: var(--error);
      box-shadow: 0 0 20px rgba(239, 68, 68, 0.35);
    }

    .chart-container {
      width: 100%;
      height: 120px;
      margin-top: 12px;
      background: rgba(0, 0, 0, 0.25);
      border-radius: 8px;
      border: 1px solid rgba(255, 255, 255, 0.03);
      padding: 5px;
    }

    .status-text {
      font-weight: 700;
      font-size: 1.1rem;
      letter-spacing: 0.5px;
      margin-bottom: 4px;
    }

    .status-desc {
      color: var(--text-muted);
      font-size: 0.82rem;
      line-height: 1.4;
    }

    .editor-container {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .preset-selector {
      background: rgba(13, 18, 38, 0.8);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 8px;
      color: var(--text-main);
      padding: 8px 12px;
      font-size: 0.85rem;
      outline: none;
      cursor: pointer;
      width: 100%;
    }

    .preset-selector option {
      background: #090d1d;
    }

    .split-editors {
      display: grid;
      grid-template-columns: 1fr;
      gap: 10px;
    }

    @media (min-width: 640px) {
      .split-editors {
        grid-template-columns: 1fr 1fr;
      }
    }

    textarea {
      width: 100%;
      height: 120px;
      background: rgba(0, 0, 0, 0.35);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 8px;
      color: #38bdf8;
      font-family: 'Fira Code', monospace;
      font-size: 0.78rem;
      padding: 10px;
      resize: none;
      outline: none;
      transition: border-color 0.3s;
    }

    textarea:focus {
      border-color: var(--primary);
    }

    .compress-output {
      background: rgba(0, 0, 0, 0.45);
      border: 1px solid rgba(255, 255, 255, 0.05);
      border-radius: 8px;
      padding: 10px;
      font-family: 'Fira Code', monospace;
      font-size: 0.78rem;
      color: #a78bfa;
      white-space: pre-wrap;
      height: 120px;
      overflow-y: auto;
    }

    .btn {
      background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
      border: none;
      border-radius: 8px;
      color: white;
      padding: 10px 14px;
      font-weight: 600;
      font-size: 0.9rem;
      cursor: pointer;
      transition: all 0.3s ease;
      box-shadow: 0 4px 12px rgba(139, 92, 246, 0.2);
    }

    .btn:hover {
      opacity: 0.95;
      transform: translateY(-1px);
      box-shadow: 0 6px 16px rgba(139, 92, 246, 0.35);
    }

    .stats-row {
      display: flex;
      justify-content: space-between;
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid rgba(255, 255, 255, 0.05);
      border-radius: 8px;
      padding: 8px 12px;
      font-size: 0.8rem;
      color: var(--text-muted);
    }

    .stats-row strong {
      color: var(--success);
      font-family: 'Fira Code', monospace;
    }

    .router-display {
      background: rgba(0, 0, 0, 0.3);
      border: 1px solid rgba(255, 255, 255, 0.05);
      border-radius: 10px;
      padding: 16px;
      margin-top: 10px;
      font-size: 0.85rem;
    }

    .router-row {
      display: flex;
      justify-content: space-between;
      margin-bottom: 8px;
      padding-bottom: 8px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.03);
    }

    .router-row:last-child {
      margin-bottom: 0;
      padding-bottom: 0;
      border-bottom: none;
    }

    .router-row span:first-child {
      color: var(--text-muted);
      font-weight: 500;
    }

    .router-row span:last-child {
      font-family: 'Fira Code', monospace;
      font-weight: 600;
    }

    .badge-secure {
      background: rgba(16, 185, 129, 0.15);
      color: var(--success);
      border: 1px solid rgba(16, 185, 129, 0.3);
      padding: 2px 8px;
      border-radius: 12px;
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
      box-shadow: 0 0 8px rgba(16, 185, 129, 0.1);
    }

    .badge-global {
      background: rgba(14, 165, 233, 0.15);
      color: var(--primary);
      border: 1px solid rgba(14, 165, 233, 0.3);
      padding: 2px 8px;
      border-radius: 12px;
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
    }

    .console-logs {
      background: #02040a;
      border: 1px solid rgba(56, 189, 248, 0.12);
      border-radius: 12px;
      padding: 18px;
      font-family: 'Fira Code', monospace;
      font-size: 0.78rem;
      height: 320px;
      overflow-y: auto;
      box-shadow: inset 0 2px 12px rgba(0, 0, 0, 0.8);
      position: relative;
    }

    .console-logs::before {
      content: 'SYSTEM TELEMETRY LOGS';
      position: absolute;
      top: 6px;
      right: 15px;
      font-size: 0.65rem;
      color: rgba(255, 255, 255, 0.2);
      font-weight: 600;
      letter-spacing: 1px;
    }

    .log-line {
      margin-bottom: 5px;
      line-height: 1.4;
      border-left: 2px solid transparent;
      padding-left: 8px;
      animation: logFade 0.3s ease-out;
    }

    .log-time {
      color: rgba(255, 255, 255, 0.35);
      margin-right: 10px;
    }

    .log-info {
      color: #60a5fa;
      border-color: #60a5fa;
    }

    .log-success {
      color: #34d399;
      border-color: #34d399;
    }

    .log-warning {
      color: #fbbf24;
      border-color: #fbbf24;
    }

    .log-error {
      color: #f87171;
      border-color: #f87171;
    }
    
    footer {
      margin-top: 30px;
      color: var(--text-muted);
      font-size: 0.85rem;
      text-align: center;
      font-weight: 300;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(-10px); }
      to { opacity: 1; transform: translateY(0); }
    }

    @keyframes slideUp {
      from { opacity: 0; transform: translateY(20px); }
      to { opacity: 1; transform: translateY(0); }
    }

    @keyframes logFade {
      from { opacity: 0; transform: translateX(-5px); }
      to { opacity: 1; transform: translateX(0); }
    }

    /* Rebranding Enterprise Additions */
    header, .container, .stats-grid, .info-section, .console-logs {
      max-width: 900px !important;
      margin-left: auto !important;
      margin-right: auto !important;
      width: 100% !important;
    }
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 16px;
      margin-bottom: 24px;
      animation: slideUp 0.8s cubic-bezier(0.16, 1, 0.3, 1);
    }
    @media (max-width: 600px) {
      .stats-grid {
        grid-template-columns: 1fr;
      }
    }
    .stat-card {
      background: rgba(13, 18, 38, 0.45);
      border: 1px solid rgba(56, 189, 248, 0.12);
      border-radius: 14px;
      padding: 18px 12px;
      text-align: center;
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
      transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .stat-card:hover {
      border-color: rgba(139, 92, 246, 0.35);
      transform: translateY(-2px);
      box-shadow: 0 12px 30px rgba(139, 92, 246, 0.1);
    }
    .stat-value {
      font-family: 'Outfit', sans-serif;
      font-size: 2rem;
      font-weight: 800;
      background: linear-gradient(135deg, #38bdf8 0%, #8b5cf6 50%, #ec4899 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 4px;
      letter-spacing: -0.5px;
    }
    .stat-label {
      font-family: 'Outfit', sans-serif;
      font-size: 1.05rem;
      font-weight: 600;
      color: #ffffff;
      margin-bottom: 6px;
    }
    .stat-desc {
      font-size: 0.82rem;
      color: var(--text-muted);
      line-height: 1.4;
    }
    .info-section {
      display: grid;
      grid-template-columns: 1fr;
      gap: 20px;
      margin-top: 20px;
      margin-bottom: 10px;
      animation: slideUp 0.8s cubic-bezier(0.16, 1, 0.3, 1);
    }
    @media (min-width: 768px) {
      .info-section {
        grid-template-columns: 1.1fr 0.9fr;
      }
    }
    .info-card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 16px;
      padding: 28px;
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.45);
      transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .info-card:hover {
      border-color: rgba(139, 92, 246, 0.3);
      box-shadow: 0 16px 40px 0 rgba(139, 92, 246, 0.12);
    }
    .info-card h2 {
      font-family: 'Outfit', sans-serif;
      font-size: 1.3rem;
      font-weight: 700;
      color: var(--primary);
      margin-bottom: 20px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
      padding-bottom: 12px;
      filter: drop-shadow(0 0 8px var(--primary));
    }
    .formula-box {
      font-family: 'Outfit', sans-serif;
      font-size: 2.8rem;
      font-weight: 800;
      text-align: center;
      margin: 20px 0;
      background: linear-gradient(135deg, #ffd700 0%, #ff8c00 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      text-shadow: 0 0 20px rgba(255, 215, 0, 0.15);
      letter-spacing: 2px;
    }
    .formula-box .exponent {
      font-size: 1.8rem;
      vertical-align: super;
      margin-left: 2px;
      background: linear-gradient(135deg, #ffd700 0%, #ff8c00 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .formula-desc {
      font-size: 0.92rem;
      line-height: 1.6;
      color: var(--text-main);
    }
    .bullet-list {
      list-style: none;
      font-size: 0.92rem;
      line-height: 1.6;
      color: var(--text-main);
    }
    .bullet-list li {
      margin-bottom: 14px;
      position: relative;
      padding-left: 24px;
    }
    .bullet-list li::before {
      content: '⚡';
      position: absolute;
      left: 0;
      color: var(--primary);
      filter: drop-shadow(0 0 4px var(--primary));
    }
  </style>
</head>
<body>

  <header class="header">
    <div class="logo-container" style="display: flex; justify-content: center; width: 100%; margin-bottom: 15px;">
      <svg viewBox="0 0 500 80" class="logo-svg" style="max-width: 500px; width: 100%; overflow: visible;">
        <defs>
          <pattern id="pixel-grid" width="10" height="10" patternUnits="userSpaceOnUse">
            <rect width="10" height="10" fill="none" />
            <circle cx="5" cy="5" r="0.7" fill="#38bdf8" fill-opacity="0.12" />
          </pattern>
          <linearGradient id="cyber-grad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#38bdf8" />
            <stop offset="50%" stop-color="#8b5cf6" />
            <stop offset="100%" stop-color="#ec4899" />
          </linearGradient>
          <!-- Reduced glow blur standard deviation (0.8 instead of 4) -->
          <filter id="glow" x="-10%" y="-10%" width="120%" height="120%">
            <feGaussianBlur stdDeviation="0.8" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        <!-- Background pixel grid -->
        <rect x="0" y="0" width="500" height="80" fill="url(#pixel-grid)" rx="8" />
        <rect x="2" y="2" width="496" height="76" fill="none" stroke="url(#cyber-grad)" stroke-width="1" stroke-opacity="0.1" rx="8" />
        
        <!-- Cyberpunk brackets -->
        <path d="M 25 15 L 10 15 L 10 65 L 25 65" fill="none" stroke="#38bdf8" stroke-width="2.5" />
        <path d="M 475 15 L 490 15 L 490 65 L 475 65" fill="none" stroke="#ec4899" stroke-width="2.5" />
        
        <!-- Top and bottom horizontal lines, similar to space banner style -->
        <line x1="30" y1="15" x2="470" y2="15" stroke="url(#cyber-grad)" stroke-width="1.5" stroke-opacity="0.4" />
        <line x1="30" y1="65" x2="470" y2="65" stroke="url(#cyber-grad)" stroke-width="1.5" stroke-opacity="0.4" />
        
        <!-- Text elements -->
        <text x="50%" y="48" font-family="'Outfit', sans-serif" font-size="28" font-weight="900" fill="url(#cyber-grad)" text-anchor="middle" letter-spacing="6" filter="url(#glow)">
          DELENTIA LABS
        </text>
      </svg>
    </div>
    <p class="subtitle" style="text-align: center; margin: 0 auto; max-width: 800px;">Enterprise Agentic Infrastructure (EAI) powered by the RCT Ecosystem. Mathematically aligned and optimized for standard resource deployment.</p>
  </header>

  <div class="stats-grid">
    <div class="stat-card">
      <div class="stat-value">&lt;0.3%</div>
      <div class="stat-label">Hallucination Rate</div>
      <div class="stat-desc">Intent-Centric AI OS Guarantee</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">RCT v7</div>
      <div class="stat-label">Architecture</div>
      <div class="stat-desc">10 Layers, 41 Algorithms, 7 Genomes</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">100%</div>
      <div class="stat-label">Sovereignty</div>
      <div class="stat-desc">Local-first, Air-gapped & PDPA Ready</div>
    </div>
  </div>

  <div class="container">

    <!-- Card 3: Regional Sovereignty Router -->
    <div class="card">
      <div class="card-content">
        <div>
          <div class="card-title">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
            Regional Sovereignty Router
          </div>

          <div class="form-group">
            <label>Sovereign Input Prompt / Test Message</label>
            <textarea id="promptInput" style="height: 60px;" placeholder="Type localized prompt (e.g. สวัสดี, Japanese, etc.)..." oninput="routePrompt()">คำนวณสิทธิประโยชน์ทางภาษีตามเงื่อนไขของประเทศไทย</textarea>
          </div>
        </div>

        <div>
          <div class="router-display">
            <div class="router-row">
              <span>Detected Language</span>
              <span id="resLang" style="color: #38bdf8;">th-TH (Thai)</span>
            </div>
            <div class="router-row">
              <span>Target Region</span>
              <span id="resRegion" style="color: #34d399;">ASEAN (th)</span>
            </div>
            <div class="router-row">
              <span>Routed Model</span>
              <span id="resModel" style="color: #a78bfa;">Typhoon-v2-7B-Instruct</span>
            </div>
            <div class="router-row" style="align-items: center;">
              <span>PDPA Status</span>
              <span id="resResidency"><span class="badge-secure">Sovereign safe</span></span>
            </div>
          </div>
          <div class="result-display" style="padding: 10px; margin-top: 10px; background: rgba(16,185,129,0.05); border-color: rgba(16,185,129,0.15);">
            <div style="font-size: 0.72rem; color: var(--success); font-weight: 600; display: flex; align-items: center; gap: 6px;">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
              Regional Adapter Data Residency Restored Local
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Log Console -->
    <div class="console-logs" id="logs">
      <div class="log-line log-info"><span class="log-time">[09:00:00]</span>[INIT] Delentia OS v0.4 Nodal Core initialized.</div>
      <div class="log-line log-success"><span class="log-time">[09:00:01]</span>[SignedAI] HexaCore consensus node connected (Supreme Architect).</div>
      <div class="log-line log-success"><span class="log-time">[09:00:02]</span>[SignedAI] 9 consensus roles online (TH-Local node active).</div>
      <div class="log-line log-info"><span class="log-time">[09:00:03]</span>[DeltaEngine] Compression initialized. Base state caching active.</div>
    </div>

  </div>

  <div class="info-section">
    <div class="info-card">
      <h2>🧮 Mathematical Constitutional Governance</h2>
      <div class="formula-box">F = D<span class="exponent">I</span> &times; A</div>
      <div class="formula-desc">
        <p>The core of Delentia's safety mechanism is the multiplicative <strong>Architect Approval Gate (A)</strong>. If signature verification fails or approval is rejected (<strong>A = 0</strong>), the composite evaluation score <strong>F</strong> mathematically collapses to <strong>0</strong>. This guarantees that security boundaries cannot be bypassed by prompt injection or model hallucination.</p>
      </div>
    </div>
    
    <div class="info-card">
      <h2>🛡️ Compliance & Legal Sovereignty</h2>
      <ul class="bullet-list">
        <li><strong>PDPA & GDPR Aligned:</strong> Designed to satisfy the stringent requirements of data privacy legislation.</li>
        <li><strong>Local-first Execution:</strong> Performs 100% on-premises offline processing to guarantee corporate data residency.</li>
        <li><strong>Thai NLP Optimized:</strong> Fine-tuned with custom token optimizations to process regional structures locally.</li>
      </ul>
    </div>
  </div>

  <footer>
    Delentia Labs &middot; Bangkok, Thailand 🇹🇭 &middot; Built for Enterprise Trust
  </footer>

  <script>
    // Regional Sovereignty Router simulator
    function routePrompt() {
      const prompt = document.getElementById('promptInput').value.trim().toLowerCase();
      const resLang = document.getElementById('resLang');
      const resRegion = document.getElementById('resRegion');
      const resModel = document.getElementById('resModel');
      const resResidency = document.getElementById('resResidency');

      let lang = "en-US (English)";
      let region = "Global (us)";
      let model = "Qwen-2.5-7B-Instruct";
      let statusHtml = '<span class="badge-global">Global Core</span>';

      if (!prompt) {
        resLang.textContent = "-";
        resRegion.textContent = "-";
        resModel.textContent = "-";
        resResidency.innerHTML = "-";
        return;
      }

      // Check Thai
      if (/[ก-๙]/.test(prompt) || prompt.includes("thai") || prompt.includes("สวัสดี")) {
        lang = "th-TH (Thai)";
        region = "ASEAN (Thailand)";
        model = "Typhoon-v2-7B-Instruct";
        statusHtml = '<span class="badge-secure">Sovereign safe</span>';
      }
      // Check Japanese
      else if (/[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff]/.test(prompt) || prompt.includes("japan") || prompt.includes("こんにちは")) {
        lang = "ja-JP (Japanese)";
        region = "East Asia (Japan)";
        model = "Rakuten-AI-7B-Instruct";
        statusHtml = '<span class="badge-secure">Sovereign safe</span>';
      }
      // Check Korean
      else if (/[\uac00-\ud7a3]/.test(prompt) || prompt.includes("korea") || prompt.includes("안녕하세요")) {
        lang = "ko-KR (Korean)";
        region = "East Asia (Korea)";
        model = "Solar-Pro-10.7B";
        statusHtml = '<span class="badge-secure">Sovereign safe</span>';
      }
      // Check Vietnamese
      else if (prompt.includes("viet") || prompt.includes("xin chào") || prompt.includes("thành phố") || prompt.includes("công nghiệp")) {
        lang = "vi-VN (Vietnamese)";
        region = "ASEAN (Vietnam)";
        model = "ViGPT-7B-Instruct";
        statusHtml = '<span class="badge-secure">Sovereign safe</span>';
      }

      resLang.textContent = lang;
      resRegion.textContent = region;
      resModel.textContent = model;
      resResidency.innerHTML = statusHtml;
    }

    // Dynamic telemetry log updates
    const logs = document.getElementById('logs');
    function addLog(type, msg) {
      const now = new Date();
      const timeStr = now.toTimeString().split(' ')[0];
      const div = document.createElement('div');
      div.className = `log-line ${type}`;
      div.innerHTML = `<span class="log-time">[${timeStr}]</span>${msg}`;
      logs.appendChild(div);
      logs.scrollTop = logs.scrollHeight;
      
      if (logs.children.length > 50) {
        logs.removeChild(logs.firstChild);
      }
    }

    const logTemplates = [
      { type: 'log-info', msg: '[Router] Active heartbeat check on regional nodes: TH-Local [OK], JP-East [OK], KR-Seoul [OK].' },
      { type: 'log-success', msg: '[SignedAI] Consensus validated on block 429188. 9 consensus roles approved.' },
      { type: 'log-info', msg: '[DeltaEngine] Memory cache compression sweep executed. Free memory space increased.' },
      { type: 'log-success', msg: '[RCT-Guardrails] Security scan clean. Zero-trust validation token generated.' },
      { type: 'log-warning', msg: '[Router] Processing transient latency anomaly on East-Asia regional proxy adapter.' },
      { type: 'log-error', msg: '[SignedAI] Block verify warning: role 7 signature missing. Initiating automatic recovery route.' },
      { type: 'log-success', msg: '[SignedAI] Consensus node signature recovered via fallback validator.' }
    ];

    setInterval(() => {
      const idx = Math.floor(Math.random() * logTemplates.length);
      const log = logTemplates[idx];
      addLog(log.type, log.msg);
    }, 6000);

    // Initial run
    routePrompt();
  </script>
</body>
</html>
"""

    if org_repo:
        temp_readme = Path("temp_org_readme.md")
        temp_readme.write_text(org_readme_content.strip(), encoding="utf-8")
        
        temp_index = Path("temp_org_index.html")
        temp_index.write_text(org_index_content.strip(), encoding="utf-8")
        
        temp_css = Path("temp_org_style.css")
        temp_css.write_text("/* Clean reset - styling is self-contained in index.html */", encoding="utf-8")
        
        print("Uploading organization Space files (README.md, index.html, style.css) ...")
        try:
            api.upload_file(
                path_or_fileobj=str(temp_readme),
                path_in_repo="README.md",
                repo_id=org_repo,
                repo_type="space",
                commit_message="feat: upload Delentia organization card Space README.md",
            )
            api.upload_file(
                path_or_fileobj=str(temp_index),
                path_in_repo="index.html",
                repo_id=org_repo,
                repo_type="space",
                commit_message="feat: upload Delentia organization portal index.html",
            )
            api.upload_file(
                path_or_fileobj=str(temp_css),
                path_in_repo="style.css",
                repo_id=org_repo,
                repo_type="space",
                commit_message="feat: upload Delentia organization portal style.css reset",
            )
            print("  [OK] Organization portal Space files live: https://huggingface.co/spaces/Delentia/README (Renders on https://huggingface.co/Delentia)")
        except Exception as e:
            print(f"  [WARN] Failed to upload organization Space files: {e}")
        finally:
            for f in (temp_readme, temp_index, temp_css):
                if f.exists():
                    f.unlink()

    # ── 2. Create Personal Profile Card (Ittirit-delentia/Ittirit-delentia) ───
    personal_repo = "Ittirit-delentia/Ittirit-delentia"
    print(f"\nCreating/verifying personal card dataset repository: {personal_repo}")
    try:
        api.create_repo(repo_id=personal_repo, repo_type="dataset", exist_ok=True, private=False)
        print(f"  [OK] Repository ready: https://huggingface.co/datasets/{personal_repo}")
    except Exception as e:
        print(f"  [WARN] Could not create personal card repository: {e}")
        personal_repo = None

    personal_readme_content = """---
title: Ittirit Saengow
colorFrom: green
colorTo: teal
pinned: false
viewer: false
---

🌐 [English Version](#english-documentation) | 🇹🇭 [เวอร์ชันภาษาไทย](#thai-documentation)

---

<h2 id="english-documentation">🇬🇧 English Documentation</h2>

> ⚠️ **Official Notice:** This is the architect's personal profile and sandbox environment. All enterprise-grade production assets for Delentia OS (including models v0.4, v0.4.1, and the latest dataset updates) have been migrated to the official organization space. 👉 **[Click here to visit Official Delentia](https://huggingface.co/Delentia)**

<div align="center">
  <h1>Ittirit Saengow (อิทธิฤทธิ์ แซ่โง้ว)</h1>
  <h3><b>Architect & Sole Creator of the RCT Ecosystem</b></h3>
  
  [![Website](https://img.shields.io/badge/Website-ittiritsaengow.link-blue.svg?style=flat-square)](https://ittiritsaengow.link)
  [![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Ittirit--delentia-orange.svg?style=flat-square)](https://huggingface.co/Ittirit-delentia)
  [![Email](https://img.shields.io/badge/Email-founder%40delentia.com-blue.svg?style=flat-square)](mailto:founder@delentia.com)

  [Personal Website](https://ittiritsaengow.link) • [Official Website](https://delentia.com) • [LinkedIn](https://www.linkedin.com/in/ittirit-saengow/) • [Twitter/X](https://x.com/ittirit_rct)
</div>

---

### 👤 About Me
I am the sole architect and developer of the **RCT (Reverse Component Thinking) Ecosystem** and **Delentia OS**. Working from Klong Toei, Bangkok, I built this system to prove a simple principle:
> *"AI safety, alignment, and governance should be mathematical guarantees built into the core operating system, not temporary policies or configurations that can be toggled off."*

Through rigorous engineering, I have designed and coded:
* An **11-layer constitutional AI operating system** that runs fully offline.
* **41 proprietary algorithms** spanning execution, routing, security, and consensus (SignedAI).
* **1,287 test cases** with a 92% coverage rate, ensuring high fidelity.
* **A 450+ page whitepaper** detailing the mathematical underpinnings of the ecosystem.
* **JITNA v0.4 GGUF Milestone:** Successfully fine-tuned and quantized the `delentia-slm-jitna-v0.4` model to 4-bit GGUF format, achieving 100% pass rates in local smoke validation tests (covering both functional logical parsing and constitutional security injection gates) on Ollama.

---

### 🧠 AI & ML Research Focus

#### 1. Cognitive OS Logic Mixing (v0.3 SLM GGUF)
Fine-tuning Small Language Models (SLMs) to execute complex, multi-domain cognitive loops. This includes memory delta compression (Delta Engine), routing recovery mechanisms (Intent Loop), and PDPA-compliant zero-trust safety blocks (RCT 7 rules). The v0.3 model is edge-deployable via Ollama using GGUF format.

#### 2. Pluggable Regional LLMs & Sovereignty
Integrating pluggable regional LLM adapters (Rakuten AI for JP, Solar Pro for KR, ViGPT for VN, Typhoon v2 for TH) to keep sensitive regional data in-region and guarantee PDPA compliance.

#### 3. Token Optimization & Hardware Accelerators
Refining TOON (Token-Oriented Object Notation) for 15-50% token savings, and developing custom CUDA/Triton hardware-accelerated kernels to accelerate local agent loop executions.

---

### 🌐 Project Links & Spaces
* **The RAG Corpus (Latest):** [delentia-os-whitepaper-rag-corpus](https://huggingface.co/datasets/Delentia/delentia-os-whitepaper-rag-corpus) — Structurally organized semantic knowledge base.
* **Official Dataset (v0.3):** [delentia-rct-intent-dataset](https://huggingface.co/datasets/Delentia/delentia-rct-intent-dataset) — Instruction-tuning dataset containing 3,184 scenarios.
* **The Cognitive Model (v0.3):** [delentia-slm-jitna-v0.4](https://huggingface.co/Delentia/delentia-slm-jitna-v0.4) — Core 8B parameter model (GGUF/bnb-4bit).
* **Under Development:** Currently fine-tuning the **delentia-slm-v0.4** model, designed as an active online gatekeeper to validate live transactions and system security.
* **Centralized Monitor:** [delentia-agent-monitor](https://huggingface.co/spaces/Delentia/delentia-agent-monitor) — Central MLflow tracking server.

---

### 🌀 Cognitive Architecture: RCT-7 Thinking
Delentia OS utilizes the RCT-7 Thinking (Reverse Component Thinking) methodology, separating the system's cognitive processing logic from the engineering infrastructure loop across two parallel layers (Dual-Layer):

<div align="center">
  <table style="width: 100%; max-width: 900px; border-collapse: collapse; border: 1px solid rgba(56, 189, 248, 0.2); font-family: 'Inter', sans-serif; background-color: #04060d; border-radius: 12px; overflow: hidden; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.45);">
    <thead>
      <tr style="background: linear-gradient(135deg, #0b132b 0%, #1c1a27 100%); border-bottom: 2px solid rgba(56, 189, 248, 0.3);">
        <th style="padding: 16px; text-align: left; width: 50%;">
          <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 1.3rem;">🧠</span>
            <div>
              <span style="font-size: 1.1rem; color: #ffffff; font-weight: 700;">RCT-7 Mental OS</span><br/>
              <span style="font-size: 0.75rem; color: #0ea5e9; font-weight: 600; letter-spacing: 1px; text-transform: uppercase;">Cognitive Loop (ตรรกะความคิด)</span>
            </div>
          </div>
        </th>
        <th style="padding: 16px; text-align: left; width: 50%;">
          <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 1.3rem;">⚙️</span>
            <div>
              <span style="font-size: 1.1rem; color: #ffffff; font-weight: 700;">RCT-7 Engineering Loop</span><br/>
              <span style="font-size: 0.75rem; color: #8b5cf6; font-weight: 600; letter-spacing: 1px; text-transform: uppercase;">System Loop (วิศวกรรมระบบ)</span>
            </div>
          </div>
        </th>
      </tr>
    </thead>
    <tbody>
      <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05); background-color: rgba(14, 165, 233, 0.02);">
        <td style="padding: 12px 16px; vertical-align: top; border-right: 1px solid rgba(56, 189, 248, 0.1);">
          <strong style="color: #0ea5e9;">1. Observe</strong><br/>
          <span style="font-size: 0.85rem; color: #9ca3af;">Gather raw situational facts & context.</span><br/>
          <span style="font-size: 0.75rem; color: #6b7280; font-style: italic;">สังเกตและรวบรวมบริบทแวดล้อมดิบ</span>
        </td>
        <td style="padding: 12px 16px; vertical-align: top;">
          <strong style="color: #8b5cf6;">1. Decompose</strong><br/>
          <span style="font-size: 0.85rem; color: #9ca3af;">Break workflows into isolated modules.</span><br/>
          <span style="font-size: 0.75rem; color: #6b7280; font-style: italic;">แยกย่อยระบบออกเป็นโมดูลอิสระ</span>
        </td>
      </tr>
      <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
        <td style="padding: 12px 16px; vertical-align: top; border-right: 1px solid rgba(56, 189, 248, 0.1);">
          <strong style="color: #0ea5e9;">2. Analyze</strong><br/>
          <span style="font-size: 0.85rem; color: #9ca3af;">Identify relationships and structure patterns.</span><br/>
          <span style="font-size: 0.75rem; color: #6b7280; font-style: italic;">วิเคราะห์ความสัมพันธ์และรูปแบบเชื่อมโยง</span>
        </td>
        <td style="padding: 12px 16px; vertical-align: top;">
          <strong style="color: #8b5cf6;">2. Reverse-Map</strong><br/>
          <span style="font-size: 0.85rem; color: #9ca3af;">Map blast radius & dependencies.</span><br/>
          <span style="font-size: 0.75rem; color: #6b7280; font-style: italic;">ทำผังผลกระทบและประเมินขอบเขตการทำงาน</span>
        </td>
      </tr>
      <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05); background-color: rgba(14, 165, 233, 0.02);">
        <td style="padding: 12px 16px; vertical-align: top; border-right: 1px solid rgba(56, 189, 248, 0.1);">
          <strong style="color: #0ea5e9;">3. Deconstruct</strong><br/>
          <span style="font-size: 0.85rem; color: #9ca3af;">Isolate requirements into base variables.</span><br/>
          <span style="font-size: 0.75rem; color: #6b7280; font-style: italic;">ถอดรากโครงสร้างความต้องการพื้นฐาน</span>
        </td>
        <td style="padding: 12px 16px; vertical-align: top;">
          <strong style="color: #8b5cf6;">3. Define Constraints</strong><br/>
          <span style="font-size: 0.85rem; color: #9ca3af;">Enforce security guarantees & boundaries.</span><br/>
          <span style="font-size: 0.75rem; color: #6b7280; font-style: italic;">กำหนดเกณฑ์ความมั่นคงและข้อจำกัดระบบ</span>
        </td>
      </tr>
      <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
        <td style="padding: 12px 16px; vertical-align: top; border-right: 1px solid rgba(56, 189, 248, 0.1);">
          <strong style="color: #0ea5e9;">4. Reverse Reasoning</strong><br/>
          <span style="font-size: 0.85rem; color: #9ca3af;">Solve backward from the target end-state.</span><br/>
          <span style="font-size: 0.75rem; color: #6b7280; font-style: italic;">คิดย้อนทางจากเป้าหมายผลลัพธ์ปลายทาง</span>
        </td>
        <td style="padding: 12px 16px; vertical-align: top;">
          <strong style="color: #8b5cf6;">4. Build + Verify</strong><br/>
          <span style="font-size: 0.85rem; color: #9ca3af;">Execute L1-L8 test assertions.</span><br/>
          <span style="font-size: 0.75rem; color: #6b7280; font-style: italic;">รันและตรวจสอบการทดสอบระดับ L1 ถึง L8</span>
        </td>
      </tr>
      <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05); background-color: rgba(14, 165, 233, 0.02);">
        <td style="padding: 12px 16px; vertical-align: top; border-right: 1px solid rgba(56, 189, 248, 0.1);">
          <strong style="color: #0ea5e9;">5. Identify Core Intent</strong><br/>
          <span style="font-size: 0.85rem; color: #9ca3af;">Extract the root purpose of user requests.</span><br/>
          <span style="font-size: 0.75rem; color: #6b7280; font-style: italic;">จำแนกและจับสาระเจตนาหลักที่แท้จริง</span>
        </td>
        <td style="padding: 12px 16px; vertical-align: top;">
          <strong style="color: #8b5cf6;">5. Assemble</strong><br/>
          <span style="font-size: 0.85rem; color: #9ca3af;">Verify SignedAI consensus signatures.</span><br/>
          <span style="font-size: 0.75rem; color: #6b7280; font-style: italic;">รวบรวมสิทธิ์ผ่านฉันทามติเข้ารหัสลับ</span>
        </td>
      </tr>
      <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
        <td style="padding: 12px 16px; vertical-align: top; border-right: 1px solid rgba(56, 189, 248, 0.1);">
          <strong style="color: #0ea5e9;">6. Reconstruct</strong><br/>
          <span style="font-size: 0.85rem; color: #9ca3af;">Synthesize solution within safe limits.</span><br/>
          <span style="font-size: 0.75rem; color: #6b7280; font-style: italic;">ประกอบและสร้างผลลัพธ์ใหม่ในเขตปลอดภัย</span>
        </td>
        <td style="padding: 12px 16px; vertical-align: top;">
          <strong style="color: #8b5cf6;">6. Monitor</strong><br/>
          <span style="font-size: 0.85rem; color: #9ca3af;">Track state changes in Delta memory.</span><br/>
          <span style="font-size: 0.75rem; color: #6b7280; font-style: italic;">ตรวจความจำส่วนต่างและบันทึกประวัติการเปลี่ยนสถานะ</span>
        </td>
      </tr>
      <tr style="background-color: rgba(14, 165, 233, 0.02);">
        <td style="padding: 12px 16px; vertical-align: top; border-right: 1px solid rgba(56, 189, 248, 0.1);">
          <strong style="color: #0ea5e9;">7. Compare</strong><br/>
          <span style="font-size: 0.85rem; color: #9ca3af;">Validate final state against original intent.</span><br/>
          <span style="font-size: 0.75rem; color: #6b7280; font-style: italic;">สอบทานและเปรียบเทียบเจตจำนงตั้งต้น</span>
        </td>
        <td style="padding: 12px 16px; vertical-align: top;">
          <strong style="color: #8b5cf6;">7. Evolve</strong><br/>
          <span style="font-size: 0.85rem; color: #9ca3af;">Optimize loops and latency profiles.</span><br/>
          <span style="font-size: 0.75rem; color: #6b7280; font-style: italic;">ปรับแต่งประสิทธิภาพและสถิติความหน่วง</span>
        </td>
      </tr>
    </tbody>
  </table>
  <div style="margin-top: 10px; font-size: 0.85rem; color: #9ca3af; font-family: monospace;">
    Cognitive Loop ── (Translated via Kernel 9 Tiers) ──► Operational Loop
  </div>
</div>

#### Process Flowchart
```
[1. Observe] ──► [2. Analyze] ──► [3. Deconstruct] ──► [4. Reverse Reasoning] ──► [5. Identify Intent] ──► [6. Reconstruct] ──► [7. Compare]
                                                               │
                                                 (Kernel 9 Tiers Translation)
                                                               ▼
[1. Decompose] ◄── [2. Reverse-Map] ◄── [3. Define Constraints] ◄── [4. Build & Verify] ◄── [5. Assemble] ◄── [6. Monitor] ◄── [7. Evolve]
```

---

### 🧮 Philosophy & The FDIA Equation
The core of Delentia's security architecture is governed by the **FDIA Equation** to ensure mathematical alignment:

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

---

<h2 id="thai-documentation">🇹🇭 เอกสารภาษาไทย (Thai Documentation)</h2>

> ⚠️ **คำแจ้งเตือนอย่างเป็นทางการ:** พื้นที่นี้คือหน้าโปรไฟล์ส่วนตัวและคลังข้อมูลทดสอบ (Sandbox) ของสถาปนิก ผลงาน Production ระดับ Enterprise ทั้งหมดของ Delentia OS (รวมถึงโมเดล v0.3, v0.4 และชุดข้อมูลอัปเดตล่าสุด) ถูกย้ายไปที่องค์กรกลางเรียบร้อยแล้ว 👉 **[คลิกที่นี่เพื่อไปยังหน้า Official Delentia](https://huggingface.co/Delentia)**

<div align="center">
  <h1>อิทธิฤทธิ์ แซ่โง้ว (Ittirit Saengow)</h1>
  <h3><b>สถาปนิกและผู้สร้างระบบนิเวศ RCT เพียงผู้เดียว</b></h3>
  
  [![Website](https://img.shields.io/badge/Website-ittiritsaengow.link-blue.svg?style=flat-square)](https://ittiritsaengow.link)
  [![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Ittirit--delentia-orange.svg?style=flat-square)](https://huggingface.co/Ittirit-delentia)
  [![Email](https://img.shields.io/badge/Email-founder%40delentia.com-blue.svg?style=flat-square)](mailto:founder@delentia.com)

  [Personal Website](https://ittiritsaengow.link) • [Official Website](https://delentia.com) • [LinkedIn](https://www.linkedin.com/in/ittirit-saengow/) • [Twitter/X](https://x.com/ittirit_rct)
</div>

---

### 👤 เกี่ยวกับฉัน
ผมคือผู้สร้างและผู้ออกแบบระบบ **RCT (Reverse Component Thinking) Ecosystem** และ **Delentia OS** จากห้องพักขนาดเล็กในชุมชนคลองเตย กรุงเทพมหานคร ด้วยปณิธานที่ต้องการพิสูจน์ว่า:
> *"การควบคุมและการรับประกันความปลอดภัยของระบบ AI (AI Governance & Safety) ควรได้รับการคุ้มครองด้วยการเข้ารหัสคณิตศาสตร์ในระดับโครงสร้างระบบปฏิบัติการ ไม่ใช่เป็นเพียงการตั้งค่าที่ปิด/เปิด หรือถูกบายพาสได้โดยง่าย"*

ตั้งแต่ปี 2025 ผมได้ทุ่มเทพัฒนาโครงข่ายของ AI OS ทั้งหมดด้วยตัวคนเดียวแบบ 100% Offline เพื่อปกป้องอธิปไตยข้อมูลส่วนบุคคลของไทย (PDPA) และมุ่งเน้นการเพิ่มประสิทธิภาพโมเดลระดับ SLM ให้มีศักยภาพการประมวลผลที่เทียบเคียง Enterprise ระดับโลก
* **ความสำเร็จล่าสุด (JITNA v0.4 GGUF):** ผมได้ทำการพัฒนาและ Fine-Tuning โมเดล **delentia-slm-jitna-v0.4** โดยการเชื่อมโยงระบบ Intent Loop, Delta Engine และ RCT v7 Rules เข้าด้วยกัน และทำการประมวลผลโมเดลให้อยู่ในฟอร์แมต GGUF 4-bit (`delentia-slm-jitna-v0.4-Q4_K_M.gguf`) ซึ่งผ่านการทดสอบ Smoke Test ในระดับเครื่องท้องถิ่นผ่าน Ollama (ทั้งด้าน Standard Logic และ Security Hostile Injection) ได้ครบถ้วน 100%

---

### 🧠 ขอบเขตการวิจัย AI & ML

#### 1. การผสมผสานลอจิกของระบบปฏิบัติการทางปัญญา (v0.3 SLM GGUF)
การปรับแต่งโมเดลภาษาขนาดเล็ก (SLM) เพื่อดำเนินการตามลูปทางปัญญาหลายโดเมนที่ซับซ้อน ซึ่งรวมถึงการบีบอัดหน่วยความจำส่วนต่าง (Delta Engine) กลไกการกู้คืนการกำหนดเส้นทาง (Intent Loop) และบล็อกความปลอดภัยแบบ Zero-trust ที่สอดคล้องกับ PDPA (กฎ RCT 7) โมเดล v0.3 สามารถใช้งานได้บนอุปกรณ์ปลายทางผ่าน Ollama โดยใช้รูปแบบ GGUF

#### 2. โมเดลภาษาภูมิภาคที่ถอดเสียบได้และอธิปไตยข้อมูล
การรวมอะแดปเตอร์โมเดลภาษาประจำภูมิภาค (เช่น Rakuten AI สำหรับญี่ปุ่น, Solar Pro สำหรับเกาหลี, ViGPT สำหรับเวียดนาม, Typhoon v2 สำหรับไทย) เพื่อเก็บรักษาข้อมูลส่วนบุคคลที่ละเอียดอ่อนไว้ภายในภูมิภาคและรับประกันการปฏิบัติตามข้อกำหนด PDPA อย่างเคร่งครัด

#### 3. การประหยัดโทเคนและตัวเร่งฮาร์ดแวร์
การพัฒนาปรับปรุง TOON (Token-Oriented Object Notation) เพื่อลดการใช้โทเคนลง 15-50% และพัฒนาเคอร์เนลเร่งความเร็วบนฮาร์ดแวร์ (CUDA/Triton) เพื่อเร่งการทำงานของวงจรประมวลผลเอเจนต์ในเครื่อง

---

### 🌐 ลิงก์โครงการและสเปซระบบนิเวศ
* **คลังข้อมูล RAG (ล่าสุด):** [delentia-os-whitepaper-rag-corpus](https://huggingface.co/datasets/Delentia/delentia-os-whitepaper-rag-corpus) — คลังข้อมูลความรู้อ้างอิงแบบมีโครงสร้างเชิงความหมาย
* **ชุดข้อมูลอย่างเป็นทางการ (v0.3):** [delentia-rct-intent-dataset](https://huggingface.co/datasets/Delentia/delentia-rct-intent-dataset) — คู่ข้อมูลคำสั่งฝึกสอน (Instruction Pairs) จำนวน 3,184 สถานการณ์
* **โมเดลประมวลผลแกนกลาง (v0.3):** [delentia-slm-jitna-v0.4](https://huggingface.co/Delentia/delentia-slm-jitna-v0.4) — โมเดลหลักขนาด 8B (GGUF/bnb-4bit)
* **อยู่ระหว่างการพัฒนา:** กำลังดำเนินการ Fine-tuning โมเดล **delentia-slm-v0.4** เพื่อใช้ทำหน้าที่เป็น Live Gatekeeper ตรวจสอบความปลอดภัยบนหน้าเว็บแบบสด
* **เซิร์ฟเวอร์มอนิเตอร์:** [delentia-agent-monitor](https://huggingface.co/spaces/Delentia/delentia-agent-monitor) — เซิร์ฟเวอร์ติดตามผลลัพธ์ผ่าน MLflow

---

### 🌀 สถาปัตยกรรมระดับปัญญา: RCT-7 Thinking
ระบบปฏิบัติการ Delentia OS ประยุกต์ใช้ระเบียบวิธีคิดย้อนกลับ **RCT-7 Thinking (Reverse Component Thinking)** ออกเป็น 2 ระดับชั้นคู่ขนาน (Dual-Layer) เพื่อแบ่งแยกตรรกะประมวลผลทางปัญญาของระบบสมองกล ออกจากกระบวนการรักษาระดับคุณภาพวิศวกรรมโครงสร้างพื้นฐานอย่างชัดเจน (รายละเอียดดูตารางเปรียบเทียบในส่วนภาษาอังกฤษด้านบน)

#### แผนภาพขั้นตอนกระบวนการคิดย้อนกลับ
```
[1. สังเกตบริบท] ──► [2. วิเคราะห์สัมพันธ์] ──► [3. แยกชิ้นส่วน] ──► [4. คิดย้อนกลับ] ──► [5. จับเจตนาหลัก] ──► [6. สร้างโซลูชัน] ──► [7. สอบเจตจำนง]
                                                                        │
                                                         (แปลตรรกะรันไทม์ผ่าน Kernel 9 Tiers)
                                                                        ▼
[1. แยกย่อยโมดูล] ◄── [2. ผังผลกระทบ] ◄── [3. กฎความมั่นคง] ◄── [4. ตรวจ L1-L8] ◄── [5. ฉันทามติ SignedAI] ◄── [6. ตรวจความจำ Delta] ◄── [7. วิวัฒนาการลดดีเลย์]
```

---

### 🧮 สมการความปลอดภัย FDIA
โครงสร้างระบบความปลอดภัยของ Delentia ถูกกำกับด้วยสมการ **FDIA** เพื่อรับประกันความสอดคล้องตามหลักคณิตศาสตร์:

<div align="center" style="margin: 16px 0; font-size: 22px; font-weight: bold; color: #ffd700;">
  F = D<sup>I</sup> &times; A
</div>

> [!IMPORTANT]
> **การรับประกันความปลอดภัยเชิงคณิตศาสตร์:** ประตูทางผ่านสถาปนิก (**A**) ทำหน้าที่เป็นตัวคูณโดยตรง หากไม่มีการลงลายมือชื่อดิจิทัลหรือปฏิเสธสิทธิ์การเข้าถึงจากมนุษย์ (**A = 0**) ผลลัพธ์สุดท้ายในการเปลี่ยนผ่านสถานะระบบ (**F**) จะถูกลดทอนให้กลายเป็น **0** โดยปริยาย ช่วยป้องกันการบายพาสผ่านการเจาะระบบ (Prompt Injection) ได้ 100%

---

<div align="center">
  <sub>อิทธิฤทธิ์ แซ่โง้ว | สร้างสรรค์ด้วยความตั้งใจในชุมชนคลองเตย กรุงเทพมหานคร ประเทศไทย 🇹🇭</sub>
</div>
"""

    if personal_repo:
        temp_file = Path("temp_personal_readme.md")
        temp_file.write_text(personal_readme_content.strip(), encoding="utf-8")
        print("Uploading personal card README.md ...")
        try:
            api.upload_file(
                path_or_fileobj=str(temp_file),
                path_in_repo="README.md",
                repo_id=personal_repo,
                repo_type="dataset",
                commit_message="feat: upload Ittirit Saengow personal card",
            )
            print("  [OK] Personal card live: https://huggingface.co/Ittirit-delentia")
        except Exception as e:
            print(f"  [WARN] Failed to upload personal card: {e}")
        finally:
            if temp_file.exists():
                temp_file.unlink()

    # ── 3. Create Unified HF Ecosystem Collection ───────────────────────
    create_delentia_collection(api, token)

    print("\n[OK] All done!")


def create_delentia_collection(api, token):
    print("\nCreating/verifying Hugging Face collection bundle...")
    collection_title = "Delentia Cognitive Framework — Delentia OS v0.4"
    collection_description = (
        "Official unified ecosystem collection for Delentia OS v0.4, "
        "featuring the 1+4 specialized LoRA pillars and the JITNA v3 protocol."
    )
    
    collection_slug = None
    try:
        collections = api.list_collections(owner="Delentia", token=token)
        for col in collections:
            if col.title == collection_title:
                collection_slug = col.slug
                print(f"  [INFO] Found existing collection: {collection_slug}")
                break
    except Exception as e:
        print(f"  [WARN] Failed to list collections: {e!r}")

    if not collection_slug:
        try:
            col = api.create_collection(
                title=collection_title,
                namespace="Delentia",
                description=collection_description,
                private=False,
                exists_ok=True,
                token=token
            )
            collection_slug = col.slug
            print(f"  [OK] Created new collection: {collection_slug}")
        except Exception as e:
            print(f"  [ERROR] Failed to create collection: {e!r}")
            return

    items = [
        {"id": "Delentia/delentia-slm-jitna-v0.4", "type": "model", "note": "Base SLM Model (8B Quantized GGUF/bnb-4bit)"},
        {"id": "Delentia/delentia-slm-jitna-router-v0.4", "type": "model", "note": "Router LoRA Adapter (v0.4)"},
        {"id": "Delentia/delentia-slm-jitna-executor-v0.4", "type": "model", "note": "Executor LoRA Adapter (v0.4)"},
        {"id": "Delentia/delentia-slm-jitna-guardian-v0.4", "type": "model", "note": "Guardian Safety LoRA Adapter (v0.4)"},
        {"id": "Delentia/delentia-slm-jitna-scribe-v0.4", "type": "model", "note": "Scribe Context Compression LoRA Adapter (v0.4)"},
        {"id": "Delentia/delentia-rct-intent-dataset", "type": "dataset", "note": "RCT Telemetry & Fine-Tuning Dataset"},
        {"id": "Delentia/delentia-os-whitepaper-rag-corpus", "type": "dataset", "note": "Delentia OS Whitepaper RAG Corpus"},
        {"id": "Delentia/delentia-trace-ecosystem", "type": "space", "note": "Unified EAI UI & Control Plane Observability Monitor"},
        {"id": "Delentia/delentia-analyserch-intent", "type": "space", "note": "Research Intent Analyzer Space"},
        {"id": "Delentia/delentia-gatekeeper", "type": "space", "note": "Guardian Gatekeeper Space"},
        {"id": "Delentia/delentia-scribe", "type": "space", "note": "Scribe Compressor Space"},
        {"id": "Delentia/delentia-executor", "type": "space", "note": "Executor Tool Compiler Space"},
        {"id": "Delentia/delentia-agent-monitor", "type": "space", "note": "Centralized MLflow Agent Monitor & Logger"}
    ]
    
    for item in items:
        try:
            api.add_collection_item(
                collection_slug=collection_slug,
                item_id=item["id"],
                item_type=item["type"],
                note=item["note"],
                exists_ok=True,
                token=token
            )
            print(f"  [OK] Added {item['type']} '{item['id']}' to collection.")
        except Exception as e:
            print(f"  [WARN] Failed to add '{item['id']}' to collection (might already exist): {e}")


if __name__ == "__main__":
    main()
