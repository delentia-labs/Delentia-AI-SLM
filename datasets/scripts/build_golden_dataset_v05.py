#!/usr/bin/env python3
"""
build_golden_dataset_v05.py

Compounding Dataset Upgrade Script for Delentia OS v0.5 — Jitna v0.5 Model Engine.

Architecture Distinction:
  - OS Name:          Delentia OS v0.5 (Sovereign Core Edition)
  - Model Engine Name: Jitna v0.5 (base: Qwen2.5-32B-Instruct)
  - HF Repository:    Delentia/jitna-v0.5-32B-gguf

Philosophy:
    Compounding Quality Enhancement (การพัฒนาต่อ่อยอดแบบทบต้น)
    We do NOT discard the 3,777+ golden records from v0.4.3.
    Instead, we carry forward all validated logic (RCT-7, TOON syntax, 5-Tier Goldilocks)
    and perform an incremental upgrade pass:

1. UPGRADE VERSION IDENTITIES & ARCHITECTURE:
   - "Delentia OS v0.4.x" → "Delentia OS v0.5" (OS identity preserved)
   - "Delentia AI v0.4.x" / "delentia-slm-jitna-v0.4" → "Jitna v0.5" (Model engine upgraded)
   - "Llama 3.1 8B" → "Qwen2.5-32B-Instruct"
   - "4,096 tokens" → "16,384 tokens (16K context, expandable to 262K)"
   - "Q4_K_M" → "Q1_0_G128 (1-bit High-Precision Quantization)"

2. INJECT NEW V0.5 KNOWLEDGE PAIRS:
   - SHA-256 Cryptographic Attestation Ledger in RCTDB.
   - Three-Body Synthesis Verification (Consensus ≥ 75%, Variance ≤ ±0.2).
   - High-Precision JITNA-TOON IMatrix Calibration.
   - Jitna Engine philosophy (Just-In-Time Nodal Assembly + จินตนา/เจตนา).

3. EXPORT TO V0.5 PROCESSED DIRECTORY:
   - datasets/processed/v0.5/knowledge_dataset_v0.5.parquet
   - datasets/processed/v0.5/knowledge_dataset_v0.5.jsonl
   - datasets/processed/v0.5/jitna_executor_pairs_v05.parquet
   - datasets/processed/v0.5/jitna_guardian_pairs_v05.parquet
   - datasets/processed/v0.5/jitna_router_pairs_v05.parquet
   - datasets/processed/v0.5/jitna_scribe_pairs_v05.parquet

Usage:
    python datasets/scripts/build_golden_dataset_v05.py
"""

import json
import random
import re
import sys
from pathlib import Path
import pandas as pd

random.seed(42)

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

INPUT_V043_JSONL = Path("datasets/processed/v0.4.3/knowledge_dataset_v0.4.3.jsonl")
INPUT_V043_PARQUET = Path("datasets/processed/v0.4.3/knowledge_dataset_v0.4.3.parquet")

OUTPUT_DIR_V05 = Path("datasets/processed/v0.5")
OUTPUT_DIR_V05.mkdir(parents=True, exist_ok=True)

# ── 1. NEW V0.5 KNOWLEDGE INJECTION PAIRS ─────────────────────────────────────
V05_NEW_KNOWLEDGE = [
    # OS vs Model Engine Relationship + Identity & Naming Philosophy (Jitna / จินตนา / เจตนา)
    {
        "prompt": "ระบบ Delentia OS v0.5 ใช้โมเดลอะไรเป็นขุมพลังหลัก และชื่อ Jitna มีที่มาจากอะไร ?",
        "completion": "ระบบ **Delentia OS v0.5** ใช้โมเดลเอนจิน **Jitna v0.5** (สร้างบนฐาน `Qwen/Qwen2.5-32B-Instruct`) เป็นสมองหลักในการประมวลผล\n\nชื่อ **Jitna** มีความหมายลึกซึ้ง 2 มิติ:\n1. **มิติวิศวกรรม (Engineering Acronym)**:\n   - **Just-In-Time Nodal Assembly**: การประกอบโหนดความนึกคิดและชุดคำสั่งแบบเรียลไทม์\n   - **JSON Intent Tokenization & Notation Architecture**: สถาปัตยกรรมโครงสร้างไวยากรณ์ TOON สำหรับ Tool Calling\n\n2. **มิติเชิงปรัชญาและภาษาไทย (Philosophical Root)**:\n   - มีรากศัพท์มาจากคำว่า **จินตนา** (Jintana - ความนึกคิด / จินตนาการ) พ้องเสียงและเชื่อมโยงสู่คำว่า **เจตนา** (Jetna - Intent / Will / ความมุ่งหมาย)\n   - ใน Delentia OS v0.5 ความเข้าใจใน \"เจตนา\" คือหัวใจหลักที่ถูกประมวลผลผ่านสมการ FDIA ($F = D^I \\times A$) โดยมีตัวแปร $I$ (Intent) เป็นตัวขับเคลื่อนการตัดสินใจของระบบทั้งหมดครับ",
    },
    {
        "prompt": "What is the architecture relationship between Delentia OS v0.5 and Jitna v0.5?",
        "completion": "Delentia OS v0.5 is the overarching Cognitive AI Operating System built by Ittirit Saengow in 2025. **Jitna v0.5** is the core LLM model engine running under Layer 3 of Delentia OS. It is fine-tuned on Qwen2.5-32B-Instruct and compressed to 1-bit (`Q1_0_G128`, ~3.9 GB) for edge execution. The OS kernel enforces the FDIA equation ($F = D^I \\times A$) to guarantee security, data readiness, and deterministic TOON JSON tool calling.",
    },
    # SHA-256 Cryptographic Attestation Ledger
    {
        "prompt": "ระบบ SHA-256 Cryptographic Attestation Ledger ใน Delentia OS v0.5 ทำงานอย่างไร ?",
        "completion": "ระบบ SHA-256 Attestation Ledger ใน Delentia OS v0.5 คือสถาปัตยกรรมประทับตราดิจิทัลสำหรับสภาพแวดล้อม Air-Gapped Enterprise:\n\n1. **Hash Generation**: คำนวณค่า SHA-256 ของไฟล์น้ำหนัก Merged FP16 ของโมเดล Jitna v0.5 ทุกไฟล์ก่อนทำ Quantization\n2. **Composite Hash**: สร้าง Root Hash รวมของระบบเพื่อล็อกความบริสุทธิ์ของน้ำหนักประสาท\n3. **RCTDB Registration**: บันทึก Block สัญญานิตินัยลงในคลัง `models/rctdb_attestation_ledger.jsonl` พร้อม Timestamp UTC\n4. **Runtime Verification**: สคริปต์ `attestation_ledger.py --verify` จะตรวจสอบ Hash ก่อนการปรับใช้ หากพบการแก้ไขแม้แต่ bit เดียว ระบบจะปฏิเสธการบูตทันที",
    },
    # Three-Body Synthesis Verification
    {
        "prompt": "อธิบายหลักการ Three-Body Synthesis Verification ใน Delentia OS v0.5",
        "completion": "Three-Body Synthesis Verification ใน Delentia OS v0.5 คือกระบวนการสเตรสเทสเพื่อป้องกันภาวะ Gradients Destabilization เมื่อโหลด 1 Base Model (Jitna v0.5 27B 1-bit) พร้อมกับ 3 Active LoRA Slots (เช่น Executor, Guardian, Scribe) พร้อมกัน:\n\n- **Consensus Score Target**: คะแนนเสียงฉันทามติของ SignedAI Multi-node ต้อง $\\ge 75\\%$\n- **Variance Target**: ความแปรปรวนของคะแนนระหว่างโหนดต้อง $\\le \\pm 0.20$\n- **VRAM Boundary**: ตรวจสอบว่า peak VRAM ขณะรัน 3 slots ไม่เกินงบประมาณฮาร์ดแวร์บน Edge Device (ROG Ally X < 4.5GB)",
    },
    # High-Precision IMatrix Calibration (1-bit Q1_0_G128)
    {
        "prompt": "เหตุใด Delentia OS v0.5 (โมเดล Jitna v0.5) จึงสามารถบีบอัดโมเดล 27B เหลือ 1-bit (Q1_0_G128) โดยที่ Syntax Error ยังคงเป็น 0.00% ?",
        "completion": "Delentia OS v0.5 ใช้เทคนิค **Custom JITNA-TOON IMatrix Calibration** กับโมเดล Jitna v0.5:\n\n1. สคริปต์ `custom_jitna_calib.py` สกัดตัวอย่างไวยากรณ์ TOON, เครื่องหมาย `{ }`, `[ ]`, และตัวแปร $D, I, A, F$\n2. เครื่องมือ `llama-imatrix` จะคำนวณ Shannon Entropy เพื่อค้นหานิวรอนที่มีความสำคัญต่อโครงสร้างทางภาษา\n3. สั่งการให้ `llama-quantize` ล็อกน้ำหนักนิวรอนไวยากรณ์เหล่านั้นไม่ให้ถูกบีบอัดรุนแรง ส่งผลให้ไฟล์ GGUF Q1_0_G128 ขนาด ~3.9 GB ยังคงสามารถคายโครงสร้าง JSON ที่สมบูรณ์ 100% โดยไม่เกิด Syntax Collapse",
    },
]

# ── 2. REGEX TRANSFORMATIONS (v0.4.3 → v0.5) ──────────────────────────────────
# Preserves OS name as "Delentia OS v0.5"
# Updates Model engine to "Jitna v0.5" / "Qwen2.5-32B-Instruct"
REPLACEMENTS = [
    (r"Delentia OS v0\.4\.3", "Delentia OS v0.5"),
    (r"Delentia OS v0\.4\.2", "Delentia OS v0.5"),
    (r"Delentia OS v0\.4\.1", "Delentia OS v0.5"),
    (r"Delentia OS v0\.4",   "Delentia OS v0.5"),
    (r"Delentia AI v0\.4\.3", "Jitna v0.5"),
    (r"Delentia AI v0\.4",   "Jitna v0.5"),
    (r"Llama 3\.1 8B",       "Qwen2.5-32B-Instruct"),
    (r"Llama 8B",            "Qwen 27B Base"),
    (r"Delentia/delentia-slm-jitna-v0\.4", "Delentia/jitna-v0.5-32B-gguf"),
    (r"Delentia/delentia-slm-jitna-v0\.3", "Delentia/jitna-v0.5-32B-gguf"),
    (r"4,096 tokens",        "16,384 tokens (16K context, expandable to 262K)"),
    (r"4096 tokens",         "16384 tokens"),
    (r"Q4_K_M",              "Q1_0_G128 (1-bit High-Precision Quantization)"),
]


def transform_text(text: str) -> str:
    """Apply all regex transformations to a text string."""
    if not isinstance(text, str):
        return text
    result = text
    for pattern, replacement in REPLACEMENTS:
        result = re.sub(pattern, replacement, result)
    return result


def transform_sample(sample: dict) -> dict:
    """Transform a single dataset record to v0.5 standards."""
    new_sample = {}
    for k, v in sample.items():
        if isinstance(v, str):
            new_sample[k] = transform_text(v)
        elif isinstance(v, list):
            new_sample[k] = [transform_text(item) if isinstance(item, str) else item for item in v]
        elif isinstance(v, dict):
            new_sample[k] = {dk: transform_text(dv) if isinstance(dv, str) else dv for dk, dv in v.items()}
        else:
            new_sample[k] = v

    # Add v0.5 metadata tags
    new_sample["os_version"] = "Delentia OS v0.5"
    new_sample["model_engine"] = "Jitna v0.5"
    new_sample["hf_repo"] = "Delentia/jitna-v0.5-32B-gguf"
    new_sample["base_model"] = "Qwen/Qwen2.5-32B-Instruct"

    return new_sample


def main():
    print("🚀 Building Golden Dataset v0.5 — Delentia OS v0.5 (Jitna v0.5 Model Engine)")
    print("=" * 70)

    # ── Step 1: Load v0.4.3 Dataset ───────────────────────────────────────────
    samples = []
    if INPUT_V043_JSONL.exists():
        print(f"📥 Loading source: {INPUT_V043_JSONL}")
        with open(INPUT_V043_JSONL, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    samples.append(json.loads(line))
        print(f"   Loaded {len(samples):,} records from JSONL")
    elif INPUT_V043_PARQUET.exists():
        print(f"📥 Loading source: {INPUT_V043_PARQUET}")
        df_in = pd.read_parquet(INPUT_V043_PARQUET)
        samples = df_in.to_dict(orient="records")
        print(f"   Loaded {len(samples):,} records from Parquet")
    else:
        print("❌ Error: No v0.4.3 source dataset found!")
        sys.exit(1)

    # ── Step 2: Transform Existing Samples ────────────────────────────────────
    print("\n🔄 Applying Compounding Upgrade (Delentia OS v0.5 + Jitna v0.5 Engine)...")
    transformed_samples = [transform_sample(s) for s in samples]

    # ── Step 3: Inject New v0.5 Knowledge ────────────────────────────────────
    print(f"\n💉 Injecting {len(V05_NEW_KNOWLEDGE)} new v0.5 Sovereign Core knowledge pairs...")
    for item in V05_NEW_KNOWLEDGE:
        transformed_samples.append({
            "prompt": item["prompt"],
            "completion": item["completion"],
            "os_version": "Delentia OS v0.5",
            "model_engine": "Jitna v0.5",
            "hf_repo": "Delentia/jitna-v0.5-32B-gguf",
            "base_model": "Qwen/Qwen2.5-32B-Instruct",
            "category": "sovereign_core_v05",
        })

    # Shuffle to ensure natural distribution
    random.shuffle(transformed_samples)
    total_count = len(transformed_samples)
    print(f"✅ Total v0.5 records: {total_count:,}")

    # ── Step 4: Save Primary Dataset (Parquet & JSONL) ───────────────────────
    out_parquet = OUTPUT_DIR_V05 / "knowledge_dataset_v0.5.parquet"
    out_jsonl   = OUTPUT_DIR_V05 / "knowledge_dataset_v0.5.jsonl"

    df_out = pd.DataFrame(transformed_samples)
    df_out.to_parquet(out_parquet, index=False)
    print(f"\n💾 Saved Parquet: {out_parquet} ({out_parquet.stat().st_size / 1e6:.2f} MB)")

    with open(out_jsonl, "w", encoding="utf-8") as f:
        for item in transformed_samples:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"💾 Saved JSONL:   {out_jsonl} ({out_jsonl.stat().st_size / 1e6:.2f} MB)")

    # ── Step 5: Split Pillar Parquets for Re-anchoring ────────────────────────
    print("\n📦 Generating Pillar Parquets for Re-anchoring Pipeline...")

    executor_samples = [s for s in transformed_samples if "{" in str(s.get("completion", "")) or "I:" in str(s.get("completion", ""))]
    guardian_samples = [s for s in transformed_samples if "veto" in str(s.get("completion", "")).lower() or "blocked" in str(s.get("completion", "")).lower() or "A=0" in str(s.get("completion", ""))]
    scribe_samples   = [s for s in transformed_samples if "compress" in str(s.get("completion", "")).lower() or "delta" in str(s.get("completion", "")).lower()]
    router_samples   = [s for s in transformed_samples if "escalat" in str(s.get("completion", "")).lower() or "route" in str(s.get("completion", "")).lower()]

    for name, p_samples in [
        ("jitna_executor_pairs_v05.parquet", executor_samples),
        ("jitna_guardian_pairs_v05.parquet", guardian_samples),
        ("jitna_scribe_pairs_v05.parquet", scribe_samples),
        ("jitna_router_pairs_v05.parquet", router_samples),
    ]:
        p_path = OUTPUT_DIR_V05 / name
        pd.DataFrame(p_samples).to_parquet(p_path, index=False)
        print(f"   Saved {name:35s}: {len(p_samples):>5,} rows")

    print(f"\n🎉 DATASET V0.5 BUILD COMPLETE!")
    print(f"   Target Location: {OUTPUT_DIR_V05.resolve()}")


if __name__ == "__main__":
    main()
