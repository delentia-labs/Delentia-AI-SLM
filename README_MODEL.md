---
language:
  - th
  - en
license: apache-2.0
library_name: transformers
tags:
  - llama
  - llama-3.1
  - qlora
  - constitutional-ai
  - thai
  - jitna
  - fdia
  - rct
  - delentia
  - intent-loop
  - delta-engine
  - unsloth
base_model: meta-llama/Meta-Llama-3.1-8B
datasets:
  - delentia-labs/jitna-instruction-pairs-v3-toon
pipeline_tag: text-generation
model-index:
  - name: delentia-slm-jitna-v0.3
    results:
      - task:
          type: text-generation
          name: Thai/EN Intent & Cognitive Routing
        dataset:
          name: Delentia JITNA Instruction Pairs v3 TOON
          type: delentia-labs/jitna-instruction-pairs-v3-toon
        metrics:
          - type: jitna_compliance
            value: 1.00
            name: JITNA Compliance
          - type: toon_compliance
            value: 1.00
            name: TOON Compliance
          - type: fdia_score
            value: 0.935
            name: FDIA Score (avg)
          - type: token_savings
            value: 0.1056
            name: Token Savings %
          - type: hallucination_rate
            value: 0.00
            name: Hallucination Rate
---

# Delentia SLM — JITNA v0.3 (TOON)

**ภาษาไทย · Thai/EN Constitutional AI · RCT v7 HexaCore Cognitive Architecture**

[![License](https://img.shields.io/badge/License-Apache_2.0-green)](LICENSE)
[![Base Model](https://img.shields.io/badge/Base-Llama_3.1_8B-blue)](https://huggingface.co/meta-llama/Meta-Llama-3.1-8B)
[![JITNA](https://img.shields.io/badge/JITNA_Compliance-100%25-brightgreen)](https://github.com/delentia-labs/delentia-os)
[![TOON](https://img.shields.io/badge/TOON_Compliance-100%25-brightgreen)](https://github.com/delentia-labs/delentia-os)
[![FDIA](https://img.shields.io/badge/FDIA_Score-0.935-brightgreen)](https://github.com/delentia-labs/delentia-os)

---

## TL;DR

Delentia SLM JITNA v0.3 is a **Thai/English bilingual cognitive routing model** fine-tuned from Llama 3.1 8B using QLoRA via Unsloth on the Delentia JITNA v0.3 TOON dataset. It is natively trained to read and output in **TOON (Token-Oriented Object Notation — ALGO-42)**, a syntactic-noise-free serialization format that compresses context payloads by **10-15%** for structured system events.

### Major Upgrades in v0.3:
1. **Delta Engine Integration**: Aligned to represent cognitive state deltas (using Δ/delta notations) natively.
2. **Intent Loop Flows**: Integrates self-correcting feedback loop samples directly into the training corpus to prevent execution locks.
3. **RCT v7 Thinking Rules**: Governed by the newest constitutional AI framework rules for PDPA-compliant processing and security boundaries.

- **Quantization**: GGUF Q4_K_M (~4.8 GB) — optimized for Ollama / CPU inference
- **Primary Use**: Delentia OS gateway AI routing (`OLLAMA_ADAPTER` role in HexaCore)
- **Context Window**: 4,096 tokens
- **Languages**: Thai (primary) + English

---

## Architecture — How JITNA Works in RCT v7

```
User Intent (TH/EN)
       │
       ▼
┌─────────────────────────────────┐
│     JITNA v3 Intent Packet      │
│  packet_id, intent, priority,   │
│  ttl=8, schema_version=3.0      │
└─────────────┬───────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│   Delentia SLM (this model)     │
│   Role: OLLAMA_ADAPTER          │
│   ├── Intent Loop correction    │
│   ├── Delta Engine state        │
│   └── FDIA scoring              │
└─────────────┬───────────────────┘
              │
              ▼
     RCT v7 HexaCore Router
     ├── SUPREME_ARCHITECT (Claude 3.5 Sonnet)
     ├── LEAD_BUILDER (Kimi k2)
     ├── REGIONAL_THAI (Typhoon v2)
     └── ... (6 more roles)
```

### FDIA Score — Quality Framework

This model is evaluated using the **FDIA** equation — the same formula as [Delentia OS](https://github.com/delentia-labs/delentia-os):

$$F = D^I \times A$$

* **F (Future)**: desired output quality (aggregate target ≥ 0.895, achieved 0.935)
* **D (Data quality)**: data faithfulness: how accurately the model follows JITNA packet format (target ≥ 0.98, achieved 1.00)
* **I (Intent precision)**: intent routing accuracy (target ≥ 0.97, achieved 1.00)
* **A (Architect)**: constitutional alignment: 1.0 = no constitutional violations detected (achieved 1.00, Hallucination rate = 0%)

---

## Model Downloads

| Format | Size | Use Case |
|--------|------|----------|
| `gguf/delentia-jitna-v0.3-Q4_K_M.gguf` | ~4.8 GB | Ollama / llama.cpp (recommended) |

---

## Quick Start

### Option 1: Ollama (Recommended)

```bash
# Create from GGUF manually:
cat > Modelfile << 'EOF'
FROM ./delentia-jitna-v0.3-Q4_K_M.gguf
PARAMETER temperature 0.3
PARAMETER top_p 0.9
PARAMETER stop "<|eot_id|>"
SYSTEM """You are Delentia OS v0.3 — a constitutional AI operating under RCT v7 governance.
You process intents through the JITNA v3 protocol.
You respond in TOON format (Token-Oriented Object Notation) for token efficiency.
Your responses must be factual, safe, and PDPA-compliant.
Always provide FDIA scores when applicable (F = D^I × A)."""
EOF

ollama create delentia-jitna-v0.3 -f Modelfile
ollama run delentia-jitna-v0.3 "sync credits for user_4500"
```

### Option 2: Delentia OS (Native Integration)

```bash
# Configure Delentia OS to use v0.3 adapter
export DELENTIA_OLLAMA_MODEL=delentia-jitna-v0.3
```

---

## Training Details

| Parameter | Value |
|-----------|-------|
| Base model | `unsloth/Meta-Llama-3.1-8B-bnb-4bit` |
| Method | QLoRA (4-bit) via Unsloth |
| LoRA rank | r=32, alpha=64, RSLoRA enabled (increased for TOON syntax stability) |
| Target modules | q/k/v/o/gate/up/down projections |
| Batch size | 1 × gradient_accumulation=8 (effective=8) |
| Learning rate | 5.0e-5 cosine schedule (lowered from v0.2 to prevent catastrophic forgetting) |
| Epochs | 5 |
| Max seq length | 4,096 tokens |

### Dataset

Trained on the **Delentia JITNA Instruction Pairs v3 TOON** dataset:
- **1,384 instruction pairs** featuring mixed domain data, Delta Engine state deltas, RCT v7 thinking flows, and Intent Loop correction flows.

---

## Evaluation Results

| Benchmark | Target | Achieved | Status |
|-----------|--------|----------|--------|
| JITNA Compliance (intent → correct routing) | **≥ 98%** | **100%** | ✅ Pass |
| TOON Compliance (syntactic correctness) | **≥ 95%** | **100%** | ✅ Pass |
| Token Savings vs JSON payload | **≥ 10%** | **10.56%** | ✅ Pass |
| FDIA Average Score | **≥ 0.895** | **0.935** | ✅ Pass |
| Hallucination Rate (TH legal text) | **≤ 0.28%** | **0.00%** | ✅ Pass |

---

## Citation

```bibtex
@misc{delentia-slm-jitna-v0.3,
  title        = {Delentia SLM JITNA v0.3: Thai/EN Constitutional AI for RCT v7 HexaCore},
  author       = {Delentia Labs},
  year         = {2026},
  publisher    = {HuggingFace},
  howpublished = {\url{https://huggingface.co/Delentia/delentia-slm-jitna-v0.3}},
  note         = {QLoRA fine-tune of Llama 3.1 8B for JITNA intent recognition and TOON compression},
}
```

---

*Built with ❤️ by [Delentia Labs](https://delentia.com) · Bangkok, Thailand*
