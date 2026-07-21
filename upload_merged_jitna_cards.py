#!/usr/bin/env python3
"""
upload_merged_jitna_cards.py

Writes README.md model cards for the 3 pre-merged models (Executor, Scribe, Guardian)
and uploads them to HuggingFace Hub repositories under the Delentia organization.

Usage:
    $env:HF_TOKEN = "hf_xxxxxxxxxxxxxxxx"
    python upload_merged_jitna_cards.py
"""

import os
import sys

if sys.platform.startswith("win"):
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:
        pass

# Define the README templates for each of the 3 pre-merged models (v0.4 aligned)
MODEL_CARDS = {
    "executor": {
        "repo_suffix": "delentia-slm-jitna-executor-v0.4",
        "title": "The Executor (Pre-Merged Tool Call)",
        "readme": r"""---
license: apache-2.0
base_model: Delentia/delentia-slm-jitna-v0.4
tags:
- gguf
- llama-cpp
- text-generation
- tool-use
- delentia-os
- JITNA
- merged
---

# Delentia SLM — The Pre-Merged Executor v0.4 (slm-jitna-executor-v0.4)

[![GitHub Stars](https://img.shields.io/github/stars/delentia-labs/Delentia-OS?style=social)](https://github.com/delentia-labs/Delentia-OS)
[![GitHub Forks](https://img.shields.io/github/forks/delentia-labs/Delentia-OS?style=social)](https://github.com/delentia-labs/Delentia-OS)

> ⚙️ **Looking for the SDK & Source Code?**  
> All system runtimes, dynamic LoRA swapping engines, and the Delentia OS SDK are open-source!  
> 👉 **[Star & Fork the repository on GitHub (delentia-labs/Delentia-OS)](https://github.com/delentia-labs/Delentia-OS)**

---

This is the **Pre-Merged GGUF/Safetensors** version of **The Executor**, the tool-calling engine of **Delentia OS**. The Executor adapter has been merged directly into the base kernel weights for high performance local edge execution via Ollama or llama.cpp without needing external adapter loading.

## ⚡ Quick Start: Local Edge Execution via Ollama

To run this tool executor model locally in under 5 minutes:

1. Download the GGUF model binary: `delentia-slm-jitna-executor-v0.4-Q4_K_M.gguf`
2. Create a local `Modelfile` with the following configuration:
```dockerfile
FROM ./delentia-slm-jitna-executor-v0.4-Q4_K_M.gguf

TEMPLATE \"\"\"<|start_header_id|>system<|end_header_id|>
You are the Executor. Translate user intent into valid JSON/TOON format.
<|start_header_id|>user<|end_header_id|>
{{ .Prompt }}<|end_header_id|>
\"\"\"
```
3. Register and run the model via Ollama CLI:
```bash
ollama create delentia-executor -f Modelfile
ollama run delentia-executor
```

## ⚡ Quick Start: Python Transformers

Alternatively, run the merged weights directly using Python Hugging Face Transformers:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "Delentia/delentia-slm-jitna-executor-v0.4"

# Load the merged weights directly
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)
```

## 🌐 Delentia OS Ecosystem Model Roster (v0.4.x)
Delentia OS is organized into two primary deployment styles: **Dynamic PEFT Adapters** (1+4 Pillars) for sub-ms switching in unified VRAM, and **Pre-Merged GGUF Models** for direct plug-and-play local execution in Ollama / llama.cpp.

| Component / Role | Deployment Type | Hugging Face Repository | Description | GGUF Support |
| :--- | :--- | :--- | :--- | :---: |
| **SLM Base Kernel** | Base Foundation | [Delentia/delentia-slm-jitna-v0.4](https://huggingface.co/Delentia/delentia-slm-jitna-v0.4) | Core cognitive LLM (8B Parameters) | ✅ |
| **The Router** | PEFT LoRA Adapter | [Delentia/delentia-lora-router-v0.4](https://huggingface.co/Delentia/delentia-lora-router-v0.4) | Intention parser & node routing | ❌ (PEFT only) |
| **The Executor** | PEFT LoRA Adapter | [Delentia/delentia-lora-executor-v0.4](https://huggingface.co/Delentia/delentia-lora-executor-v0.4) | JSON tool payload generation | ✅ (Merged GGUF below) |
| **The Guardian** | PEFT LoRA Adapter | [Delentia/delentia-lora-guardian-v0.4](https://huggingface.co/Delentia/delentia-lora-guardian-v0.4) | Zero-trust constitutional safety | ✅ (Merged GGUF below) |
| **The Scribe** | PEFT LoRA Adapter | [Delentia/delentia-lora-scribe-v0.4](https://huggingface.co/Delentia/delentia-lora-scribe-v0.4) | Context compression/summarization | ✅ (Merged GGUF below) |
| **Pre-Merged Executor** | Pre-Merged GGUF | [Delentia/delentia-slm-jitna-executor-v0.4](https://huggingface.co/Delentia/delentia-slm-jitna-executor-v0.4) | Complete tool executor (plug-and-play) | ✅ |
| **Pre-Merged Guardian** | Pre-Merged GGUF | [Delentia/delentia-slm-jitna-guardian-v0.4](https://huggingface.co/Delentia/delentia-slm-jitna-guardian-v0.4) | Full safety guardrail model | ✅ |
| **Pre-Merged Scribe** | Pre-Merged GGUF | [Delentia/delentia-slm-jitna-scribe-v0.4](https://huggingface.co/Delentia/delentia-slm-jitna-scribe-v0.4) | Out-of-the-box context compressor | ✅ |
"""
    },
    "guardian": {
        "repo_suffix": "delentia-slm-jitna-guardian-v0.4",
        "title": "The Guardian (Pre-Merged Safety Shield)",
        "readme": r"""---
license: apache-2.0
base_model: Delentia/delentia-slm-jitna-v0.4
tags:
- gguf
- llama-cpp
- text-generation
- safety
- delentia-os
- JITNA
- merged
---

# Delentia SLM — The Pre-Merged Guardian v0.4 (slm-jitna-guardian-v0.4)

[![GitHub Stars](https://img.shields.io/github/stars/delentia-labs/Delentia-OS?style=social)](https://github.com/delentia-labs/Delentia-OS)
[![GitHub Forks](https://img.shields.io/github/forks/delentia-labs/Delentia-OS?style=social)](https://github.com/delentia-labs/Delentia-OS)

> ⚙️ **Looking for the SDK & Source Code?**  
> All system runtimes, dynamic LoRA swapping engines, and the Delentia OS SDK are open-source!  
> 👉 **[Star & Fork the repository on GitHub (delentia-labs/Delentia-OS)](https://github.com/delentia-labs/Delentia-OS)**

---

This is the **Pre-Merged GGUF/Safetensors** version of **The Guardian**, the zero-trust Constitutional AI guardrail engine of **Delentia OS**. The Guardian safety adapter has been merged directly into the base weights to enable out-of-the-box system policy checks locally.

## ⚡ Quick Start: Local Edge Execution via Ollama

To run this constitutional safety model locally:

1. Download the GGUF model binary: `delentia-slm-jitna-guardian-v0.4-Q4_K_M.gguf`
2. Create a local `Modelfile` with the following configuration:
```dockerfile
FROM ./delentia-slm-jitna-guardian-v0.4-Q4_K_M.gguf

TEMPLATE \"\"\"<|start_header_id|>system<|end_header_id|>
You are the Guardian. Evaluate intent safety against ZK-FDIA state parameters.
<|start_header_id|>user<|end_header_id|>
{{ .Prompt }}<|end_header_id|>
\"\"\"
```
3. Register and run the model via Ollama CLI:
```bash
ollama create delentia-guardian -f Modelfile
ollama run delentia-guardian
```

## ⚡ Quick Start: Python Transformers

Alternatively, load the merged weights directly using Python Hugging Face Transformers:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "Delentia/delentia-slm-jitna-guardian-v0.4"

# Load the merged weights directly
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)
```

## 🌐 Delentia OS Ecosystem Model Roster (v0.4.x)
Delentia OS is organized into two primary deployment styles: **Dynamic PEFT Adapters** (1+4 Pillars) for sub-ms switching in unified VRAM, and **Pre-Merged GGUF Models** for direct plug-and-play local execution in Ollama / llama.cpp.

| Component / Role | Deployment Type | Hugging Face Repository | Description | GGUF Support |
| :--- | :--- | :--- | :--- | :---: |
| **SLM Base Kernel** | Base Foundation | [Delentia/delentia-slm-jitna-v0.4](https://huggingface.co/Delentia/delentia-slm-jitna-v0.4) | Core cognitive LLM (8B Parameters) | ✅ |
| **The Router** | PEFT LoRA Adapter | [Delentia/delentia-lora-router-v0.4](https://huggingface.co/Delentia/delentia-lora-router-v0.4) | Intention parser & node routing | ❌ (PEFT only) |
| **The Executor** | PEFT LoRA Adapter | [Delentia/delentia-lora-executor-v0.4](https://huggingface.co/Delentia/delentia-lora-executor-v0.4) | JSON tool payload generation | ✅ (Merged GGUF below) |
| **The Guardian** | PEFT LoRA Adapter | [Delentia/delentia-lora-guardian-v0.4](https://huggingface.co/Delentia/delentia-lora-guardian-v0.4) | Zero-trust constitutional safety | ✅ (Merged GGUF below) |
| **The Scribe** | PEFT LoRA Adapter | [Delentia/delentia-lora-scribe-v0.4](https://huggingface.co/Delentia/delentia-lora-scribe-v0.4) | Context compression/summarization | ✅ (Merged GGUF below) |
| **Pre-Merged Executor** | Pre-Merged GGUF | [Delentia/delentia-slm-jitna-executor-v0.4](https://huggingface.co/Delentia/delentia-slm-jitna-executor-v0.4) | Complete tool executor (plug-and-play) | ✅ |
| **Pre-Merged Guardian** | Pre-Merged GGUF | [Delentia/delentia-slm-jitna-guardian-v0.4](https://huggingface.co/Delentia/delentia-slm-jitna-guardian-v0.4) | Full safety guardrail model | ✅ |
| **Pre-Merged Scribe** | Pre-Merged GGUF | [Delentia/delentia-slm-jitna-scribe-v0.4](https://huggingface.co/Delentia/delentia-slm-jitna-scribe-v0.4) | Out-of-the-box context compressor | ✅ |
"""
    },
    "scribe": {
        "repo_suffix": "delentia-slm-jitna-scribe-v0.4",
        "title": "The Scribe (Pre-Merged Context Compressor)",
        "readme": r"""---
license: apache-2.0
base_model: Delentia/delentia-slm-jitna-v0.4
tags:
- gguf
- llama-cpp
- text-generation
- context-compression
- delentia-os
- JITNA
- merged
---

# Delentia SLM — The Pre-Merged Scribe v0.4 (slm-jitna-scribe-v0.4)

[![GitHub Stars](https://img.shields.io/github/stars/delentia-labs/Delentia-OS?style=social)](https://github.com/delentia-labs/Delentia-OS)
[![GitHub Forks](https://img.shields.io/github/forks/delentia-labs/Delentia-OS?style=social)](https://github.com/delentia-labs/Delentia-OS)

> ⚙️ **Looking for the SDK & Source Code?**  
> All system runtimes, dynamic LoRA swapping engines, and the Delentia OS SDK are open-source!  
> 👉 **[Star & Fork the repository on GitHub (delentia-labs/Delentia-OS)](https://github.com/delentia-labs/Delentia-OS)**

---

This is the **Pre-Merged GGUF/Safetensors** version of **The Scribe**, the context compression engine of **Delentia OS**. The Scribe adapter has been merged directly into the base weights to allow offline context-summarization directly in Ollama.

## ⚡ Quick Start: Local Edge Execution via Ollama

To run this context compressor model locally:

1. Download the GGUF model binary: `delentia-slm-jitna-scribe-v0.4-Q4_K_M.gguf`
2. Create a local `Modelfile` with the following configuration:
```dockerfile
FROM ./delentia-slm-jitna-scribe-v0.4-Q4_K_M.gguf

TEMPLATE \"\"\"<|start_header_id|>system<|end_header_id|>
You are the Scribe. Compress long context segments recursively.
<|start_header_id|>user<|end_header_id|>
{{ .Prompt }}<|end_header_id|>
\"\"\"
```
3. Register and run the model via Ollama CLI:
```bash
ollama create delentia-scribe -f Modelfile
ollama run delentia-scribe
```

## ⚡ Quick Start: Python Transformers

Alternatively, load the merged weights directly using Python Hugging Face Transformers:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "Delentia/delentia-slm-jitna-scribe-v0.4"

# Load the merged weights directly
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)
```

## 🌐 Delentia OS Ecosystem Model Roster (v0.4.x)
Delentia OS is organized into two primary deployment styles: **Dynamic PEFT Adapters** (1+4 Pillars) for sub-ms switching in unified VRAM, and **Pre-Merged GGUF Models** for direct plug-and-play local execution in Ollama / llama.cpp.

| Component / Role | Deployment Type | Hugging Face Repository | Description | GGUF Support |
| :--- | :--- | :--- | :--- | :---: |
| **SLM Base Kernel** | Base Foundation | [Delentia/delentia-slm-jitna-v0.4](https://huggingface.co/Delentia/delentia-slm-jitna-v0.4) | Core cognitive LLM (8B Parameters) | ✅ |
| **The Router** | PEFT LoRA Adapter | [Delentia/delentia-lora-router-v0.4](https://huggingface.co/Delentia/delentia-lora-router-v0.4) | Intention parser & node routing | ❌ (PEFT only) |
| **The Executor** | PEFT LoRA Adapter | [Delentia/delentia-lora-executor-v0.4](https://huggingface.co/Delentia/delentia-lora-executor-v0.4) | JSON tool payload generation | ✅ (Merged GGUF below) |
| **The Guardian** | PEFT LoRA Adapter | [Delentia/delentia-lora-guardian-v0.4](https://huggingface.co/Delentia/delentia-lora-guardian-v0.4) | Zero-trust constitutional safety | ✅ (Merged GGUF below) |
| **The Scribe** | PEFT LoRA Adapter | [Delentia/delentia-lora-scribe-v0.4](https://huggingface.co/Delentia/delentia-lora-scribe-v0.4) | Context compression/summarization | ✅ (Merged GGUF below) |
| **Pre-Merged Executor** | Pre-Merged GGUF | [Delentia/delentia-slm-jitna-executor-v0.4](https://huggingface.co/Delentia/delentia-slm-jitna-executor-v0.4) | Complete tool executor (plug-and-play) | ✅ |
| **Pre-Merged Guardian** | Pre-Merged GGUF | [Delentia/delentia-slm-jitna-guardian-v0.4](https://huggingface.co/Delentia/delentia-slm-jitna-guardian-v0.4) | Full safety guardrail model | ✅ |
| **Pre-Merged Scribe** | Pre-Merged GGUF | [Delentia/delentia-slm-jitna-scribe-v0.4](https://huggingface.co/Delentia/delentia-slm-jitna-scribe-v0.4) | Out-of-the-box context compressor | ✅ |
"""
    }
}

def main():
    try:
        from huggingface_hub import HfApi, get_token, login
    except ImportError:
        print("ERROR: huggingface_hub not installed. Run: pip install huggingface_hub")
        sys.exit(1)

    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN") or get_token()
    if not token:
        print("ERROR: HF Token not found. Set HF_TOKEN env var first.")
        sys.exit(1)

    login(token=token)
    api = HfApi()

    org_user = "Delentia"
    temp_dir = os.path.join(os.path.dirname(__file__), "temp_merged_readme")
    os.makedirs(temp_dir, exist_ok=True)

    print("🚀 Starting Model Cards Upload for the 3 Pre-Merged Models...")

    for key, info in MODEL_CARDS.items():
        suffix = info["repo_suffix"]
        title = info["title"]
        readme_content = info["readme"]

        # Write to temporary file
        temp_file_path = os.path.join(temp_dir, f"README_{key}.md")
        with open(temp_file_path, "w", encoding="utf-8") as f:
            f.write(readme_content)

        repo_id = f"{org_user}/{suffix}"
        print(f"\nUploading model card to: {repo_id}...")
        try:
            # Ensure repository exists
            api.create_repo(repo_id=repo_id, repo_type="model", exist_ok=True, private=False)
            
            # Upload README
            api.upload_file(
                path_or_fileobj=temp_file_path,
                path_in_repo="README.md",
                repo_id=repo_id,
                repo_type="model",
                commit_message=f"docs: restructure and update Model Card for {title}",
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

    print("\n✅ All Pre-Merged JITNA Model Cards uploaded successfully!")

if __name__ == "__main__":
    main()
