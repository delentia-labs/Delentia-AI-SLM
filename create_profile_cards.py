import os
import sys
from pathlib import Path

def main():
    try:
        from huggingface_hub import HfApi, login, get_token
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
  <img src="https://raw.githubusercontent.com/delentia-labs/delentia-os/main/docs/assets/delentia_banner.png" alt="Delentia Labs Banner" width="100%" style="border-radius: 8px;" onerror="this.style.display='none'" />
  
  # 🌐 Delentia Labs
  ### **The Constitutional AI Operating System — RCT Ecosystem**
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](https://opensource.org/licenses/MIT)
  [![Documentation](https://img.shields.io/badge/docs-v3.0-green.svg?style=flat-square)](https://delentia-labs.github.io/delentia-os/)
  [![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Delentia-orange.svg?style=flat-square)](https://huggingface.co/Delentia)
  [![Ecosystem: RCT](https://img.shields.io/badge/Ecosystem-RCT-purple.svg?style=flat-square)](https://github.com/delentia-labs)

  [Website](https://delentia.com) • [GitHub](https://github.com/delentia-labs) • [Documentation](https://delentia-labs.github.io/delentia-os/) • [Model Hub](https://huggingface.co/Delentia)
</div>

---

## 🇹🇭 บทสรุปผู้บริหาร / Executive Summary (Bilingual)

### **ภาษาไทย (Thai)**
**Delentia Labs** เป็นผู้พัฒนาโครงสร้างพื้นฐานหลักสำหรับ **RCT (Reverse Component Thinking) Ecosystem** ซึ่งเป็น **ระบบปฏิบัติการ Intent-Centric AI OS ตัวแรกของโลกที่มีการรับประกันความปลอดภัยเชิงคณิตศาสตร์ (Constitutional Guarantees)** 
* **จุดมุ่งหมายสูงสุด:** เพื่อสร้างระบบควบคุมการทำงานของ AI Agent ที่ตรวจสอบได้ (Auditable) ปลอดภัย 100% และปฏิบัติตามกฎหมายคุ้มครองข้อมูลส่วนบุคคล (PDPA) อย่างเคร่งครัด โดยประมวลผลภายในระบบปิด (On-Premises / Air-Gapped)

### **English**
**Delentia Labs** designs the core infrastructure for the **RCT (Reverse Component Thinking) Ecosystem** — the world's first **Intent-Centric AI Operating System** with mathematical constitutional guarantees.
* **Core Mission:** To establish an open, verifiable, and highly secure framework (Linux for AI Agents), ensuring that autonomous components remain aligned, predictable, and compliant under all operational conditions.

---

## 🛠️ Core Technologies & Enterprise Features

### 1. Delentia OS & JITNA Assembly (Just-In-Time Nodal Assembly)
The open-source core SDK of the intent-centric AI operating system. It orchestrates dynamic execution loops, state tracking, and secure tool routing.
- **Enterprise Benefit:** Zero-trust component-level sandboxing. Every action is compiled into a verifiable execution block.

### 2. SignedAI & HexaCore Consensus Layer
A multi-LLM consensus layer utilizing ED25519 cryptographic signatures to validate model outputs.
- **The 9-Role Consensus:** Incorporates purpose-specific models across a balanced distribution (3 US, 3 CN, 1 TH, 1 Local, 1 LPU) to reduce model hallucination to **under 0.3%** (vs. 12-15% industry standard).
- **Security Guarantee:** Every decision is cryptographically signed and stored in immutable trails, ensuring compliance with corporate audits and national AI regulations.

### 3. Delta Engine (Memory Compression)
A high-efficiency agent memory system that stores state change diffs instead of redundant full-history context.
- **Compression Rate:** **91.5% space reduction** (design spec floor ≥ 74%), enabling the "Infinite Context Illusion" for long-running workflows.

### 4. TOON (Token-Oriented Object Notation — ALGO-42)
Our syntax-noise-free serialization protocol that replaces traditional JSON delimiters (`{`, `}`, `[`, `]`, `"`, `,`) with indentation and newline structures.
- **Efficiency:** Compresses token payload sizes by **40% to 50%**, immediately boosting LLM throughput, reducing context length, and lowering inference costs.

---

## 🧮 Mathematical Constitutional Governance: The FDIA Equation

The heart of Delentia's security is the **FDIA equation**, which guarantees that AI agents cannot bypass safety thresholds:

$$F = D^I \\times A$$

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
      max-width: 1280px;
      width: 100%;
      display: grid;
      grid-template-columns: 1fr;
      gap: 24px;
      margin-bottom: 30px;
      animation: slideUp 0.8s cubic-bezier(0.16, 1, 0.3, 1);
    }

    @media (min-width: 1024px) {
      .container {
        grid-template-columns: 1fr 1fr 1fr;
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
      grid-column: 1 / -1;
      background: #02040a;
      border: 1px solid rgba(56, 189, 248, 0.12);
      border-radius: 12px;
      padding: 18px;
      font-family: 'Fira Code', monospace;
      font-size: 0.8rem;
      height: 180px;
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
  </style>
</head>
<body>

  <header>
    <h1>DELENTIA LABS</h1>
    <p>The Intent-Centric AI Operating System powered by the RCT Ecosystem. Mathematically aligned and optimized for standard resource deployment.</p>
  </header>

  <div class="container">
    
    <!-- Card 1: FDIA State Gatekeeper -->
    <div class="card">
      <div class="card-content">
        <div>
          <div class="card-title">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
            FDIA Algorithmic Gatekeeper
          </div>
          
          <div class="form-group">
            <label>Data Quality (D) <span id="valD">0.85</span></label>
            <input type="range" id="inputD" min="0" max="1" step="0.01" value="0.85">
          </div>

          <div class="form-group">
            <label>Intent Precision (I) <span id="valI">1.50</span></label>
            <input type="range" id="inputI" min="1" max="3" step="0.05" value="1.50">
          </div>

          <div class="switch-container">
            <span style="color: var(--text-muted); font-size: 0.88rem; font-weight: 500;">Human Architect Gate (A)</span>
            <label class="switch">
              <input type="checkbox" id="inputA" checked>
              <span class="slider"></span>
            </label>
          </div>
        </div>

        <div>
          <div class="chart-container">
            <svg id="fdiaChart" width="100%" height="100%" viewBox="0 0 300 120" style="overflow: visible;">
              <defs>
                <linearGradient id="curveGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stop-color="#0ea5e9" stop-opacity="0.3"/>
                  <stop offset="100%" stop-color="#8b5cf6" stop-opacity="0.9"/>
                </linearGradient>
              </defs>
              <!-- Grid lines -->
              <line x1="40" y1="20" x2="260" y2="20" stroke="rgba(255,255,255,0.05)" stroke-dasharray="2,2"/>
              <line x1="40" y1="70" x2="260" y2="70" stroke="rgba(255,255,255,0.05)" stroke-dasharray="2,2"/>
              <line x1="40" y1="120" x2="260" y2="120" stroke="rgba(255,255,255,0.1)"/>
              <line x1="40" y1="20" x2="40" y2="120" stroke="rgba(255,255,255,0.1)"/>
              
              <!-- Labels -->
              <text x="35" y="24" fill="rgba(255,255,255,0.3)" font-size="7" text-anchor="end">1.0</text>
              <text x="35" y="74" fill="rgba(255,255,255,0.3)" font-size="7" text-anchor="end">0.5</text>
              <text x="35" y="124" fill="rgba(255,255,255,0.3)" font-size="7" text-anchor="end">0.0</text>
              <text x="40" y="132" fill="rgba(255,255,255,0.3)" font-size="7" text-anchor="middle">D=0</text>
              <text x="260" y="132" fill="rgba(255,255,255,0.3)" font-size="7" text-anchor="middle">D=1</text>
              
              <!-- Curve path -->
              <path id="curvePath" d="M 40,120 Q 150,120 260,20" fill="none" stroke="url(#curveGrad)" stroke-width="2.5"/>
              
              <!-- Active Dot -->
              <circle id="activeDot" cx="227" cy="48" r="5" fill="#10b981" style="filter: drop-shadow(0 0 6px #10b981); transition: cx 0.1s, cy 0.1s;"/>
            </svg>
          </div>

          <div class="result-display">
            <div class="score-container">
              <div class="score-circle success" id="scoreCircle">0.67</div>
              <div style="text-align: left;">
                <div class="status-text" id="statusText" style="color: var(--success);">State Authorized</div>
                <div class="status-desc" id="statusDesc">State transition allowed under constitutional consensus constraints.</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Card 2: TOON Compressor -->
    <div class="card">
      <div class="card-content">
        <div>
          <div class="card-title">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 14h6v6H4zm10 0h6v6h-6zM4 4h6v6H4zm10 0h6v6h-6z"/></svg>
            TOON Protocol Compressor (ALGO-42)
          </div>
          
          <div class="form-group">
            <label style="margin-bottom: 6px;">Select Template Payload</label>
            <select class="preset-selector" id="toonPreset" onchange="loadPreset()">
              <option value="intent">Tax Calculation Intent</option>
              <option value="simple">Simple System Command</option>
              <option value="complex">Multi-Model Agent Plan</option>
            </select>
          </div>

          <div class="editor-container">
            <div class="split-editors">
              <div>
                <span style="font-size: 0.75rem; color: var(--text-muted); display: block; margin-bottom: 4px; font-weight: 600;">RAW JSON</span>
                <textarea id="jsonInput" oninput="compress()">{
  "packet_id": "6afff5d6-7fa3-4f2c-92b0-b1a77fd42a93",
  "priority": 3,
  "payload": {
    "intent": "คำนวณภาษีบุคคลธรรมดา 1 ล้านบาท",
    "currency": "THB",
    "income": 1000000
  }
}</textarea>
              </div>
              <div>
                <span style="font-size: 0.75rem; color: var(--text-muted); display: block; margin-bottom: 4px; font-weight: 600;">COMPRESSED TOON</span>
                <div class="compress-output" id="toonOutput">packet_id: 6afff5d6-7fa3-4f2c-92b0-b1a77fd42a93
priority: 3
payload:
  intent: คำนวณภาษีบุคคลธรรมดา 1 ล้านบาท
  currency: THB
  income: 1000000</div>
              </div>
            </div>
          </div>
        </div>

        <div style="margin-top: 15px; display: flex; flex-direction: column; gap: 10px;">
          <button class="btn" onclick="compress()">Serialize context to TOON</button>
          
          <div class="stats-row">
            <span>JSON: <span id="jsonBytes">198</span> chars</span>
            <span>TOON: <span id="toonBytes">122</span> chars</span>
            <span>Savings: <strong id="savingsPct">38.4%</strong></span>
          </div>
        </div>
      </div>
    </div>

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
      <div class="log-line log-info"><span class="log-time">[09:00:00]</span>[INIT] Delentia OS v3.0 Nodal Core initialized.</div>
      <div class="log-line log-success"><span class="log-time">[09:00:01]</span>[SignedAI] HexaCore consensus node connected (Supreme Architect).</div>
      <div class="log-line log-success"><span class="log-time">[09:00:02]</span>[SignedAI] 9 consensus roles online (TH-Local node active).</div>
      <div class="log-line log-info"><span class="log-time">[09:00:03]</span>[DeltaEngine] Compression initialized. Base state caching active.</div>
    </div>

  </div>

  <footer>
    Delentia Labs &middot; Bangkok, Thailand 🇹🇭 &middot; Built for Enterprise Trust
  </footer>

  <script>
    const inputD = document.getElementById('inputD');
    const inputI = document.getElementById('inputI');
    const inputA = document.getElementById('inputA');
    const valD = document.getElementById('valD');
    const valI = document.getElementById('valI');
    const scoreCircle = document.getElementById('scoreCircle');
    const statusText = document.getElementById('statusText');
    const statusDesc = document.getElementById('statusDesc');
    const logs = document.getElementById('logs');

    // Preset examples for TOON Compressor
    const presets = {
      intent: {
        packet_id: "6afff5d6-7fa3-4f2c-92b0-b1a77fd42a93",
        priority: 3,
        payload: {
          intent: "คำนวณภาษีบุคคลธรรมดา 1 ล้านบาท",
          currency: "THB",
          income: 1000000
        }
      },
      simple: {
        packet_id: "9f8e7d6c-5b4a-3f2e-1d0c-9b8a7f6e5d4c",
        cmd: "sys_status",
        target: "rct_kernel_v3.0",
        verbose: true
      },
      complex: {
        packet_id: "3a4b5c6d-7e8f-9a0b-1c2d-3e4f5a6b7c8d",
        agent: "Delentia-Consensus-Supervisor",
        steps: [
          { action: "fetch_pdpa_policy", node: "TH-Local" },
          { action: "run_consensus", threshold: 0.95 },
          { action: "sign_execution_block", signature: "ed25519_node_signature" }
        ],
        checksum: "sha256_e3b0c442"
      }
    };

    function loadPreset() {
      const presetKey = document.getElementById('toonPreset').value;
      const data = presets[presetKey];
      document.getElementById('jsonInput').value = JSON.stringify(data, null, 2);
      compress();
    }

    function addLog(type, msg) {
      const now = new Date();
      const timeStr = now.toTimeString().split(' ')[0];
      const div = document.createElement('div');
      div.className = `log-line ${type}`;
      div.innerHTML = `<span class="log-time">[${timeStr}]</span>${msg}`;
      logs.appendChild(div);
      logs.scrollTop = logs.scrollHeight;
      
      // Limit total logs shown in DOM
      if (logs.children.length > 50) {
        logs.removeChild(logs.firstChild);
      }
    }

    function calculateFDIA() {
      const D = parseFloat(inputD.value);
      const I = parseFloat(inputI.value);
      const A = inputA.checked ? 1 : 0;
      
      valD.textContent = D.toFixed(2);
      valI.textContent = I.toFixed(2);

      const F = Math.pow(D, I) * A;
      scoreCircle.textContent = F.toFixed(2);

      scoreCircle.className = 'score-circle';
      
      if (A === 0) {
        scoreCircle.classList.add('error');
        statusText.textContent = "BLOCKED";
        statusText.style.color = "var(--error)";
        statusDesc.textContent = "Architect Gate is closed (A=0). Operation mathematically aborted.";
      } else if (F < 0.5) {
        scoreCircle.classList.add('error');
        statusText.textContent = "FAIL";
        statusText.style.color = "var(--error)";
        statusDesc.textContent = "Score too low due to insufficient data quality (D) or intent precision (I).";
      } else {
        scoreCircle.classList.add('success');
        statusText.textContent = "State Authorized";
        statusText.style.color = "var(--success)";
        statusDesc.textContent = "State transition allowed under constitutional consensus constraints.";
      }

      updateSVGGraph(D, I, A);
    }

    function updateSVGGraph(D, I, A) {
      const points = [];
      const startX = 40;
      const endX = 260;
      const startY = 120;
      const endY = 20;

      for (let xVal = 0; xVal <= 1.05; xVal += 0.05) {
        const yVal = Math.pow(xVal, I) * A;
        const xSVG = startX + xVal * (endX - startX);
        const ySVG = startY - yVal * (startY - endY);
        points.push(`${xSVG},${ySVG}`);
      }

      const pathData = `M ${points.join(' L ')}`;
      document.getElementById('curvePath').setAttribute('d', pathData);

      // Active Dot
      const currentF = Math.pow(D, I) * A;
      const dotX = startX + D * (endX - startX);
      const dotY = startY - currentF * (startY - endY);
      const activeDot = document.getElementById('activeDot');
      activeDot.setAttribute('cx', dotX);
      activeDot.setAttribute('cy', dotY);

      if (A === 0 || currentF < 0.5) {
        activeDot.setAttribute('fill', 'var(--error)');
        activeDot.style.filter = 'drop-shadow(0 0 6px var(--error))';
      } else {
        activeDot.setAttribute('fill', 'var(--success)');
        activeDot.style.filter = 'drop-shadow(0 0 6px var(--success))';
      }
    }

    inputD.addEventListener('input', () => {
      calculateFDIA();
    });
    inputI.addEventListener('input', () => {
      calculateFDIA();
    });
    inputA.addEventListener('change', () => {
      calculateFDIA();
      const state = inputA.checked ? "OPEN" : "CLOSED";
      const logClass = inputA.checked ? "log-success" : "log-warning";
      addLog(logClass, `[FDIAGate] Human Architect Gate A toggled ${state}`);
    });

    function jsonToToon(obj, indent = 0) {
      let result = '';
      const space = ' '.repeat(indent);
      
      if (Array.isArray(obj)) {
        for (const item of obj) {
          if (typeof item === 'object' && item !== null) {
            result += `${space}-\n${jsonToToon(item, indent + 2)}`;
          } else {
            result += `${space}- ${item}\n`;
          }
        }
      } else if (typeof obj === 'object' && obj !== null) {
        for (const [key, val] of Object.entries(obj)) {
          if (typeof val === 'object' && val !== null) {
            result += `${space}${key}:\n${jsonToToon(val, indent + 2)}`;
          } else {
            result += `${space}${key}: ${val}\n`;
          }
        }
      } else {
        result += `${space}${obj}\n`;
      }
      return result;
    }

    function compress() {
      const jsonInput = document.getElementById('jsonInput').value;
      const toonOutput = document.getElementById('toonOutput');
      const jsonBytes = document.getElementById('jsonBytes');
      const toonBytes = document.getElementById('toonBytes');
      const savingsPct = document.getElementById('savingsPct');

      try {
        const parsed = JSON.parse(jsonInput);
        const toon = jsonToToon(parsed).trim();
        toonOutput.textContent = toon;
        
        const jsonLen = jsonInput.length;
        const toonLen = toon.length;
        const savings = ((jsonLen - toonLen) / jsonLen) * 100;

        jsonBytes.textContent = jsonLen;
        toonBytes.textContent = toonLen;
        savingsPct.textContent = savings.toFixed(1) + '%';
      } catch (e) {
        toonOutput.textContent = "Error: Invalid JSON Input.";
      }
    }

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
    calculateFDIA();
    compress();
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
            print(f"  [OK] Organization portal Space files live: https://huggingface.co/spaces/Delentia/README (Renders on https://huggingface.co/Delentia)")
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
---

<div align="center">
  <h1>อิทธิฤทธิ์ แซ่โง้ว (Ittirit Saengow)</h1>
  <h3><b>Architect & Sole Creator of the RCT Ecosystem</b></h3>
  
  [![GitHub](https://img.shields.io/badge/GitHub-Ittirit--delentia-black.svg?style=flat-square&logo=github)](https://github.com/ittirit-delentia)
  [![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Ittirit--delentia-orange.svg?style=flat-square)](https://huggingface.co/Ittirit-delentia)
  [![Email](https://img.shields.io/badge/Email-founder%40delentia.com-blue.svg?style=flat-square)](mailto:founder@delentia.com)

  [GitHub](https://github.com/ittirit-delentia) • [LinkedIn](https://www.linkedin.com/in/ittirit-saengow/) • [Twitter/X](https://x.com/ittirit_rct) • [Website](https://ittiritsaengow.link)
</div>

---

## 👤 About Me / เกี่ยวกับฉัน

### **ภาษาไทย (Thai)**
ผมคือผู้สร้างและผู้ออกแบบระบบ **RCT (Reverse Component Thinking) Ecosystem** และ **Delentia OS** จากห้องพักขนาดเล็กในสลัมคลองเตย กรุงเทพมหานคร ด้วยปณิธานที่ต้องการพิสูจน์ว่า:
> *"การควบคุมและการรับประกันความปลอดภัยของระบบ AI (AI Governance & Safety) ควรได้รับการคุ้มครองด้วยการเข้ารหัสคณิตศาสตร์ในระดับโครงสร้างระบบปฏิบัติการ ไม่ใช่เป็นเพียงการตั้งค่าที่ปิด/เปิด หรือถูกบายพาสได้โดยง่าย"*

ตั้งแต่ปี 2025 ผมได้ทุ่มเทพัฒนาโครงข่ายของ AI OS ทั้งหมดด้วยตัวคนเดียวแบบ 100% Offline เพื่อปกป้องอธิปไตยข้อมูลส่วนบุคคลของไทย (PDPA) และมุ่งเน้นการเพิ่มประสิทธิภาพโมเดลระดับ SLM ให้มีศักยภาพการประมวลผลที่เทียบเคียง Enterprise ระดับโลก

### **English**
I am the sole architect and developer of the **RCT Ecosystem** and **Delentia OS**. Working from Klong Toei, Bangkok, I built this system to prove a simple principle:
> *"AI safety, alignment, and governance should be mathematical guarantees built into the core operating system, not temporary policies or configurations that can be toggled off."*

Through rigorous engineering, I have designed and coded:
* An **11-layer constitutional AI operating system** that runs fully offline.
* **41 proprietary algorithms** spanning execution, routing, security, and consensus (SignedAI).
* **1,287 test cases** with a 92% coverage rate, ensuring high fidelity.
* **A 450+ page whitepaper** detailing the mathematical underpinnings of the ecosystem.

---

## 🧠 AI & ML Research Focus

### 1. Cognitive OS Logic Mixing (v0.3 SLM)
Fine-tuning Small Language Models (SLMs) to execute complex, multi-domain cognitive loops. This includes memory delta compression (Delta Engine), routing recovery mechanisms (Intent Loop), and PDPA-compliant zero-trust safety blocks (RCT 7 rules).

### 2. Pluggable Regional LLMs & Sovereignty
Integrating pluggable regional LLM adapters (Rakuten AI for JP, Solar Pro for KR, ViGPT for VN, Typhoon v2 for TH) to keep sensitive regional data in-region and guarantee PDPA compliance.

### 3. Token Optimization & Hardware Accelerators
Refining TOON (Token-Oriented Object Notation) for 15-50% token savings, and developing custom CUDA/Triton hardware-accelerated kernels (via Hugging Face Kernel Hub) to accelerate local agent loop executions.

---

## 🌐 Project Links & Spaces

* **Official Dataset:** [delentia-rct-intent-dataset](https://huggingface.co/datasets/Delentia/delentia-rct-intent-dataset) — indexable intent, document, and artifact CSV sheets.
* **Centralized Monitor:** [delentia-agent-monitor](https://huggingface.co/spaces/Delentia/delentia-agent-monitor) — Centralized MLflow tracking server.
* **JITNA Benchmark:** [delentia-leaderboard](https://huggingface.co/spaces/Delentia/delentia-leaderboard) — JITNA compliance leaderboard.
* **Chat Compiler Demo:** [delentia-slm-demo](https://huggingface.co/spaces/Delentia/delentia-slm-demo) — Interactive Gradio compiler.
* **Guardrails Simulation:** [delentia-guardrails-demo](https://huggingface.co/spaces/Delentia/delentia-guardrails-demo) — Zero-trust intrusion block demo.

---

## 🧮 Theoretical Foundation: The FDIA Equation

Our security architecture is governed by the **FDIA Equation** to ensure mathematical alignment:

$$F = D^I \\times A$$

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

<div align="center">
  <sub>Ittirit Saengow | Made with ❤️ in Klong Toei, Bangkok, Thailand 🇹🇭</sub>
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
            print(f"  [OK] Personal card live: https://huggingface.co/Ittirit-delentia")
        except Exception as e:
            print(f"  [WARN] Failed to upload personal card: {e}")
        finally:
            if temp_file.exists():
                temp_file.unlink()

    print("\n[OK] All done!")

if __name__ == "__main__":
    main()
