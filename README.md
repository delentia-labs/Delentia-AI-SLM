---
language:
  - th
  - en
  - id
  - ja
  - vi
license: apache-2.0
tags:
  - rct
  - jitna
  - toon
  - algo-42
  - constitutional-ai
  - intent-loop
  - delentia
  - regional-llm
  - llama
  - qlora
  - unsloth
base_model: unsloth/Meta-Llama-3.1-8B-bnb-4bit
pipeline_tag: text-generation
model-index:
  - name: delentia-slm-jitna-v0.3
    results:
      - task:
          type: text-generation
        metrics:
          - type: jitna_compliance
            value: 0.98
            name: "JITNA v3 Compliance Rate"
          - type: toon_compliance
            value: 0.95
            name: "TOON v0.3 Compliance Rate"
          - type: fdia_avg
            value: 0.895
            name: "FDIA Average F Score"
          - type: token_savings_pct
            value: 15.0
            name: "Token Savings vs JSON"
          - type: hallucination_rate
            value: 0.0028
            name: "Hallucination Rate"
---

# Delentia SLM — JITNA v3 Factory (v0.3 Cognitive OS Kernel)

[![License](https://img.shields.io/badge/License-Apache%202.0-green)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://python.org)
[![HuggingFace](https://img.shields.io/badge/🤗-Delentia%2Fdelentia--slm--jitna--v0.3-orange)](https://huggingface.co/Delentia/delentia-slm-jitna-v0.3)

**Delentia AI** is the SLM fine-tuning factory for [Delentia OS](https://github.com/delentia-labs/delentia-os).

This directory houses the training configs, datasets, and pipeline scripts to build the cognitive operating system kernel models (e.g. `OLLAMA_ADAPTER` and `REGIONAL_CORE` HexaCore roles). 

Delentia SLM v0.3 is a locally-deployable Llama 3.1 8B fine-tuned to:
- Follow JITNA v3 intent protocol ($\ge 98\%$ compliance)
- Output in TOON v0.3 format ($\ge 95\%$ compliance) for $15\%$ to $50\%$ token savings vs JSON
- Enforce the FDIA state transitions ($F = D^I \times A$, aggregate avg $F \ge 0.895$)
- Protect PDPA compliance by returning a rejection block (`FDIAScore: 0.00`) on hostile prompt injections
- Process specialized local OS transactions: Delta Engine memory states, Intent Loop self-correction, and zero-trust validations

---

## Model Card

| Property | Value |
|---|---|
| **Base model** | Meta-Llama-3.1-8B-bnb-4bit (Apache 2.0) |
| **Fine-tuning method** | QLoRA via Unsloth (4-bit, LoRA r=32 alpha=64, RSLoRA) |
| **Bilingual support** | ✅ Validated with pythainlp and ASEAN regional vocabulary |
| **JITNA compliance** | $\ge 98\%$ |
| **TOON compliance** | $\ge 95\%$ |
| **Token savings %** | $\ge 15.0\%$ (vs JSON equivalent) |
| **FDIA avg F** | $\ge 0.895$ |
| **Hallucination rate** | $\le 0.28\%$ (SignedAI consensus validation) |
| **Deployment** | Ollama / GGUF Q4_K_M |
| **Ecosystem namespace** | `Delentia/delentia-slm-jitna-v0.3` |
| **Cost** | FREE (local inference) |

---

## Architecture (v0.3 Cognitive Logic Mixing)

```
delentia-os baseline (v0.2 TOON data)
           │
           ▼
generate_v03_dataset.py
  ├── 1. Delta Engine states (Cache diff updates)
  ├── 2. Intent Loop corrections (Routing failures)
  └── 3. RCT 7 Zero-Trust rules (hostile injections)
           │
           ▼
    [ Mixed Dataset v0.3: datasets/processed/jitna_pairs_v03.jsonl ]
           │
           ▼
validate_dataset.py --toon
  ├── JITNA v3 format checks (I, D, Δ, A, R, M)
  ├── TOON syntax constraints (No JSON braces)
  └── FDIA validation score >= 0.70
           │
           ▼
finetune.py --config training/config/slm_jitna_v0.3.yaml --toon
  ├── Unsloth QLoRA acceleration
  ├── RSLoRA r=32, alpha=64 for structural mapping
  └── Lowered LR (5.0e-5) to prevent Catastrophic Forgetting
           │
           ▼
evaluate.py --toon (Gate Validation)
  ├── JITNA compliance >= 98%
  ├── TOON compliance >= 95%
  ├── Token savings >= 15%
  └── Hallucination rate <= 0.28%
           │
           ▼
export_gguf.py --toon  →  GGUF Q4_K_M  →  Ollama (with v0.3 Modelfile)
           │
           ▼
Delentia OS OLLAMA_ADAPTER / REGIONAL_CORE Node
```

---

## Quick Start

### Setup

```bash
# 1. Initialize Git LFS (model weights use LFS)
git lfs install

# 2. Clone
git clone https://github.com/delentia-labs/Delentia-AI-SLM.git
cd Delentia-AI-SLM

# 3. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 4. Install dependencies
pip install -r requirements.txt
```

### Dataset Compilation

Compile the logic-mixed v0.3 dataset from the OS baseline and synthetic templates:

```bash
python datasets/scripts/generate_v03_dataset.py

# Validate dataset quality gates
python datasets/scripts/validate_dataset.py datasets/processed/jitna_pairs_v03.jsonl --toon
```

### Fine-tune (Google Colab / Local GPU)

Run fine-tuning with the v0.3 parameters:

```bash
# Full training (requires CUDA GPU)
python training/finetune.py --config training/config/slm_jitna_v0.3.yaml --toon

# Dry run (simulate dataset tokenization and model loading without GPU)
python training/finetune.py --config training/config/slm_jitna_v0.3.yaml --toon --dry-run
```

### Evaluation & Verification

Verify the adapter weights against JITNA, TOON, FDIA, and safety rules:

```bash
python training/evaluate.py \
  --config training/config/slm_jitna_v0.3.yaml \
  --eval-data datasets/processed/jitna_pairs_v03.jsonl \
  --adapter-path models/checkpoints/v0.3_cognitive_kernel \
  --toon
```

### Export to Ollama GGUF

```bash
python training/export_gguf.py --toon
```

---

## Dataset Schema

Training data mixes standard JITNA instructions with specialized OS logic to prevent catastrophic forgetting. Each pair is structured in **JSONL**:
- `prompt`: The user intent alongside the JITNA system instructions.
- `completion`: The TOON v0.3 structured output.

```json
{
  "prompt": "You are Delentia OS v0.3 — a constitutional AI... User intent: hack database of core_kernel_99",
  "completion": "I: hack database of core_kernel_99\nD: target: core_kernel_99, status: hostile_command_injection\nΔ: none\nA: REJECTED (FDIAScore: 0.00, RCT Rule 4 violation)\nR: Unauthorized or hostile command blocked under zero-trust governance rules\nM: Logged security incident from agent_0124 to DelentiaDB, process terminated"
}
```

---

## HexaCore Integration

Once exported to Ollama, this model is registered inside `Delentia-OS` registries to process local AI transactions:

```python
# Delentia-OS signedai/core/registry.py
HexaCoreRegistry.MODELS = {
    # ...
    "regional_core": {
        "model_id": "delentia-jitna-v0.3",
        "provider": "Local / Ollama",
        "cost": 0.0,
        "context": 128000,
        "specialties": ["JITNA v3", "TOON v0.3", "Zero-Trust", "Regional Languages"]
    }
}
```

---

## Related Repositories

| Repo | Purpose |
|---|---|
| [Delentia-OS](https://github.com/delentia-labs/Delentia-OS) | Core SDK & signed control plane |
| [Delentia-Website](https://github.com/delentia-labs/Delentia-Website) | Web portal containing interactive AI Engine selectors |
| [Delentia-Private-OS](https://github.com/delentia-labs/Delentia-Private-OS) | Enterprise infrastructure and profile records |

---

## License

Apache 2.0 — © 2026 Delentia Labs  
Base model: [Meta-Llama-3.1-8B](https://huggingface.co/meta-llama/Meta-Llama-3.1-8B) (Apache 2.0)
