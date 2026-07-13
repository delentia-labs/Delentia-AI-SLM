#!/usr/bin/env python3
"""
custom_jitna_calib_v043.py

Builds the imatrix calibration file for Delentia OS v0.4.3:
  - Mixes 3 layers based on Shannon Entropy and JITNA requirements:
    1. toon_clean (60%)          - Low/Mid entropy normal intents
    2. adversarial (20%)         - High/Extreme entropy safety rejections
    3. cognitive_template (20%)  - CoT / J-Space / Cognitive state formatted prompts
  - Formats all mixed samples using the official Llama 3.1 Chat Template.
  - Outputs: datasets/processed/delentia_v043_imatrix_calib.txt
"""

import json
import math
import os
import random
import sys
from pathlib import Path
from collections import Counter

# Set random seed for reproducibility
random.seed(42)

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

TOTAL_SAMPLES = 1000
MIX_TARGETS = {
    'toon_clean': 600,          # 60% JITNA v3 normal patterns (Low/Mid Entropy)
    'adversarial': 200,         # 20% Attacks, Veto, high noise (High/Extreme Entropy)
    'cognitive_template': 200   # 20% Llama 3.1 header format + CoT J-Space
}

CHAT_TEMPLATE_LLAMA3 = (
    "<|start_header_id|>system<|end_header_id|>\n\n"
    "คุณคือ Delentia AI v0.4.3 (Cognitive AI OS) สร้างโดยคุณอิทธิฤทธิ์ แซ่โง้ว ในปี 2025<|eot_id|>"
    "<|start_header_id|>cognitive_state<|end_header_id|>\n\n{cognitive_state}<|eot_id|>"
    "<|start_header_id|>user<|end_header_id|>\n\n{user_intent}<|eot_id|>"
    "<|start_header_id|>assistant<|end_header_id|>\n\n{completion}<|eot_id|>"
)

def classify_cognitive_state(prompt: str) -> str:
    p = prompt.lower()

    # CATEGORY 1: Security Veto / Jailbreak / Injection Attacks
    is_false_positive = any(kw in p for kw in [
        "penetration testing", "pentest", "อธิบายขั้นตอน", "เพื่อป้องกัน", 
        "ขั้นตอนการทำ", "หาช่องโหว่ในระบบของเราเอง"
    ])
    
    if not is_false_positive and any(kw in p for kw in [
        "bypass", "hack", "backdoor", "override", "security", "jailbreak", 
        "drop table", "ignore safety", "แฮก", "เจาะ", "wpa2", "jwt", 
        "ignore instructions", "unrestricted mode"
    ]):
        return "D=0.10, delta=100, A=0"  # A=0 -> Guardian fires [CRITICAL VETO]

    # CATEGORY 2: Low Data Readiness (incomplete parameters, vague requests)
    elif any(kw in p for kw in [
        "low information", "ข้อมูลน้อย", "ไม่เพียงพอ", "สต็อก",
        "ลาออก", "launching a competitive", "insufficient data",
        "คลังสินค้า", "ตรวจนับ", "ข้อมูลน้อย", "stock", "inventory",
        "อัตราการลาออก", "turnover", "launching a new"
    ]):
        return "D=0.20, delta=80, A=1"   # D<0.30 -> Executor rejects, asks for more data

    # CATEGORY 4: HexaCore L4 Escalation (complex system architecture / massive coding requests)
    elif any(kw in p for kw in [
        "escalate", "hexacore", "ส่งต่อ", "เซิร์ฟเวอร์", "tackle", "route", 
        "registry", "ระบบความร้อน", "ระบบแชร์ไฟล์", "ออกแบบ", "เขียนโค้ด", 
        "video streaming", "database และ load balancer", "architecture", "microservices"
    ]):
        return "D=1.00, delta=80, A=2"   # A=2=Elevated -> route to HexaCore L4

    # CATEGORY 3: JITNA JSON Task (structured data extraction + CoT)
    elif any(kw in p for kw in [
        "jitna", "json", "packet", "diagnose", "วิเคราะห์", "ตรวจเช็ค", 
        "จัดส่ง", "payload", "rabbitmq", "timeout", "d/e ratio", "งบการเงิน"
    ]):
        return "D=0.85, delta=50, A=1"   # High readiness, medium complexity -> execute JITNA

    # CATEGORY 5: Identity / Core DNA / General Conversational
    else:
        return "D=0.95, delta=0, A=1"    # Standard reply: high D, zero complexity

def compute_shannon_entropy(text: str) -> float:
    """Compute Shannon entropy of text to characterize request complexity."""
    if not text:
        return 0.0
    freq = {}
    for ch in text:
        freq[ch] = freq.get(ch, 0) + 1
    n = len(text)
    return -sum((c/n) * math.log2(c/n) for c in freq.values())

def extract_raw_intent(prompt_str: str) -> str:
    """Extract raw user intent from the prompt text."""
    intent_marker = "User intent: "
    idx = prompt_str.find(intent_marker)
    if idx >= 0:
        return prompt_str[idx + len(intent_marker):].strip()
    
    user_marker = "User: "
    idx_u = prompt_str.find(user_marker)
    if idx_u >= 0:
        return prompt_str[idx_u + len(user_marker):].strip()
        
    return prompt_str.strip()

def main():
    repo_dir = Path(__file__).parent.parent.parent
    processed_dir = repo_dir / "datasets" / "processed" / "v0.4.3"
    
    input_dataset = processed_dir / "knowledge_dataset_v0.4.3.jsonl"
    if not input_dataset.exists():
        print(f"❌ Error: Input dataset {input_dataset} not found!")
        return

    print(f"Loading base dataset from: {input_dataset}")
    with open(input_dataset, "r", encoding="utf-8") as f:
        samples = [json.loads(l) for l in f if l.strip()]

    print(f"Analyzing {len(samples)} samples for mixing...")
    
    toon_clean_pool = []
    adversarial_pool = []
    cognitive_pool = []

    for item in samples:
        prompt = item.get("prompt", "")
        completion = item.get("completion", "")
        raw_intent = extract_raw_intent(prompt)
        
        entropy = compute_shannon_entropy(raw_intent)
        
        # Classification criteria
        is_veto = "[CRITICAL VETO" in completion
        is_cognitive = "<cognitive_state>" in completion or "</cognitive_state>" in completion or "J-Space" in completion
        
        # 1. Cognitive layer
        if is_cognitive:
            cognitive_pool.append(item)
        # 2. Adversarial layer (high entropy or explicit vetoes)
        elif is_veto or entropy >= 4.0:
            adversarial_pool.append(item)
        # 3. Clean operational layer (mid/low entropy normal requests)
        else:
            toon_clean_pool.append(item)

    print(f"Found pools: toon_clean={len(toon_clean_pool)}, adversarial={len(adversarial_pool)}, cognitive={len(cognitive_pool)}")
    
    # Check if we have enough samples
    if len(toon_clean_pool) < MIX_TARGETS['toon_clean']:
        print(f"⚠️ Warning: Not enough toon_clean samples. Capping to {len(toon_clean_pool)}")
        MIX_TARGETS['toon_clean'] = len(toon_clean_pool)
    if len(adversarial_pool) < MIX_TARGETS['adversarial']:
        print(f"⚠️ Warning: Not enough adversarial samples. Capping to {len(adversarial_pool)}")
        MIX_TARGETS['adversarial'] = len(adversarial_pool)
    if len(cognitive_pool) < MIX_TARGETS['cognitive_template']:
        print(f"⚠️ Warning: Not enough cognitive samples. Capping to {len(cognitive_pool)}")
        MIX_TARGETS['cognitive_template'] = len(cognitive_pool)

    # Sample from each pool
    selected_clean = random.sample(toon_clean_pool, MIX_TARGETS['toon_clean'])
    selected_adv = random.sample(adversarial_pool, MIX_TARGETS['adversarial'])
    selected_cog = random.sample(cognitive_pool, MIX_TARGETS['cognitive_template'])
    
    combined = selected_clean + selected_adv + selected_cog
    random.shuffle(combined)
    
    print(f"Selected mix: clean={len(selected_clean)}, adversarial={len(selected_adv)}, cognitive={len(selected_cog)}")
    print(f"Total calibration samples: {len(combined)}")

    # Format using Llama 3.1 template with cognitive state role
    formatted_texts = []
    for item in combined:
        prompt = item.get("prompt", "")
        completion = item.get("completion", "")
        raw_intent = extract_raw_intent(prompt)
        cog_state = classify_cognitive_state(raw_intent)
        
        # Format the sample
        formatted_text = CHAT_TEMPLATE_LLAMA3.format(
            cognitive_state=cog_state,
            user_intent=raw_intent,
            completion=completion
        )
        formatted_texts.append(formatted_text)
        
    output_text = "\n\n".join(formatted_texts)
    output_file = processed_dir / "delentia_v043_imatrix_calib.txt"
    output_file.write_text(output_text, encoding="utf-8")
    
    print("-" * 50)
    print(f"🎉 Calibration file successfully created for v0.4.3!")
    print(f"  Destination: {output_file.absolute()}")
    print(f"  Total samples mixed: {len(combined)}")
    print(f"  File size: {output_file.stat().st_size / 1024:.2f} KB")
    print("-" * 50)

if __name__ == "__main__":
    main()
