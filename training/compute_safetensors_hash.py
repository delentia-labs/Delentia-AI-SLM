#!/usr/bin/env python3
"""
compute_safetensors_hash.py

Calculates SHA-256 checksums of Delentia LoRA adapter weights (adapter_model.safetensors).
Used to generate reference hash values for DELENTIA_4_PILLAR_AUDITOR.ipynb integrity verification.

Usage:
    python training/compute_safetensors_hash.py --adapter-dir models/adapters
"""

import argparse
import hashlib
import os
from pathlib import Path


def calculate_sha256(file_path: Path) -> str:
    """Calculate SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def main():
    parser = argparse.ArgumentParser(description="Compute safetensors SHA-256 hashes.")
    parser.add_argument(
        "--adapter-dir",
        type=str,
        default="models/adapters",
        help="Path to the directory containing trained adapters.",
    )
    args = parser.parse_args()

    adapter_dir = Path(args.adapter_dir)
    if not adapter_dir.exists():
        print(f"❌ Error: Directory '{adapter_dir}' does not exist.")
        return

    print("🔑 Delentia LoRA Checksum Calculator")
    print("=" * 65)

    # Search for safetensors files in subdirectories
    found = False
    for path in adapter_dir.rglob("adapter_model.safetensors"):
        found = True
        relative_folder = path.parent.relative_to(adapter_dir.parent)
        print(f"\n📂 Adapter Folder: {relative_folder}")
        print("  Calculating hash...")
        file_hash = calculate_sha256(path)
        print(f"  SHA-256: {file_hash}")
        print(f"  Expected Whitepaper String: SHA256:{file_hash[:15]}...")

    if not found:
        print(
            "⚠️ No 'adapter_model.safetensors' found under the specified directory."
        )
        print(
            "   Make sure adapters are downloaded or present in models/adapters/."
        )


if __name__ == "__main__":
    main()
