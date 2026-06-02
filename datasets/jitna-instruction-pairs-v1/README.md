---
dataset_info:
  dataset_name: jitna-instruction-pairs-v1
  task_categories:
    - text-generation
    - conversational
  language:
    - th
    - en
  pretty_name: "Delentia JITNA Instruction Pairs v1"
  size_categories:
    - 1K<n<10K

license: apache-2.0
tags:
  - jitna
  - intent
  - fdia
  - constitutional-ai
  - thai
  - instruction-following
  - delentia-os
---

# JITNA Instruction Pairs v1

**Dataset for fine-tuning SLMs on the JITNA v3 (Just-In-Time Nodal Assembly) intent protocol.**

Used to train [Ittirit-delentia/delentia-slm-jitna-v0.1](https://huggingface.co/Ittirit-delentia/delentia-slm-jitna-v0.1).

## Dataset Structure

Each sample contains:
- `instruction` — Task description in Thai or English
- `input` — User's natural language request
- `output` — Correct JITNA v3 packet JSON
- `language` — `th` or `en`
- `fdia_score` — Expected FDIA score F = D^I × A (0.0–1.0)
- `domain` — Domain category (pdpa, governance, enterprise, general)

## JITNA Packet Format

```json
{
  "packet_id": "uuid-v4",
  "intent": "action_verb_noun",
  "priority": 1-10,
  "language": "th|en",
  "fdia_score": 0.0-1.0,
  "architect_required": true|false,
  "payload": { "...": "domain-specific fields" }
}
```

## FDIA Equation

$$F = D^I \times A$$

- **F** = Final trust score (0.0–1.0)
- **D** = Data quality (0.0–1.0)
- **I** = Intent precision exponent
- **A** = Architect authorization gate (0 or 1)

When `A = 0`, the packet is blocked regardless of F score.

## Statistics

| Split | Samples | Languages | Domains |
|-------|---------|-----------|---------|
| train | 500 | TH, EN | pdpa, governance, enterprise, general |
| test  | 100 | TH, EN | pdpa, governance, enterprise, general |

## Citation

```bibtex
@dataset{delentia_jitna_v1_2026,
  author    = {Ittirit Saengow},
  title     = {Delentia JITNA Instruction Pairs v1},
  year      = {2026},
  publisher = {Hugging Face},
  url       = {https://huggingface.co/datasets/delentia-labs/jitna-instruction-pairs-v1}
}
```
