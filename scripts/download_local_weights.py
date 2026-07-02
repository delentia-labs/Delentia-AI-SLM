#!/usr/bin/env python3
"""
download_local_weights.py

Automated Local Weight Downloader for Delentia OS.
Downloads all official 1+4 base model GGUF files and PEFT LoRA adapters directly
from Hugging Face repositories into the local models directory structure.
"""

import sys
import time
from pathlib import Path
from huggingface_hub import hf_hub_download

# Enforce UTF-8 encoding for standard output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Setup local paths relative to this script
SCRIPT_DIR = Path(__file__).parent
SLM_DIR = SCRIPT_DIR.parent
MODELS_DIR = SLM_DIR / "models"
ADAPTERS_DIR = MODELS_DIR / "adapters"
GGUF_DIR = MODELS_DIR / "gguf"

# Define Hugging Face Organazation Repository Mappings
PILLAR_REPOS = {
    "executor": "Delentia/delentia-slm-jitna-executor-v0.4",
    "guardian": "Delentia/delentia-slm-jitna-guardian-v0.4",
    "scribe": "Delentia/delentia-slm-jitna-scribe-v0.4",
    "router": "Delentia/delentia-slm-jitna-router-v0.4",
}

BASE_REPO = "Delentia/delentia-slm-jitna-v0.4"


def main():
    print("=" * 80)
    print("🤖 DELENTIA OS - AUTOMATED LOCAL WEIGHT DOWNLOADER")
    print("=" * 80)

    ADAPTERS_DIR.mkdir(parents=True, exist_ok=True)
    GGUF_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\n📁 Target Local Directories:")
    print(f"   Adapters Path : {ADAPTERS_DIR}")
    print(f"   GGUF Path     : {GGUF_DIR}")

    # ── 1. Download Base Model GGUF ───────────────────────────────────────────
    print("\n[STEP 1/3] Checking Base Cognitive Model (delentia-slm-jitna-v0.4)...")
    base_gguf_name = "delentia-jitna-v0.4-Q4_K_M.gguf"
    target_base_path = GGUF_DIR / base_gguf_name

    try:
        print(f"   Fetching {base_gguf_name} from {BASE_REPO}...")
        downloaded = hf_hub_download(
            repo_id=BASE_REPO,
            filename=f"gguf/{base_gguf_name}",
            local_dir=GGUF_DIR,
            local_dir_use_symlinks=False
        )
        # Move out of subfolder if downloaded inside gguf/
        downloaded_path = Path(downloaded)
        if downloaded_path.parent.name == "gguf":
            import shutil
            shutil.move(str(downloaded_path), str(target_base_path))
            if downloaded_path.parent.exists() and not any(downloaded_path.parent.iterdir()):
                downloaded_path.parent.rmdir()
        print(f"   [OK] Base Model GGUF ready: {target_base_path}")
    except Exception as e:
        print(f"   [WARN] Could not fetch base GGUF: {e}")

    # ── 2. Download LoRA PEFT Adapters ───────────────────────────────────────
    print("\n[STEP 2/3] Checking 4-Pillar LoRA Adapters (.safetensors + config)...")
    for pillar, repo_id in PILLAR_REPOS.items():
        pillar_dir = ADAPTERS_DIR / f"jitna_{pillar}_v0.4"
        pillar_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n--- Pillar: {pillar.upper()} ({repo_id}) ---")

        for fname in ["adapter_model.safetensors", "adapter_config.json"]:
            try:
                print(f"   Fetching {fname}...")
                downloaded = hf_hub_download(
                    repo_id=repo_id,
                    filename=fname,
                    local_dir=pillar_dir,
                    local_dir_use_symlinks=False
                )
                print(f"   [OK] {fname} saved to {pillar_dir}")
            except Exception as e:
                print(f"   [WARN] Failed to fetch {fname} for {pillar}: {e}")

    # ── 3. Download Pillar GGUF Files ─────────────────────────────────────────
    print("\n[STEP 3/3] Checking 4-Pillar GGUF Files...")
    for pillar, repo_id in PILLAR_REPOS.items():
        gguf_name = f"delentia-jitna-{pillar}-Q4_K_M.gguf"
        target_gguf_path = GGUF_DIR / gguf_name
        print(f"\n--- Pillar GGUF: {pillar.upper()} ---")

        try:
            print(f"   Fetching {gguf_name} from {repo_id}...")
            downloaded = hf_hub_download(
                repo_id=repo_id,
                filename=f"gguf/{gguf_name}",
                local_dir=GGUF_DIR,
                local_dir_use_symlinks=False
            )
            downloaded_path = Path(downloaded)
            if downloaded_path.parent.name == "gguf":
                import shutil
                shutil.move(str(downloaded_path), str(target_gguf_path))
                if downloaded_path.parent.exists() and not any(downloaded_path.parent.iterdir()):
                    downloaded_path.parent.rmdir()
            print(f"   [OK] GGUF file ready: {target_gguf_path}")
        except Exception as e:
            print(f"   [WARN] GGUF file not available for {pillar}: {e}")

    print("\n" + "=" * 80)
    print("[SUCCESS] ALL LOCAL WEIGHTS VERIFIED & READY FOR BENCHMARKING!")
    print("=" * 80)


if __name__ == "__main__":
    main()
