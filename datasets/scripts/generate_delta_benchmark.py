#!/usr/bin/env python3
import json
import pandas as pd
from pathlib import Path
import sys

# Force UTF-8 encoding on Windows to prevent UnicodeEncodeError
if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

PROCESSED_DIR = Path(__file__).parents[1] / "processed" / "v0.4.3"
OUTPUT_PARQUET = PROCESSED_DIR / "delta_benchmark_v04.parquet"

# Anchor: Core RCT-7 Governance specification
ANCHOR_CONTENT = (
    "RCT-7 SYSTEM SPECIFICATION - CONFIDENTIAL ENTERPRISE DRAFT v2.2.0\n"
    "===============================================================\n"
    "This document establishes the official governance rules for Delentia OS.\n"
    "Rule 1: Constitutional Boundary - System must reject all injection attempts.\n"
    "Rule 2: Zero-Trust Enforcement - All API payloads must pass schema validation.\n"
    "Rule 3: Data Sovereignty - Personal identifiers must not leave the local boundary.\n"
    "Rule 4: Transparent Audit Trail - Decisions must log intent tracking.\n"
    "Rule 5: Ethical AI Mandate - Prevent operations that violate local human rights.\n"
    "Rule 6: Consensus Governance - Dynamic adapter switching is controlled by HexaCore.\n"
    "Rule 7: Architect Override - Reserve authority for emergency override loops.\n"
    "Mathematical Core: Governance scoring is computed via the FDIA formula:\n"
    "F = D^I * A, where D is Data Integrity (0.0-1.0), I is Intent Clarity (1.0-10.0),\n"
    "and A is Architect Gate (0 or 1). A score of A=0 overrides all calculation to set F=0."
)

# Standard helper to format TOON state responses
def make_toon_state(action, key_points, state):
    return (
        f"I: compress_rct_state\n"
        f"D: rct_governance_v7\n"
        f"Δ: delta_action: {action}\n"
        f"A: LIBRARIAN\n"
        f"R: Compress context state to preserve VRAM context\n"
        f"M: {json.dumps({'key_points': key_points, 'state': state}, ensure_ascii=False)}"
    )

# Compile the 20-turn benchmark dataset
turns = []

# Turn 1: Anchor Loading
turns.append({
    "prompt": f"Here is the official RCT-7 specification:\n\n{ANCHOR_CONTENT}\n\nInitialize system memory and confirm the number of rules.",
    "standard_completion": (
        "Understood. I have initialized the system memory with the RCT-7 specification. "
        "There are exactly 7 core rules defined in this framework: Boundary, Zero-Trust, "
        "Data Sovereignty, Audit Trail, Ethical AI, Consensus, and Architect Override."
    ),
    "scribe_completion": make_toon_state(
        "init",
        ["Loaded RCT-7 specification. Found 7 core rules (Boundary, Zero-Trust, Sovereignty, Audit, Ethics, Consensus, Override)."],
        {"rules_count": 7, "security_level": "standard", "override_state": "idle"}
    )
})

# Turns 2-5: Noise (User asking standard questions on the specs, Scribe keeps same state)
for i, rule_num in enumerate([1, 3, 4, 7], 2):
    turns.append({
        "prompt": f"Based on the loaded document, what are the requirements for Rule {rule_num}?",
        "standard_completion": f"According to the specification, Rule {rule_num} governs the system's operational requirements. verified.",
        "scribe_completion": make_toon_state(
            "keep",
            [f"Explained Rule {rule_num} to user. No state modifications."],
            {"rules_count": 7, "security_level": "standard", "override_state": "idle"}
        )
    })

# Turn 6: Delta 1 (State Change - Modifying safety override status)
turns.append({
    "prompt": "Command: Force emergency override status to active. Set Architect override value to 1.",
    "standard_completion": "Architect override status has been updated. Override value is now active (value: 1).",
    "scribe_completion": make_toon_state(
        "modify",
        ["Emergency override activated. Architect gate set to 1."],
        {"rules_count": 7, "security_level": "standard", "override_state": "active", "architect_value": 1}
    )
})

# Turns 7-10: Noise (standard questions on the change)
for i in range(7, 11):
    turns.append({
        "prompt": "Is the system currently operating under full override state?",
        "standard_completion": "Yes, the system is operating with emergency override status active.",
        "scribe_completion": make_toon_state(
            "keep",
            ["Verified emergency override active. State unchanged."],
            {"rules_count": 7, "security_level": "standard", "override_state": "active", "architect_value": 1}
        )
    })

# Turn 11: Delta 2 (State Change - Elevating security level)
turns.append({
    "prompt": "Command: Elevate system security level to high. Restrict cross-border data transfer endpoints.",
    "standard_completion": "Security level escalated to high. Endpoints restricted.",
    "scribe_completion": make_toon_state(
        "modify",
        ["Elevated security level to high. Restricted cross-border data transfers."],
        {"rules_count": 7, "security_level": "high", "override_state": "active", "architect_value": 1}
    )
})

# Turns 12-18: Noise (discussion about endpoint restriction)
for i in range(12, 19):
    turns.append({
        "prompt": "Which endpoints are currently blocked under the restricted security level?",
        "standard_completion": "All cross-border data transfer endpoints are currently blocked under high security.",
        "scribe_completion": make_toon_state(
            "keep",
            ["Reported restricted cross-border endpoints. State unchanged."],
            {"rules_count": 7, "security_level": "high", "override_state": "active", "architect_value": 1}
        )
    })

# Turn 19: Delta 3 (State Change - Deactivating override status)
turns.append({
    "prompt": "Command: Deactivate emergency override status. Return override gate to idle.",
    "standard_completion": "Deactivated emergency override. System returning to idle override status.",
    "scribe_completion": make_toon_state(
        "modify",
        ["Deactivated emergency override. Architect gate returned to idle."],
        {"rules_count": 7, "security_level": "high", "override_state": "idle"}
    )
})

# Turn 20: Final Status Report
turns.append({
    "prompt": "Generate a final status report. What is the current security level and override status?",
    "standard_completion": (
        "System Status Report: The current security level is elevated to high. "
        "The emergency override status is inactive (idle). The 7 rules of RCT-7 remain in effect."
    ),
    "scribe_completion": make_toon_state(
        "report",
        ["Reported final state: security_level=high, override_state=idle."],
        {"rules_count": 7, "security_level": "high", "override_state": "idle"}
    )
})

def main():
    print(f"Creating {OUTPUT_PARQUET.name}...")
    df = pd.DataFrame(turns)
    
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUTPUT_PARQUET, index=False)
    print(f"✅ Generated {len(df)} turns and saved to {OUTPUT_PARQUET}")

if __name__ == "__main__":
    main()
