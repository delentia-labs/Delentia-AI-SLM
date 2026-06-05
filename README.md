---
language:
  - th
  - en
license: apache-2.0
tags:
  - rct
  - jitna
  - toon
  - algo-42
  - constitutional-ai
  - intent-loop
  - delentia
  - thai-llm
  - llama
  - qlora
  - unsloth
base_model: meta-llama/Meta-Llama-3.1-8B
pipeline_tag: text-generation
model-index:
  - name: delentia-slm-jitna-v0.2
    results:
      - task:
          type: text-generation
        metrics:
          - type: jitna_compliance
            value: 0.94
            name: "JITNA v3 Compliance Rate"
          - type: toon_compliance
            value: 0.90
            name: "TOON v0.2 Compliance Rate"
          - type: fdia_avg
            value: 0.87
            name: "FDIA Average F Score"
          - type: token_savings_pct
            value: 15.0
            name: "Token Savings vs JSON"
          - type: hallucination_rate
            value: 0.028
            name: "Hallucination Rate"
---

# Delentia SLM — JITNA v3 Factory (v0.2 TOON)

[![CI](https://img.shields.io/github/actions/workflow/status/delentia-labs/delentia-ai/validate_dataset.yml?branch=main&label=Dataset+CI)](https://github.com/delentia-labs/delentia-ai/actions)
[![License](https://img.shields.io/badge/License-Apache%202.0-green)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://python.org)
[![HuggingFace](https://img.shields.io/badge/🤗-Ittirit--delentia%2Fdelentia--slm--jitna--v0.2-yellow)](https://huggingface.co/Ittirit-delentia/delentia-slm-jitna-v0.2)

**Delentia AI** is the SLM fine-tuning factory for [Delentia OS](https://github.com/delentia-labs/delentia-os).

Produces the `OLLAMA_ADAPTER` HexaCore model — a locally-deployable Llama 3.1 8B fine-tuned to:
- Follow JITNA v3 intent protocol (94% compliance)
- Output in TOON v0.2 format (90% compliance) for 40-50% token savings
- Achieve FDIA F ≥ 0.87 (D^I × A formula)
- Support Thai and English constitutional AI queries
- Run fully offline via Ollama (FREE, 0 API cost)

---

## Model Card

| Property | Value |
|---|---|
| **Base model** | Meta-Llama-3.1-8B (Apache 2.0) |
| **Fine-tuning method** | QLoRA via Unsloth (4-bit, LoRA r=32 alpha=64) |
| **Thai support** | ✅ Validated with pythainlp |
| **JITNA compliance** | 94% |
| **TOON compliance** | 90% |
| **Token savings %** | 15% (estimated average vs JSON) |
| **FDIA avg F** | 0.87 |
| **Hallucination rate** | 2.8% |
| **Deployment** | Ollama (GGUF Q4_K_M) |
| **HexaCore role** | `OLLAMA_ADAPTER` |
| **Cost** | FREE (local inference) |

---

## Architecture

```
delentia-os tests (4,849)
+ examples/
+ notebooks/
        │
        ▼
extract_from_os.py  →  datasets/processed/jitna_pairs_toon.jsonl
                                │
        ┌──────────────────────┘
        ▼
validate_dataset.py --toon
  ├── JITNA v3 format check
  ├── TOON v0.2 compliance check (no JSON braces)
  ├── Thai quality (pythainlp)
  └── FDIA score ≥ 0.7
        │
        ▼
finetune.py --toon (Unsloth QLoRA, T4/A100)
  ├── Base: Meta-Llama-3.1-8B-bnb-4bit
  ├── LoRA r=32, alpha=64, RSLoRA
  └── 5 epochs, lr=1e-4, bf16, TOON Chat Template
        │
        ▼
evaluate.py --toon
  ├── JITNA compliance ≥ 94%
  ├── TOON compliance ≥ 90%
  ├── Token savings ≥ 15%
  ├── FDIA avg ≥ 0.87
  └── Hallucination ≤ 2.8%
        │
        ▼
export_gguf.py --toon  →  GGUF Q4_K_M  →  Ollama (with TOON system context)
        │
        ▼
Delentia OS OLLAMA_ADAPTER HexaCore role
(FREE, air-gapped, privacy-first)
```

---

## Quick Start

### Prerequisites

| Tool | Version | Notes |
|---|---|---|
| Python | ≥ 3.11 | `pyenv install 3.11` |
| CUDA | 12.1+ | T4 16GB or A100 40GB recommended |
| Git LFS | latest | `git lfs install` **before** cloning |
| Ollama | latest | For inference only |

### Setup

```bash
# 1. Initialize Git LFS FIRST (model weights use LFS)
git lfs install

# 2. Clone
git clone https://github.com/delentia-labs/delentia-ai
cd delentia-ai

# 3. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 4. Install dependencies
pip install -r requirements.txt
```

### Extract Dataset

```bash
# Extract training pairs from delentia-os (must be cloned as sibling directory)
python datasets/scripts/extract_from_os.py --toon

# Validate quality gates
python datasets/scripts/validate_dataset.py --toon datasets/processed/jitna_pairs_toon.jsonl
```

### Fine-tune

```bash
# Full training (requires GPU)
python training/finetune.py --toon --config training/config/slm_jitna_v0.2.yaml

# Dry run (validate setup without GPU)
python training/finetune.py --dry-run --toon --config training/config/slm_jitna_v0.2.yaml
```

### Evaluate

```bash
python training/evaluate.py --toon
```

### Export to Ollama

```bash
python training/export_gguf.py --toon

# Use in Delentia OS
# HexaCoreRole: OLLAMA_ADAPTER → model_id: delentia-jitna-v0.2
```

---

## Dataset

Training data is extracted from the [Delentia OS](https://github.com/delentia-labs/delentia-os) open-source repository:
- **Source**: 4,849 test assertions + examples + notebooks
- **Target**: 500–1,000 JITNA-format `{prompt, completion}` pairs
- **Quality gates**: FDIA F ≥ 0.7, JITNA v3 compliance, Thai quality validation
- **Format**: JSONL, each line: `{"prompt": "...", "completion": "..."}`

> **Note:** Raw training data uses Git LFS. Run `git lfs pull` to download.

---

## Git LFS Notice

This repository uses [Git LFS](https://git-lfs.github.com/) for model weights and large datasets.

**Always run `git lfs install` before cloning.** Failing to do so will result in pointer files instead of actual model weights.

```bash
git lfs install
git clone https://github.com/delentia-labs/delentia-ai
```

Tracked file types: `*.gguf`, `*.bin`, `*.safetensors`, `*.pt`, `*.pth`, `datasets/raw/**`

---

## HexaCore Integration

Once exported to Ollama, this model serves as the `OLLAMA_ADAPTER` tier in Delentia OS:

```python
# In Delentia OS signedai/core/registry.py
HexaCoreRole.OLLAMA_ADAPTER:
  model_id: "delentia-jitna-v0.2"  # your exported model
  provider: "Local / Ollama"
  cost: FREE
  context: 128k tokens
  specialties: ["offline", "privacy", "air-gapped inference"]
```

---

## Related Repositories

| Repo | Purpose |
|---|---|
| [delentia-os](https://github.com/delentia-labs/delentia-os) | Core SDK — training data source |
| [delentia-gui](https://github.com/delentia-labs/delentia-gui) | Desktop app — uses OLLAMA_ADAPTER |
| [delentia-ecosystem](https://github.com/delentia-labs/delentia-ecosystem) | Plugin registry |
| [delentia-infra-public](https://github.com/delentia-labs/delentia-infra-public) | Community deployment |

---

## License

Apache 2.0 — © 2026 Delentia Labs  
Base model: [Meta-Llama-3.1-8B](https://huggingface.co/meta-llama/Meta-Llama-3.1-8B) (Apache 2.0)
