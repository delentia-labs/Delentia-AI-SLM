#!/usr/bin/env python3
"""
upload_dataset.py

Converts Delentia SLM JSONL datasets (v0.2 and v0.3) into structured tabular CSVs
and uploads them to HuggingFace Hub (both Personal and Org spaces) to enable
the Dataset Viewer interface.
"""

import csv
import json
import os
import sys
from pathlib import Path

# Setup paths
SCRIPT_DIR = Path(__file__).parent
DATASETS_DIR = SCRIPT_DIR.parent
PROCESSED_DIR = DATASETS_DIR / "processed"
HF_EXPORT_DIR = DATASETS_DIR / "hf_export"


def parse_toon_completion(completion_text: str) -> dict:
    """Parse JITNA 6-field TOON completion text."""
    fields = {"I": "", "D": "", "Δ": "", "A": "", "R": "", "M": ""}
    lines = completion_text.strip().splitlines()
    
    current_key = None
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        
        # Check field headers
        found_header = False
        for key in fields.keys():
            header_prefix = f"{key}:"
            alt_prefix = "delta:" if key == "Δ" else None
            
            if stripped.startswith(header_prefix):
                current_key = key
                fields[key] = stripped[len(header_prefix):].strip()
                found_header = True
                break
            elif alt_prefix and stripped.startswith(alt_prefix):
                current_key = "Δ"
                fields["Δ"] = stripped[len(alt_prefix):].strip()
                found_header = True
                break
                
        if not found_header and current_key:
            fields[current_key] += " " + stripped
            
    return fields


def convert_jsonl_to_csvs(version: str, jsonl_name: str):
    """Convert a JSONL JITNA dataset into three relational CSV sheets."""
    jsonl_path = PROCESSED_DIR / jsonl_name
    if not jsonl_path.exists():
        print(f"⚠️ Warning: Dataset file {jsonl_path} does not exist. Skipping conversion for {version}.")
        return False
        
    version_dir = HF_EXPORT_DIR / version
    version_dir.mkdir(parents=True, exist_ok=True)
    
    intents = []
    documents = []
    artifacts = []
    
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            pair = json.loads(line)
            prompt = pair["prompt"]
            completion = pair["completion"]
            
            # Extract raw intent
            intent_marker = "User intent: "
            idx = prompt.find(intent_marker)
            raw_intent = prompt[idx + len(intent_marker):].strip() if idx >= 0 else prompt.strip()
            
            # Clean up prompt prefix for intent
            if raw_intent.startswith("You are Delentia"):
                # fallback parsing if system prompt wasn't stripped
                lines_prompt = raw_intent.splitlines()
                raw_intent = lines_prompt[-1].strip() if lines_prompt else raw_intent
                
            toon_fields = parse_toon_completion(completion)
            intent_id = f"intent_{i:04d}"
            
            # 1. Intents row
            intents.append({
                "intent_id": intent_id,
                "title": f"Scenario {i}",
                "description": raw_intent,
                "category": toon_fields["A"][:40] if toon_fields["A"] else "standard",
                "difficulty": 3,
                "split": "train" if i % 10 != 0 else "validation"
            })
            
            # 2. Documents row
            documents.append({
                "doc_id": f"doc_{i:04d}",
                "intent_id": intent_id,
                "source_type": "rct_spec_v5",
                "title": f"Context parameters for intent {i}",
                "content": toon_fields["D"],
                "is_relevant": 1
            })
            
            # 3. Artifacts row
            artifacts.append({
                "artifact_id": f"art_{i:04d}",
                "intent_id": intent_id,
                "artifact_type": "toon_spec_v3",
                "content": completion,
                "quality_label": 5
            })
            
    # Write CSV files
    with open(version_dir / "intents.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=intents[0].keys())
        writer.writeheader()
        writer.writerows(intents)
        
    with open(version_dir / "documents.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=documents[0].keys())
        writer.writeheader()
        writer.writerows(documents)
        
    with open(version_dir / "artifacts.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=artifacts[0].keys())
        writer.writeheader()
        writer.writerows(artifacts)
        
    print(f"Converted {len(intents)} pairs to CSV in {version_dir}")
    return True


def upload_dataset():
    """Upload structured CSVs, JSONL files, and dataset card to HuggingFace Hub."""
    try:
        from huggingface_hub import HfApi, get_token, login
    except ImportError:
        print("ERROR: huggingface_hub not installed. Run: pip install huggingface_hub")
        sys.exit(1)

    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN") or get_token()
    if not token:
        print("ERROR: Set HF_TOKEN environment variable or login using 'huggingface-cli login'.")
        sys.exit(1)

    login(token=token)
    api = HfApi()

    # Repositories targets
    repos = [
        "Ittirit-delentia/delentia-rct-intent-dataset",
        "Delentia/delentia-rct-intent-dataset"
    ]
    
    # Check if we have README_DATASET.md
    dataset_card_path = DATASETS_DIR / "README_DATASET.md"
    
    for repo_id in repos:
        print(f"\nCreating/verifying HuggingFace dataset repo: {repo_id}")
        try:
            api.create_repo(repo_id=repo_id, repo_type="dataset", exist_ok=True, private=False)
            print(f"  [OK] Repository verified: https://huggingface.co/datasets/{repo_id}")
        except Exception as e:
            print(f"  [WARN] Could not verify repo {repo_id}: {e}")
            print(f"  Skipping {repo_id} — check workspace write permissions.")
            continue
            
        # 1. Upload raw JSONL files
        for version, fname in [("v0.2", "jitna_pairs_toon.jsonl"), ("v0.3", "jitna_pairs_v03.jsonl")]:
            src_file = PROCESSED_DIR / fname
            if src_file.exists():
                print(f"  Uploading raw JSONL {fname}...")
                api.upload_file(
                    path_or_fileobj=str(src_file),
                    path_in_repo=f"data/{version}_{fname}",
                    repo_id=repo_id,
                    repo_type="dataset",
                    commit_message=f"Upload raw {version} JSONL dataset"
                )
                
        # 2. Upload structured CSVs
        for version in ["v0.2", "v0.3"]:
            v_dir = HF_EXPORT_DIR / version
            if v_dir.exists():
                for csv_file in v_dir.glob("*.csv"):
                    cname = csv_file.name
                    print(f"  Uploading tabular CSV {version}/{cname}...")
                    api.upload_file(
                        path_or_fileobj=str(csv_file),
                        path_in_repo=f"tabular/{version}/{cname}",
                        repo_id=repo_id,
                        repo_type="dataset",
                        commit_message=f"Upload tabular CSV {version}/{cname}"
                    )
                    
        # 3. Upload Dataset Card (README_DATASET.md -> README.md)
        if dataset_card_path.exists():
            print("  Uploading Dataset Card README.md...")
            api.upload_file(
                path_or_fileobj=str(dataset_card_path),
                path_in_repo="README.md",
                repo_id=repo_id,
                repo_type="dataset",
                commit_message="feat: upload JITNA TOON dataset card documentation"
            )
            print("  [OK] Dataset card live.")
            
    print("\n[OK] Dataset publishing pipeline complete!")


def main():
    print("Delentia SLM Dataset Formatter & Publisher")
    print("-" * 50)
    
    # 1. Convert datasets
    v02_ok = convert_jsonl_to_csvs("v0.2", "jitna_pairs_toon.jsonl")
    v03_ok = convert_jsonl_to_csvs("v0.3", "jitna_pairs_v03.jsonl")
    
    if not (v02_ok or v03_ok):
        print("Error: No datasets found to convert. Run generate_v03_dataset.py first.")
        sys.exit(1)
        
    # 2. Publish to Hugging Face
    upload_dataset()


if __name__ == "__main__":
    main()
