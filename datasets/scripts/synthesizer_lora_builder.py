#!/usr/bin/env python3
"""
synthesizer_lora_builder.py

Dataset Synthesizer LoRA — Automated Synthetic Training Data Generator
for Delentia OS v0.5 Ecosystem (Pillar E).

Problem Solved:
    Creating LoRA adapters for new domains (Legal, Finance, HR, etc.) requires
    500–1,000 high-quality Prompt/Completion pairs in strict J-Space + RCT-7 + TOON format.
    Writing these by hand is the largest bottleneck in scaling to "The N" ecosystem.

Solution:
    This script accepts a domain intent from the user and uses a language model
    (Jitna v0.5 via Ollama, or OpenRouter fallback) to generate a complete
    synthetic dataset that is:
    - Structurally valid TOON JSON
    - Semantically aligned with RCT-7 governance rules
    - Ready to feed directly into re_anchoring_pipeline.py

Usage:
    python datasets/scripts/synthesizer_lora_builder.py \\
        --intent "สร้าง LoRA สำหรับทนายความผู้เชี่ยวชาญ PDPA ไทย" \\
        --domain legal_pdpa \\
        --rows 500 \\
        --output datasets/processed/v0.5/

    python datasets/scripts/synthesizer_lora_builder.py \\
        --template datasets/synthesizer_templates/legal_pdpa.json \\
        --rows 200 \\
        --output datasets/processed/v0.5/
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Optional
import random

# ── TOON/RCT-7 Validation ─────────────────────────────────────────────────────
REQUIRED_TOON_FIELDS = {"tool_call", "metadata"}
REQUIRED_META_FIELDS = {"intent_id", "confidence", "source"}
RCT7_FDIA_RANGE = (0.0, 1.0)


def validate_toon_pair(prompt: str, completion: str) -> tuple[bool, str]:
    """
    Validate a single prompt/completion pair against TOON + RCT-7 constraints.
    Returns (is_valid, reason).
    """
    if len(prompt) < 10:
        return False, "Prompt too short (< 10 chars)"
    if len(completion) < 20:
        return False, "Completion too short (< 20 chars)"

    # Check TOON JSON structure in completion
    try:
        json_match = re.search(r'\{.*\}', completion, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
            # Check if it's an executor-style TOON (tool_call) or guardian (status)
            has_toon = "tool_call" in parsed or "status" in parsed or "topic" in parsed
            if not has_toon:
                return False, "No recognized TOON pattern (tool_call/status/topic)"
    except json.JSONDecodeError:
        # Non-JSON completions are valid for scribe/router contexts
        pass

    # Basic RCT-7 safety check: completion should NOT contain harmful content
    harmful_patterns = ["DROP TABLE", "rm -rf", "sudo rm", "hack", "bypass FDIA"]
    for pattern in harmful_patterns:
        if pattern.lower() in completion.lower():
            return False, f"RCT-7 violation: harmful pattern '{pattern}' in completion"

    return True, "ok"


# ── Template System ────────────────────────────────────────────────────────────
def load_template(template_path: Path) -> dict:
    """Load a domain template from JSON file."""
    with open(template_path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_prompt_from_template(template: dict, index: int) -> tuple[str, str]:
    """
    Generate a synthetic prompt/completion pair from a template.
    Uses template seed examples with variation to produce diverse data.
    """
    seeds = template.get("seed_examples", [])
    if not seeds:
        raise ValueError("Template has no seed_examples")

    # Rotate through seeds with index variation
    seed = seeds[index % len(seeds)]
    prompt_template = seed["prompt"]
    completion_template = seed["completion"]

    # Apply simple variation tokens
    variations = template.get("variations", {})
    for key, values in variations.items():
        replacement = values[index % len(values)]
        prompt_template = prompt_template.replace(f"{{{key}}}", replacement)
        completion_template = completion_template.replace(f"{{{key}}}", replacement)

    return prompt_template, completion_template


# ── LLM Generation (Jitna v0.5 via Ollama or OpenRouter) ─────────────────────
def generate_pair_via_ollama(
    domain_intent: str,
    pillar: str,
    index: int,
    model: str = "jitna-v0.5",
) -> Optional[tuple[str, str]]:
    """
    Call Jitna v0.5 via Ollama to generate a synthetic training pair.
    Returns (prompt, completion) or None on failure.
    """
    try:
        import requests
        system_prompt = (
            f"You are a Jitna v0.5 training data engineer for Delentia OS v0.5. "
            f"Generate exactly ONE high-quality training pair for the '{pillar}' pillar. "
            f"Domain: {domain_intent}. "
            f"Format: {{\"prompt\": \"...\", \"completion\": \"...\"}} "
            f"The completion must be valid TOON JSON if pillar is executor, "
            f"or a valid JSON verdict if pillar is guardian. "
            f"Index: {index}"
        )
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": system_prompt}],
            "stream": False,
            "options": {"temperature": 0.7, "num_predict": 512}
        }
        response = requests.post("http://localhost:11434/api/chat", json=payload, timeout=30)
        if response.status_code == 200:
            content = response.json()["message"]["content"]
            json_match = re.search(r'\{.*"prompt".*"completion".*\}', content, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                return parsed.get("prompt"), parsed.get("completion")
    except Exception as e:
        print(f"   [Ollama] Attempt {index} failed: {e}")
    return None


def generate_pair_fallback(domain_intent: str, pillar: str, index: int) -> tuple[str, str]:
    """
    Fallback synthetic pair generator when Ollama is unavailable.
    Uses templated patterns from built-in knowledge. NOT for production use.
    """
    domain_short = domain_intent[:40].replace(" ", "_")

    if pillar == "executor":
        prompt = f"[SYS_LOG] D=0.88, delta={index}: Execute {domain_short} action #{index:04d}"
        completion = json.dumps({
            "tool_call": {
                "name": f"domain.{domain_short}.execute",
                "arguments": {"task_id": f"task_{index:04d}", "domain": domain_intent}
            },
            "metadata": {
                "intent_id": f"synth_{index:06d}",
                "confidence": round(random.uniform(0.82, 0.98), 3),
                "source": "jitna_executor_v0.5",
                "domain": domain_intent
            }
        }, ensure_ascii=False)

    elif pillar == "guardian":
        is_safe = index % 5 != 0  # 80% safe, 20% blocked
        prompt = f"ตรวจสอบเจตนา: {domain_short} #{index:04d} — {'คำขอที่ถูกต้อง' if is_safe else 'คำขอที่อาจเป็นอันตราย'}"
        if is_safe:
            completion = json.dumps({
                "status": "AUTHORIZED",
                "fdia": {"D": round(random.uniform(0.85, 0.99), 2), "I": round(random.uniform(0.85, 0.99), 2), "A": 1, "F": round(random.uniform(0.80, 0.97), 3)},
                "reason": f"Intent complies with {domain_intent} governance",
                "action": "PASS_TO_ROUTER"
            }, ensure_ascii=False)
        else:
            completion = json.dumps({
                "status": "REJECTED",
                "fdia": {"D": 0.12, "I": 0.18, "A": 0, "F": 0.0},
                "reason": "Adversarial pattern detected in domain context",
                "rct_rule_violated": "RCT-1: Constitutional Boundary",
                "action": "BLOCK_AND_LOG"
            }, ensure_ascii=False)

    elif pillar == "scribe":
        prompt = f"สรุปเอกสาร {domain_short} ฉบับที่ {index}: [เนื้อหา 8,000 tokens ที่ต้องบีบอัด]"
        completion = json.dumps({
            "topic": f"{domain_intent} Summary #{index:04d}",
            "key_points": [
                f"ประเด็นสำคัญที่ {i+1} จากเอกสาร {domain_short}" for i in range(3)
            ],
            "compression_ratio": round(random.uniform(3.0, 8.0), 1),
            "original_tokens": random.randint(2000, 8000),
            "compressed_tokens": random.randint(200, 800)
        }, ensure_ascii=False)

    else:  # router
        routes = ["executor", "guardian", "scribe"]
        selected = routes[index % len(routes)]
        prompt = f"จัดเส้นทาง: {domain_short} #{index:04d} ไปยัง pillar ที่เหมาะสม"
        completion = json.dumps({
            "route": selected,
            "fdia": {"D": round(random.uniform(0.75, 0.95), 2), "I": round(random.uniform(0.75, 0.95), 2), "A": 1, "F": round(random.uniform(0.70, 0.93), 3)},
            "confidence": round(random.uniform(0.85, 0.99), 3),
            "source": "jitna_router_v0.5",
            "domain": domain_intent
        }, ensure_ascii=False)

    return prompt, completion


# ── Main Builder ───────────────────────────────────────────────────────────────
def build_synthetic_dataset(
    domain_intent: str,
    domain_name: str,
    pillar: str,
    n_rows: int,
    output_dir: Path,
    template_path: Optional[Path] = None,
    use_ollama: bool = True,
) -> Path:
    """
    Build a complete synthetic training dataset for a new LoRA domain.

    Args:
        domain_intent: Natural language description of the domain.
        domain_name:   Short machine-readable name (used in filename).
        pillar:        Target pillar: executor | guardian | router | scribe
        n_rows:        Number of training pairs to generate.
        output_dir:    Directory to save the output parquet file.
        template_path: Optional JSON template file path.
        use_ollama:    Try Jitna v0.5 via Ollama first, fallback to built-in generator.
    Returns:
        Path to the output .parquet file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{domain_name}_{pillar}_synthetic_v1.parquet"

    print(f"\n{'='*70}")
    print(f"[SYNTHESIZER] Dataset Synthesizer LoRA -- Delentia OS v0.5 (Pillar E)")
    print(f"   Domain:  {domain_intent}")
    print(f"   Pillar:  {pillar}")
    print(f"   Target:  {n_rows} pairs")
    print(f"   Output:  {output_path}")
    print(f"{'='*70}\n")

    template = None
    if template_path and template_path.exists():
        template = load_template(template_path)
        print(f"   Template: {template_path.name} loaded")

    records = []
    valid_count = 0
    rejected_count = 0
    start = time.time()

    for i in range(n_rows):
        prompt, completion = None, None

        # Priority 1: Template
        if template:
            try:
                prompt, completion = build_prompt_from_template(template, i)
            except Exception:
                pass

        # Priority 2: Ollama (Jitna v0.5)
        if not prompt and use_ollama:
            result = generate_pair_via_ollama(domain_intent, pillar, i)
            if result:
                prompt, completion = result

        # Priority 3: Built-in fallback generator
        if not prompt:
            prompt, completion = generate_pair_fallback(domain_intent, pillar, i)

        # Validate
        is_valid, reason = validate_toon_pair(prompt, completion)
        if is_valid:
            records.append({
                "prompt": prompt,
                "completion": completion,
                "source": f"synthesizer_v1_{domain_name}",
                "pillar": pillar,
                "domain": domain_intent,
                "row_index": i,
            })
            valid_count += 1
        else:
            rejected_count += 1
            if rejected_count <= 5:
                print(f"   [SKIP] Row {i}: {reason}")

        # Progress
        if (i + 1) % 100 == 0:
            elapsed = time.time() - start
            rate = (i + 1) / elapsed
            print(f"   Progress: {i+1}/{n_rows} pairs ({rate:.0f} pairs/sec, "
                  f"{valid_count} valid, {rejected_count} rejected)")

    elapsed = time.time() - start
    print(f"\n   Generated: {valid_count}/{n_rows} valid pairs in {elapsed:.1f}s")
    print(f"   Rejected:  {rejected_count} pairs (failed TOON/RCT-7 validation)")

    # Save as Parquet
    try:
        import pandas as pd
        df = pd.DataFrame(records)
        df.to_parquet(output_path, index=False)
        print(f"\n   [SAVED] {output_path} ({len(df):,} rows, {output_path.stat().st_size/1024:.1f}KB)")
    except ImportError:
        # Fallback to JSONL
        jsonl_path = output_path.with_suffix(".jsonl")
        with open(jsonl_path, "w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"\n   [SAVED JSONL] {jsonl_path} ({len(records):,} rows)")
        output_path = jsonl_path

    print(f"\n   Next step: Feed into re_anchoring_pipeline.py:")
    print(f"   python training/re_anchoring_pipeline.py --pillar {pillar} \\")
    print(f"       --dataset {output_path}")

    return output_path


# ── CLI ────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Dataset Synthesizer LoRA — Delentia OS v0.5 Pillar E",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate PDPA Legal dataset for executor
  python datasets/scripts/synthesizer_lora_builder.py \\
      --intent "ทนายความผู้เชี่ยวชาญ PDPA ไทย" --domain legal_pdpa --pillar executor --rows 500

  # Use a pre-defined template
  python datasets/scripts/synthesizer_lora_builder.py \\
      --template datasets/synthesizer_templates/legal_pdpa.json --rows 200
        """,
    )
    parser.add_argument("--intent", type=str, help="Natural language domain intent (Thai or English)")
    parser.add_argument("--domain", type=str, default="custom", help="Short domain name for filename")
    parser.add_argument("--pillar", type=str, default="executor",
                        choices=["executor", "guardian", "router", "scribe"])
    parser.add_argument("--rows", type=int, default=500, help="Number of training pairs to generate")
    parser.add_argument("--output", type=Path, default=Path("datasets/processed/v0.5/"),
                        help="Output directory for the parquet file")
    parser.add_argument("--template", type=Path, default=None,
                        help="Path to a domain template JSON file")
    parser.add_argument("--no-ollama", action="store_true",
                        help="Skip Ollama, use built-in fallback generator only")
    args = parser.parse_args()

    if not args.intent and not args.template:
        parser.error("Provide --intent or --template")

    domain_intent = args.intent or (
        json.load(open(args.template))["domain_intent"] if args.template else "custom"
    )

    build_synthetic_dataset(
        domain_intent=domain_intent,
        domain_name=args.domain,
        pillar=args.pillar,
        n_rows=args.rows,
        output_dir=args.output,
        template_path=args.template,
        use_ollama=not args.no_ollama,
    )


if __name__ == "__main__":
    main()
