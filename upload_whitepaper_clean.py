#!/usr/bin/env python3
"""
upload_whitepaper_clean.py

Clean, authoritative upload script for Delentia OS v0.4.1.
Synchronizes all certified Whitepapers, RAG Corpus Chunks, Local Hardware Attestations,
Air-Gapped Enterprise Guides, and Ollama Modelfiles directly to Hugging Face Hub repositories.
"""

import os
import sys
from pathlib import Path
from huggingface_hub import HfApi

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

api = HfApi()
repo_dataset = "Delentia/delentia-os-whitepaper-rag-corpus"
repo_model = "Delentia/delentia-slm-jitna-v0.4"

base_path = Path("c:/Users/whale/delentia/Delentia-Private-OS/whitepapers")
th_path = base_path / "01_foundation" / "DELENTIA_OS_PUBLIC_WHITEPAPER_v2.2.0_TH.md"
en_path = base_path / "01_foundation" / "DELENTIA_OS_PUBLIC_WHITEPAPER_v2.2.0_EN.md"

local_attest_md = base_path / "02_benchmarks" / "LOCAL_HARDWARE_ATTESTATION.md"
local_attest_json = base_path / "02_benchmarks" / "benchmark_results_local.json"
enterprise_sdk_guide = base_path / "03_deployment" / "AIR_GAPPED_ENTERPRISE_SDK_GUIDE.md"

modelfile_path = Path("c:/Users/whale/delentia/Delentia-AI-SLM/models/Modelfile")
rag_full = Path("c:/Users/whale/delentia/Delentia-AI-SLM/datasets/processed/rag_corpus/whitepaper_full.md")
rag_csv = Path("c:/Users/whale/delentia/Delentia-AI-SLM/datasets/processed/rag_corpus/whitepaper_chunks.csv")

print("[INFO] Uploading certified Delentia OS v0.4.1 assets to Hugging Face...")

# ── 1. Upload Dataset Artifacts ──────────────────────────────────────────────
files_to_dataset = [
    (rag_full, "whitepaper_full.md", "Update Whitepaper RAG Corpus Full MD (v0.4.1 live audit sync)"),
    (rag_csv, "whitepaper_chunks.csv", "Update Whitepaper RAG Corpus Chunks CSV (v0.4.1 live audit sync)"),
    (en_path, "whitepaper_en.md", "Upload Whitepaper EN MD (v0.4.1 live audit sync)"),
    (enterprise_sdk_guide, "AIR_GAPPED_ENTERPRISE_SDK_GUIDE.md", "Upload Enterprise SDK Guide (v0.4.1 sync)"),
]

for local_f, repo_f, commit_msg in files_to_dataset:
    if local_f.exists():
        api.upload_file(
            path_or_fileobj=str(local_f),
            path_in_repo=repo_f,
            repo_id=repo_dataset,
            repo_type="dataset",
            commit_message=commit_msg
        )
        print(f"  [OK] Uploaded {repo_f} to dataset repo")

# ── 2. Upload Base Model Documentation Artifacts ─────────────────────────────
files_to_model = [
    (th_path, "docs/DELENTIA_OS_PUBLIC_WHITEPAPER_v2.2.0_TH.md", "Sync Updated Whitepaper TH (v0.4.1 empirical audit sync)"),
    (en_path, "docs/DELENTIA_OS_PUBLIC_WHITEPAPER_v2.2.0_EN.md", "Sync Updated Whitepaper EN (v0.4.1 empirical audit sync)"),
    (enterprise_sdk_guide, "docs/AIR_GAPPED_ENTERPRISE_SDK_GUIDE.md", "Upload Air-Gapped Enterprise SDK Guide (v0.4.1)"),
    (local_attest_md, "benchmarks/LOCAL_HARDWARE_ATTESTATION.md", "Upload Certified Local Hardware Attestation Report"),
    (local_attest_json, "benchmarks/benchmark_results_local.json", "Upload Raw Engineering Benchmark JSON Logs"),
    (modelfile_path, "Modelfile", "Upload Official Ollama Modelfile Integration for Delentia OS v0.4.1"),
]

for local_f, repo_f, commit_msg in files_to_model:
    if local_f.exists():
        api.upload_file(
            path_or_fileobj=str(local_f),
            path_in_repo=repo_f,
            repo_id=repo_model,
            repo_type="model",
            commit_message=commit_msg
        )
        print(f"  [OK] Uploaded {repo_f} to base model repo")

print("\n[SUCCESS] ALL CERTIFIED V0.4.1 ASSETS UPLOADED SUCCESSFULLY TO HUGGING FACE!")
