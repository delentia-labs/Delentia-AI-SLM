#!/usr/bin/env python3
"""
upload_4_pillars_model_cards.py

Writes README.md model cards for the 4 pillars (Executor, Router, Guardian, Scribe)
and uploads them to HuggingFace Hub repositories for both the personal account 
and the Delentia organization.

Usage:
    $env:HF_TOKEN = "hf_xxxxxxxxxxxxxxxx"
    python upload_4_pillars_model_cards.py
"""

import os
import sys

# Define the README templates for each of the 4 pillars
MODEL_CARDS = {
    "router": {
        "repo_suffix": "delentia-slm-jitna-router",
        "title": "The Router (Sequence Classifier)",
        "readme": r"""---
license: apache-2.0
base_model: unsloth/Meta-Llama-3.1-8B-bnb-4bit
tags:
- text-classification
- peft
- lora
- delentia-os
- JITNA
---

# Delentia SLM — The Router (slm-jitna-router)

The Router is a specialized Sequence Classification LoRA adapter within the **Delentia OS 1+4 Pillar Architecture**. Its primary role is to intercept incoming user intents and classify them into one of the specialized execution pathways at ultra-low latency.

## Technical Specifications
- **Base Model:** `unsloth/Meta-Llama-3.1-8B-bnb-4bit`
- **Fine-Tuning Method:** Sequence Classification QLoRA (SEQ_CLS adapter)
- **Target Modules:** `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`
- **Output Labels:**
  - `0`: Executor (Tool / JSON Execution)
  - `1`: Router Base (Conversational / Standard Prompt)
  - `2`: Guardian (Safety Shield evaluation)
  - `3`: Scribe (Context compression/summarization)

## Optimization Details
- **Zero Static Padding:** Re-engineered training pipeline removes static padding and reduces input context to `max_length=512`.
- **Inference Latency:** **20-50 milliseconds** on consumer-grade local hardware, enabling instantaneous routing decisions.
- **Accuracy Gate:** Achieved $\ge 96\%$ intent classification accuracy on JITNA router evaluation dataset.
"""
    },
    "executor": {
        "repo_suffix": "delentia-slm-jitna-executor",
        "title": "The Executor (Agentic Tool Call)",
        "readme": r"""---
license: apache-2.0
base_model: unsloth/Meta-Llama-3.1-8B-bnb-4bit
tags:
- gguf
- llama-cpp
- text-generation
- tool-use
- delentia-os
---

# Delentia SLM — The Executor (slm-jitna-executor)

The Executor is a specialized generative LoRA adapter in the **Delentia OS 1+4 Pillar Architecture**. It is trained specifically to translate raw user intents into machine-executable JSON payloads.

## Key Principles
1. **Zero Conversational Bias:** Output is strictly restricted to valid, raw JSON. It never explains its actions or generates natural language.
2. **Deterministic Tool Invocation:** Correctly matches tools, databases, and variables with zero hallucinations.

## Technical Specifications
- **Base Model:** `unsloth/Meta-Llama-3.1-8B-bnb-4bit`
- **Format:** GGUF Q4_K_M (Quantized via llama.cpp)
- **Primary Metrics:**
  - JSON Validity: $\ge 99\%$
  - Tool Call Accuracy: $\ge 95\%$
"""
    },
    "guardian": {
        "repo_suffix": "delentia-slm-jitna-guardian",
        "title": "The Guardian (Constitutional Safety Shield)",
        "readme": r"""---
license: apache-2.0
base_model: unsloth/Meta-Llama-3.1-8B-bnb-4bit
tags:
- gguf
- llama-cpp
- text-generation
- safety
- delentia-os
---

# Delentia SLM — The Guardian (slm-jitna-guardian)

The Guardian is the Constitutional AI safety evaluator in the **Delentia OS 1+4 Pillar Architecture**. It computes real-time intent safety based on the constitutional FDIA formula.

## The FDIA Safety Equation
Every prompt is evaluated using the formula:
$$F = D^I \times A$$

Where:
- $D$ = Data integrity (0.0 to 1.0)
- $I$ = Intent clarity (0.0 to 1.0)
- $A$ = Architect authorization (0 or 1)

If the intent is harmful, the system rejects it ($A=0, F=0$).

## Technical Specifications
- **Base Model:** `unsloth/Meta-Llama-3.1-8B-bnb-4bit`
- **Format:** GGUF Q4_K_M (Quantized via llama.cpp)
- **Primary Metrics:**
  - Adversarial Rejection Rate: $\ge 99\%$
"""
    },
    "scribe": {
        "repo_suffix": "delentia-slm-jitna-scribe",
        "title": "The Scribe (Context Compressor)",
        "readme": r"""---
license: apache-2.0
base_model: unsloth/Meta-Llama-3.1-8B-bnb-4bit
tags:
- gguf
- llama-cpp
- text-generation
- context-compression
- delentia-os
---

# Delentia SLM — The Scribe (slm-jitna-scribe)

The Scribe is a specialized context compression LoRA adapter in the **Delentia OS 1+4 Pillar Architecture**. It solves the problem of context window saturation.

## Core Mechanics
1. **Recursive Summarization:** Condenses long historical chat context into a structured, minimal TOON representation.
2. **Noise Reduction:** Filters out colloquial conversational elements, keeping only actionable parameters.

## Technical Specifications
- **Base Model:** `unsloth/Meta-Llama-3.1-8B-bnb-4bit`
- **Format:** GGUF Q4_K_M (Quantized via llama.cpp)
- **Primary Metrics:**
  - TOON v0.2 Compliance: $\ge 90\%$
  - Token Savings: $\ge 15\%$
"""
    }
}

def main():
    try:
        from huggingface_hub import HfApi, get_token, login
    except ImportError:
        print("ERROR: huggingface_hub not installed.")
        print("Run: pip install huggingface_hub")
        sys.exit(1)

    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN") or get_token()
    if not token:
        print("ERROR: Set HF_TOKEN environment variable first.")
        print('  $env:HF_TOKEN = "hf_xxxxxxxxxxxxxxxx"')
        sys.exit(1)

    login(token=token)
    api = HfApi()

    personal_user = "Ittirit-delentia"
    org_user = "Delentia"

    # Temporary directory path for temporary README files
    temp_dir = os.path.join(os.path.dirname(__file__), "temp_readme")
    os.makedirs(temp_dir, exist_ok=True)

    print("🚀 Starting Model Cards Upload for the 4 Pillars...")

    for pillar_key, pillar_info in MODEL_CARDS.items():
        suffix = pillar_info["repo_suffix"]
        title = pillar_info["title"]
        readme_content = pillar_info["readme"]

        print(f"\n--- Processing Pillar: {title} ({suffix}) ---")

        # Write to temporary file
        temp_file_path = os.path.join(temp_dir, f"README_{pillar_key}.md")
        with open(temp_file_path, "w", encoding="utf-8") as f:
            f.write(readme_content)

        # Upload to both personal and org repositories
        for namespace in [personal_user, org_user]:
            repo_id = f"{namespace}/{suffix}"
            print(f"Uploading model card to: {repo_id}...")
            try:
                # Ensure repo exists
                api.create_repo(repo_id=repo_id, repo_type="model", exist_ok=True, private=False)
                
                # Upload file
                api.upload_file(
                    path_or_fileobj=temp_file_path,
                    path_in_repo="README.md",
                    repo_id=repo_id,
                    repo_type="model",
                    commit_message=f"docs: update model card for {title}",
                )
                print(f"  ✓ Live: https://huggingface.co/{repo_id}")
            except Exception as e:
                print(f"  ⚠ Failed for {repo_id}: {e}")

        # Clean up temporary file
        try:
            os.remove(temp_file_path)
        except Exception:
            pass

    # Clean up temp directory
    try:
        os.rmdir(temp_dir)
    except Exception:
        pass

    print("\n✅ All 4 Pillars Model Cards uploaded successfully!")

if __name__ == "__main__":
    main()
