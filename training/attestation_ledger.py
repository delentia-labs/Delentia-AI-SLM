#!/usr/bin/env python3
"""
attestation_ledger.py

SHA-256 Cryptographic Attestation for Delentia OS Sovereign Core v0.5.

Extends compute_safetensors_hash.py to provide a full RCTDB-compatible
Digital Forensics Ledger — critical for Air-Gapped Enterprise deployment
and PDPA/GDPR compliance audits.

Pipeline Position:
    Phase 2 — AFTER FP16 Merge, BEFORE Quantization
    (Attest the clean merged weights before they are compressed)

Usage:
    python training/attestation_ledger.py --merged-dir qwen27b_delentia_merged
    python training/attestation_ledger.py --merged-dir qwen27b_delentia_merged --verify
    python training/attestation_ledger.py --list-ledger
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Constants ─────────────────────────────────────────────────────────────────
RCTDB_LEDGER_PATH = Path("models/rctdb_attestation_ledger.jsonl")
VERSION = "v0.5"


# ── Core Hash Functions (from compute_safetensors_hash.py) ────────────────────
def calculate_sha256(file_path: Path) -> str:
    """Calculate SHA-256 hash of a file using chunked reading."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def hash_directory(directory: Path, extensions: tuple = (".safetensors", ".json", ".gguf")) -> dict:
    """Hash all model files in a directory. Returns {filename: sha256}."""
    hashes = {}
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    for ext in extensions:
        for file_path in sorted(directory.rglob(f"*{ext}")):
            relative = str(file_path.relative_to(directory))
            hashes[relative] = calculate_sha256(file_path)
    return hashes


# ── Attestation Block ─────────────────────────────────────────────────────────
def create_attestation_block(
    merged_dir: Path,
    base_model: str = "Qwen/Qwen2.5-32B-Instruct",
    notes: str = "",
) -> dict:
    """
    Create a cryptographic attestation block for a merged model.

    Returns a RCTDB-compatible ledger entry with:
      - SHA-256 hashes of all weight files
      - Timestamp (UTC)
      - Model version metadata
      - Composite integrity hash (hash of all hashes)
    """
    print(f"\n🔒 Computing SHA-256 hashes for: {merged_dir}")
    print("   This may take 2-5 minutes for 54GB FP16 weights...\n")

    hashes = hash_directory(merged_dir)

    if not hashes:
        raise ValueError(f"No model files found in {merged_dir}. Check --merged-dir path.")

    # Composite hash: hash the sorted concatenation of all individual hashes
    composite_input = "".join(f"{k}:{v}" for k, v in sorted(hashes.items()))
    composite_hash = hashlib.sha256(composite_input.encode()).hexdigest()

    block = {
        "schema_version": "1.0",
        "delentia_version": VERSION,
        "base_model": base_model,
        "merged_dir": str(merged_dir.resolve()),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "file_hashes": hashes,
        "composite_sha256": composite_hash,
        "attestation_status": "SIGNED",
        "notes": notes,
    }

    print(f"   Files attested: {len(hashes)}")
    print(f"   Composite SHA-256: {composite_hash[:16]}...{composite_hash[-8:]}")

    return block


# ── RCTDB Ledger Operations ───────────────────────────────────────────────────
def write_to_ledger(block: dict, ledger_path: Path = RCTDB_LEDGER_PATH) -> None:
    """Append an attestation block to the RCTDB ledger (JSONL format)."""
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with open(ledger_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(block, ensure_ascii=False) + "\n")
    print(f"\n✅ Attestation block written to RCTDB: {ledger_path}")
    print(f"   Composite hash: SHA256:{block['composite_sha256']}")
    print(f"   Timestamp:      {block['timestamp_utc']}")
    print(f"   Status:         {block['attestation_status']}")


def verify_against_ledger(
    target_dir: Path,
    ledger_path: Path = RCTDB_LEDGER_PATH,
    version: str = VERSION,
) -> bool:
    """
    Verify a model directory against its RCTDB attestation record.
    Returns True if integrity is confirmed, False if tampering is detected.
    """
    if not ledger_path.exists():
        print(f"❌ RCTDB Ledger not found: {ledger_path}")
        return False

    # Load all entries and find the latest matching version
    matching_entries = []
    with open(ledger_path, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line.strip())
            if entry.get("delentia_version") == version:
                matching_entries.append(entry)

    if not matching_entries:
        print(f"❌ No attestation record found for version {version}")
        return False

    # Use the most recent entry
    reference = matching_entries[-1]
    print(f"\n🔍 Verifying against attestation from: {reference['timestamp_utc']}")
    print(f"   Reference composite: {reference['composite_sha256'][:16]}...")

    # Recompute current hashes
    current_hashes = hash_directory(target_dir)
    current_composite_input = "".join(
        f"{k}:{v}" for k, v in sorted(current_hashes.items())
    )
    current_composite = hashlib.sha256(current_composite_input.encode()).hexdigest()

    if current_composite == reference["composite_sha256"]:
        print(f"   Current composite:   {current_composite[:16]}...")
        print("\n✅ INTEGRITY VERIFIED — Model weights are unmodified.")
        return True
    else:
        print(f"   Current composite:   {current_composite[:16]}...")
        print("\n🚨 INTEGRITY VIOLATION DETECTED — Weights may have been tampered with!")
        print("   DO NOT deploy this model for Air-Gapped Enterprise use.")
        return False


def list_ledger(ledger_path: Path = RCTDB_LEDGER_PATH) -> None:
    """Display all attestation records in the RCTDB ledger."""
    if not ledger_path.exists():
        print(f"⚠️  No RCTDB ledger found at: {ledger_path}")
        return

    print(f"\n📋 RCTDB Attestation Ledger: {ledger_path}")
    print("=" * 70)
    with open(ledger_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            entry = json.loads(line.strip())
            print(f"\n[Entry #{i}]")
            print(f"  Version:   {entry.get('delentia_version', 'unknown')}")
            print(f"  Base:      {entry.get('base_model', 'unknown')}")
            print(f"  Timestamp: {entry.get('timestamp_utc', 'unknown')}")
            print(f"  Files:     {len(entry.get('file_hashes', {}))}")
            print(f"  Hash:      SHA256:{entry.get('composite_sha256', '')[:24]}...")
            print(f"  Status:    {entry.get('attestation_status', 'unknown')}")


# ── CLI Entry Point ───────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Delentia OS v0.5 — SHA-256 Cryptographic Attestation Ledger",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Sign a freshly merged model (run BEFORE quantization)
  python training/attestation_ledger.py --merged-dir qwen27b_delentia_merged

  # Verify model integrity before deployment
  python training/attestation_ledger.py --merged-dir qwen27b_delentia_merged --verify

  # List all attestation records
  python training/attestation_ledger.py --list-ledger
        """,
    )
    parser.add_argument(
        "--merged-dir",
        type=Path,
        default=None,
        help="Path to the merged FP16 model directory to attest.",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify integrity of --merged-dir against the RCTDB ledger.",
    )
    parser.add_argument(
        "--list-ledger",
        action="store_true",
        help="List all entries in the RCTDB attestation ledger.",
    )
    parser.add_argument(
        "--ledger-path",
        type=Path,
        default=RCTDB_LEDGER_PATH,
        help=f"Path to the RCTDB ledger file (default: {RCTDB_LEDGER_PATH})",
    )
    parser.add_argument(
        "--base-model",
        type=str,
        default="Qwen/Qwen2.5-32B-Instruct",
        help="Base model name for attestation metadata.",
    )
    parser.add_argument(
        "--notes",
        type=str,
        default="",
        help="Optional notes to attach to this attestation block.",
    )
    args = parser.parse_args()

    print("🔒 Delentia OS v0.5 — Cryptographic Attestation System (RCTDB)")
    print("=" * 60)

    if args.list_ledger:
        list_ledger(args.ledger_path)
        return

    if args.verify:
        if not args.merged_dir:
            print("❌ --merged-dir is required for verification.")
            sys.exit(1)
        success = verify_against_ledger(args.merged_dir, args.ledger_path)
        sys.exit(0 if success else 1)

    if args.merged_dir:
        block = create_attestation_block(
            merged_dir=args.merged_dir,
            base_model=args.base_model,
            notes=args.notes,
        )
        write_to_ledger(block, args.ledger_path)
        print("\n📌 Next step: Run quantization (Phase 3)")
        print("   python training/custom_jitna_calib.py")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
