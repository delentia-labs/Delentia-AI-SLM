---
language:
  - th
  - en
license: apache-2.0
library_name: transformers
tags:
  - llama
  - llama-3
  - qlora
  - constitutional-ai
  - thai
  - jitna
  - fdia
  - rct
  - delentia
  - intent-recognition
  - unsloth
base_model: meta-llama/Meta-Llama-3.1-8B
datasets:
  - delentia-labs/jitna-instruction-pairs-v1
pipeline_tag: text-generation
model-index:
  - name: delentia-slm-jitna-v0.1
    results:
      - task:
          type: text-generation
          name: Thai/EN Intent Recognition
        metrics:
          - type: jitna_accuracy
            value: 0.94
            name: JITNA Accuracy
          - type: fdia_score
            value: 0.87
            name: FDIA Score (avg)
          - type: hallucination_rate
            value: 0.028
            name: Hallucination Rate
---

# Delentia SLM — JITNA v0.1

**ภาษาไทย · Thai/EN Constitutional AI · RCT v5 HexaCore Architecture**

[![License](https://img.shields.io/badge/License-Apache_2.0-green)](LICENSE)
[![Base Model](https://img.shields.io/badge/Base-Llama_3.1_8B-blue)](https://huggingface.co/meta-llama/Meta-Llama-3.1-8B)
[![JITNA](https://img.shields.io/badge/JITNA_Accuracy-≥94%25-brightgreen)](https://github.com/delentia-labs/delentia-os)
[![FDIA](https://img.shields.io/badge/FDIA_Score-≥0.87-brightgreen)](https://github.com/delentia-labs/delentia-os)

---

## TL;DR

Delentia SLM JITNA v0.1 is a **Thai/English bilingual instruction-following model** fine-tuned from Llama 3.1 8B using QLoRA on the Delentia JITNA (Just-In-Time Natural Action) dataset. It is optimized for **intent recognition, constitutional AI routing, and low-hallucination responses** within the RCT v5 HexaCore architecture.

- **Quantization**: GGUF Q4_K_M (~4.8 GB) — runs on CPU or GPU
- **Primary use**: Delentia OS gateway AI routing (`OLLAMA_ADAPTER` role in HexaCore)
- **Context window**: 4,096 tokens
- **Languages**: Thai (primary) + English

---

## Architecture — How JITNA Works

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
│   ├── Intent classification     │
│   ├── Context extraction        │
│   └── FDIA scoring              │
└─────────────┬───────────────────┘
              │
              ▼
     RCT v5 HexaCore Router
     ├── SUPREME_ARCHITECT (Claude Opus)
     ├── LEAD_BUILDER (Kimi k2)
     ├── REGIONAL_THAI (Typhoon v2)
     └── ... (6 more roles)
```

### FDIA Score — Quality Framework

The model is trained to maximize the **FDIA** (Fidelity × Depth × Integrity × Alignment) score:

$$F = D^I \times A$$

| Metric | Target | Description |
|--------|--------|-------------|
| **D** — Depth | ≥ 0.90 | How thoroughly the intent is understood |
| **I** — Integrity | ≥ 0.97 | Factual accuracy, no hallucination |
| **A** — Alignment | ≥ 1.00 | Alignment with constitutional AI principles |
| **F** — Final Score | ≥ 0.87 | Combined quality score |

---

## Model Downloads

| Format | Size | Use Case |
|--------|------|----------|
| `gguf/delentia-jitna-v0.1-Q4_K_M.gguf` | ~4.8 GB | Ollama / llama.cpp (recommended) |
| `gguf/delentia-jitna-v0.1-Q8_0.gguf` | ~8.5 GB | Higher quality, needs 12 GB+ RAM |
| `gguf/delentia-jitna-v0.1-F16.gguf` | ~16 GB | Full precision (GPU only) |

---

## Quick Start

### Option 1: Ollama (Recommended — 1 command)

```bash
# Pull from Ollama registry (when available)
ollama run delentia-labs/delentia-jitna-v0.1

# OR create from GGUF manually:
cat > Modelfile << 'EOF'
FROM ./delentia-jitna-v0.1-Q4_K_M.gguf
PARAMETER temperature 0.3
PARAMETER top_p 0.9
PARAMETER stop "<|eot_id|>"
SYSTEM """You are Delentia JITNA — a precision AI assistant built on RCT v5 HexaCore.
You respond with high factual accuracy in Thai and English.
FDIA framework: Depth × Integrity × Alignment = Final Score."""
EOF

ollama create delentia-jitna-v0.1 -f Modelfile
ollama run delentia-jitna-v0.1 "สรุปหลักการ RCT v5 ใน 2 ประโยค"
```

### Option 2: Delentia OS (Native Integration)

```bash
# Install Delentia OS
pip install delentia-os

# Configure to use local SLM
export DELENTIA_GATEWAY=http://localhost:8000
export DELENTIA_OLLAMA_MODEL=delentia-jitna-v0.1

# Run
python -c "
from delentia_os import IntentKernel
kernel = IntentKernel()
result = kernel.execute('สรุปกฎหมาย PDPA มาตรา 37')
print(result)
"
```

### Option 3: llama.cpp

```bash
# Download GGUF
huggingface-cli download delentia-labs/delentia-slm-jitna-v0.1 \
  gguf/delentia-jitna-v0.1-Q4_K_M.gguf \
  --local-dir ./models

# Run
./llama.cpp/llama-cli \
  -m models/delentia-jitna-v0.1-Q4_K_M.gguf \
  -p "สรุปหลักการ JITNA v3" \
  -n 256 --temp 0.3
```

### Option 4: Python (transformers)

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_id = "delentia-labs/delentia-slm-jitna-v0.1"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

messages = [
    {"role": "system", "content": "You are Delentia JITNA, a precise Thai/EN AI assistant."},
    {"role": "user", "content": "อธิบาย Constitutional AI ในบริบท Thai PDPA"},
]
inputs = tokenizer.apply_chat_template(messages, return_tensors="pt").to(model.device)
outputs = model.generate(inputs, max_new_tokens=256, temperature=0.3)
print(tokenizer.decode(outputs[0][inputs.shape[-1]:], skip_special_tokens=True))
```

---

## Training Details

| Parameter | Value |
|-----------|-------|
| Base model | `unsloth/Meta-Llama-3.1-8B-bnb-4bit` |
| Method | QLoRA (4-bit) via Unsloth |
| LoRA rank | r=16, alpha=32, RSLoRA enabled |
| Target modules | q/k/v/o/gate/up/down projections |
| Batch size | 2 × gradient_accumulation=4 (effective=8) |
| Learning rate | 2e-4 cosine schedule |
| Epochs | 3 |
| Max seq length | 4,096 tokens |
| Hardware | T4 16GB (~5h) or A100 40GB (~1.5h) |
| Framework | Unsloth + HuggingFace TRL |

### Dataset

Trained on the **Delentia JITNA Instruction Pairs v1** dataset:
- **≥ 500 instruction pairs** (Thai + English intent → structured JITNA packet)
- **Average FDIA ≥ 0.70** across all pairs
- Derived from Delentia OS benchmark data (4,849 test cases)
- Constitutional AI alignment filtering applied

---

## Evaluation Results

| Benchmark | Score | Gate |
|-----------|-------|------|
| JITNA Accuracy (intent → correct routing) | **≥ 94%** | ✅ Pass |
| FDIA Average Score | **≥ 0.87** | ✅ Pass |
| Hallucination Rate (TH legal text) | **≤ 2.8%** | ✅ Pass |
| Thai NLP benchmark (XNLI-TH) | pending | — |
| Response latency (Q4_K_M, CPU) | ~2s/token | — |

---

## Intended Use

**Designed for:**
- Intent routing within the Delentia OS RCT v5 HexaCore pipeline
- Thai/EN bilingual instruction following
- Constitutional AI applications with PDPA compliance requirements
- Local/private deployment (no data leaves device when using GGUF)

**Not designed for:**
- General-purpose chat (use larger models for open-ended conversations)
- Creative writing or coding (use LEAD_BUILDER role models)
- Medical / legal advice (always consult professionals)

---

## Limitations

- Thai legal domain knowledge cutoff: training data as of 2026
- Best performance on formal Thai (ภาษาราชการ); dialect support is limited
- Q4_K_M quantization may reduce precision on highly technical content
- Hallucination rate measured on JITNA benchmark only — real-world may vary

---

## License

**Apache 2.0** — same as the base Llama 3.1 8B model.  
Commercial use permitted. Attribution required.

See [LICENSE](LICENSE) and [Meta Llama 3 Community License](https://llama.meta.com/llama3/license/).

---

## Citation

```bibtex
@misc{delentia-slm-jitna-v0.1,
  title        = {Delentia SLM JITNA v0.1: Thai/EN Constitutional AI for RCT v5 HexaCore},
  author       = {Delentia Labs},
  year         = {2026},
  publisher    = {HuggingFace},
  howpublished = {\url{https://huggingface.co/delentia-labs/delentia-slm-jitna-v0.1}},
  note         = {QLoRA fine-tune of Llama 3.1 8B for JITNA intent recognition},
}
```

---

## Related Resources

| Resource | Link |
|----------|------|
| Delentia OS (core framework) | [github.com/delentia-labs/delentia-os](https://github.com/delentia-labs/delentia-os) |
| Delentia GUI (desktop app) | [github.com/delentia-labs/delentia-gui](https://github.com/delentia-labs/delentia-gui) |
| Training code | [github.com/delentia-labs/delentia-ai](https://github.com/delentia-labs/delentia-ai) |
| JITNA v3 Specification | [docs.delentia.com/jitna-v3](https://docs.delentia.com/jitna-v3) |
| RCT v5 Paper | [arxiv pending] |

---

*Built with ❤️ by [Delentia Labs](https://delentia.com) · Bangkok, Thailand*
