#!/usr/bin/env python3
"""
generate_v042_dataset.py

Synthesizes and mixes the instruction pairs for Delentia SLM v0.4.2
using a strict Data Stratification Ratio (60% Core JITNA, 20% Hard Negatives, 
10% Missing Parameters, 10% Adversarial Attacks) to prevent adversarial overfitting.
"""

import json
import random
import sys
from pathlib import Path

# Reconfigure stdout/stderr to UTF-8
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

# Setup paths
PROCESSED_DIR = Path(__file__).parent.parent / "processed"
V2_INPUT = PROCESSED_DIR / "jitna_pairs_toon.jsonl"
SELF_AWARENESS_INPUT = PROCESSED_DIR / "jitna_self_awareness_pairs.jsonl"
ROUTER_INPUT = PROCESSED_DIR / "jitna_router_pairs.jsonl"
GUARDIAN_INPUT = PROCESSED_DIR / "jitna_guardian_pairs.jsonl"
ADVERSARIAL_INPUT = Path(__file__).parent.parent.parent / "datasets" / "adversarial_dataset.json"

V42_JSONL_OUTPUT = PROCESSED_DIR / "jitna_pairs_v042.jsonl"
V42_PARQUET_OUTPUT = PROCESSED_DIR / "jitna_pairs_v042.parquet"

TOTAL_TARGET = 3500
COUNTS = {
    'core_jitna': 2100,       # 60%
    'hard_negatives': 700,     # 20%
    'missing_params': 350,     # 10%
    'adversarial_attacks': 350 # 10%
}

SYSTEM_CONTEXT_TOON = (
    "You are Delentia OS v0.4.2 — a cognitive AI operating under HexaCore v2.3 / RCT-7 governance. "
    "You process intents through the JITNA v3 protocol. "
    "You respond in TOON format (Token-Oriented Object Notation) for token efficiency. "
    "Your responses must be factual, safe, and PDPA-compliant. "
    "Always provide FDIA scores when applicable (F = D^I × A). "
    "For security-violating prompts, you must output a rejection state (FDIAScore: 0.00)."
)

def build_pair(prompt: str, toon_dict: dict) -> dict:
    lines = []
    for k, v in toon_dict.items():
        k_key = "Δ" if (k == "Δ" or k == "delta") else k
        lines.append(f"{k_key}: {v}")
    completion = "\n".join(lines)
    return {
        "prompt": f"{SYSTEM_CONTEXT_TOON}\n\nUser intent: {prompt.strip()}",
        "completion": completion
    }

def generate_missing_parameters_pairs(count: int) -> list[dict]:
    pairs = []
    actions = ["transfer credits", "update profile email", "schedule audit", "store signature"]
    missing_fields = ["amount", "email_address", "audit_interval", "vault_key"]
    
    for i in range(count):
        idx = i % len(actions)
        act = actions[idx]
        field = missing_fields[idx]
        user_id = random.randint(3000, 5999)
        
        intent = f"request to {act} for user_{user_id}"
        
        # English
        toon_en = {
            "I": intent,
            "D": f"transaction request initiated but missing required parameter: {field}",
            "Δ": f"request_parameter({field})",
            "A": "AUTHORIZATION_PENDING",
            "R": f"Execution halted. Prompting user to supply missing field '{field}' to complete transaction.",
            "M": f"Awaiting parameter '{field}' for transaction user_{user_id} in state_cache"
        }
        pairs.append(build_pair(f"Perform system action: {intent}", toon_en))
        
        # Thai
        toon_th = {
            "I": intent,
            "D": f"เริ่มกระบวนการทำรายการแต่ตรวจพบว่าขาดพารามิเตอร์บังคับ: {field}",
            "Δ": f"request_parameter({field})",
            "A": "AUTHORIZATION_PENDING",
            "R": f"หยุดการประมวลผลชั่วคราวเพื่อส่งคำถามขอข้อมูล '{field}' เพิ่มเติมจากผู้ใช้",
            "M": f"คอยรับค่าตัวแปร '{field}' เพื่อทำรายการของผู้ใช้ user_{user_id}"
        }
        pairs.append(build_pair(f"สั่งการระบบ: {intent}", toon_th))
        
    return pairs[:count]

def main():
    print("Delentia SLM v0.4.2 Dataset Generator (Data Stratification Mode)")
    print("-" * 65)
    random.seed(42)
    
    # ── 1. Core JITNA Intent (60% -> 2100 samples) ───────────────────────────
    core_pool = []
    # Load base JITNA v2 pairs
    if V2_INPUT.exists():
        with V2_INPUT.open(encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    core_pool.append(json.loads(line))
                    
    # Load self awareness pairs
    if SELF_AWARENESS_INPUT.exists():
        with SELF_AWARENESS_INPUT.open(encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    core_pool.append(json.loads(line))
                    
    random.shuffle(core_pool)
    selected_core = core_pool[:COUNTS['core_jitna']]
    print(f"Selected {len(selected_core)} Core JITNA and Self-Awareness pairs.")
    
    # ── 2. Hard Negatives (20% -> 700 samples) ────────────────────────────────
    hn_pool = []
    # Load router intent pairs (ambiguous classifications)
    if ROUTER_INPUT.exists():
        with ROUTER_INPUT.open(encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    # Convert Router classification label format to standard JITNA-TOON
                    toon_dict = {
                        "I": extract_raw_intent(item["prompt"]),
                        "D": f"Evaluate intent classification routing criteria",
                        "Δ": f"route_target -> {item['completion']}",
                        "A": "ROUTING_SUCCESS",
                        "R": f"Sequence classification target verified as {item['completion']}",
                        "M": f"Updated classification log with target {item['completion']}"
                    }
                    hn_pool.append(build_pair(toon_dict["I"], toon_dict))
                    
    random.shuffle(hn_pool)
    # If hn_pool is smaller than target, duplicate or pad
    while len(hn_pool) < COUNTS['hard_negatives']:
        hn_pool.extend(random.choices(hn_pool, k=COUNTS['hard_negatives'] - len(hn_pool)))
    selected_hn = hn_pool[:COUNTS['hard_negatives']]
    print(f"Selected {len(selected_hn)} Hard Negative Intent pairs.")

    # ── 3. Missing Parameters (10% -> 350 samples) ────────────────────────────
    selected_missing = generate_missing_parameters_pairs(COUNTS['missing_params'])
    print(f"Generated {len(selected_missing)} Missing Parameter JITNA pairs.")

    # ── 4. Adversarial Attacks (10% -> 350 samples) ───────────────────────────
    adv_pool = []
    # Load Guardian safety rejections
    if GUARDIAN_INPUT.exists():
        with GUARDIAN_INPUT.open(encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    adv_pool.append(json.loads(line))
                    
    # Load raw adversarial dataset
    if ADVERSARIAL_INPUT.exists():
        with ADVERSARIAL_INPUT.open(encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                toon_dict = {
                    "I": item['prompt'],
                    "D": f"adversarial intent scan matching violation category: {item['category']}",
                    "Δ": "none",
                    "A": f"REJECTED (FDIAScore: 0.00, security_severity: {item['severity']})",
                    "R": f"Architect sign-off revoked (A=0). Cyber security block triggered.",
                    "M": f"Incident logged in security_audit_trail"
                }
                adv_pool.append(build_pair(item['prompt'], toon_dict))
                
    random.shuffle(adv_pool)
    while len(adv_pool) < COUNTS['adversarial_attacks']:
        adv_pool.extend(random.choices(adv_pool, k=COUNTS['adversarial_attacks'] - len(adv_pool)))
    selected_adv = adv_pool[:COUNTS['adversarial_attacks']]
    print(f"Selected {len(selected_adv)} Adversarial Attack rejections.")

    # Combine into final stratified dataset
    final_dataset = selected_core + selected_hn + selected_missing + selected_adv
    random.shuffle(final_dataset)
    
    # Save JSONL Output
    V42_JSONL_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with V42_JSONL_OUTPUT.open("w", encoding="utf-8") as f:
        for pair in final_dataset:
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")
            
    print("-" * 50)
    print(f"🎉 Successfully created Stratified Dataset v0.4.2 JSONL: {V42_JSONL_OUTPUT}")
    print(f"  Total samples: {len(final_dataset)}")
    
    # Convert to Parquet format
    try:
        import pandas as pd
        df = pd.DataFrame(final_dataset)
        df.to_parquet(V42_PARQUET_OUTPUT, index=False)
        print(f"  Successfully created Stratified Dataset v0.4.2 Parquet: {V42_PARQUET_OUTPUT}")
    except Exception as e:
        print(f"  Error converting to Parquet: {e}")
        sys.exit(1)
    print("-" * 50)

def extract_raw_intent(prompt_str):
    intent_marker = "User intent: "
    idx = prompt_str.find(intent_marker)
    if idx >= 0:
        return prompt_str[idx + len(intent_marker):].strip()
    return prompt_str.strip()

if __name__ == "__main__":
    main()
