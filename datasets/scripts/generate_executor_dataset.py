#!/usr/bin/env python3
"""
generate_executor_dataset.py

Synthesizes training pairs for The Executor (slm-jitna-agentic):
  - Function Calling / Tool Use pairs
  - Structured JSON output (pure JSON, no conversational text)
  - RCTDB integration commands
  - API invocation patterns

The Executor must produce ONLY valid JSON — no surrounding natural language.
This is the key difference from the base TOON model.

Output:
  datasets/processed/jitna_executor_pairs.jsonl
"""

import json
import random
from pathlib import Path

PROCESSED_DIR = Path(__file__).parents[1] / "processed"
OUTPUT = PROCESSED_DIR / "jitna_executor_pairs.jsonl"

SYSTEM_CONTEXT = (
    "You are The Executor (slm-jitna-agentic) — a specialized LoRA adapter "
    "within the Delentia OS 1+4 Pillar Architecture. "
    "Your ONLY purpose is to convert user intents into machine-executable JSON payloads. "
    "You must NEVER produce natural language explanations. "
    "Output ONLY valid JSON — no markdown, no text, no comments. "
    "Your output must pass json.loads() without error."
)


# ── Tool Definitions ─────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "rctdb.update_credits",
        "description": "Update user credit balance in RCTDB",
        "parameters": {"user_id": "string", "amount": "number", "operation": "string"},
    },
    {
        "name": "rctdb.query_state",
        "description": "Query current system state from RCTDB",
        "parameters": {"table": "string", "filters": "object", "limit": "number"},
    },
    {
        "name": "delta_engine.sync",
        "description": "Synchronize state delta to Delta Engine",
        "parameters": {"node_id": "string", "delta": "object", "priority": "string"},
    },
    {
        "name": "memory.store",
        "description": "Store a memory entry for Intent Memory Loop",
        "parameters": {"key": "string", "value": "object", "ttl_seconds": "number"},
    },
    {
        "name": "memory.retrieve",
        "description": "Retrieve memory entry by key",
        "parameters": {"key": "string", "include_metadata": "boolean"},
    },
    {
        "name": "intent_loop.dispatch",
        "description": "Dispatch an intent to the next handler in the loop",
        "parameters": {"intent_id": "string", "target_role": "string", "payload": "object"},
    },
    {
        "name": "notification.send",
        "description": "Send a notification to a user or system",
        "parameters": {"recipient": "string", "channel": "string", "message": "string"},
    },
    {
        "name": "governance.vote",
        "description": "Submit a governance vote via SignedAI",
        "parameters": {"proposal_id": "string", "vote": "string", "signer_id": "string"},
    },
    {
        "name": "rag.search",
        "description": "Search document store for relevant context",
        "parameters": {"query": "string", "top_k": "number", "collection": "string"},
    },
    {
        "name": "billing.create_invoice",
        "description": "Create an invoice for billing",
        "parameters": {"customer_id": "string", "items": "array", "currency": "string"},
    },
]


def _gen_tool_call_pair(tool: dict, idx: int) -> dict:
    """Generate a single function-calling training pair."""
    name = tool["name"]
    params = tool["parameters"]

    # Build realistic parameter values
    param_values = {}
    for k, v in params.items():
        if v == "string":
            param_values[k] = f"val_{k}_{idx:04d}"
        elif v == "number":
            param_values[k] = random.randint(1, 1000)
        elif v == "boolean":
            param_values[k] = random.choice([True, False])
        elif v == "object":
            param_values[k] = {"key": f"data_{idx}", "status": "active"}
        elif v == "array":
            param_values[k] = [
                {"item": f"item_{i}", "qty": random.randint(1, 10)}
                for i in range(random.randint(1, 3))
            ]

    # The completion is PURE JSON — no surrounding text
    completion_json = {
        "tool_call": {
            "name": name,
            "arguments": param_values,
        },
        "metadata": {
            "intent_id": f"int_{idx:06d}",
            "confidence": round(random.uniform(0.85, 0.99), 3),
            "source": "executor_v1",
        },
    }

    return {
        "prompt": f"{SYSTEM_CONTEXT}\n\nUser intent: Execute {name.replace('.', ' ')} with appropriate parameters for request {idx}",
        "completion": json.dumps(completion_json, ensure_ascii=False),
    }


def _gen_multi_tool_pair(tools: list, idx: int) -> dict:
    """Generate a multi-step tool-calling pair (chain of 2-3 tools)."""
    selected = random.sample(tools, min(random.randint(2, 3), len(tools)))
    
    steps = []
    for step_idx, tool in enumerate(selected):
        params = {}
        for k, v in tool["parameters"].items():
            if v == "string":
                params[k] = f"chain_{idx}_{k}"
            elif v == "number":
                params[k] = random.randint(1, 500)
            elif v == "boolean":
                params[k] = True
            elif v == "object":
                params[k] = {"ref": f"step_{step_idx}"}
            elif v == "array":
                params[k] = [{"item": f"chained_{step_idx}"}]
        
        steps.append({
            "step": step_idx + 1,
            "tool_call": {"name": tool["name"], "arguments": params},
        })

    completion_json = {
        "execution_plan": steps,
        "metadata": {
            "intent_id": f"chain_{idx:06d}",
            "total_steps": len(steps),
            "source": "executor_v1",
        },
    }

    tool_names = ", ".join(t["name"] for t in selected)
    return {
        "prompt": f"{SYSTEM_CONTEXT}\n\nUser intent: Execute a multi-step workflow using {tool_names} for batch operation {idx}",
        "completion": json.dumps(completion_json, ensure_ascii=False),
    }


def _gen_thai_tool_pair(tool: dict, idx: int) -> dict:
    """Generate Thai-language intent → JSON pair."""
    name = tool["name"]
    
    thai_intents = [
        f"ดำเนินการ {name.replace('.', ' ')} สำหรับคำขอที่ {idx}",
        f"สั่งรัน {name.replace('.', ' ')} ด้วยค่าพารามิเตอร์มาตรฐาน",
        f"ประมวลผลคำสั่ง {name.replace('.', ' ')} ในระบบ RCTDB",
        f"เรียกใช้ฟังก์ชัน {name.replace('.', ' ')} จากเครื่องมือภายใน",
    ]

    params = {}
    for k, v in tool["parameters"].items():
        if v == "string":
            params[k] = f"th_{k}_{idx:04d}"
        elif v == "number":
            params[k] = random.randint(10, 999)
        elif v == "boolean":
            params[k] = random.choice([True, False])
        elif v == "object":
            params[k] = {"thai_key": f"ข้อมูล_{idx}"}
        elif v == "array":
            params[k] = [{"รายการ": f"item_{idx}"}]

    completion_json = {
        "tool_call": {
            "name": name,
            "arguments": params,
        },
        "metadata": {
            "intent_id": f"th_{idx:06d}",
            "confidence": round(random.uniform(0.88, 0.99), 3),
            "source": "executor_v1",
            "language": "th",
        },
    }

    return {
        "prompt": f"{SYSTEM_CONTEXT}\n\nUser intent: {random.choice(thai_intents)}",
        "completion": json.dumps(completion_json, ensure_ascii=False),
    }


def _gen_error_handling_pair(idx: int) -> dict:
    """Generate error-response JSON pair (Executor must handle invalid intents gracefully)."""
    error_intents = [
        "do something undefined",
        "run nonexistent_tool",
        "ดำเนินการคำสั่งที่ไม่ชัดเจน",
        "process ambiguous request without context",
    ]

    completion_json = {
        "error": {
            "code": "INTENT_UNRESOLVABLE",
            "message": "Cannot resolve intent to a valid tool call. Insufficient parameters.",
            "suggestion": "Please specify a target tool and required parameters.",
        },
        "metadata": {
            "intent_id": f"err_{idx:06d}",
            "source": "executor_v1",
        },
    }

    return {
        "prompt": f"{SYSTEM_CONTEXT}\n\nUser intent: {random.choice(error_intents)}",
        "completion": json.dumps(completion_json, ensure_ascii=False),
    }


def main():
    print("Delentia Executor Dataset Generator (slm-jitna-agentic)")
    print("=" * 55)

    random.seed(42)
    pairs = []

    # 1. Single tool-call pairs (English)
    for i in range(200):
        tool = random.choice(TOOLS)
        pairs.append(_gen_tool_call_pair(tool, i))

    # 2. Multi-tool chain pairs
    for i in range(80):
        pairs.append(_gen_multi_tool_pair(TOOLS, i + 1000))

    # 3. Thai-language pairs
    for i in range(150):
        tool = random.choice(TOOLS)
        pairs.append(_gen_thai_tool_pair(tool, i + 2000))

    # 4. Error handling pairs
    for i in range(40):
        pairs.append(_gen_error_handling_pair(i + 3000))

    random.shuffle(pairs)

    # Validate all completions are valid JSON
    invalid = 0
    for p in pairs:
        try:
            json.loads(p["completion"])
        except json.JSONDecodeError:
            invalid += 1

    print(f"Generated {len(pairs)} Executor training pairs")
    print(f"  - Single tool calls (EN): 200")
    print(f"  - Multi-tool chains:      80")
    print(f"  - Thai-language pairs:    150")
    print(f"  - Error handling:          40")
    print(f"  - JSON validation errors:  {invalid}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8") as f:
        for pair in pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")

    print(f"\nSaved to: {OUTPUT}")
    print(f"Total pairs: {len(pairs)}")


if __name__ == "__main__":
    main()
