#!/usr/bin/env python3
"""
generate_scribe_dataset.py

Synthesizes training pairs for The Scribe (slm-jitna-scribe):
  - Context compression (long text → concise summary)
  - RAG result ranking and filtering
  - Hierarchical summarization
  - Token-efficient knowledge extraction

The Scribe takes long context and compresses it into minimal, high-signal output.

Output:
  datasets/processed/jitna_scribe_pairs.jsonl
"""

import json
import random
from pathlib import Path

PROCESSED_DIR = Path(__file__).parents[1] / "processed"
OUTPUT = PROCESSED_DIR / "jitna_scribe_pairs.jsonl"

SYSTEM_CONTEXT = (
    "You are The Scribe (slm-jitna-scribe) — a specialized LoRA adapter "
    "within the Delentia OS 1+4 Pillar Architecture. "
    "Your purpose is to compress large contexts into minimal, high-signal summaries. "
    "Remove noise. Keep only actionable information. "
    "Output must be structured and token-efficient. "
    "Report compression statistics in every response."
)

# ── Document Templates ───────────────────────────────────────────────────

LONG_DOCUMENTS = [
    {
        "topic": "PDPA Compliance",
        "content": (
            "The Personal Data Protection Act (PDPA) of Thailand, B.E. 2562 (2019), "
            "establishes comprehensive requirements for the collection, use, and disclosure "
            "of personal data. Organizations must obtain consent before collecting personal "
            "data and must clearly state the purpose of collection. The Act applies to any "
            "organization that collects, uses, or discloses personal data in Thailand, "
            "regardless of where the organization is located. Key requirements include: "
            "1) Lawful basis for processing, 2) Data minimization principle, "
            "3) Purpose limitation, 4) Storage limitation, 5) Data subject rights "
            "including right to access, correct, delete, restrict processing, "
            "data portability, and object to processing. "
            "Penalties for non-compliance can reach up to 5 million THB in fines. "
            "The Data Protection Committee oversees enforcement. "
            "Organizations must appoint a Data Protection Officer (DPO) if processing "
            "large volumes of sensitive data. Cross-border data transfers require "
            "adequate safeguards. Data breach notification must be made within 72 hours."
        ),
        "summary": {
            "topic": "PDPA Compliance",
            "key_points": [
                "Consent required before data collection",
                "Applies to all organizations processing Thai personal data",
                "6 data subject rights (access, correct, delete, restrict, portability, object)",
                "Max penalty: 5M THB",
                "DPO required for large-scale sensitive data",
                "72-hour breach notification requirement",
            ],
            "compression_ratio": 4.2,
            "original_tokens": 180,
            "compressed_tokens": 43,
        },
    },
    {
        "topic": "RCT Governance Framework",
        "content": (
            "The Real-time Constitutional Trust (RCT) framework is a multi-layered "
            "governance system designed for autonomous AI operations. Version 7 introduces "
            "seven core rules: Rule 1 (Constitutional Boundary) ensures all AI actions "
            "operate within pre-defined ethical boundaries. Rule 2 (Zero-Trust Enforcement) "
            "requires verification at every decision point. Rule 3 (Data Sovereignty) "
            "guarantees data remains under the control of the designated authority. "
            "Rule 4 (Transparent Audit Trail) mandates complete logging of all decisions. "
            "Rule 5 (Ethical AI Mandate) prohibits actions that cause harm to individuals. "
            "Rule 6 (Consensus Governance) requires multi-stakeholder agreement for "
            "critical decisions. Rule 7 (Architect Override) reserves ultimate authority "
            "to the system architect for emergency interventions. The framework uses "
            "the FDIA scoring formula F = D^I × A to calculate governance compliance, "
            "where D represents data integrity, I represents intent clarity, and A "
            "is the architect approval gate (binary 0 or 1). A score of 0 from the "
            "architect gate immediately blocks any action regardless of other scores."
        ),
        "summary": {
            "topic": "RCT v7 Governance",
            "key_points": [
                "7 core rules: Boundary, Zero-Trust, Data Sovereignty, Audit, Ethics, Consensus, Override",
                "FDIA formula: F = D^I × A",
                "A=0 blocks all actions immediately",
                "Transparent audit trail mandatory",
                "Multi-stakeholder consensus for critical decisions",
            ],
            "compression_ratio": 3.8,
            "original_tokens": 165,
            "compressed_tokens": 44,
        },
    },
    {
        "topic": "Delta Engine Architecture",
        "content": (
            "The Delta Engine is a state management subsystem within Delentia OS "
            "responsible for tracking all changes (deltas) in the system. It operates "
            "on the principle of event sourcing where every state change is recorded "
            "as an immutable event. The engine maintains a rolling cache of recent "
            "deltas for fast access and periodically compacts older deltas into "
            "summary snapshots. Key features include: bidirectional sync between "
            "nodes, conflict resolution via vector clocks, automatic garbage "
            "collection of expired deltas, and real-time delta streaming via "
            "WebSocket connections. The Delta Engine integrates with RCTDB for "
            "persistent storage and with the Intent Memory Loop for contextual "
            "decision making. Performance metrics show average delta processing "
            "latency of 12ms with throughput of 10,000 deltas per second on "
            "standard hardware. The engine supports both full and partial state "
            "reconstruction from the delta log."
        ),
        "summary": {
            "topic": "Delta Engine",
            "key_points": [
                "Event-sourcing based state management",
                "Rolling cache + periodic compaction to snapshots",
                "Bidirectional sync with vector clock conflict resolution",
                "12ms average latency, 10K deltas/sec throughput",
                "Integrates with RCTDB and Intent Memory Loop",
            ],
            "compression_ratio": 3.5,
            "original_tokens": 142,
            "compressed_tokens": 41,
        },
    },
    {
        "topic": "LoRA Multiplexing Architecture",
        "content": (
            "LoRA Multiplexing is the architectural pattern used by Delentia OS "
            "to run multiple specialized AI models using a single base model in "
            "GPU memory. The base model (kernel) is loaded once into VRAM and "
            "occupies approximately 6-8 GB for an 8 billion parameter model "
            "quantized to 4-bit. Four specialized LoRA adapters (Router, Executor, "
            "Guardian, Scribe) are stored as small weight files of 50-150 MB each. "
            "When the AI Orchestrator receives a command, it dynamically swaps the "
            "appropriate LoRA adapter into the base model within milliseconds. "
            "This approach provides the functional equivalent of four separate "
            "specialized models while consuming the memory of only one model. "
            "The swap mechanism uses PEFT library's set_adapter() method and "
            "requires no model reloading. Adapter selection is determined by "
            "the Router model's classification output. Average swap latency "
            "is under 50ms including adapter weight injection and attention "
            "head reconfiguration."
        ),
        "summary": {
            "topic": "LoRA Multiplexing",
            "key_points": [
                "Single base model in VRAM (~6-8 GB for 8B params Q4)",
                "4 LoRA adapters: Router, Executor, Guardian, Scribe (50-150 MB each)",
                "Dynamic swap via PEFT set_adapter() in <50ms",
                "Memory cost = 1 model, capability = 4 specialized models",
                "Router classification determines adapter selection",
            ],
            "compression_ratio": 3.9,
            "original_tokens": 155,
            "compressed_tokens": 40,
        },
    },
]

# Thai documents
LONG_DOCUMENTS_TH = [
    {
        "topic": "ระบบ Intent Memory Loop",
        "content": (
            "ระบบ Intent Memory Loop เป็นกลไกหลักของ Delentia OS ที่ทำหน้าที่ "
            "เชื่อมโยงการรับคำสั่ง การดำเนินการ และการจดจำผลลัพธ์เข้าด้วยกันเป็นวงจรปิด "
            "เมื่อผู้ใช้ส่งเจตนาเข้ามา ระบบจะประมวลผลผ่าน Router เพื่อจำแนกประเภท "
            "ส่งต่อไปยัง Guardian เพื่อตรวจสอบความปลอดภัย จากนั้น Scribe จะดึงข้อมูล "
            "บริบทที่เกี่ยวข้อง และ Executor จะแปลงเจตนาเป็นคำสั่งที่เครื่องจักรเข้าใจได้ "
            "ผลลัพธ์ของการดำเนินการจะถูกบันทึกลงในฐานข้อมูลความจำ (Memory Database) "
            "เพื่อให้ระบบสามารถดึงกลับมาใช้ประกอบการตัดสินใจในรอบถัดไป "
            "วงจรนี้ทำให้ AI มีความสามารถในการเรียนรู้จากประสบการณ์ "
            "และปรับปรุงการตอบสนองอย่างต่อเนื่อง ระบบรองรับการทำงานแบบ "
            "หลายเธรดพร้อมกันและมีกลไกป้องกันการวนซ้ำไม่สิ้นสุด"
        ),
        "summary": {
            "topic": "Intent Memory Loop",
            "key_points": [
                "วงจรปิด: รับคำสั่ง → ประมวลผล → จดจำ → ใช้ซ้ำ",
                "ลำดับ: Router → Guardian → Scribe → Executor → Memory",
                "บันทึกผลลัพธ์ลง Memory Database สำหรับรอบถัดไป",
                "รองรับหลายเธรด + ป้องกันการวนซ้ำ",
            ],
            "compression_ratio": 4.1,
            "original_tokens": 160,
            "compressed_tokens": 39,
        },
    },
    {
        "topic": "สถาปัตยกรรม HexaCore",
        "content": (
            "HexaCore เป็นสถาปัตยกรรมหลักของ Delentia OS ที่ประกอบด้วย 6 บทบาทหลัก "
            "ได้แก่ LIBRARIAN (ค้นหาและจัดการข้อมูล), LEAD_BUILDER (สร้างและวางแผนงาน), "
            "SPECIALIST (ผู้เชี่ยวชาญเฉพาะด้าน), HUMANIZER (แปลงข้อมูลให้มนุษย์เข้าใจ), "
            "ARCHITECT (สถาปนิกระบบที่มีอำนาจสูงสุด), OLLAMA_ADAPTER (เชื่อมต่อโมเดล AI). "
            "แต่ละบทบาทมีขอบเขตความรับผิดชอบที่ชัดเจนและทำงานร่วมกันผ่าน "
            "ระบบ RCT Control Plane ที่ควบคุมการไหลของข้อมูลและการตัดสินใจ "
            "สถาปัตยกรรมนี้ออกแบบมาให้รองรับการขยายตัวในอนาคต "
            "โดยสามารถเพิ่มบทบาทใหม่ได้โดยไม่กระทบกับระบบที่มีอยู่"
        ),
        "summary": {
            "topic": "HexaCore Architecture",
            "key_points": [
                "6 บทบาท: Librarian, Lead Builder, Specialist, Humanizer, Architect, Ollama Adapter",
                "ทำงานผ่าน RCT Control Plane",
                "ขอบเขตความรับผิดชอบชัดเจน",
                "ออกแบบให้ขยายตัวได้ (เพิ่มบทบาทใหม่ได้)",
            ],
            "compression_ratio": 3.3,
            "original_tokens": 130,
            "compressed_tokens": 39,
        },
    },
]


def _build_compression_pair(doc: dict, idx: int) -> dict:
    """Build a context compression training pair."""
    completion = json.dumps(doc["summary"], ensure_ascii=False, indent=None)
    return {
        "prompt": f"{SYSTEM_CONTEXT}\n\nCompress the following document:\n\n{doc['content']}",
        "completion": completion,
    }


def _gen_rag_filter_pair(idx: int) -> dict:
    """Generate a RAG result filtering pair (noise removal)."""
    relevant_docs = [
        f"[Doc {idx}] PDPA requires consent for personal data collection.",
        f"[Doc {idx+1}] FDIA scoring uses F = D^I × A formula.",
    ]
    noise_docs = [
        f"[Doc {idx+2}] The weather in Bangkok is 35°C today.",
        f"[Doc {idx+3}] Stock prices rose by 2.3% yesterday.",
        f"[Doc {idx+4}] A new restaurant opened in Sukhumvit.",
    ]

    all_docs = relevant_docs + noise_docs
    random.shuffle(all_docs)

    query = random.choice([
        "What are the requirements for data protection compliance?",
        "How does the AI governance scoring system work?",
        "ข้อกำหนดการปฏิบัติตาม PDPA มีอะไรบ้าง",
        "ระบบให้คะแนนการกำกับดูแล AI ทำงานอย่างไร",
    ])

    completion = json.dumps({
        "query": query,
        "relevant_results": relevant_docs,
        "filtered_noise": len(noise_docs),
        "total_retrieved": len(all_docs),
        "precision": round(len(relevant_docs) / len(all_docs), 3),
    }, ensure_ascii=False)

    return {
        "prompt": (
            f"{SYSTEM_CONTEXT}\n\n"
            f"Query: {query}\n\n"
            f"Retrieved documents:\n" + "\n".join(all_docs) + "\n\n"
            "Filter noise and return only relevant results."
        ),
        "completion": completion,
    }


def main():
    print("Delentia Scribe Dataset Generator (slm-jitna-scribe)")
    print("=" * 55)

    random.seed(42)
    pairs = []

    # 1. Context compression pairs (English)
    for i in range(40):
        doc = random.choice(LONG_DOCUMENTS)
        pairs.append(_build_compression_pair(doc, i))

    # 2. Context compression pairs (Thai)
    for i in range(30):
        doc = random.choice(LONG_DOCUMENTS_TH)
        pairs.append(_build_compression_pair(doc, i + 500))

    # 3. RAG filtering pairs
    for i in range(50):
        pairs.append(_gen_rag_filter_pair(i + 1000))

    # 4. Multi-document compression (combining 2-3 docs)
    for _ in range(30):
        docs = random.sample(LONG_DOCUMENTS, min(2, len(LONG_DOCUMENTS)))
        combined_content = "\n\n---\n\n".join(d["content"] for d in docs)
        combined_summary = {
            "topics": [d["summary"]["topic"] for d in docs],
            "key_points": [pt for d in docs for pt in d["summary"]["key_points"][:3]],
            "total_compression_ratio": round(
                sum(d["summary"]["compression_ratio"] for d in docs) / len(docs), 2
            ),
        }
        pairs.append({
            "prompt": f"{SYSTEM_CONTEXT}\n\nCompress these multiple documents:\n\n{combined_content}",
            "completion": json.dumps(combined_summary, ensure_ascii=False),
        })

    random.shuffle(pairs)

    print(f"Generated {len(pairs)} Scribe compression pairs")
    print("  - Single doc compression (EN): 40")
    print("  - Single doc compression (TH): 30")
    print("  - RAG filtering pairs:         50")
    print("  - Multi-doc compression:       30")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8") as f:
        for pair in pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")

    print(f"\nSaved to: {OUTPUT}")
    print(f"Total pairs: {len(pairs)}")


if __name__ == "__main__":
    main()
