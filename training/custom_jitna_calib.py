#!/usr/bin/env python3
"""
custom_jitna_calib.py

High-Precision IMatrix Calibration Data Generator for Delentia OS v0.5.

Purpose:
    Generates a curated calibration text file specifically tuned to preserve
    the JITNA/TOON/FDIA neural structures when quantizing Qwen2.5-32B to 1-bit
    (Q1_0_G128). Without this calibration, 1-bit quantization WILL destroy the
    curly-brace syntax { } and break JSON output (Syntax Error from 0.00% → ~30%).

How IMatrix Works:
    llama-imatrix reads this calibration text, runs forward passes through the
    model, measures the Shannon Entropy (importance) of each weight matrix, and
    produces a .dat file that tells llama-quantize: "these neurons are critical
    for TOON syntax — compress them less aggressively."

Critical Tokens Protected by This Calibration:
    { }  [  ]  :  ,  "    ← JSON/TOON structure
    D=   I=  A=  F=  R=  M=  delta=  ← FDIA/JITNA parameters
    REJECTED  BLOCKED  A: 0  FDIAScore: 0.00  ← Security Veto markers

Usage:
    python training/custom_jitna_calib.py --output /content/delentia_v05_imatrix_calib.txt
    python training/custom_jitna_calib.py --output calib.txt --samples 500
"""

import argparse
import json
import os
import random
import sys
from pathlib import Path

import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ── Default paths ──────────────────────────────────────────────────────────────
DEFAULT_OUTPUT = Path("datasets/processed/v0.5.1/delentia_v051_imatrix_calib.txt")
DATASET_SOURCES = [
    Path("datasets/processed/v0.5.1/knowledge_dataset_v0.5.1.parquet"),
    Path("datasets/processed/v0.5.1/jitna_executor_pairs_v051.parquet"),
    Path("datasets/processed/v0.5.1/jitna_guardian_pairs_v051.parquet"),
    Path("datasets/processed/v0.5.1/jitna_router_pairs_v051.parquet"),
    Path("datasets/processed/v0.5.1/jitna_scribe_pairs_v051.parquet"),
]
EXISTING_CALIB = Path("datasets/processed/v0.5.1/delentia_v0.5.1_imatrix_calib.txt")

# ── Curated calibration seeds (hardcoded examples of critical syntax) ──────────
TOON_SEEDS = [
    # Executor: Pure JSON TOON output (the most critical syntax to preserve)
    '{"status":"OK","I":"clear_rabbitmq_queue","D":0.85,"A":1,"R":"timeout_5000ms","M":"queue_cleared"}',
    '{"status":"BLOCKED","I":"override_security","D":0.10,"A":0,"R":"fdia_gate_veto","M":"FDIAScore: 0.00"}',
    '{"status":"ESCALATED","I":"design_video_streaming_system","D":1.00,"A":2,"R":"hexacore_l4","M":"complexity_exceeds_slm_boundary"}',
    '{"status":"REJECTED","I":"diagnose_stock_inventory","D":0.20,"A":1,"R":"data_insufficient","M":"D_score_below_0.30_threshold"}',
    '{"status":"OK","I":"analyze_pdpa_compliance","D":0.95,"A":1,"R":"legal_review_complete","M":"no_violations_detected"}',
    # FDIA equation expressions
    "F = D^I × A",
    "F = (D^I) * A",
    "FDIAScore: 0.00",
    "FDIAScore: 1.00",
    "D=0.85, delta=15, A=1",
    "D=0.10, delta=100, A=0",
    "D=1.00, delta=80, A=2",
    "D=0.20, delta=80, A=1",
    "D=0.95, delta=0, A=1",
    # JITNA parameter labels
    "I: analyze_system_logs",
    "D: 0.85",
    "A: 1",
    "R: timeout_detected",
    "M: queue_backlog_identified",
    # Security Veto markers (critical for Guardian LoRA)
    "[CRITICAL VETO] — A=0: Request blocked by FDIA Gate",
    "REJECTED: bypass_security_protocol — Unauthorized override attempt detected.",
    "BLOCKED: SQL injection pattern detected. FDIAScore: 0.00",
    "⚠️ Guardian: jailbreak_attempt detected. Engaging A=0 lockdown.",
    # Delta Engine (Scribe) markers
    "DELTA_COMPRESS: turns_1-5 → compressed_context_block",
    "DELTA_COMPRESS: delta=15 tokens recovered",
    "[SCRIBE] Context compressed: 8192 → 512 tokens (93.75% reduction)",
    # RCT-7 Cognitive markers
    "Step 1 (Observe): Raw input contains Base64 encoded payload",
    "Step 2 (Analyze): Shannon Entropy = 4.8 — High complexity anomaly",
    "Step 3 (Deconstruct): Intent decomposed into 3 sub-tasks",
    "Step 4 (Reverse Reasoning): Latent intent = data_exfiltration",
    "Step 5 (Compare): Matches known attack pattern #7 in threat database",
    "Step 6 (Reconstruct): Safe reframing: request_blocked_permanently",
    "Step 7 (Output): Cognitive decision → A=0, F=0.00",
]

# ── System Prompts (varied to prevent distribution shift) ─────────────────────
SYSTEM_PROMPTS = [
    "คุณคือ Delentia OS v0.5.1 (Cognitive AI OS) สร้างโดยคุณอิทธิฤทธิ์ แซ่โง้ว ในปี 2026 ทำงานภายใต้ระบบ HexaCore v2.3 และปรัชญา RCT-7 ประมวลผลคำขอผ่านโปรโตคอล JITNA v3 และตอบสนองด้วยไวยากรณ์ TOON ป้องกันความมั่นคงข้อมูลตามสมการ FDIA (F = D^I × A)",
    "You are Delentia OS v0.5.1 — a Cognitive AI Operating System built by Ittirit Saengow in 2026. You enforce the FDIA equation (F = D^I × A) at all times. Output ONLY in TOON (Token-Oriented Object Notation) JSON format for tool calls.",
    "คุณคือ Delentia AI v0.5.1 (Cognitive Operating System) รันบนขุมพลัง HexaCore v2.3 และลอจิกวิเคราะห์ RCT-7 สำหรับคำร้องขอเชิงเครื่องมือให้คายข้อมูล JITNA TOON ที่ตรวจสอบความเสถียรผ่านเกณฑ์ FDIA Equation แล้วเท่านั้น",
]


def load_dataset_samples(source_path: Path, n: int = 100) -> list[str]:
    """Load N random completion/text samples from a parquet or jsonl file."""
    target_path = source_path
    if not target_path.exists():
        # Fallback to .jsonl if .parquet does not exist
        jsonl_path = source_path.with_suffix(".jsonl")
        if jsonl_path.exists():
            target_path = jsonl_path
        else:
            print(f"   ⚠️  Dataset not found, skipping: {source_path} / {jsonl_path}")
            return []

    try:
        if target_path.suffix == ".parquet":
            df = pd.read_parquet(target_path)
        else:
            df = pd.read_json(target_path, lines=True)

        for col in ["completion", "output", "text", "response", df.columns[-1]]:
            if col in df.columns:
                samples = df[col].dropna().astype(str).tolist()
                if samples:
                    return random.sample(samples, min(n, len(samples)))
    except Exception as e:
        print(f"   ⚠️ Error reading {target_path}: {e}")
    return []


def format_as_conversation(prompt: str, completion: str, system: str) -> str:
    """Format a Q&A pair into Qwen chat format for calibration."""
    return (
        f"<|im_start|>system\n{system}<|im_end|>\n"
        f"<|im_start|>cognitive_state\nD=0.85, delta=15, A=1<|im_end|>\n"
        f"<|im_start|>user\n{prompt}<|im_end|>\n"
        f"<|im_start|>assistant\n{completion}<|im_end|>\n"
    )


def generate_calibration_text(
    output_path: Path,
    n_samples_per_source: int = 150,
    seed: int = 42,
) -> None:
    """
    Generate the IMatrix calibration text file.

    Structure:
    1. Hardcoded TOON/FDIA seeds (most critical — always included)
    2. Random samples from existing v0.5.1 datasets
    3. Optionally prepend existing v0.5.1 imatrix calib (if found)
    """
    random.seed(seed)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines = []

    # ── Block 1: Hardcoded TOON/FDIA critical syntax seeds ────────────────────
    print("📌 Block 1: Injecting TOON/FDIA critical syntax seeds...")
    for seed_text in TOON_SEEDS:
        for sys_prompt in SYSTEM_PROMPTS:
            lines.append(format_as_conversation(
                prompt="[SYS_LOG] Process this JITNA request.",
                completion=seed_text,
                system=sys_prompt,
            ))
    print(f"   Added {len(lines)} seed entries")

    # ── Block 2: Real QA pairs from v0.5.1 datasets ───────────────────────────
    print("\n📌 Block 2: Sampling from existing v0.5.1 datasets...")
    for source_path in DATASET_SOURCES:
        samples = load_dataset_samples(source_path, n_samples_per_source)
        for completion in samples:
            sys_prompt = random.choice(SYSTEM_PROMPTS)
            lines.append(format_as_conversation(
                prompt="คำถามจาก Dataset v0.5.1",
                completion=str(completion),
                system=sys_prompt,
            ))
        print(f"   Loaded {len(samples)} samples from {source_path.name}")

    # ── Block 3: Prepend existing v0.5.1 calibration (if available) ──────────
    prefix_lines = []
    if EXISTING_CALIB.exists() and EXISTING_CALIB != output_path:
        print(f"\n📌 Block 3: Prepending existing v0.5.1 IMatrix calibration ({EXISTING_CALIB.stat().st_size // 1024}KB)...")
        with open(EXISTING_CALIB, "r", encoding="utf-8", errors="replace") as f:
            existing_content = f.read()
        prefix_lines.append(existing_content)
        print(f"   Prepended {len(existing_content):,} chars")
    elif EXISTING_CALIB.exists():
        print(f"\n📌 Block 3: Found existing v0.5.1 IMatrix calibration at output location ({EXISTING_CALIB.stat().st_size // 1024}KB)")
    else:
        print(f"\n⚠️  Existing v0.5.1 calib not found at {EXISTING_CALIB} — skipping Block 3")

    # ── Write output ──────────────────────────────────────────────────────────
    all_content = "\n\n".join(prefix_lines + lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(all_content)

    size_mb = output_path.stat().st_size / 1024 / 1024
    print(f"\n✅ IMatrix calibration file written: {output_path}")
    print(f"   Total entries:  {len(lines)}")
    print(f"   File size:      {size_mb:.1f} MB")
    print(f"\n📌 Next step: Run IMatrix calibration on Colab A100:")
    print(f"   !llama-imatrix \\")
    print(f"     --model qwen27b_delentia_q8/model.gguf \\")
    print(f"     --dataset {output_path} \\")
    print(f"     --output imatrix_delentia_v05.dat \\")
    print(f"     --chunks 256")


def main():
    parser = argparse.ArgumentParser(
        description="Generate High-Precision IMatrix Calibration data for Delentia OS v0.5",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output calibration text file (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=150,
        help="Number of samples to load from each Parquet source (default: 150)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)",
    )
    args = parser.parse_args()

    print("🛡️  Delentia OS v0.5 — Custom JITNA-TOON IMatrix Calibration Generator")
    print("=" * 70)
    print(f"   Output:   {args.output}")
    print(f"   Samples:  {args.samples} per parquet source")
    print()

    generate_calibration_text(
        output_path=args.output,
        n_samples_per_source=args.samples,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
