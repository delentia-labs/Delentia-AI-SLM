#!/usr/bin/env python3
"""
split_pillars_parquet.py

Local preprocessing script for the Delentia OS 1+4 Pillars v0.4.
This script:
1. Executes the 4 specialized dataset generators to create raw JSONL files.
2. Performs schema validation and sanity checks on each dataset.
3. Converts the JSONL files to compressed, strictly-typed Parquet files locally.
"""

import os
import sys
import subprocess
import json
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
REPO_DIR = SCRIPT_DIR.parents[1]
PROCESSED_DIR = REPO_DIR / "datasets" / "processed"

GENERATORS = {
    "executor": SCRIPT_DIR / "generate_executor_dataset.py",
    "router": SCRIPT_DIR / "generate_router_dataset.py",
    "guardian": SCRIPT_DIR / "generate_guardian_dataset.py",
    "scribe": SCRIPT_DIR / "generate_scribe_dataset.py",
    "delta_benchmark": SCRIPT_DIR / "generate_delta_benchmark.py"
}

OUTPUT_FILES = {
    "executor": {
        "jsonl": PROCESSED_DIR / "jitna_executor_pairs.jsonl",
        "parquet": PROCESSED_DIR / "jitna_executor_pairs.parquet"
    },
    "router": {
        "jsonl": PROCESSED_DIR / "jitna_router_pairs.jsonl",
        "parquet": PROCESSED_DIR / "jitna_router_pairs.parquet"
    },
    "guardian": {
        "jsonl": PROCESSED_DIR / "jitna_guardian_pairs.jsonl",
        "parquet": PROCESSED_DIR / "jitna_guardian_pairs.parquet"
    },
    "scribe": {
        "jsonl": PROCESSED_DIR / "jitna_scribe_pairs.jsonl",
        "parquet": PROCESSED_DIR / "jitna_scribe_pairs.parquet"
    }
}

def validate_schema(pillar: str, jsonl_path: Path) -> bool:
    """Validate JSONL schema for specific pillar requirements."""
    print(f"🔍 Validating schema for {pillar}...")
    with open(jsonl_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    if not lines:
        print(f"❌ Error: {jsonl_path} is empty.")
        return False
        
    for i, line in enumerate(lines, 1):
        try:
            data = json.loads(line)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON at line {i}: {e}")
            return False
            
        if "prompt" not in data or "completion" not in data:
            print(f"❌ Missing required keys 'prompt' or 'completion' at line {i}.")
            return False
            
        # Executor specific JSON constraint
        if pillar == "executor":
            try:
                # Executor completion must be valid JSON
                json.loads(data["completion"])
            except json.JSONDecodeError:
                print(f"❌ Executor completion is not valid JSON at line {i}: {data['completion']}")
                return False
                
    print(f"  ✅ Schema validation passed for {pillar} ({len(lines)} pairs).")
    return True

def convert_to_parquet(jsonl_path: Path, parquet_path: Path):
    """Convert JSONL dataset file to Parquet format."""
    import pandas as pd
    print(f"📦 Converting {jsonl_path.name} to Parquet...")
    df = pd.read_json(jsonl_path, lines=True)
    df.to_parquet(parquet_path, index=False)
    print(f"  ✅ Saved to {parquet_path.name} (Size: {parquet_path.stat().st_size / 1024:.1f} KB)")

def main():
    print("=" * 60)
    print("Delentia 1+4 Pillars Local Parquet Preprocessing & Splitter")
    print("=" * 60)
    
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Run generators
    for pillar, script_path in GENERATORS.items():
        if not script_path.exists():
            print(f"❌ Error: Generator script not found for {pillar} at {script_path}")
            sys.exit(1)
            
        print(f"\n🚀 Running dataset generator for: {pillar}...")
        result = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True, encoding="utf-8")
        if result.returncode != 0:
            print(f"❌ Error running generator for {pillar}:")
            print(result.stderr)
            sys.exit(1)
        print(result.stdout.strip())
        
    # 2. Validate and convert
    for pillar, paths in OUTPUT_FILES.items():
        jsonl = paths["jsonl"]
        parquet = paths["parquet"]
        
        if not jsonl.exists():
            print(f"❌ Error: Synthesized JSONL not found for {pillar} at {jsonl}")
            sys.exit(1)
            
        # Validate schema locally
        if not validate_schema(pillar, jsonl):
            print(f"❌ Schema validation failed for {pillar}. Stopping pipeline.")
            sys.exit(1)
            
        # Convert to parquet
        try:
            convert_to_parquet(jsonl, parquet)
        except Exception as e:
            print(f"❌ Parquet conversion failed for {pillar}: {e}")
            sys.exit(1)
            
    print("\n🎉 All 1+4 Pillar datasets generated, validated, and converted to Parquet successfully!")

if __name__ == "__main__":
    main()
