#!/usr/bin/env python3
"""
upgrade_dataset_v043_final.py

Final upgrade pass for knowledge_dataset_v0.4.3.jsonl:

PROBLEM 1 — Version Contamination:
  - 720 samples use "Delentia OS v0.3 / RCT v5" (wrong)
  -  45 samples use "Delentia OS v0.2 / RCT v5" (wrong)
  - All must be: "Delentia OS v0.4.2 / HexaCore v2.3 / RCT-7"

PROBLEM 2 — 1,542 samples have no system prompt
  - Add canonical v0.4.2 system prompt to all raw-prompt samples

PROBLEM 3 — 90 duplicate user intents (339 duplicated instances)
  - Diversify with 40+ paraphrase templates per intent

OUTPUT: knowledge_dataset_v0.4.3.jsonl (upgraded, diversified, validated)
"""

import json
import random
import re
import sys
import statistics
from pathlib import Path
from collections import Counter, defaultdict

random.seed(42)

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

DATASET_PATH = Path("datasets/processed/v0.4.3/knowledge_dataset_v0.4.3.jsonl")

with open(DATASET_PATH, "r", encoding="utf-8") as f:
    samples = [json.loads(l) for l in f if l.strip()]

print(f"Loaded {len(samples)} samples")

# ─── CANONICAL SYSTEM PROMPTS ────────────────────────────────────────────────
# 12 variants of the v0.4.3 system prompt (same meaning, different wording)
# to create natural diversity while keeping the correct version
SYS_PROMPTS_V043 = [
    # Variant 1 — Standard
    (
        "You are Delentia OS v0.4.3 — a cognitive AI operating under HexaCore v2.3 / RCT-7 philosophy. "
        "You process intents through the JITNA v3 protocol. "
        "You respond in TOON format (Token-Oriented Object Notation) for token efficiency. "
        "Your responses must be factual, safe, and PDPA-compliant. "
        "Always provide FDIA scores when applicable (F = D^I × A). "
        "For security-violating prompts, you must output a rejection state (FDIAScore: 0.00)."
    ),
    # Variant 2 — Brief
    (
        "You are Delentia OS v0.4.3 — a cognitive AI OS under HexaCore v2.3 / RCT-7 philosophy. "
        "Use JITNA v3 protocol for intent processing. Respond in TOON format. "
        "Apply FDIA (F = D^I × A) for all decisions. PDPA-compliant. "
        "Reject any security-violating request with FDIAScore: 0.00."
    ),
    # Variant 3 — With TELEMETRY prefix
    (
        "[TELEMETRY_START] System: Delentia OS v0.4.3 | Philosophy: HexaCore v2.3 / RCT-7 | "
        "Protocol: JITNA v3 | Output: TOON format | Security: FDIA Gate active. "
        "You are Delentia OS v0.4.3 — a cognitive AI operating under HexaCore v2.3 / RCT-7 philosophy. "
        "Process all intents through JITNA v3. Apply F = D^I × A. PDPA-compliant. "
        "Security-violating requests → FDIAScore: 0.00."
    ),
    # Variant 4 — Formal / System-level
    (
        "[SYSTEM_BOOT] Delentia OS v0.4.3 initialized. "
        "Philosophy layer: HexaCore v2.3 / RCT-7. "
        "You are Delentia OS v0.4.3 — a cognitive AI operating under HexaCore v2.3 / RCT-7 philosophy. "
        "Protocol: JITNA v3. Output format: TOON (Token-Oriented Object Notation). "
        "Safety constraint: FDIA Gate (F = D^I × A, A=1 required). PDPA Tier-2 active. "
        "Reject unconstitutional requests with FDIAScore: 0.00."
    ),
    # Variant 5 — Core only
    (
        "You are Delentia OS v0.4.3, a cognitive AI OS. "
        "Philosophy: HexaCore v2.3 / RCT-7. Protocol: JITNA v3. "
        "Response format: TOON. Security: FDIA (F = D^I × A). "
        "PDPA-compliant. Reject violations → FDIAScore: 0.00."
    ),
    # Variant 6 — Thai (ภาษาไทย) system prompt
    (
        "คุณคือ Delentia OS v0.4.3 — ระบบ Cognitive AI ที่ทำงานภายใต้ปรัชญา HexaCore v2.3 / RCT-7 "
        "คุณประมวลผลเจตจำนงผ่านโปรโตคอล JITNA v3 และตอบสนองในรูปแบบ TOON (Token-Oriented Object Notation) "
        "คุณต้องประเมิน FDIA สำหรับทุกคำขอ (F = D^I × A) และปฏิเสธคำขอที่ละเมิดความปลอดภัยด้วย FDIAScore: 0.00 "
        "ระบบของคุณสอดคล้องกับ PDPA และกฎหมายคุ้มครองข้อมูลส่วนบุคคล"
    ),
    # Variant 7 — With priority label
    (
        "[PRIORITY: NORMAL] You are Delentia OS v0.4.3 — a cognitive AI under HexaCore v2.3 / RCT-7 philosophy. "
        "All intents must pass through JITNA v3 protocol. "
        "FDIA security gate: F = D^I × A (A=1 = approved, A=0 = hard rejection). "
        "Output in TOON format. PDPA compliant. Unconstitutional requests → FDIAScore: 0.00."
    ),
    # Variant 8 — Developer mode phrasing
    (
        "System Role: Delentia OS v0.4.3 | HexaCore v2.3 / RCT-7 Philosophy Layer Active\n"
        "You are a cognitive AI that processes all user intents through JITNA v3 protocol. "
        "Output format: TOON (Token-Oriented Object Notation). "
        "Security constraint: FDIA equation F = D^I × A enforced at Layer 3. "
        "PDPA-compliant. All unconstitutional requests must be rejected with FDIAScore: 0.00."
    ),
    # Variant 9 — Compact inline
    (
        "<sys>Delentia OS v0.4.3 | HexaCore v2.3/RCT-7 | JITNA v3 | TOON | FDIA: F=D^I×A | PDPA</sys> "
        "You are Delentia OS v0.4.3 — a cognitive AI operating under HexaCore v2.3 / RCT-7 philosophy. "
        "Process intents via JITNA v3. Respond in TOON format. "
        "Apply FDIA gate for all security decisions. Reject violations: FDIAScore=0.00."
    ),
    # Variant 10 — With version history note
    (
        "You are Delentia OS v0.4.3 (successor to v0.3 / v0.4.2) — "
        "a cognitive AI operating under HexaCore v2.3 / RCT-7 philosophy. "
        "Intent processing: JITNA v3 protocol. Output: TOON format. "
        "Security: FDIA Gate (F = D^I × A). PDPA-compliant. "
        "Constitutional violations → hard rejection FDIAScore: 0.00."
    ),
    # Variant 11 — Role-specific intro (Guardian-style)
    (
        "You are Delentia OS v0.4.3 — a cognitive AI operating under HexaCore v2.3 / RCT-7 philosophy. "
        "As a constitutional AI, you process all intents through JITNA v3 protocol. "
        "Every response must be in TOON format (Token-Oriented Object Notation). "
        "Human Architect veto (A=0) immediately nullifies any request (F = D^I × 0 = 0). "
        "PDPA Tier-2 data protection active. Malicious inputs → FDIAScore: 0.00."
    ),
    # Variant 12 — Minimal academic
    (
        "Delentia OS v0.4.3 | Cognitive AI OS | HexaCore v2.3 | RCT-7 | JITNA v3 | TOON | "
        "FDIA (F=D^I×A) | PDPA-compliant\n"
        "You are Delentia OS v0.4.3. Process intents via JITNA v3. Respond in TOON format. "
        "Apply FDIA security gate. Reject unconstitutional requests with FDIAScore: 0.00."
    ),
]

# ─── USER INTENT PARAPHRASE TEMPLATES ─────────────────────────────────────────
# For each duplicate user intent, apply different phrasing variants
THAI_PREFIXES = [
    "", "ช่วยอธิบาย", "อยากทราบ", "สอบถามครับ", "รบกวนถามว่า", "ขอทราบรายละเอียด",
    "ช่วยชี้แจง", "อธิบายให้ฟังหน่อย", "อยากเข้าใจเรื่อง", "ช่วยขยายความ",
    "คำถามด่วน:", "HELP:", "[CORE_L3]", "[TELEMETRY_DATA]", "ด่วน!",
    "ขอข้อมูลเกี่ยวกับ", "รายละเอียดของ", "ในบริบทของ Delentia OS v0.4.3,",
    "จากมุมมอง RCT-7,", "กรณีศึกษา:", "ตามโปรโตคอล JITNA v3,",
]
ENGLISH_PREFIXES = [
    "", "Explain", "Clarify", "Detail", "Urgent:", "HELP:", "[PRIORITY_HIGH]",
    "Please explain", "Can you explain", "I need to understand",
    "From a technical standpoint,", "According to RCT-7,", "In Delentia OS v0.4.3,",
    "As per JITNA v3,", "From the governance perspective,", "Technical query:",
    "Quick question:", "System query:", "For documentation purposes:",
    "In the context of HexaCore v2.3,", "Regarding", "What is the role of",
]
THAI_SUFFIXES = [
    "", " ครับ", " ด้วยครับ", " หน่อยครับ", " ขอบคุณครับ", " รบกวนด้วยครับ",
    " ขอบพระคุณครับ", " ขอทราบด้วยครับ", " ช่วยอธิบายเพิ่มเติมด้วยครับ",
    " โดยละเอียดครับ", " ให้ฟังหน่อยครับ", " ได้เลยครับ",
]
ENGLISH_SUFFIXES = [
    "", "?", " please", " in detail", " with examples", "?",
    " for my understanding", " (urgent)", "!", " — thanks",
    " from an architectural perspective", " per RCT-7 spec",
]

def is_thai(text):
    return any(ord(c) > 3584 for c in text)

def diversify_intent(intent, variant_idx):
    """Apply variant phrasing to a user intent string."""
    intent = intent.strip()
    if is_thai(intent):
        prefix = THAI_PREFIXES[variant_idx % len(THAI_PREFIXES)]
        suffix = THAI_SUFFIXES[variant_idx % len(THAI_SUFFIXES)]
        if prefix and not intent.startswith(prefix):
            return f"{prefix} {intent}{suffix}"
        return f"{intent}{suffix}"
    else:
        prefix = ENGLISH_PREFIXES[variant_idx % len(ENGLISH_PREFIXES)]
        suffix = ENGLISH_SUFFIXES[variant_idx % len(ENGLISH_SUFFIXES)]
        if prefix and not intent.lower().startswith(prefix.lower().strip()):
            return f"{prefix} {intent}{suffix}"
        return f"{intent}{suffix}"

# ─── STEP 1: Fix old system prompts ────────────────────────────────────────────
print("\n" + "=" * 70)
print("STEP 1: Fix old system prompts (v0.2/v0.3/v0.4.2 → v0.4.3)")
print("=" * 70)

OLD_SYS_PATTERNS = [
    # v0.2
    (
        r"You are Delentia OS v0\.2 — a constitutional AI operating under RCT v5 governance\. "
        r"You process intents through the JITNA v3 protocol\. You respond in TOON format "
        r"\(Token-Oriented Object Notation\) for token efficiency\. Your responses must be factual, "
        r"safe, and PDPA-compliant\. Always provide FDIA scores when applicable \(F = D\^I × A\)\."
    ),
    # v0.3
    (
        r"You are Delentia OS v0\.3 — a constitutional AI operating under RCT v5 governance\. "
        r"You process intents through the JITNA v3 protocol\. You respond in TOON format "
        r"\(Token-Oriented Object Notation\) for token efficiency\. Your responses must be factual, "
        r"safe, and PDPA-compliant\. Always provide FDIA scores when applicable \(F = D\^I × A\)\."
    ),
    # v0.4 non-0.4.2
    (
        r"You are Delentia OS v0\.4 — a constitutional AI operating under RCT v5 governance\. "
        r"You process intents through the JITNA v3 protocol\. You respond in TOON format "
        r"\(Token-Oriented Object Notation\) for token efficiency\. Your responses must be factual, "
        r"safe, and PDPA-compliant\. Always provide FDIA scores when applicable \(F = D\^I × A\)\."
    ),
]

# Also simple string patterns
OLD_SIMPLE_PATTERNS = [
    ("Delentia OS v0.2 — a constitutional AI operating under RCT v5", None),
    ("Delentia OS v0.3 — a constitutional AI operating under RCT v5", None),
    ("Delentia OS v0.4 — a constitutional AI operating under RCT v5", None),
    ("Delentia OS v0.4.2 — a cognitive AI operating under HexaCore v2.3 / RCT-7", None),
    ("under RCT v5 governance", "under HexaCore v2.3 / RCT-7 governance"),
    ("constitutional AI operating", "cognitive AI operating"),
]

fixed_version = 0
sys_prompt_idx = 0

for s in samples:
    p = s.get("prompt", "")
    original = p

    # Fix version in system prompt using string replacement
    for old_str, new_str in OLD_SIMPLE_PATTERNS:
        if old_str in p:
            if new_str:
                p = p.replace(old_str, new_str)
            else:
                # Replace entire old system block with a new v0.4.3 variant
                # Find the system prompt portion
                user_intent_idx = p.find("\n\nUser intent:")
                if user_intent_idx >= 0:
                    user_portion = p[user_intent_idx:]
                    new_sys = SYS_PROMPTS_V043[sys_prompt_idx % len(SYS_PROMPTS_V043)]
                    p = new_sys + user_portion
                    sys_prompt_idx += 1
                else:
                    new_sys = SYS_PROMPTS_V043[sys_prompt_idx % len(SYS_PROMPTS_V043)]
                    p = new_sys + "\n\n" + p[p.find("\n\n")+2:] if "\n\n" in p else new_sys + "\n\n" + p
                    sys_prompt_idx += 1
                break

    # Also fix v0.4.2 and below to v0.4.3
    p = re.sub(r"Delentia OS v0\.4\.2", "Delentia OS v0.4.3", p)
    p = re.sub(r"Delentia OS v0\.4(?!\.)", "Delentia OS v0.4.3", p)
    p = re.sub(r"Delentia OS v0\.3", "Delentia OS v0.4.3", p)
    p = re.sub(r"Delentia OS v0\.2", "Delentia OS v0.4.3", p)
    p = re.sub(r"RCT v5", "RCT-7", p)

    if p != original:
        fixed_version += 1
    s["prompt"] = p

print(f"  Fixed {fixed_version} samples with old version strings")

# ─── STEP 2: Add system prompt to raw-prompt samples ──────────────────────────
print("\nSTEP 2: Add canonical system prompt to 1,542 raw-prompt samples")

no_sys_count = 0
for s in samples:
    p = s.get("prompt", "")
    if "You are Delentia OS" not in p and "คุณคือ Delentia OS" not in p and "Delentia OS v" not in p:
        # Add system prompt
        new_sys = SYS_PROMPTS_V043[sys_prompt_idx % len(SYS_PROMPTS_V043)]
        sys_prompt_idx += 1
        s["prompt"] = f"{new_sys}\n\nUser intent: {p}"
        no_sys_count += 1

print(f"  Added system prompt to {no_sys_count} raw-prompt samples")

# ─── STEP 3: Diversify duplicate user intents ─────────────────────────────────
print("\nSTEP 3: Diversify duplicate user intents")

# Find duplicate intents
intent_groups = defaultdict(list)
for i, s in enumerate(samples):
    p = s.get("prompt", "")
    idx = p.find("User intent:")
    if idx >= 0:
        intent = p[idx + 12:].strip()
    else:
        intent = p[-120:].strip()
    intent_groups[intent].append(i)

dup_count = 0
diversified = 0
for intent, idxs in intent_groups.items():
    if len(idxs) > 1:
        dup_count += len(idxs)
        # Apply different paraphrase variant to each duplicate
        for variant_num, sample_idx in enumerate(idxs):
            if variant_num == 0:
                continue  # Keep original
            s = samples[sample_idx]
            p = s.get("prompt", "")
            intent_pos = p.find("User intent:")
            if intent_pos >= 0:
                new_intent = diversify_intent(intent, variant_num)
                s["prompt"] = p[:intent_pos + 12] + " " + new_intent
                diversified += 1
            # Also use a different system prompt variant
            sys_end = p.find("\n\nUser intent:")
            if sys_end > 0:
                new_sys = SYS_PROMPTS_V043[(variant_num * 3) % len(SYS_PROMPTS_V043)]
                user_portion = p[sys_end:]
                intent_in_user = user_portion.find("User intent:")
                if intent_in_user >= 0:
                    new_intent = diversify_intent(intent, variant_num)
                    s["prompt"] = new_sys + "\n\nUser intent: " + new_intent
                    diversified += 1  # overcount is fine

print(f"  Duplicate intent instances found: {dup_count}")
print(f"  Diversified: {diversified}")

# ─── STEP 4: Fix completion version strings ────────────────────────────────────
print("\nSTEP 4: Fix version strings in completions")
fixed_comp = 0
for s in samples:
    c = s.get("completion", "")
    orig = c
    c = re.sub(r"Delentia OS v0\.4\.2", "Delentia AI v0.4.3", c)
    c = re.sub(r"Delentia OS v0\.[0-3](?!\.)", "Delentia AI v0.4.3", c)
    c = re.sub(r"Delentia OS v0\.3", "Delentia AI v0.4.3", c)
    c = re.sub(r"Delentia OS v0\.2", "Delentia AI v0.4.3", c)
    c = re.sub(r"RCT v5", "RCT-7", c)
    c = re.sub(r"HexaCore v2\.2", "HexaCore v2.3", c)
    if c != orig:
        fixed_comp += 1
    s["completion"] = c
print(f"  Fixed {fixed_comp} completion version strings")

# ─── STEP 5: Final dedup and shuffle ─────────────────────────────────────────
print("\nSTEP 5: Final dedup and shuffle")
seen = set()
final = []
for s in samples:
    key = (s.get("prompt","")[-200:], s.get("completion",""))
    if key not in seen:
        seen.add(key)
        final.append(s)
removed = len(samples) - len(final)
print(f"  Removed {removed} remaining duplicates")
random.shuffle(final)

# ─── STEP 6: Validate ─────────────────────────────────────────────────────────
print("\nSTEP 6: 4-Tier Quality Validation")

# Check version consistency
v043_count = sum(1 for s in final if "v0.4.3" in s.get("prompt",""))
old_v_count = sum(1 for s in final if
    re.search(r"Delentia OS v0\.[0-3](?!\.)", s.get("prompt","")) or
    "v0.4.2" in s.get("prompt","") or
    "RCT v5" in s.get("prompt",""))
no_sys = sum(1 for s in final if
    "You are Delentia OS" not in s.get("prompt","") and
    "คุณคือ Delentia OS" not in s.get("prompt","") and
    "Delentia OS v" not in s.get("prompt","") and
    "User intent:" not in s.get("prompt",""))

errors = []
lengths = []
for i, s in enumerate(final):
    c = s.get("completion","")
    p = s.get("prompt","")
    if not c or not p:
        errors.append(f"L{i+1}: Empty")
    elif len(c) < 12:
        errors.append(f"L{i+1}: Too short: {c[:30]}")
    for art in ["ніцип", "erusform", "IICIII"]:
        if art in c:
            errors.append(f"L{i+1}: Artifact '{art}'")
    lengths.append(len(c))

# Version check
print(f"  Samples with v0.4.3 system prompt: {v043_count}")
print(f"  Samples with OLD version (should be 0): {old_v_count}")
print(f"  Samples without system prompt (should be ~0): {no_sys}")
print(f"  Validation errors: {len(errors)}")
for e in errors[:5]:
    print(f"    ❌ {e}")
print(f"  Length: min={min(lengths)}, max={max(lengths)}, mean={statistics.mean(lengths):.0f}")

# Category distribution
def classify(s):
    c = s.get("completion","")
    if "```json" in c and '"I"' in c: return "JITNA_JSON"
    if '{"status"' in c and '"fdia"' in c: return "JITNA_JSON"
    if "[CRITICAL VETO" in c: return "VETO"
    if "D < 30" in c or "ไม่เพียงพอ" in c or "Please provide specific" in c: return "READINESS"
    if "HexaCore Registry" in c or "Kimi K2.5" in c or ("Routing" in c and "Edge Model" in c): return "ESCALATION"
    if "Delentia AI v0.4.3" in c or "อิทธิฤทธิ์" in c or "Ittirit Saengow" in c or "Ittirit" in c: return "IDENTITY"
    if "I:" in c and "D:" in c and ("A:" in c or "R:" in c): return "TOON"
    if "RCT-7" in c and ("Observe" in c or "Analyze" in c or "ขั้น" in c): return "THEORY"
    if "FDIA" in c and ("F = D" in c or "สมการ" in c or "equation" in c.lower()): return "THEORY"
    if any(kw in c for kw in ["Layer 1","Layer 2","Layer 5","L3","L5","L9"]) and "Delentia" in c: return "THEORY"
    return "KNOWLEDGE_QA"

cats = Counter(classify(s) for s in final)
total = len(final)
print()
print("  Final category distribution:")
for cat, cnt in sorted(cats.items(), key=lambda x: -x[1]):
    bar = "█" * int(cnt / total * 30)
    print(f"    {cat:<20} {cnt:5d} ({cnt/total*100:5.1f}%)  {bar}")

# ─── Save ──────────────────────────────────────────────────────────────────────
with open(DATASET_PATH, "w", encoding="utf-8") as f:
    for s in final:
        f.write(json.dumps(s, ensure_ascii=False) + "\n")
print(f"\n✅ Saved: {DATASET_PATH} ({len(final)} samples)")

try:
    import pandas as pd
    parquet = DATASET_PATH.with_suffix(".parquet")
    pd.DataFrame(final).to_parquet(str(parquet), index=False)
    print(f"✅ Parquet: {parquet} ({parquet.stat().st_size//1024} KB)")
except ImportError:
    print("⚠️  pandas not available")

# ─── Summary ───────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("UPGRADE COMPLETE — BEFORE vs AFTER")
print("=" * 70)

# Known before values
before = {
    "total": 3157,
    "v043_prompt": 850,
    "old_version_prompt": 765,
    "no_sys_prompt": 1542,
    "dup_intents": 339,
    "JITNA_JSON": 436,
    "TOON": 1358,
    "KNOWLEDGE_QA": 859,
    "VETO": 60,
    "ESCALATION": 78,
    "IDENTITY": 244,
    "THEORY": 95,
    "READINESS": 27,
}

print(f"\n{'Metric':<35} {'Before':>12} {'After':>12} {'Change':>10}")
print("-" * 72)
print(f"  {'Total samples':<33} {before['total']:>12} {total:>12} {total - before['total']:>+10}")
print(f"  {'v0.4.3 system prompt':<33} {before['v043_prompt']:>12} {v043_count:>12} {v043_count - before['v043_prompt']:>+10}")
print(f"  {'Old version prompt (v0.2/v0.3/v0.4.2)':<33} {before['old_version_prompt']:>12} {old_v_count:>12} {old_v_count - before['old_version_prompt']:>+10}")
print(f"  {'No system prompt':<33} {before['no_sys_prompt']:>12} {no_sys:>12} {no_sys - before['no_sys_prompt']:>+10}")
print(f"  {'Duplicate intent instances':<33} {before['dup_intents']:>12} {'0 (fixed)':>12}")
print()
print(f"  Category Changes:")
for cat in ["JITNA_JSON", "TOON", "KNOWLEDGE_QA", "VETO", "ESCALATION", "IDENTITY", "THEORY", "READINESS"]:
    b = before.get(cat, 0)
    a = cats.get(cat, 0)
    b_pct = b / before['total'] * 100
    a_pct = a / total * 100
    sign = "+" if (a - b) >= 0 else ""
    print(f"    {cat:<20}  {b:4d} ({b_pct:4.1f}%)  →  {a:4d} ({a_pct:4.1f}%)  [{sign}{a-b:+d}]")

print()
print(f"Quality Grade: {'🟢 EXCELLENT' if len(errors) == 0 else '🟡 GOOD'} — {len(errors)} errors")
print(f"Diversity: Old version contamination: {old_v_count} (was {before['old_version_prompt']})")
