#!/usr/bin/env python3
"""
re_anchoring_pipeline.py

Automated Re-anchoring Pipeline for Delentia OS v0.5 Ecosystem.

Problem This Solves (Distribution Shift):
    The v0.4.3 LoRA adapters (Executor, Guardian, Router, Scribe) were trained
    on Llama 3.1 8B weight space. When you swap the base model to Qwen2.5-32B,
    the coordinate space of the neural network changes COMPLETELY.

    Applying old LoRA adapters on the new base = Catastrophic Hallucination.
    The adapters will produce garbage output or crash immediately.

Solution:
    This script takes the existing TRAINING DATA for each LoRA adapter
    and re-runs fine-tuning on the NEW Qwen2.5-32B base, anchoring the
    adapters to the correct neural coordinate space.

Architecture:
    For each Pillar in [Executor, Guardian, Router, Scribe]:
        1. Load Qwen2.5-32B (the new base)
        2. Attach fresh LoRA with pillar-specific config
        3. Fine-tune on pillar's existing dataset (JSONL/Parquet)
        4. Save re-anchored adapter
        5. Compute SHA-256 attestation

Usage:
    python training/re_anchoring_pipeline.py --all
    python training/re_anchoring_pipeline.py --pillar executor
    python training/re_anchoring_pipeline.py --pillar guardian --dry-run
"""

import os
os.environ["UNSLOTH_COMPILE_DISABLE"] = "1"  # Bypass Unsloth compilation bug for Qwen3.5 architecture
import argparse
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path

# ── Pillar Configurations ─────────────────────────────────────────────────────
@dataclass
class PillarConfig:
    name: str
    dataset_path: Path
    lora_r: int
    lora_alpha: int
    learning_rate: float
    num_epochs: int
    max_seq_length: int
    save_path: Path
    description: str


PILLAR_CONFIGS = {
    "executor": PillarConfig(
        name="Executor",
        dataset_path=Path("datasets/processed/v0.5.1/jitna_executor_pairs_v051.jsonl"),
        lora_r=64,           # Higher rank: JSON syntax requires more precision
        lora_alpha=128,
        learning_rate=3e-5,  # Lower LR: forces precise JSON structure learning
        num_epochs=5,
        max_seq_length=16384,
        save_path=Path("models/adapters/v0.5.1/jitna_executor_v0.5.1"),
        description="JSON/TOON output — must maintain 0.00% Syntax Error on Q1_0_G128",
    ),
    "guardian": PillarConfig(
        name="Guardian",
        dataset_path=Path("datasets/processed/v0.5.1/jitna_guardian_pairs_v051.jsonl"),
        lora_r=32,           # Lower rank: binary safety decisions don't need high complexity
        lora_alpha=64,
        learning_rate=5e-5,
        num_epochs=5,
        max_seq_length=8192,
        save_path=Path("models/adapters/v0.5.1/jitna_guardian_v0.5.1"),
        description="Security Veto (A=0) — 100% block rate on adversarial prompts",
    ),
    "router": PillarConfig(
        name="Router",
        dataset_path=Path("datasets/processed/v0.5.1/jitna_router_pairs_v051.jsonl"),
        lora_r=32,
        lora_alpha=64,
        learning_rate=5e-5,
        num_epochs=5,
        max_seq_length=8192,
        save_path=Path("models/adapters/v0.5.1/jitna_router_v0.5.1"),
        description="Intent Classification & Routing — D/I parameter assignment",
    ),
    "scribe": PillarConfig(
        name="Scribe",
        dataset_path=Path("datasets/processed/v0.5.1/jitna_scribe_pairs_v051.jsonl"),
        lora_r=64,           # Higher rank: context compression requires nuanced understanding
        lora_alpha=128,
        learning_rate=5e-5,
        num_epochs=5,
        max_seq_length=32768,  # Scribe needs the longest context (compressing 262K input)
        save_path=Path("models/adapters/v0.5.1/jitna_scribe_v0.5.1"),
        description="Context Compression (DELTA_COMPRESS) — Delta Engine 262K handler",
    ),
}

BASE_MODEL = "Qwen/Qwen3.6-27B"


def check_environment() -> bool:
    """Verify that required packages and GPU are available."""
    print("🔍 Environment Check:")
    try:
        import torch
        gpu_available = torch.cuda.is_available()
        vram = torch.cuda.get_device_properties(0).total_memory / 1e9 if gpu_available else 0
        print(f"   GPU:  {'✅' if gpu_available else '❌'} {torch.cuda.get_device_name(0) if gpu_available else 'Not found'}")
        print(f"   VRAM: {vram:.1f} GB {'(sufficient ✅)' if vram >= 20 else '(WARNING: may be insufficient)'}")
    except ImportError:
        print("   ❌ PyTorch not installed")
        return False

    try:
        import unsloth  # noqa: F401
        print("   Unsloth: ✅ Installed")
    except ImportError:
        print("   ⚠️  Unsloth not installed — will use standard PEFT (slower)")

    return True


def validate_dataset(pillar_config: PillarConfig) -> int:
    """Validate the dataset for a pillar. Returns row count or 0 on failure."""
    dataset_path = pillar_config.dataset_path
    if not dataset_path.exists():
        print(f"   ❌ Dataset not found: {dataset_path}")
        return 0

    try:
        import pandas as pd
        df = pd.read_json(dataset_path, lines=True) if dataset_path.suffix == ".jsonl" else None
        if df is not None:
            print(f"   Dataset: {dataset_path.name} — {len(df):,} rows ✅")
            return len(df)
    except Exception as e:
        print(f"   ❌ Dataset read error: {e}")
    return 0


def retrain_pillar(pillar_config: PillarConfig, dry_run: bool = False) -> bool:
    """
    Re-anchor a single LoRA pillar on Qwen2.5-32B.
    Returns True on success.
    """
    cfg = pillar_config
    print(f"\n{'─'*60}")
    print(f"🔄 RE-ANCHORING: {cfg.name.upper()} LoRA → Qwen2.5-32B")
    print(f"   {cfg.description}")
    print(f"   Dataset:    {cfg.dataset_path}")
    print(f"   LoRA r/α:   {cfg.lora_r}/{cfg.lora_alpha}")
    print(f"   LR:         {cfg.learning_rate:.0e}")
    print(f"   Epochs:     {cfg.num_epochs}")
    print(f"   Max seq:    {cfg.max_seq_length:,}")
    print(f"   Save path:  {cfg.save_path}")

    row_count = validate_dataset(cfg)
    if row_count == 0:
        print(f"   ❌ Cannot proceed — dataset missing or empty")
        return False

    if dry_run:
        print(f"   [DRY RUN] Would train {cfg.name} LoRA on {row_count:,} samples")
        print(f"   [DRY RUN] Estimated time on A100: ~{row_count // 200} minutes")
        return True

    try:
        # Dynamic import (only available on training machine)
        from unsloth import FastLanguageModel
        import torch
        from trl import SFTTrainer, SFTConfig
        from datasets import Dataset
        import pandas as pd
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        print("   Run this script on Colab A100 with Unsloth installed")
        return False

    # Load base model
    print(f"\n   Loading {BASE_MODEL}...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=BASE_MODEL,
        max_seq_length=cfg.max_seq_length,
        dtype=torch.bfloat16,
        load_in_4bit=True,
    )

    # Attach LoRA
    model = FastLanguageModel.get_peft_model(
        model,
        r=cfg.lora_r,
        lora_alpha=cfg.lora_alpha,
        lora_dropout=0,
        bias="none",
        use_rslora=True,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
        random_state=42,
    )

    # Load dataset
    df = pd.read_json(cfg.dataset_path, lines=True)
    dataset = Dataset.from_pandas(df)

    # Train
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        args=SFTConfig(
            dataset_text_field="completion",
            max_seq_length=cfg.max_seq_length,
            per_device_train_batch_size=2,
            gradient_accumulation_steps=4,
            num_train_epochs=cfg.num_epochs,
            learning_rate=cfg.learning_rate,
            bf16=True,
            optim="adamw_8bit",
            lr_scheduler_type="cosine",
            warmup_ratio=0.05,
            weight_decay=0.01,
            logging_steps=10,
            save_steps=100,
            save_total_limit=2,
            output_dir=str(cfg.save_path / "checkpoints"),
            completion_only_loss=True,
            seed=42,
        ),
    )

    print(f"   Training {cfg.name} LoRA on {len(dataset):,} samples...")
    start = time.time()
    trainer.train()
    elapsed = time.time() - start
    print(f"   Training complete in {elapsed/60:.1f} minutes")

    # Save adapter
    cfg.save_path.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(str(cfg.save_path))
    tokenizer.save_pretrained(str(cfg.save_path))
    print(f"   ✅ {cfg.name} LoRA saved to: {cfg.save_path}")



    return True


def run_attestation(pillars_done: list[str]) -> None:
    """Run SHA-256 attestation on all newly re-anchored adapters."""
    print(f"\n{'='*60}")
    print("🔒 Running SHA-256 Attestation on re-anchored adapters...")
    for pillar_name in pillars_done:
        cfg = PILLAR_CONFIGS[pillar_name]
        if cfg.save_path.exists():
            import subprocess
            result = subprocess.run(
                [sys.executable, "training/attestation_ledger.py",
                 "--merged-dir", str(cfg.save_path),
                 "--notes", f"re-anchored_{pillar_name}_v0.5.1"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                print(f"   ✅ {cfg.name}: Attested")
            else:
                print(f"   ⚠️  {cfg.name}: Attestation failed — {result.stderr[:100]}")


def main():
    parser = argparse.ArgumentParser(
        description="Re-anchoring Pipeline: Re-train LoRA adapters on Qwen2.5-32B base",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Re-anchor all 4 pillars (recommended — run on Colab A100)
  python training/re_anchoring_pipeline.py --all

  # Re-anchor only the Executor (test first)
  python training/re_anchoring_pipeline.py --pillar executor

  # Dry run to check setup without training
  python training/re_anchoring_pipeline.py --all --dry-run
        """,
    )
    parser.add_argument(
        "--pillar",
        choices=list(PILLAR_CONFIGS.keys()),
        help="Re-anchor a specific pillar only",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Re-anchor ALL 4 pillars (Executor → Guardian → Router → Scribe)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate setup and estimate time without training",
    )

    parser.add_argument(
        "--skip-attestation",
        action="store_true",
        help="Skip SHA-256 attestation after re-anchoring",
    )
    args = parser.parse_args()

    if not args.all and not args.pillar:
        parser.print_help()
        sys.exit(1)

    print("🔄 Delentia OS v0.5 — Automated Re-anchoring Pipeline")
    print("=" * 60)
    print(f"   New Base: {BASE_MODEL} (Dynamically loaded in 4-bit via Unsloth)")
    print(f"   Old Base: Qwen 0.5 (v0.5)")
    print(f"   Mode:     {'DRY RUN' if args.dry_run else 'FULL TRAINING'}")
    print()

    if not args.dry_run:
        check_environment()

    # Determine which pillars to process
    # Order matters: Executor first (most critical for JSON integrity validation)
    pillar_order = ["executor", "guardian", "router", "scribe"]
    pillars_to_run = pillar_order if args.all else [args.pillar]

    print(f"\n📋 Pillars to re-anchor: {[p.upper() for p in pillars_to_run]}")

    results = {}
    for pillar_name in pillars_to_run:
        cfg = PILLAR_CONFIGS[pillar_name]
        success = retrain_pillar(cfg, dry_run=args.dry_run)
        results[pillar_name] = success

    # Summary
    print(f"\n{'='*60}")
    print("📊 RE-ANCHORING SUMMARY")
    print(f"{'='*60}")
    all_success = True
    for pillar_name, success in results.items():
        status = "✅ DONE" if success else "❌ FAILED"
        print(f"   {PILLAR_CONFIGS[pillar_name].name:12s}: {status}")
        if not success:
            all_success = False

    if all_success and not args.dry_run and not args.skip_attestation:
        run_attestation(list(results.keys()))

    if all_success:
        print("\n✅ Re-anchoring complete — all adapters anchored to Qwen2.5-32B")
        print("   Next: Run Three-Body Synthesis Verification")
        print("   python training/test_three_body_synthesis.py --gguf-path jitna-v0.5-32B.gguf")
    else:
        print("\n❌ Some pillars failed — review errors above")
        sys.exit(1)


if __name__ == "__main__":
    main()
