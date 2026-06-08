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

* **F (Future)**: The final composite evaluation score of the proposed state transition.
* **D (Data Quality)**: Accuracy, freshness, and completeness of JITNA context inputs ($0.0 \\le D \\le 1.0$).
* **I (Intent Precision)**: Acts as an **exponent** to amplify aligned intents ($I \\ge 1.0$).
* **A (Architect Gate)**: A strict binary or continuous gate representing human authorization or cryptographic consent. **If $A = 0$, the state transition is mathematically blocked ($F = 0$), regardless of the agent's intelligence.**

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
      --bg-dark: #060913;
      --card-bg: rgba(13, 18, 38, 0.7);
      --card-border: rgba(59, 130, 246, 0.15);
      --card-border-glow: rgba(139, 92, 246, 0.35);
      --text-main: #f3f4f6;
      --text-muted: #9ca3af;
      --primary: #3b82f6;
      --accent: #8b5cf6;
      --success: #10b981;
      --error: #ef4444;
      --warning: #f59e0b;
    }
    
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      background-color: var(--bg-dark);
      background-image: 
        radial-gradient(at 0% 0%, rgba(59, 130, 246, 0.15) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(139, 92, 246, 0.15) 0px, transparent 50%);
      color: var(--text-main);
      font-family: 'Inter', sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: flex-start;
      padding: 40px 20px;
    }

    header {
      text-align: center;
      margin-bottom: 40px;
      max-width: 800px;
    }

    header h1 {
      font-family: 'Outfit', sans-serif;
      font-size: 3rem;
      font-weight: 800;
      background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 50%, #f472b6 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 12px;
      letter-spacing: -1px;
    }

    header p {
      color: var(--text-muted);
      font-size: 1.15rem;
      line-height: 1.6;
    }

    .container {
      max-width: 1200px;
      width: 100%;
      display: grid;
      grid-template-columns: 1fr;
      gap: 30px;
      margin-bottom: 30px;
    }

    @media (min-width: 900px) {
      .container {
        grid-template-columns: 1fr 1fr;
      }
    }

    .card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 16px;
      padding: 30px;
      backdrop-filter: blur(12px);
      box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }

    .card:hover {
      border-color: var(--card-border-glow);
      box-shadow: 0 12px 40px 0 rgba(139, 92, 246, 0.15);
      transform: translateY(-2px);
    }

    .card-title {
      font-family: 'Outfit', sans-serif;
      font-size: 1.5rem;
      font-weight: 600;
      margin-bottom: 20px;
      display: flex;
      align-items: center;
      gap: 10px;
      background: linear-gradient(90deg, #f3f4f6, #9ca3af);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .form-group {
      margin-bottom: 24px;
    }

    .form-group label {
      display: flex;
      justify-content: space-between;
      color: var(--text-muted);
      font-size: 0.9rem;
      margin-bottom: 8px;
      font-weight: 500;
    }

    .form-group label span {
      color: var(--primary);
      font-weight: 600;
    }

    input[type="range"] {
      width: 100%;
      height: 6px;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 3px;
      outline: none;
      -webkit-appearance: none;
    }

    input[type="range"]::-webkit-slider-thumb {
      -webkit-appearance: none;
      width: 18px;
      height: 18px;
      border-radius: 50%;
      background: var(--primary);
      cursor: pointer;
      box-shadow: 0 0 10px var(--primary);
      transition: all 0.2s;
    }

    input[type="range"]::-webkit-slider-thumb:hover {
      transform: scale(1.2);
    }

    .switch-container {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 30px;
    }

    .switch {
      position: relative;
      display: inline-block;
      width: 50px;
      height: 26px;
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
      transition: .4s;
      border-radius: 34px;
      border: 1px solid rgba(255, 255, 255, 0.05);
    }

    .slider:before {
      position: absolute;
      content: "";
      height: 18px;
      width: 18px;
      left: 3px;
      bottom: 3px;
      background-color: white;
      transition: .4s;
      border-radius: 50%;
    }

    input:checked + .slider {
      background-color: var(--success);
    }

    input:checked + .slider:before {
      transform: translateX(24px);
    }

    .result-display {
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid rgba(255, 255, 255, 0.05);
      border-radius: 12px;
      padding: 20px;
      text-align: center;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
    }

    .score-circle {
      width: 100px;
      height: 100px;
      border-radius: 50%;
      border: 4px solid var(--primary);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.75rem;
      font-family: 'Outfit', sans-serif;
      font-weight: 700;
      margin-bottom: 15px;
      position: relative;
      box-shadow: 0 0 15px rgba(59, 130, 246, 0.2);
      transition: all 0.3s;
    }

    .score-circle.success {
      border-color: var(--success);
      color: var(--success);
      box-shadow: 0 0 20px rgba(16, 185, 129, 0.3);
    }

    .score-circle.error {
      border-color: var(--error);
      color: var(--error);
      box-shadow: 0 0 20px rgba(239, 68, 68, 0.3);
    }

    .status-text {
      font-weight: 600;
      font-size: 1.1rem;
      margin-bottom: 5px;
    }

    .status-desc {
      color: var(--text-muted);
      font-size: 0.85rem;
      line-height: 1.4;
    }

    .editor-container {
      display: flex;
      flex-direction: column;
      gap: 15px;
      height: 100%;
    }

    textarea {
      width: 100%;
      height: 150px;
      background: rgba(0, 0, 0, 0.3);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 8px;
      color: #38bdf8;
      font-family: 'Fira Code', monospace;
      font-size: 0.85rem;
      padding: 12px;
      resize: none;
      outline: none;
    }

    textarea:focus {
      border-color: var(--primary);
    }

    .btn {
      background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
      border: none;
      border-radius: 8px;
      color: white;
      padding: 12px;
      font-weight: 600;
      cursor: pointer;
      transition: opacity 0.2s;
    }

    .btn:hover {
      opacity: 0.9;
    }

    .compress-output {
      background: rgba(0, 0, 0, 0.4);
      border: 1px solid rgba(255, 255, 255, 0.05);
      border-radius: 8px;
      padding: 12px;
      font-family: 'Fira Code', monospace;
      font-size: 0.85rem;
      color: var(--text-main);
      white-space: pre-wrap;
      height: 150px;
      overflow-y: auto;
    }

    .stats-row {
      display: flex;
      justify-content: space-between;
      background: rgba(255, 255, 255, 0.02);
      border-radius: 8px;
      padding: 10px 15px;
      font-size: 0.85rem;
      color: var(--text-muted);
    }

    .stats-row span strong {
      color: var(--success);
    }

    .console-logs {
      grid-column: 1 / -1;
      background: #020308;
      border: 1px solid rgba(59, 130, 246, 0.1);
      border-radius: 12px;
      padding: 20px;
      font-family: 'Fira Code', monospace;
      font-size: 0.8rem;
      height: 200px;
      overflow-y: auto;
      box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.9);
    }

    .log-line {
      margin-bottom: 6px;
      line-height: 1.4;
    }

    .log-time {
      color: var(--text-muted);
      margin-right: 10px;
    }

    .log-info {
      color: #60a5fa;
    }

    .log-success {
      color: #34d399;
    }

    .log-warning {
      color: #fbbf24;
    }
    
    footer {
      margin-top: 20px;
      color: var(--text-muted);
      font-size: 0.85rem;
      text-align: center;
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
          <span style="color: var(--text-muted); font-size: 0.9rem; font-weight: 500;">Human Architect Gate (A)</span>
          <label class="switch">
            <input type="checkbox" id="inputA" checked>
            <span class="slider"></span>
          </label>
        </div>
      </div>

      <div class="result-display">
        <div class="score-circle success" id="scoreCircle">0.67</div>
        <div class="status-text" id="statusText">State Authorized</div>
        <div class="status-desc" id="statusDesc">State transition allowed under constitutional consensus constraints.</div>
      </div>
    </div>

    <!-- Card 2: TOON Compressor -->
    <div class="card">
      <div class="card-title">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 14h6v6H4zm10 0h6v6h-6zM4 4h6v6H4zm10 0h6v6h-6z"/></svg>
        TOON Protocol Compressor (ALGO-42)
      </div>
      
      <div class="editor-container">
        <textarea id="jsonInput">{
  "packet_id": "6afff5d6-7fa3-4f2c-92b0-b1a77fd42a93",
  "priority": 3,
  "payload": {
    "intent": "คำนวณภาษีบุคคลธรรมดา 1 ล้านบาท",
    "currency": "THB",
    "income": 1000000
  }
}</textarea>
        
        <button class="btn" onclick="compress()">Compress to TOON</button>
        
        <div class="compress-output" id="toonOutput">packet_id: 6afff5d6-7fa3-4f2c-92b0-b1a77fd42a93
priority: 3
payload:
  intent: คำนวณภาษีบุคคลธรรมดา 1 ล้านบาท
  currency: THB
  income: 1000000</div>
        
        <div class="stats-row">
          <span>JSON: <span id="jsonBytes">198</span> chars</span>
          <span>TOON: <span id="toonBytes">122</span> chars</span>
          <span>Savings: <strong id="savingsPct">38.4%</strong></span>
        </div>
      </div>
    </div>

    <!-- Log Console -->
    <div class="console-logs" id="logs">
      <div class="log-line"><span class="log-time">[15:00:00]</span><span class="log-info">[INIT] Delentia OS v3.0 Nodal Core initialized.</span></div>
      <div class="log-line"><span class="log-time">[15:00:01]</span><span class="log-success">[SignedAI] HexaCore consensus node connected (Supreme Architect).</span></div>
      <div class="log-line"><span class="log-time">[15:00:02]</span><span class="log-success">[SignedAI] 9 consensus roles online (TH-Local node active).</span></div>
      <div class="log-line"><span class="log-time">[15:00:03]</span><span class="log-info">[DeltaEngine] Compression initialized. Base state caching active.</span></div>
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

    function addLog(type, msg) {
      const now = new Date();
      const timeStr = now.toTimeString().split(' ')[0];
      const div = document.createElement('div');
      div.className = 'log-line';
      div.innerHTML = `<span class="log-time">[${timeStr}]</span><span class="${type}">${msg}</span>`;
      logs.appendChild(div);
      logs.scrollTop = logs.scrollHeight;
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
    }

    inputD.addEventListener('input', () => {
      calculateFDIA();
      addLog('log-info', `[FDIAGate] Input parameter D adjusted to ${inputD.value}`);
    });
    inputI.addEventListener('input', () => {
      calculateFDIA();
      addLog('log-info', `[FDIAGate] Input parameter I adjusted to ${inputI.value}`);
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
        
        addLog('log-success', `[TOON] Serialization complete. Token count reduced by ${savings.toFixed(1)}%`);
      } catch (e) {
        alert("Invalid JSON payload. Please enter valid JSON formatting.");
        addLog('log-warning', `[TOON] Serialization failed. Invalid JSON payload format.`);
      }
    }
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

My research leverages the **FDIA equation** to ensure absolute alignment:

$$F = D^I \\times A$$

By incorporating the human/architect gate ($A$) as a multiplicative element, the system guarantees that if $A = 0$ (meaning approval is rejected or signature verification fails), the final output state transition ($F$) is mathematically reduced to $0$. This ensures that security boundaries are not bypassable through prompt injection or behavioral overrides.

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
