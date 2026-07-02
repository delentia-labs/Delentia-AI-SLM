#!/usr/bin/env python3
"""
setup_ollama_delentia.py

Helper script to package and register Delentia OS GGUF model into Ollama local CLI.
"""

import sys
import subprocess
from pathlib import Path

# Enforce UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SCRIPT_DIR = Path(__file__).parent
MODELS_DIR = SCRIPT_DIR.parent / "models"
MODELFILE_PATH = MODELS_DIR / "Modelfile"


def main():
    print("=" * 80)
    print("🦙 DELENTIA OS — OLLAMA AUTOMATED PACKAGING & INTEGRATION")
    print("=" * 80)

    if not MODELFILE_PATH.exists():
        print(f"[ERROR] Modelfile not found at {MODELFILE_PATH}")
        sys.exit(1)

    print(f"✓ Modelfile found: {MODELFILE_PATH}")
    print("\n[STEP 1] Checking Ollama installation...")
    try:
        res = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        print(f"   ✓ {res.stdout.strip() if res.stdout else 'Ollama detected'}")
    except FileNotFoundError:
        print("   [INFO] Ollama executable not found in PATH.")
        print("   👉 To run Delentia OS seamlessly via Ollama CLI:")
        print("      1. Download Ollama for Windows from https://ollama.com")
        print("      2. Run command: ollama create delentia-os -f models/Modelfile")
        print("      3. Chat live: ollama run delentia-os")
        return

    print("\n[STEP 2] Creating 'delentia-os' model in Ollama...")
    try:
        subprocess.run(["ollama", "create", "delentia-os", "-f", str(MODELFILE_PATH)], check=True, cwd=str(MODELS_DIR))
        print("\n🎉 [SUCCESS] Delentia OS registered in Ollama!")
        print("👉 You can now run: ollama run delentia-os")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to create model in Ollama: {e}")


if __name__ == "__main__":
    main()
