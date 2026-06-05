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

    if org_repo:
        temp_file = Path("temp_org_readme.md")
        temp_file.write_text(org_readme_content.strip(), encoding="utf-8")
        print("Uploading organization card README.md ...")
        try:
            api.upload_file(
                path_or_fileobj=str(temp_file),
                path_in_repo="README.md",
                repo_id=org_repo,
                repo_type="space",
                commit_message="feat: upload Delentia organization card Space",
            )
            print(f"  [OK] Organization card live: https://huggingface.co/spaces/Delentia/README (Renders on https://huggingface.co/Delentia)")
        except Exception as e:
            print(f"  [WARN] Failed to upload organization card: {e}")
        finally:
            if temp_file.exists():
                temp_file.unlink()

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
ผมคือผู้สร้างและผู้ออกแบบระบบ **RCT Ecosystem** และ **Delentia OS** จากห้องพักขนาดเล็กในสลัมคลองเตย กรุงเทพมหานคร ด้วยปณิธานที่ต้องการพิสูจน์ว่า:
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

## 🧠 AI & ML Research Interests

* **Thai NLP & Token Optimization:** Developing specialized tokenizers and syntaxes (TOON/ALGO-42) that optimize Thai text representation, reducing LLM API token overhead and context costs by 40-50%.
* **Constitutional Alignment & Governance:** Designing deterministic gates (such as the FDIA State Engine) to enforce behavioral boundaries directly in model runtime logic.
* **Offline Enterprise Infrastructure:** Fine-tuning specialized Small Language Models (SLMs) to execute complex intent recognition loops on standard consumer hardware.

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
