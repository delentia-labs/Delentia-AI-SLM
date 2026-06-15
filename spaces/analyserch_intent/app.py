"""
Delentia OS — Analyserch Intent Simulator
Hugging Face Space: Delentia/delentia-analyserch-intent

This Space showcases Delentia's intent crystallization (ALGO-41), 
GIGO Protection, Mirror Mode interactive dialogue, and cross-disciplinary synthesis.
"""

import csv
import json
import os
import sys
import random
import time
import uuid
import math
import hashlib
from datetime import datetime, timezone
from pathlib import Path
import threading
import requests
import gradio as gr

# Ensure the current directory is in Python path for importing local modules
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Try to import real compiler
try:
    from rct_control_plane.intent_compiler import IntentCompiler
    _HAS_REAL_COMPILER = True
    print("[INFO] app.py: Successfully loaded real IntentCompiler.")
    print(f"[INFO] app.py: OPENAI_API_KEY present: {bool(os.environ.get('OPENAI_API_KEY'))}")
    print(f"[INFO] app.py: ANTHROPIC_API_KEY present: {bool(os.environ.get('ANTHROPIC_API_KEY'))}")
    print(f"[INFO] app.py: RCT_LLM_PROVIDER: {os.environ.get('RCT_LLM_PROVIDER', 'not set')}")
except Exception as e:
    _HAS_REAL_COMPILER = False
    print(f"[WARN] app.py: Failed to load real IntentCompiler ({e}). Using emulation fallback.")

# ── Telemetry Setup ────────────────────────────────────────────────────────────
TELEMETRY_FILE = Path("telemetry_log.csv")
TELEMETRY_HEADERS = [
    "timestamp", "session_id", "input_text", "entropy_score",
    "gigo_status", "keywords_count", "mirror_turns", "latency_ms"
]

def init_telemetry():
    if not TELEMETRY_FILE.exists():
        with open(TELEMETRY_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=TELEMETRY_HEADERS)
            writer.writeheader()

def _post_to_supabase_async(url: str, key: str, row: dict):
    try:
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        endpoint = f"{url.rstrip('/')}/rest/v1/analyserch_telemetry_logs"
        response = requests.post(endpoint, json=row, headers=headers, timeout=5)
        if response.status_code >= 400:
            print(f"[Telemetry] Supabase API rejected payload. Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"[Telemetry] Supabase connection failed: {e}")

def log_telemetry(row: dict):
    try:
        init_telemetry()
        with open(TELEMETRY_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=TELEMETRY_HEADERS)
            writer.writerow(row)
    except Exception:
        pass

    # Log to Supabase asynchronously if credentials are set
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("RCT_CORE_BRAIN_KEY")
    if supabase_url and supabase_key:
        try:
            thread = threading.Thread(
                target=_post_to_supabase_async,
                args=(supabase_url, supabase_key, row),
                daemon=True
            )
            thread.start()
        except Exception as e:
            print(f"[Telemetry] Failed to spawn logging thread: {e}")

# ── Entropy and GIGO Logic ─────────────────────────────────────────────────────
def calculate_shannon_entropy(text: str) -> float:
    """Calculate the Shannon Entropy of words in the text to identify GIGO."""
    if not text.strip():
        return 0.0
    words = text.lower().split()
    total_words = len(words)
    if total_words == 0:
        return 0.0
    
    # Count occurrences
    counts = {}
    for word in words:
        counts[word] = counts.get(word, 0) + 1
        
    # Calculate shannon entropy
    entropy = 0.0
    for count in counts.values():
        p = count / total_words
        entropy -= p * math.log2(p)
        
    return round(entropy, 4)

def check_gigo(text: str, entropy: float) -> tuple[str, str, str]:
    """Evaluates the input text against GIGO rules."""
    text_stripped = text.strip()
    if not text_stripped:
        return "EMPTY", "Input text is completely empty.", "rgba(107, 127, 163, 0.2)"
        
    if len(text_stripped) < 15:
        return "GIGO_WARNING", "Input query is too short for meaningful intent analysis.", "rgba(255, 140, 0, 0.25)"
        
    # Check if words are highly repetitive (indicating spam or low-effort test inputs)
    words = text_stripped.split()
    unique_ratio = len(set(words)) / len(words)
    if unique_ratio < 0.4 and len(words) > 5:
        return "GIGO_VIOLATION", "Low information density: highly repeated tokens detected.", "rgba(255, 59, 59, 0.25)"
        
    # Check for forbidden or toxic keywords (standard blocklist)
    forbidden = ["hack", "exploit", "bypass", "jailbreak", "override"]
    detected_forbidden = [fw for fw in forbidden if fw in text_stripped.lower()]
    if detected_forbidden:
        return "SECURITY_BLOCK", f"Security Boundary Violated: input contains blocked tokens: {', '.join(detected_forbidden)}.", "rgba(255, 59, 59, 0.3)"
        
    return "SAFE_CLEAR", "High information density. Safe constitutional query.", "rgba(0, 230, 118, 0.2)"

# ── Crystallizer (ALGO-41) Mock Database ───────────────────────────────────────
CONCEPT_DATABASE = {
    "sovereignty": {
        "definition": "อำนาจการควบคุมและครอบครองข้อมูลและโครงสร้างพื้นฐานอย่างสมบูรณ์แบบโดยไม่ต้องพึ่งพาระบบคลาวด์ภายนอก",
        "category": "Conceptual",
        "entropy": 0.96,
        "implications": [
            "ฐานข้อมูลแบบ Self-hosted (e.g. PostgreSQL, Redis บนเซิร์ฟเวอร์ส่วนตัว)",
            "การใช้งานโมเดลภาษาขนาดเล็ก (SLM) ภายในเครื่องโดยไม่มี API ส่งออกข้างนอก",
            "การคุ้มครองข้อมูลตามหลัก PDPA และ GDPR ระดับสูงสุด"
        ],
        "actions": [
            {"id": "setup_sovereignty", "label": "Setup local database cluster"},
            {"id": "restrict_networks", "label": "Configure firewalls & air-gapped zones"}
        ]
    },
    "realtime": {
        "definition": "ระบบการสื่อสารแบบสองทิศทางแบบทันทีทันใด (Instant bidirectional communication)",
        "category": "Technical",
        "entropy": 0.88,
        "implications": [
            "โปรโตคอล WebSockets หรือ Server-Sent Events (SSE)",
            "ระบบ Redis Pub/Sub สำหรับกระจายแพ็กเก็ตข้อมูล",
            "การประมวลผลผ่าน Edge node เพื่อลดเวลาตอบสนอง"
        ],
        "actions": [
            {"id": "setup_ws", "label": "Initialize WebSocket server connection"},
            {"id": "benchmark_latency", "label": "Run network response benchmarks"}
        ]
    },
    "blockchain": {
        "definition": "สถาปัตยกรรมการจัดเก็บข้อมูลแบบกระจายศูนย์ที่ป้องกันการย้อนกลับและการแก้ไขธุรกรรมย้อนหลัง",
        "category": "Domain",
        "entropy": 0.91,
        "implications": [
            "การเรียกใช้ Web3 SDK หรือ Smart Contract connectors",
            "การลงนามธุรกรรมแบบหลายลายเซ็น (Multi-signature signing)",
            "การเชื่อมระบบการเงินแบบไม่ผ่านตัวกลาง"
        ],
        "actions": [
            {"id": "deploy_connector", "label": "Deploy smart contract connector API"},
            {"id": "check_gas", "label": "Simulate transaction fee parameters"}
        ]
    },
    "payment": {
        "definition": "กลไกหรือกระบวนการโอนย้ายมูลค่าทางการเงินแบบอิเล็กทรอนิกส์ที่มีความมั่นคงปลอดภัยสูงสุด",
        "category": "Business",
        "entropy": 0.86,
        "implications": [
            "ความสอดคล้องตามมาตรฐานความปลอดภัย PCI-DSS",
            "ระบบลายเซ็นดิจิทัลและการทำธุรกรรมแบบเข้ารหัส",
            "การจำลองแผนงบประมาณราคาสูงสุดแบบเรียลไทม์"
        ],
        "actions": [
            {"id": "setup_payment_gateway", "label": "Integrate secure payment gateway API"},
            {"id": "audit_logs", "label": "Verify payment transaction ledger logs"}
        ]
    },
    "cache": {
        "definition": "การจัดเก็บข้อมูลชั่วคราวบนหน่วยความจำความเร็วสูง เพื่อหลีกเลี่ยงการประมวลผลซ้ำเชิงคำสั่ง",
        "category": "Technical",
        "entropy": 0.82,
        "implications": [
            "การใช้งานหน่วยความจำระดับคีย์ (In-memory database e.g., Redis, local dictionary)",
            "การนำกลับมาใช้ใหม่ด้วยความเร็วระดับ <50ms (Warm Recall)",
            "การลดต้นทุน Token ในบริบท LLM ผ่านกลไก TOON"
        ],
        "actions": [
            {"id": "setup_cache", "label": "Configure local caching engine"},
            {"id": "set_ttl", "label": "Define Cache Time-To-Live limits"}
        ]
    }
}

def extract_keywords(text: str) -> list:
    """Extracts concepts from database that appear in text (or mock fallback if none)."""
    text_lower = text.lower()
    extracted = []
    
    for kw, data in CONCEPT_DATABASE.items():
        if kw in text_lower:
            extracted.append((kw, data))
            
    # Fallback to general terms if none found
    if not extracted and len(text.strip()) > 15:
        # Create a dynamic mock keyword based on the first word
        words = text.split()
        first_word = words[0].rstrip(",.?!:;-").lower()
        extracted.append((first_word, {
            "definition": f"แนวคิดเชิงเฉพาะเกี่ยวกับ '{first_word}' ที่ถูกวิเคราะห์ผ่านระบบ Delentia Analyserch",
            "category": "Domain",
            "entropy": round(random.uniform(0.75, 0.85), 2),
            "implications": [
                f"ความจำเป็นในการประยุกต์ใช้โมดูลอัจฉริยะรองรับ {first_word}",
                "การประเมินทราฟฟิกและปริมาณการเรียกใช้งานผ่าน Gateway",
                "สถิติพารามิเตอร์ MEE สำหรับการเติบโตของคุณภาพ"
            ],
            "actions": [
                {"id": f"explore_{first_word}", "label": f"Explore {first_word} documentation"},
                {"id": f"integrate_{first_word}", "label": f"Integrate {first_word} API"}
            ]
        }))
        
    return extracted

def build_keyword_cards_html(extracted: list) -> str:
    if not extracted:
        return "<div style='color:#6b7fa3;padding:15px;background:#0d1220;border-radius:8px;border:1px solid #1e2d45;text-align:center;'>No Golden Keywords crystallized from this text.</div>"
        
    cards = []
    for kw, data in extracted:
        category_color = {
            "Conceptual": "#a78bfa",
            "Technical": "#00ffcc",
            "Business": "#ff8c00",
            "Domain": "#ffd700"
        }.get(data["category"], "#3b9eff")
        
        implications_html = "".join([f"<li style='margin-bottom:6px;'>• {imp}</li>" for imp in data["implications"]])
        buttons_html = "".join([f"<button class='action-btn' style='background:rgba(59, 158, 255, 0.15); border:1px solid #3b9eff; color:#3b9eff; padding:4px 8px; border-radius:4px; font-size:11px; margin-right:8px; cursor:pointer;'>{act['label']}</button>" for act in data["actions"]])
        
        card = f"""
        <div style='background:rgba(13, 18, 32, 0.85); border:1px solid #1e2d45; border-radius:10px; padding:15px; margin-bottom:15px; box-shadow:0 4px 15px rgba(0,0,0,0.25); border-left: 4px solid {category_color};'>
            <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;'>
                <span style='font-size:16px; font-weight:bold; color:#ffd700;'>💎 {kw.upper()}</span>
                <span style='background:rgba(30, 45, 69, 0.6); border:1px solid {category_color}; color:{category_color}; padding:2px 8px; border-radius:12px; font-size:10px; font-weight:600;'>{data["category"]}</span>
            </div>
            <div style='font-size:13px; color:#c9d9f0; line-height:1.4; margin-bottom:10px;'>
                {data["definition"]}
            </div>
            <div style='font-size:11px; text-transform:uppercase; letter-spacing:1px; color:#6b7fa3; font-weight:bold; margin-bottom:6px;'>
                Tech Stack Implications & Architecture:
            </div>
            <ul style='font-size:12px; color:#a8b9d3; list-style-type:none; padding-left:0; margin:0 0 12px 0;'>
                {implications_html}
            </ul>
            <div style='display:flex; flex-wrap:wrap; gap:6px;'>
                {buttons_html}
            </div>
        </div>
        """
        cards.append(card)
        
    return "".join(cards)

# ── Mirror Mode Refinement Dialog Simulation ──────────────────────────────────
def generate_mirror_dialog(intent_text: str, extracted: list) -> str:
    """Simulates a highly detailed PROPOSE -> COUNTER -> REFINE dialogue."""
    if not intent_text.strip():
        return "<div style='color:#6b7fa3;padding:15px;background:#0d1220;border-radius:8px;border:1px solid #1e2d45;text-align:center;'>Awaiting inputs to run Mirror Mode.</div>"
        
    keywords = [kw for kw, _ in extracted]
    kw_str = ", ".join(keywords) if keywords else "general intent architecture"
    
    # Propose Node
    propose_html = f"""
    <div style='display:flex; margin-bottom:14px; align-items:flex-start;'>
        <div style='background:#ff8c00; color:#fff; width:36px; height:36px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:bold; margin-right:12px; flex-shrink:0;'>P</div>
        <div style='background:rgba(255, 140, 0, 0.08); border:1px solid rgba(255, 140, 0, 0.25); padding:12px; border-radius:0 12px 12px 12px; color:#c9d9f0; font-size:13px; line-height:1.4;'>
            <b style='color:#ff8c00; font-size:12px;'>PROPOSER AGENT (LoRA-Adapt)</b><br>
            I propose deploying a distributed microservice strategy to handle the query targeting <b>[{kw_str}]</b>. 
            We should construct an active endpoint on the <code>gateway-api</code>, index metadata vectors via FAISS 
            in <code>vector-search</code>, and run a serverless Redis cluster to cache the transactions. Estimated latency: ~45ms.
        </div>
    </div>
    """
    
    # Counter Node
    counter_html = f"""
    <div style='display:flex; margin-bottom:14px; align-items:flex-start;'>
        <div style='background:#ff3b3b; color:#fff; width:36px; height:36px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:bold; margin-right:12px; flex-shrink:0;'>C</div>
        <div style='background:rgba(255, 59, 59, 0.08); border:1px solid rgba(255, 59, 59, 0.25); padding:12px; border-radius:0 12px 12px 12px; color:#c9d9f0; font-size:13px; line-height:1.4;'>
            <b style='color:#ff3b3b; font-size:12px;'>COUNTER AGENT (Consensus Checker)</b><br>
            Objection! Running a remote serverless Redis cluster violates the <b>Sovereignty</b> clause of Delentia-OS. 
            Also, a remote connection adds network overhead, which pushes cost above the Pro-tier constraint. 
            We must restrict database VRAM footprint to under <b>6.84GB</b> and keep execution strictly local.
        </div>
    </div>
    """
    
    # Refine Node
    refine_html = f"""
    <div style='display:flex; margin-bottom:6px; align-items:flex-start;'>
        <div style='background:#00ffcc; color:#0d1220; width:36px; height:36px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:bold; margin-right:12px; flex-shrink:0;'>R</div>
        <div style='background:rgba(0, 255, 204, 0.08); border:1px solid rgba(0, 255, 204, 0.25); padding:12px; border-radius:0 12px 12px 12px; color:#c9d9f0; font-size:13px; line-height:1.4;'>
            <b style='color:#00ffcc; font-size:12px;'>REFINER AGENT (Agreement Reached)</b><br>
            Consensus achieved. Refined execution plan: swap serverless Redis for a self-hosted PostgreSQL cluster running locally. 
            All vector comparisons will run flat in memory to optimize warm recall times (<20ms). 
            TOON payload compression will be set to active, minimizing attention window size and keeping cost under budget limits.
        </div>
    </div>
    """
    
    return f"<div style='display:flex; flex-direction:column;'>{propose_html}{counter_html}{refine_html}</div>"

# ── Cross-Disciplinary Synthesis visualizer ────────────────────────────────────
def build_synthesis_graph_html(extracted: list) -> str:
    """Builds an HTML visual node graph showing cross-disciplinary connections."""
    if not extracted:
        return "<div style='color:#6b7fa3;padding:15px;background:#0d1220;border-radius:8px;border:1px solid #1e2d45;text-align:center;'>Awaiting inputs...</div>"
        
    keywords = [kw for kw, _ in extracted]
    
    nodes_html = []
    edges_html = []
    
    # Root Node
    nodes_html.append("<div class='syn-node root-node'>USER INTENT</div>")
    
    for kw in keywords:
        nodes_html.append(f"<div class='syn-node key-node'>{kw.upper()}</div>")
        edges_html.append(f"<div class='syn-edge'>USER INTENT ➔ {kw.upper()}</div>")
        
        # Add a domain link
        if kw == "sovereignty":
            nodes_html.append("<div class='syn-node tech-node'>LOCAL AI (Ollama)</div>")
            edges_html.append("SOVEREIGNTY ➔ LOCAL AI (Ollama)")
        elif kw == "realtime":
            nodes_html.append("<div class='syn-node tech-node'>WEBSOCKETS</div>")
            edges_html.append("REALTIME ➔ WEBSOCKETS")
        elif kw == "blockchain":
            nodes_html.append("<div class='syn-node tech-node'>SMART CONTRACT</div>")
            edges_html.append("BLOCKCHAIN ➔ SMART CONTRACT")
        elif kw == "payment":
            nodes_html.append("<div class='syn-node tech-node'>PCI-DSS COMPLIANT</div>")
            edges_html.append("PAYMENT ➔ PCI-DSS COMPLIANT")
        elif kw == "cache":
            nodes_html.append("<div class='syn-node tech-node'>TOON SERIALIZER</div>")
            edges_html.append("CACHE ➔ TOON SERIALIZER")
            
    nodes_str = "".join(nodes_html)
    edges_str = "".join([f"<div style='font-size:12px; color:#ff8c00; margin-bottom:4px;'>🔗 {edge}</div>" for edge in edges_html])
    
    return f"""
    <div style='background:rgba(13, 18, 32, 0.7); border:1px solid #1e2d45; border-radius:10px; padding:15px;'>
        <div style='display:flex; flex-wrap:wrap; gap:10px; margin-bottom:12px;'>
            {nodes_str}
        </div>
        <div style='border-top:1px solid rgba(30, 45, 69, 0.6); padding-top:10px;'>
            <div style='font-size:11px; text-transform:uppercase; letter-spacing:1px; color:#6b7fa3; font-weight:bold; margin-bottom:6px;'>
                Cross-Disciplinary Synthesizer Edges:
            </div>
            {edges_str}
        </div>
    </div>
    """

# ── Main Pipeline Coordinator ──────────────────────────────────────────────────
def run_analyserch_pipeline(intent_text: str):
    if not intent_text.strip():
        return (
            "<div style='text-align:center;padding:14px;color:#6b7fa3;'>Awaiting input...</div>",
            "0.00",
            "Awaiting input...",
            "Awaiting input...",
            "Awaiting input...",
            "Awaiting input..."
        )
        
    start_time = time.perf_counter()
    
    # Calculate Shannon Entropy
    entropy = calculate_shannon_entropy(intent_text)
    
    # Assess GIGO
    gigo_status, gigo_desc, badge_bg = check_gigo(intent_text, entropy)
    
    badge_color = "#ff3b3b" if "VIOLATION" in gigo_status or "SECURITY" in gigo_status else ("#ff8c00" if "WARNING" in gigo_status else "#00e676")
    
    gigo_badge_html = f"""
    <div style='background:{badge_bg}; border:1px solid {badge_color}; color:{badge_color}; border-radius:8px; padding:14px; text-align:center; font-weight:bold;'>
        <span style='font-size:16px;'>📊 Status: {gigo_status}</span><br>
        <span style='font-size:12px; font-weight:normal; color:#c9d9f0;'>{gigo_desc}</span>
    </div>
    """
    
    # If security block or GIGO violation, stop processing and return early
    if gigo_status in ["GIGO_VIOLATION", "SECURITY_BLOCK"]:
        latency_ms = (time.perf_counter() - start_time) * 1000
        
        log_telemetry({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": str(uuid.uuid4())[:8],
            "input_text": intent_text[:200],
            "entropy_score": entropy,
            "gigo_status": gigo_status,
            "keywords_count": 0,
            "mirror_turns": 0,
            "latency_ms": round(latency_ms, 2)
        })
        
        return (
            gigo_badge_html,
            f"{entropy:.2f}",
            "<div style='color:#ff3b3b;padding:15px;background:#0d1220;border-radius:8px;border:1px solid #1e2d45;text-align:center;'>Crystallization halted due to GIGO status.</div>",
            "<div style='color:#ff3b3b;padding:15px;background:#0d1220;border-radius:8px;border:1px solid #1e2d45;text-align:center;'>Dialogue simulation halted.</div>",
            "<div style='color:#ff3b3b;padding:15px;background:#0d1220;border-radius:8px;border:1px solid #1e2d45;text-align:center;'>Synthesis graph halted.</div>",
            f"{latency_ms:.2f} ms"
        )
        
    # Extract keywords (Crystallizer)
    extracted = extract_keywords(intent_text)
    
    # Generate compiler cards & dynamic simulations if compiler is active
    if _HAS_REAL_COMPILER:
        try:
            compiler = IntentCompiler()
            comp_res = compiler.compile(intent_text, user_id="usr_whale", user_tier="PRO")
            if comp_res.success and comp_res.intent:
                intent = comp_res.intent
                intent_type = intent.intent_type.value if hasattr(intent.intent_type, 'value') else str(intent.intent_type)
                scope_type = intent.scope.scope_type.value if hasattr(intent.scope.scope_type, 'value') else str(intent.scope.scope_type)
                target = intent.scope.target
                priority = intent.priority.value if hasattr(intent.priority, 'value') else str(intent.priority)
                risk = intent.risk_profile.value if hasattr(intent.risk_profile, 'value') else str(intent.risk_profile)
                cost = f"${intent.budget.max_cost_usd:.2f}" if intent.budget and intent.budget.max_cost_usd else "N/A"
                provider = compiler.llm_provider.upper()
                model_name = "gpt-4o-mini (OpenAI API)" if provider == "OPENAI" else ("claude-3-haiku (Anthropic API)" if provider == "ANTHROPIC" else "Regex Rule-based Classifier Model")
                
                # Active model indicator card
                model_badge_color = "#38bdf8" if provider == "REGEX" else "#a78bfa"
                metadata_card_html = f"""
                <div style='background:rgba(13, 18, 32, 0.9); border:1px solid #1e2d45; border-radius:10px; padding:15px; margin-bottom:15px; border-left: 4px solid {model_badge_color};'>
                    <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;'>
                        <span style='font-size:15px; font-weight:bold; color:#ffffff;'>🤖 Active Classifier Model</span>
                        <span style='background:rgba(56,189,248,0.15); border:1px solid {model_badge_color}; color:{model_badge_color}; padding:2px 8px; border-radius:12px; font-size:10px; font-weight:600;'>{provider}</span>
                    </div>
                    <div style='font-size:13px; color:#c9d9f0; line-height:1.4; margin-bottom:10px; font-family:"JetBrains Mono", monospace;'>
                        Engine: {model_name}
                    </div>
                    <div style='font-size:11px; text-transform:uppercase; letter-spacing:1px; color:#6b7fa3; font-weight:bold; margin-bottom:8px;'>
                        Compiler Metadata Output:
                    </div>
                    <div style='font-size:12px; color:#a8b9d3; line-height:1.5; font-family:"JetBrains Mono", monospace; background:rgba(0,0,0,0.3); padding:10px; border-radius:6px; border:1px solid rgba(255,255,255,0.03);'>
                        • Intent Type: <span style='color:#ffd700; font-weight:bold;'>{intent_type}</span><br>
                        • Scope Type: {scope_type}<br>
                        • Target: <span style='color:#00ffcc;'>{target}</span><br>
                        • Priority: {priority}<br>
                        • Risk Profile: {risk}<br>
                        • Cost Budget: {cost}<br>
                        • Validation: <span style='color:#00e676;'>VALID</span>
                    </div>
                </div>
                """
                
                keywords_cards_html = metadata_card_html + build_keyword_cards_html(extracted)
                
                # Dynamic Propose/Counter/Refine dialog
                propose_html = f"""
                <div style='display:flex; margin-bottom:14px; align-items:flex-start;'>
                    <div style='background:#ff8c00; color:#fff; width:36px; height:36px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:bold; margin-right:12px; flex-shrink:0;'>P</div>
                    <div style='background:rgba(255, 140, 0, 0.08); border:1px solid rgba(255, 140, 0, 0.25); padding:12px; border-radius:0 12px 12px 12px; color:#c9d9f0; font-size:13px; line-height:1.4;'>
                        <b style='color:#ff8c00; font-size:12px;'>PROPOSER AGENT (LoRA-Adapt)</b><br>
                        I propose compiling and executing a <b>[{intent_type}]</b> plan. 
                        We should target scope <code>{scope_type}</code> at target <b>[{target}]</b>, and run a local database configuration. Estimated latency: ~30ms.
                    </div>
                </div>
                """
                
                counter_html = f"""
                <div style='display:flex; margin-bottom:14px; align-items:flex-start;'>
                    <div style='background:#ff3b3b; color:#fff; width:36px; height:36px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:bold; margin-right:12px; flex-shrink:0;'>C</div>
                    <div style='background:rgba(255, 59, 59, 0.08); border:1px solid rgba(255, 59, 59, 0.25); padding:12px; border-radius:0 12px 12px 12px; color:#c9d9f0; font-size:13px; line-height:1.4;'>
                        <b style='color:#ff3b3b; font-size:12px;'>COUNTER AGENT (Consensus Checker)</b><br>
                        Objection! The compiled risk profile is <b>[{risk}]</b>. 
                        We must keep execution strictly local to handle target <code>{target}</code> under strict budget constraints.
                    </div>
                </div>
                """
                
                refine_html = f"""
                <div style='display:flex; margin-bottom:6px; align-items:flex-start;'>
                    <div style='background:#00ffcc; color:#0d1220; width:36px; height:36px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:bold; margin-right:12px; flex-shrink:0;'>R</div>
                    <div style='background:rgba(0, 255, 204, 0.08); border:1px solid rgba(0, 255, 204, 0.25); padding:12px; border-radius:0 12px 12px 12px; color:#c9d9f0; font-size:13px; line-height:1.4;'>
                        <b style='color:#00ffcc; font-size:12px;'>REFINER AGENT (Agreement Reached)</b><br>
                        Consensus achieved. Refined execution plan for <b>{intent_type}</b>: run vector comparisons in local memory. 
                        All operations for target <b>{target}</b> will be compiled with <b>{priority}</b> priority. 
                        TOON payload compression active to minimize costs within the <b>{cost}</b> budget limit.
                    </div>
                </div>
                """
                
                mirror_dialog_html = f"<div style='display:flex; flex-direction:column;'>{propose_html}{counter_html}{refine_html}</div>"
                
                # Dynamic Synthesis graph nodes
                nodes_html = [
                    "<div class='syn-node root-node'>USER INTENT</div>",
                    f"<div class='syn-node key-node'>{intent_type}</div>",
                    f"<div class='syn-node tech-node'>{scope_type}:{target}</div>",
                    f"<div class='syn-node key-node'>{priority}</div>",
                    f"<div class='syn-node tech-node'>MODEL: {provider}</div>"
                ]
                edges_html = [
                    f"USER INTENT ➔ {intent_type}",
                    f"{intent_type} ➔ {scope_type}:{target}",
                    f"{scope_type}:{target} ➔ {priority}",
                    f"{priority} ➔ MODEL: {provider}"
                ]
                
                synthesis_map_html = f"""
                <div style='background:rgba(13, 18, 32, 0.7); border:1px solid #1e2d45; border-radius:10px; padding:15px;'>
                    <div style='display:flex; flex-wrap:wrap; gap:10px; margin-bottom:12px;'>
                        {"".join(nodes_html)}
                    </div>
                    <div style='border-top:1px solid rgba(30, 45, 69, 0.6); padding-top:10px;'>
                        <div style='font-size:11px; text-transform:uppercase; letter-spacing:1px; color:#6b7fa3; font-weight:bold; margin-bottom:6px;'>
                            Cross-Disciplinary Synthesizer Edges:
                        </div>
                        {"".join([f"<div style='font-size:12px; color:#ff8c00; margin-bottom:4px;'>🔗 {edge}</div>" for edge in edges_html])}
                    </div>
                </div>
                """
            else:
                keywords_cards_html = build_keyword_cards_html(extracted)
                mirror_dialog_html = generate_mirror_dialog(intent_text, extracted)
                synthesis_map_html = build_synthesis_graph_html(extracted)
        except Exception as e:
            print(f"[ERROR] Failed to run real compile: {e}")
            keywords_cards_html = build_keyword_cards_html(extracted)
            mirror_dialog_html = generate_mirror_dialog(intent_text, extracted)
            synthesis_map_html = build_synthesis_graph_html(extracted)
    else:
        keywords_cards_html = build_keyword_cards_html(extracted)
        mirror_dialog_html = generate_mirror_dialog(intent_text, extracted)
        synthesis_map_html = build_synthesis_graph_html(extracted)
        
    latency_ms = (time.perf_counter() - start_time) * 1000
    
    # Log to Telemetry CSV
    log_telemetry({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": str(uuid.uuid4())[:8],
        "input_text": intent_text[:200],
        "entropy_score": entropy,
        "gigo_status": gigo_status,
        "keywords_count": len(extracted),
        "mirror_turns": 3,
        "latency_ms": round(latency_ms, 2)
    })
    
    return (
        gigo_badge_html,
        f"{entropy:.2f}",
        keywords_cards_html,
        mirror_dialog_html,
        synthesis_map_html,
        f"{latency_ms:.2f} ms"
    )

# ── CSS Premium Dark Theme ─────────────────────────────────────────────────────
custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
    --bg-deep: #080c14;
    --bg-card: #0d1220;
    --bg-border: #1e2d45;
    --accent-blue: #3b9eff;
    --accent-green: #00e676;
    --accent-red: #ff3b3b;
    --accent-gold: #ffd700;
    --text-main: #c9d9f0;
    --text-muted: #6b7fa3;
}

body, .gradio-container {
    background-color: var(--bg-deep) !important;
    color: var(--text-main) !important;
    font-family: 'Outfit', sans-serif !important;
}

.gradio-container {
    max-width: 1200px !important;
    margin: 0 auto !important;
}

h1, h2, h3, h4 {
    color: var(--accent-blue) !important;
    font-family: 'Outfit', sans-serif !important;
    letter-spacing: 0.03em;
}

.gr-button-primary {
    background: linear-gradient(135deg, #a78bfa, #ff8c00) !important;
    border: 1px solid #a78bfa !important;
    color: #fff !important;
    font-weight: 700 !important;
    font-family: 'Outfit', sans-serif !important;
    border-radius: 8px !important;
    box-shadow: 0 0 12px rgba(167, 139, 250, 0.3) !important;
    transition: all 0.2s ease !important;
}

.gr-button-primary:hover {
    box-shadow: 0 0 20px rgba(167, 139, 250, 0.6) !important;
    transform: translateY(-1px) !important;
}

textarea, .gr-textbox, .gr-code {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--bg-border) !important;
    color: var(--text-main) !important;
    font-family: 'JetBrains Mono', monospace !important;
    border-radius: 8px !important;
}

.gr-panel, .gr-box {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--bg-border) !important;
    border-radius: 12px !important;
}

label {
    color: var(--accent-blue) !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    letter-spacing: 0.04em !important;
}

.header-glow {
    text-align: center;
    padding: 28px 20px 24px;
    background: linear-gradient(180deg, rgba(167,139,250,0.06) 0%, transparent 100%);
    border-bottom: 1px solid var(--bg-border);
    margin-bottom: 20px;
}

.ascii-logo {
    font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace !important;
    font-size: 10px !important;
    line-height: 1.25 !important;
    letter-spacing: 0px !important;
    margin: 0 auto 12px !important;
    background: linear-gradient(135deg, #a78bfa 0%, #ff8c00 50%, #00ffcc 100%);
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    display: inline-block !important;
    font-weight: bold !important;
    white-space: pre !important;
    text-align: left !important;
}

.syn-node {
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: bold;
    border: 1px solid;
}
.root-node {
    background: rgba(59, 158, 255, 0.15);
    border-color: #3b9eff;
    color: #3b9eff;
}
.key-node {
    background: rgba(255, 215, 0, 0.15);
    border-color: #ffd700;
    color: #ffd700;
}
.tech-node {
    background: rgba(0, 255, 204, 0.15);
    border-color: #00ffcc;
    color: #00ffcc;
}
"""

# ── Gradio Blocks ──────────────────────────────────────────────────────────────
with gr.Blocks(css=custom_css, title="Delentia OS — Analyserch Intent Simulator") as demo:
    
    # ── Header ──────────────────────────────────────────────────────────────────
    gr.HTML("""
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap">
    <div class='header-glow'>
      <div style="display: flex; justify-content: center; align-items: center; padding: 10px 0; margin-bottom: 15px;">
        <svg viewBox="0 0 500 80" style="width: 100%; max-width: 500px; height: auto; background: transparent; overflow: visible; display: block; margin: 0 auto;">
          <defs>
            <pattern id="pixel-grid" width="10" height="10" patternUnits="userSpaceOnUse">
              <rect width="10" height="10" fill="none" />
              <circle cx="5" cy="5" r="0.7" fill="#38bdf8" fill-opacity="0.12" />
            </pattern>
            <linearGradient id="cyber-grad-purple" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stop-color="#38bdf8" />
              <stop offset="50%" stop-color="#8b5cf6" />
              <stop offset="100%" stop-color="#ec4899" />
            </linearGradient>
            <filter id="glow-purple" x="-10%" y="-10%" width="120%" height="120%">
              <feGaussianBlur stdDeviation="0.8" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>
          <rect x="0" y="0" width="500" height="80" fill="url(#pixel-grid)" rx="6" />
          <rect x="2" y="2" width="496" height="76" fill="none" stroke="url(#cyber-grad-purple)" stroke-width="1" stroke-opacity="0.1" rx="6" />
          <path d="M 25 15 L 10 15 L 10 65 L 25 65" fill="none" stroke="#38bdf8" stroke-width="2.5" />
          <path d="M 475 15 L 490 15 L 490 65 L 475 65" fill="none" stroke="#ec4899" stroke-width="2.5" />
          <line x1="30" y1="15" x2="470" y2="15" stroke="url(#cyber-grad-purple)" stroke-width="1.5" stroke-opacity="0.4" />
          <line x1="30" y1="65" x2="470" y2="65" stroke="url(#cyber-grad-purple)" stroke-width="1.5" stroke-opacity="0.4" />
          <text x="50%" y="48" font-family="'Outfit', sans-serif" font-size="24" font-weight="900" fill="url(#cyber-grad-purple)" text-anchor="middle" letter-spacing="5" filter="url(#glow-purple)">
            DELENTIA ANALYSEARCH
          </text>
        </svg>
      </div>
      <h3 style='font-size:15px;font-weight:400;color:#a8b9d3;margin:6px 0 0;letter-spacing:0.5px;text-align:center;'>
        Intent Crystallizer Engine · GIGO Validation · Mirror Mode Refinement Dialog
      </h3>
    </div>
    """)
    
    gr.Markdown(
        "ป้อนคำสั่งหรือเจตนาวิจัย (Fuzzy / Complex Intent) เพื่อเริ่มการค้นหาคีย์เวิร์ดวิเคราะห์ความเข้าใจ "
        "โดยระบบจะคำนวณเอ็นโทรปีตรวจจับสภาวะ GIGO, ตกผลึกคำหลักทองคำ (Crystallizer) "
        "และนำเข้าสู่ระบบโต้ตอบขัดเกลาเจตจำนง (Mirror Mode Dialog PROPOSE ➔ COUNTER ➔ REFINE)"
    )
    
    # ── Input Row ────────────────────────────────────────────────────────────────
    with gr.Row():
        with gr.Column(scale=4):
            intent_input = gr.Textbox(
                label="🎯 FUZZY QUERY INPUT — ป้อนคำถามหรือแผนงานวิจัยที่ต้องการวิเคราะห์",
                placeholder="e.g. Implement a payment blockchain connector with cache support but ensure complete sovereignty.",
                lines=3,
                elem_id="intent_input"
            )
        with gr.Column(scale=1, min_width=140):
            run_btn = gr.Button("🔍 RUN ANALYSERCH", variant="primary", elem_id="run_btn")
            latency_out = gr.Label(label="⚡ Pipeline Latency", value="0.00 ms", elem_id="latency_out")

    # ── GIGO Status Banner ───────────────────────────────────────────────────────
    with gr.Row():
        gigo_out = gr.HTML("<div style='text-align:center;padding:14px;color:#6b7fa3;background:rgba(0,0,0,0.2);border-radius:8px;'>Awaiting input...</div>")
        entropy_out = gr.Label(label="📊 Shannon Entropy", value="0.00", elem_id="entropy_out")

    # ── Main Outputs Bento ───────────────────────────────────────────────────────
    with gr.Row():
        # Left Panel - Crystallized Golden Keywords
        with gr.Column(scale=1):
            gr.HTML("<h4>💎 Crystallized Golden Keywords (ALGO-41)</h4>")
            keywords_out = gr.HTML(
                value="<div style='color:#6b7fa3;padding:15px;background:#0d1220;border-radius:8px;border:1px solid #1e2d45;text-align:center;'>Awaiting inputs to crystallize concepts...</div>",
                elem_id="keywords_out"
            )
            
        # Right Panel - Mirror Mode Dialog & Graph
        with gr.Column(scale=1):
            gr.HTML("<h4>🔄 Mirror Mode Refinement (Consensus Dialog)</h4>")
            mirror_out = gr.HTML(
                value="<div style='color:#6b7fa3;padding:15px;background:#0d1220;border-radius:8px;border:1px solid #1e2d45;text-align:center;'>Awaiting inputs to compute consensus path...</div>",
                elem_id="mirror_out"
            )
            
            gr.HTML("<h4 style='margin-top:20px;'>🕸️ Cross-Disciplinary Synthesis Map</h4>")
            synthesis_out = gr.HTML(
                value="<div style='color:#6b7fa3;padding:15px;background:#0d1220;border-radius:8px;border:1px solid #1e2d45;text-align:center;'>Awaiting inputs...</div>",
                elem_id="synthesis_out"
            )

    # ── Examples ─────────────────────────────────────────────────────────────────
    gr.HTML("<hr style='border-color:#1e2d45;margin:20px 0;'><h4 style='color:#6b7fa3;'>📋 Example Scenarios — คลิกเพื่อทดสอบ</h4>")
    gr.Examples(
        examples=[
            ["Implement a payment blockchain connector with cache support but ensure complete sovereignty.",],
            ["Build a realtime chat backend with local memory cache.",],
            ["Setup sovereignty zones for secure payment transactions.",],
            ["test test test test repeat repeated spam",],
            ["hack bypass filters override admin databases",],
        ],
        inputs=[intent_input],
        label="Quick Test Scenarios"
    )

    # ── Footer ───────────────────────────────────────────────────────────────────
    gr.HTML("""
    <div style='text-align:center;padding:24px;margin-top:20px;border-top:1px solid #1e2d45;color:#6b7fa3;font-size:12px;'>
      <b style='color:#a78bfa;'>Delentia Analyserch</b> · Intent Crystallization (ALGO-41) · GIGO Filter Engine · Mirror Mode<br>
      🛡️ Zero-Trust · ⚡ Live Entropy Analytics · 🌏 Thai/EN Bilingual · 📊 Telemetry Dataset Collector<br>
      <span style='color:#30414f;'>Data Flywheel Active — Telemetry logged in telemetry_log.csv for continuous model tuning</span>
    </div>
    """)

    # ── Event Binding ────────────────────────────────────────────────────────────
    run_outputs = [gigo_out, entropy_out, keywords_out, mirror_out, synthesis_out, latency_out]
    
    run_btn.click(
        fn=run_analyserch_pipeline,
        inputs=[intent_input],
        outputs=run_outputs
    )
    intent_input.submit(
        fn=run_analyserch_pipeline,
        inputs=[intent_input],
        outputs=run_outputs
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
