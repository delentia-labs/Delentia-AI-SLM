#!/usr/bin/env python3
import csv
import json
import os
import sys
from pathlib import Path

# Setup paths
SLM_DIR = Path(__file__).parents[2]
OS_DIR = SLM_DIR.parent / "Delentia-OS"
PROCESSED_DIR = SLM_DIR / "datasets" / "processed"
KAGGLE_EXPORT_DIR = SLM_DIR / "datasets" / "kaggle_export"

# Fallback environment configuration to support user's Colab secret typo KAGGLE_k
if not os.environ.get("KAGGLE_KEY"):
    if os.environ.get("KAGGLE_k"):
        os.environ["KAGGLE_KEY"] = os.environ["KAGGLE_k"]
        print("KAGGLE_KEY set from KAGGLE_k environment fallback.")

def parse_toon_completion(completion_text: str) -> dict:
    """Parse JITNA v3 6-field TOON completion text."""
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

def export_to_csv():
    """Convert JSONL JITNA TOON pairs into structured intents, documents, and artifacts CSVs."""
    jsonl_path = PROCESSED_DIR / "jitna_pairs_toon.jsonl"
    if not jsonl_path.exists():
        print(f"Error: Dataset {jsonl_path} does not exist. Run extract_from_os.py first.")
        sys.exit(1)
        
    KAGGLE_EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    
    intents = []
    documents = []
    artifacts = []
    
    with open(jsonl_path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            pair = json.loads(line)
            prompt = pair["prompt"]
            completion = pair["completion"]
            
            # Extract raw intent
            intent_marker = "User intent: "
            idx = prompt.find(intent_marker)
            raw_intent = prompt[idx + len(intent_marker):].strip() if idx >= 0 else prompt.strip()
            
            toon_fields = parse_toon_completion(completion)
            intent_id = f"intent_{i:04d}"
            
            # 1. Intents row
            intents.append({
                "intent_id": intent_id,
                "title": f"Intent Scenario {i}",
                "description": raw_intent,
                "category": toon_fields["A"][:30],
                "difficulty": 3,
                "split": "train" if i % 10 != 0 else "valid"
            })
            
            # 2. Documents row
            documents.append({
                "doc_id": f"doc_{i:04d}",
                "intent_id": intent_id,
                "source_type": "rct_spec",
                "title": f"Context parameters for intent {i}",
                "content": toon_fields["D"],
                "is_relevant": 1
            })
            
            # 3. Artifacts row
            artifacts.append({
                "artifact_id": f"art_{i:04d}",
                "intent_id": intent_id,
                "artifact_type": "toon_spec",
                "content": completion,
                "quality_label": 5
            })
            
    # Write CSV files
    with open(KAGGLE_EXPORT_DIR / "intents.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=intents[0].keys())
        writer.writeheader()
        writer.writerows(intents)
        
    with open(KAGGLE_EXPORT_DIR / "documents.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=documents[0].keys())
        writer.writeheader()
        writer.writerows(documents)
        
    with open(KAGGLE_EXPORT_DIR / "artifacts.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=artifacts[0].keys())
        writer.writeheader()
        writer.writerows(artifacts)
        
    print(f"Exported {len(intents)} structured dataset rows to {KAGGLE_EXPORT_DIR}")

def upload_dataset():
    """Upload dataset directory to Kaggle Hub."""
    username = os.environ.get("KAGGLE_USERNAME")
    key = os.environ.get("KAGGLE_KEY")
    
    if not username or not key:
        print("Skipping Kaggle upload: KAGGLE_USERNAME or KAGGLE_KEY environment variables not set.")
        return
        
    try:
        import kagglehub
        print("Authenticating with Kaggle Hub...")
        # kagglehub uses standard environment variable credentials
        
        dataset_handle = f"{username}/delentia-rct-intent-dataset"
        print(f"Uploading JITNA TOON dataset to Kaggle: {dataset_handle}...")
        
        # Create dataset metadata metadata if not exist
        meta_file = KAGGLE_EXPORT_DIR / "dataset-metadata.json"
        if not meta_file.exists():
            metadata = {
                "title": "Delentia RCT Intent Dataset",
                "id": dataset_handle,
                "licenses": [{"name": "CC0-1.0"}]
            }
            with open(meta_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)
                
        # Call upload API
        path = kagglehub.dataset_upload(
            handle=dataset_handle,
            local_dataset_dir=str(KAGGLE_EXPORT_DIR)
        )
        print(f"Successfully uploaded dataset! Access URL: {path}")
    except ImportError:
        print("kagglehub library not installed. Install with: pip install kagglehub")
    except Exception as e:
        print(f"Failed to upload to Kaggle Hub: {e}")

if __name__ == "__main__":
    export_to_csv()
    upload_dataset()
