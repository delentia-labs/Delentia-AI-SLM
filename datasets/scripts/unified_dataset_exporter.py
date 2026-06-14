#!/usr/bin/env python3
"""
unified_dataset_exporter.py

Unified Data Pipeline for Delentia OS SLM:
1. Converts processed JSONL datasets (v0.2 and v0.3) into relational CSV format.
2. Packages metadata and dataset cards.
3. Uploads files directly to both Kaggle Hub and HuggingFace Hub.
"""

import csv
import json
import os
import sys
from pathlib import Path

# Reconfigure stdout/stderr to UTF-8 on Windows to prevent CP874 UnicodeEncodeError
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

# Setup paths
SCRIPT_DIR = Path(__file__).parent
DATASETS_DIR = SCRIPT_DIR.parent
PROCESSED_DIR = DATASETS_DIR / "processed"
HF_EXPORT_DIR = DATASETS_DIR / "hf_export"
KAGGLE_EXPORT_DIR = DATASETS_DIR / "kaggle_export"

# Fallback environment configuration to support user's Colab secret typo KAGGLE_k
if not os.environ.get("KAGGLE_KEY") and os.environ.get("KAGGLE_k"):
    os.environ["KAGGLE_KEY"] = os.environ["KAGGLE_k"]
    print("[INFO] KAGGLE_KEY configured from fallback KAGGLE_k environment variable.")


def parse_toon_completion(completion_text: str) -> dict:
    """Parse JITNA 6-field TOON completion text."""
    fields = {"I": "", "D": "", "Δ": "", "A": "", "R": "", "M": ""}
    lines = completion_text.strip().splitlines()
    
    current_key = None
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        
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


def convert_dataset_to_csv(version: str, jsonl_name: str, target_dir: Path) -> bool:
    """Read JITNA JSONL and write relation intents.csv, documents.csv, and artifacts.csv."""
    jsonl_path = PROCESSED_DIR / jsonl_name
    if not jsonl_path.exists():
        print(f"⚠️  [WARN] Dataset {jsonl_path} does not exist. Skipping conversion.")
        return False
        
    target_dir.mkdir(parents=True, exist_ok=True)
    
    intents = []
    documents = []
    artifacts = []
    
    with open(jsonl_path, encoding="utf-8") as f:
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
            
            toon_fields = parse_toon_completion(completion)
            intent_id = f"intent_{i:04d}"
            
            intents.append({
                "intent_id": intent_id,
                "title": f"Scenario {i}",
                "description": raw_intent,
                "category": toon_fields["A"][:30] if toon_fields["A"] else "standard",
                "difficulty": 3,
                "split": "train" if i % 10 != 0 else "valid"
            })
            
            documents.append({
                "doc_id": f"doc_{i:04d}",
                "intent_id": intent_id,
                "source_type": "rct_spec",
                "title": f"Context parameters for intent {i}",
                "content": toon_fields["D"],
                "is_relevant": 1
              })
              
            artifacts.append({
                "artifact_id": f"art_{i:04d}",
                "intent_id": intent_id,
                "artifact_type": "toon_spec",
                "content": completion,
                "quality_label": 5
            })
            
    # Write CSV sheets
    for name, data in [("intents", intents), ("documents", documents), ("artifacts", artifacts)]:
        with open(target_dir / f"{name}.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
            
    print(f"✅ [OK] Converted {len(intents)} pairs for {version} in {target_dir}")
    return True


def upload_to_huggingface():
    """Publish to HuggingFace Hub (tabular and raw data)."""
    try:
        from huggingface_hub import HfApi, get_token, login
    except ImportError:
        print("[SKIP] huggingface_hub not installed. Run 'pip install huggingface_hub' to enable HF uploads.")
        return

    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN") or get_token()
    if not token:
        print("[SKIP] Hugging Face Token not configured in environment variables (HF_TOKEN).")
        return

    try:
        login(token=token)
        api = HfApi()
        
        # Deploy to official organization or personal account spaces
        repos = [
            "Ittirit-delentia/delentia-rct-intent-dataset",
            "Delentia/delentia-rct-intent-dataset"
        ]
        
        dataset_card_path = DATASETS_DIR / "README_DATASET.md"
        
        for repo_id in repos:
            print(f"\n🚀 Verifying HuggingFace Repository: {repo_id}")
            api.create_repo(repo_id=repo_id, repo_type="dataset", exist_ok=True, private=False)
            
            # Upload JSONL files
            for version, fname in [("v0.2", "jitna_pairs_toon.jsonl"), ("v0.3", "jitna_pairs_v03.jsonl")]:
                src_file = PROCESSED_DIR / fname
                if src_file.exists():
                    print(f"  Uploading {version} raw JSONL...")
                    api.upload_file(
                        path_or_fileobj=str(src_file),
                        path_in_repo=f"data/{version}_{fname}",
                        repo_id=repo_id,
                        repo_type="dataset"
                    )
                    
            # Upload CSV files
            for version in ["v0.2", "v0.3"]:
                v_dir = HF_EXPORT_DIR / version
                if v_dir.exists():
                    for csv_file in v_dir.glob("*.csv"):
                        print(f"  Uploading tabular {version}/{csv_file.name}...")
                        api.upload_file(
                            path_or_fileobj=str(csv_file),
                            path_in_repo=f"tabular/{version}/{csv_file.name}",
                            repo_id=repo_id,
                            repo_type="dataset"
                        )
            
            # Upload README Dataset Card
            if dataset_card_path.exists():
                api.upload_file(
                    path_or_fileobj=str(dataset_card_path),
                    path_in_repo="README.md",
                    repo_id=repo_id,
                    repo_type="dataset"
                )
                print("  [OK] Dataset card uploaded.")
                
        print("🎉 [SUCCESS] Uploaded datasets successfully to HuggingFace Hub!")
    except Exception as e:
        print(f"❌ Failed HuggingFace upload: {e}")


def upload_to_kaggle():
    """Publish CSV files and Metadata to Kaggle Hub."""
    username = os.environ.get("KAGGLE_USERNAME")
    key = os.environ.get("KAGGLE_KEY")
    
    if not (username and key):
        print("\n[SKIP] Kaggle credentials not configured in environment variables (KAGGLE_USERNAME, KAGGLE_KEY).")
        return
        
    try:
        import kagglehub
        dataset_handle = f"{username}/delentia-rct-intent-dataset"
        print(f"\n🚀 Packaging and uploading CSV data to Kaggle: {dataset_handle}...")
        
        # Write metadata file
        meta_file = KAGGLE_EXPORT_DIR / "dataset-metadata.json"
        metadata = {
            "title": "Delentia RCT Intent Dataset",
            "id": dataset_handle,
            "licenses": [{"name": "CC-BY-4.0"}]
        }
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
            
        path = kagglehub.dataset_upload(
            handle=dataset_handle,
            local_dataset_dir=str(KAGGLE_EXPORT_DIR)
        )
        print(f"🎉 [SUCCESS] Uploaded dataset successfully to Kaggle! Access URL: {path}")
    except ImportError:
        print("[SKIP] kagglehub not installed. Run 'pip install kagglehub' to enable Kaggle uploads.")
    except Exception as e:
        print(f"❌ Failed Kaggle upload: {e}")


def main():
    print("=" * 60)
    print("Delentia Unified Dataset Exporter & Publishing Hub")
    print("=" * 60)
    
    # 1. Export v0.2 to CSV (for Kaggle Export and HF tabular v0.2)
    v02_ok = convert_dataset_to_csv("v0.2", "jitna_pairs_toon.jsonl", HF_EXPORT_DIR / "v0.2")
    # Copy to Kaggle folder for unified packaging
    if v02_ok:
        convert_dataset_to_csv("v0.2", "jitna_pairs_toon.jsonl", KAGGLE_EXPORT_DIR)
        
    # 2. Export v0.3 to CSV
    v03_ok = convert_dataset_to_csv("v0.3", "jitna_pairs_v03.jsonl", HF_EXPORT_DIR / "v0.3")
    
    if not (v02_ok or v03_ok):
        print("❌ Error: No datasets found in 'datasets/processed'. Exiting.")
        sys.exit(1)
        
    # 3. Publish to endpoints
    upload_to_huggingface()
    upload_to_kaggle()
    
    print("\n🏁 [OK] Pipeline finished.")


if __name__ == "__main__":
    main()
