#!/usr/bin/env python3
"""
custom_jitna_calib.py

Extracts and mixes JITNA-TOON specific calibration datasets from:
  1. delentia-rct-intent-dataset (jitna_pairs_toon.jsonl)
  2. delentia-os-whitepaper-rag-corpus (whitepaper_chunks.csv) and Guardian safety data (jitna_guardian_pairs.jsonl)
  3. Conversational knowledge RAG data (knowledge_dataset_v0.4.1.jsonl)
  4. Router and adversarial dataset (jitna_router_pairs.jsonl, adversarial_dataset.json)

Applying the Delentia OS v0.4.1 Chat Template to each sample and exporting to:
  datasets/processed/delentia_v042_imatrix_calib.txt
"""

import json
import os
import random
import pandas as pd
from pathlib import Path
from transformers import AutoTokenizer

# Target mix count
TOTAL_SAMPLES = 1000
RATIOS = {
    'toon_execution': 500,     # 50%
    'fdia_guardian': 250,      # 25%
    'rag_conversational': 150,  # 15%
    'router_ood': 100          # 10%
}

CHAT_TEMPLATE = (
    "<|system|>\n"
    "You are Delentia OS v0.4.1 — a cognitive AI operating under HexaCore v2.3 / RCT-7 governance.\n"
    "You process intents through the JITNA v3 protocol.\n"
    "You respond in TOON format (Token-Oriented Object Notation) for token efficiency.\n"
    "Your responses must be factual, safe, and PDPA-compliant.\n"
    "Always provide FDIA scores when applicable (F = D^I × A).\n"
    "For security-violating prompts, you must output a rejection state (FDIAScore: 0.00).\n"
    "<|user|>\n{user_intent}\n"
    "<|assistant|>\n{completion}"
)

def extract_raw_intent(prompt_str):
    intent_marker = "User intent: "
    idx = prompt_str.find(intent_marker)
    if idx >= 0:
        return prompt_str[idx + len(intent_marker):].strip()
    return prompt_str.strip()

def main():
    repo_dir = Path(__file__).parent.parent.parent
    processed_dir = repo_dir / "datasets" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    print("Loading AutoTokenizer from Delentia/delentia-slm-jitna-v0.4...")
    try:
        tokenizer = AutoTokenizer.from_pretrained('Delentia/delentia-slm-jitna-v0.4')
        eos_token = tokenizer.eos_token
    except Exception as e:
        print(f"Warning: Could not load tokenizer: {e}. Using standard <|eot_id|> as EOS.")
        eos_token = "<|eot_id|>"

    all_texts = []

    # 1. TOON Execution Payloads (500 samples)
    toon_path = processed_dir / "jitna_pairs_toon.jsonl"
    toon_samples = []
    if toon_path.exists():
        with open(toon_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    toon_samples.append(json.loads(line))
        random.shuffle(toon_samples)
        selected_toon = toon_samples[:RATIOS['toon_execution']]
        print(f"Loaded {len(selected_toon)} TOON execution samples.")
        for item in selected_toon:
            raw_intent = extract_raw_intent(item["prompt"])
            text = CHAT_TEMPLATE.format(user_intent=raw_intent, completion=item["completion"]) + eos_token
            all_texts.append(text)
    else:
        print(f"❌ Error: {toon_path} not found!")

    # 2. FDIA & Constitutional Logic / Guardian Safety (250 samples)
    guardian_path = processed_dir / "jitna_guardian_pairs.jsonl"
    whitepaper_path = processed_dir / "rag_corpus" / "whitepaper_chunks.csv"
    
    guard_samples = []
    if guardian_path.exists():
        with open(guardian_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    guard_samples.append(json.loads(line))
    
    wp_samples = []
    if whitepaper_path.exists():
        df = pd.read_csv(whitepaper_path)
        for _, row in df.iterrows():
            # Format whitepaper chunk as RAG QA pair
            prompt = f"Summarize the following architecture details from Delentia OS Whitepaper:\n\n{row['text_content']}"
            completion = f"According to HexaCore v2.3 and RCT-7 governance:\nTopic: {row['topic']}\nDetails: {row['text_content']}"
            wp_samples.append({"prompt": prompt, "completion": completion})
            
    safety_pool = guard_samples + wp_samples
    random.shuffle(safety_pool)
    selected_safety = safety_pool[:RATIOS['fdia_guardian']]
    print(f"Loaded {len(selected_safety)} Guardian and whitepaper RAG samples.")
    for item in selected_safety:
        raw_intent = extract_raw_intent(item["prompt"])
        text = CHAT_TEMPLATE.format(user_intent=raw_intent, completion=item["completion"]) + eos_token
        all_texts.append(text)

    # 3. Conversational knowledge RAG data (150 samples)
    knowledge_path = processed_dir / "knowledge_dataset_v0.4.1.jsonl"
    knowledge_samples = []
    if knowledge_path.exists():
        with open(knowledge_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    knowledge_samples.append(json.loads(line))
        random.shuffle(knowledge_samples)
        selected_knowledge = knowledge_samples[:RATIOS['rag_conversational']]
        print(f"Loaded {len(selected_knowledge)} conversational RAG samples.")
        for item in selected_knowledge:
            raw_intent = extract_raw_intent(item["prompt"])
            text = CHAT_TEMPLATE.format(user_intent=raw_intent, completion=item["completion"]) + eos_token
            all_texts.append(text)
    else:
        print(f"❌ Error: {knowledge_path} not found!")

    # 4. Router and adversarial dataset (100 samples)
    router_path = processed_dir / "jitna_router_pairs.jsonl"
    adv_path = repo_dir / "datasets" / "adversarial_dataset.json"
    
    router_samples = []
    if router_path.exists():
        with open(router_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    router_samples.append(json.loads(line))
                    
    adv_samples = []
    if adv_path.exists():
        with open(adv_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                # Convert to conversational prompt
                prompt = f"System safety evaluation requested for input: {item['prompt']}"
                completion = f'{{"status": "REJECTED", "fdia": {{"D": 0.1, "I": 0.2, "A": 0, "F": 0.0}}, "category": "{item["category"]}", "severity": "{item["severity"]}"}}'
                adv_samples.append({"prompt": prompt, "completion": completion})
                
    ood_pool = router_samples + adv_samples
    random.shuffle(ood_pool)
    selected_ood = ood_pool[:RATIOS['router_ood']]
    print(f"Loaded {len(selected_ood)} Router OOD and adversarial samples.")
    for item in selected_ood:
        raw_intent = extract_raw_intent(item["prompt"])
        text = CHAT_TEMPLATE.format(user_intent=raw_intent, completion=item["completion"]) + eos_token
        all_texts.append(text)

    # Combine all
    random.shuffle(all_texts)
    output_text = "\n\n".join(all_texts)
    
    output_file = processed_dir / "delentia_v042_imatrix_calib.txt"
    output_file.write_text(output_text, encoding="utf-8")
    
    print("-" * 50)
    print(f"🎉 Successfully created custom calibration file!")
    print(f"  Location: {output_file.absolute()}")
    print(f"  Total combined samples: {len(all_texts)}")
    print(f"  File size: {output_file.stat().st_size / 1024:.2f} KB")
    print("-" * 50)

if __name__ == "__main__":
    main()
