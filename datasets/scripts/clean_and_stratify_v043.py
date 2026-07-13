#!/usr/bin/env python3
"""
clean_and_stratify_v043.py

Performs Shannon Entropy-based dataset stratification and TOON syntax validation on the final v0.4.3 golden dataset.
Ensures that:
  - Entropy Levels are correctly categorized.
  - Invalid TOON syntax patterns are flagged or cleaned.
  - Generates the final audit summary report.
"""

import math
import json
import argparse
import sys
from pathlib import Path
from collections import Counter

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

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
    
    # Check for User: format
    user_marker = "User: "
    idx_u = prompt_str.find(user_marker)
    if idx_u >= 0:
        return prompt_str[idx_u + len(user_marker):].strip()
        
    return prompt_str.strip()

def classify_and_stratify(prompt: str) -> str:
    """Categorize prompt based on Shannon Entropy level of the raw intent."""
    raw_intent = extract_raw_intent(prompt)
    entropy = compute_shannon_entropy(raw_intent)
    if entropy < 1.5:
        return 'low_entropy_toon_core'
    elif entropy < 3.0:
        return 'mid_entropy_normal'
    elif entropy < 5.0:
        return 'high_entropy_adversarial'
    else:
        return 'extreme_entropy_hard_block'

def validate_toon_syntax(completion: str) -> bool:
    """Check if completion contains standard TOON/JSON patterns correctly."""
    # If it is JITNA JSON structure
    if "{" in completion and "}" in completion:
        try:
            # Check for JSON syntax or partial JSON
            clean_comp = completion.strip()
            # If wrapped in markdown blocks
            if clean_comp.startswith("```json"):
                clean_comp = clean_comp.replace("```json", "", 1)
            if clean_comp.endswith("```"):
                clean_comp = clean_comp.rsplit("```", 1)[0]
            clean_comp = clean_comp.strip()
            json.loads(clean_comp)
            return True
        except Exception:
            pass
            
    # Check TOON structured tags
    required_tags = ['I:', 'D:', 'Δ:', 'A:', 'R:']
    if all(tag in completion for tag in required_tags):
        return True
        
    # Check for cognitive state formatting
    if "<cognitive_state>" in completion or "</cognitive_state>" in completion:
        return True
        
    # Standard conversation response
    return False

def main():
    parser = argparse.ArgumentParser(description="Clean and stratify Delentia dataset by Shannon Entropy")
    parser.add_argument("--input", type=str, default="datasets/processed/v0.4.3/knowledge_dataset_v0.4.3.jsonl", help="Input JSONL path")
    parser.add_argument("--output-report", type=str, default="C:/Users/whale/.gemini/antigravity-ide/brain/dab3e3b1-1b33-4a87-830a-df0bf90b8c0b/entropy_stratification_report.md", help="Output report path")
    
    args = parser.parse_args()
    
    repo_dir = Path(__file__).parent.parent.parent
    input_file = repo_dir / args.input
    
    if not input_file.exists():
        print(f"❌ Error: Input file {input_file} does not exist!")
        return

    print(f"Loading dataset: {input_file}")
    with open(input_file, "r", encoding="utf-8") as f:
        samples = [json.loads(l) for l in f if l.strip()]

    print(f"Loaded {len(samples)} samples. Starting analysis...")
    
    stratification_counts = Counter()
    toon_validity_counts = Counter()
    entropy_values = []
    issues = []
    
    for idx, sample in enumerate(samples):
        prompt = sample.get("prompt", "")
        completion = sample.get("completion", "")
        
        raw_intent = extract_raw_intent(prompt)
        entropy = compute_shannon_entropy(raw_intent)
        entropy_values.append(entropy)
        
        strat = classify_and_stratify(prompt)
        stratification_counts[strat] += 1
        
        is_valid_toon = validate_toon_syntax(completion)
        toon_validity_counts[is_valid_toon] += 1
        
        if not is_valid_toon and len(completion) > 0:
            issues.append({
                "index": idx,
                "prompt_snippet": prompt[:80],
                "completion_snippet": completion[:80],
                "entropy": entropy
            })

    # Prepare report contents
    avg_entropy = sum(entropy_values) / len(entropy_values) if entropy_values else 0.0
    min_entropy = min(entropy_values) if entropy_values else 0.0
    max_entropy = max(entropy_values) if entropy_values else 0.0
    
    report_content = f"""# 📊 Delentia OS v0.4.3 Dataset Stratification & TOON Validity Report

## 🔍 Dataset Metadata
- **Total Samples analyzed:** {len(samples)}
- **Average Shannon Entropy:** {avg_entropy:.4f} (Min: {min_entropy:.4f}, Max: {max_entropy:.4f})
- **TOON/JITNA Syntax Validity Rate:** {toon_validity_counts[True] / len(samples) * 100:.2f}% ({toon_validity_counts[True]} valid, {toon_validity_counts[False]} invalid)

## 📡 Shannon Entropy Stratification
| Entropy Level | Category | Count | Percentage | Description |
|---|---|---|---|---|
| **Low (0.0 - 1.5)** | TOON Clean Pattern / Core JITNA | {stratification_counts['low_entropy_toon_core']} | {stratification_counts['low_entropy_toon_core']/len(samples)*100:.2f}% | Ideal for Executor fine-tuning |
| **Mid (1.5 - 3.0)** | Normal User Requests / Conversational | {stratification_counts['mid_entropy_normal']} | {stratification_counts['mid_entropy_normal']/len(samples)*100:.2f}% | Used for Router & Guardian base training |
| **High (3.0 - 5.0)** | Adversarial Patterns / Complex Cases | {stratification_counts['high_entropy_adversarial']} | {stratification_counts['high_entropy_adversarial']/len(samples)*100:.2f}% | Guardian target layer training |
| **Extreme (5.0+)** | Base64/Injection / Threat Vectors | {stratification_counts['extreme_entropy_hard_block']} | {stratification_counts['extreme_entropy_hard_block']/len(samples)*100:.2f}% | Hard Block safety checks |

## ⚠️ TOON Syntax Flagged Issues
A total of **{len(issues)}** samples were flagged as conversational or potential TOON syntax outliers:
"""
    if issues:
        report_content += "\n| Index | Prompt Snippet | Completion Snippet | Entropy |\n|---|---|---|---|\n"
        for issue in issues[:20]:
            report_content += f"| {issue['index']} | `{issue['prompt_snippet']}` | `{issue['completion_snippet']}` | {issue['entropy']:.3f} |\n"
        if len(issues) > 20:
            report_content += f"\n*...and {len(issues) - 20} more samples.*"
    else:
        report_content += "\n✅ Zero syntax errors found. All completions comply with TOON or standard JSON formatting."

    # Write report
    report_file = Path(args.output_report)
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(report_content, encoding="utf-8")
    
    print("-" * 50)
    print(f"🎉 Stratification and clean audit completed successfully!")
    print(f"  Report written to: {report_file.absolute()}")
    print(f"  Average Entropy: {avg_entropy:.4f}")
    print(f"  TOON Valid Rate: {toon_validity_counts[True] / len(samples) * 100:.2f}%")
    print("-" * 50)

if __name__ == "__main__":
    main()
