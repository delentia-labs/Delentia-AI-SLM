"""
Delentia OS — Analyserch Intent Simulator (v2.0)
Hugging Face Space: Delentia/delentia-analyserch-intent

Architecture v2.0 (Delentia OS Native):
  User Input
    → FDIA Gate (constitutional validation)
    → Memory Layer (warm recall < 50ms)
    → AnalysearchCoreEngine (ALGO-41/05/26/Mirror Mode) ← PRIMARY ENGINE
    → EscalationRouter (external LLM only when confidence < 0.50)
    → DB Commit (Supabase async)
    → UI Result

No external LLMs required for standard operation.
External LLMs (via OpenRouter) used ONLY as escalation layer.
"""

import csv
import json
import os
import sys
import time
import uuid
import math
import threading
from datetime import datetime, timezone
from pathlib import Path
import requests
import gradio as gr

# ── Path Setup ─────────────────────────────────────────────────────────────────
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# ── Load Delentia OS Native Engine ────────────────────────────────────────────
try:
    from delentia_engine import DelentiaEngine, EscalationLevel, GIGOStatus
    _DELENTIA_ENGINE = DelentiaEngine()
    _ENGINE_READY = True
    print("[INFO] Delentia OS Native Engine loaded successfully.")
    print("[INFO]    FDIA Gate: ACTIVE")
    print("[INFO]    Memory Layer: ACTIVE (max 500 entries)")
    print("[INFO]    Core Engine: ALGO-41/05/26 ACTIVE")
    print("[INFO]    Escalation Router: ACTIVE")
    print("[INFO]    OpenRouter API:", 'CONFIGURED' if os.environ.get('RCT_CORE_BRAIN_KEY') or os.environ.get('OPENROUTER_API_KEY') else 'NOT SET (native only)')
except Exception as e:
    _DELENTIA_ENGINE = None
    _ENGINE_READY = False
    print(f"[WARN] Delentia OS Engine failed to load: {e}")
    print("[WARN]    Falling back to legacy mode.")

# ── Legacy Fallback: IntentCompiler ────────────────────────────────────────────
_HAS_LEGACY_COMPILER = False
try:
    from rct_control_plane.intent_compiler import IntentCompiler
    _HAS_LEGACY_COMPILER = True
    print("[INFO] Legacy IntentCompiler available as fallback.")
except Exception:
    pass

# ── Telemetry ──────────────────────────────────────────────────────────────────
TELEMETRY_FILE = Path("telemetry_log.csv")
TELEMETRY_HEADERS = [
    "timestamp", "session_id", "input_text", "entropy_score",
    "gigo_status", "keywords_count", "mirror_turns", "latency_ms",
    "confidence", "escalation_level", "cache_hit", "engine_version"
]

def _init_telemetry():
    if not TELEMETRY_FILE.exists():
        with open(TELEMETRY_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=TELEMETRY_HEADERS)
            writer.writeheader()

def _post_supabase_async(row: dict):
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("RCT_CORE_BRAIN_KEY") or os.environ.get("SUPABASE_KEY")
    if not supabase_url or not supabase_key:
        return
    def _post():
        try:
            headers = {
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal",
            }
            endpoint = f"{supabase_url.rstrip('/')}/rest/v1/analyserch_telemetry_logs"
            # Filter to only standard telemetry fields
            telemetry_row = {k: row.get(k, "") for k in TELEMETRY_HEADERS}
            requests.post(endpoint, json=telemetry_row, headers=headers, timeout=5)
        except Exception as ex:
            print(f"[Telemetry] Supabase failed (non-critical): {ex}")
    threading.Thread(target=_post, daemon=True).start()

def log_telemetry(row: dict):
    try:
        _init_telemetry()
        with open(TELEMETRY_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=TELEMETRY_HEADERS)
            # Fill missing fields with empty string
            complete_row = {k: row.get(k, "") for k in TELEMETRY_HEADERS}
            writer.writerow(complete_row)
    except Exception:
        pass
    _post_supabase_async(row)

# ─────────────────────────────────────────────────────────────────────────────
# UI HTML Builders
# ─────────────────────────────────────────────────────────────────────────────

def _build_engine_status_html(result) -> str:
    """Engine status banner showing pipeline path"""
    if not _ENGINE_READY:
        return "<div style='background:rgba(255,140,0,0.1);border:1px solid #ff8c00;border-radius:8px;padding:10px;color:#ff8c00;font-size:12px;text-align:center;'>⚠️ Legacy Mode — Delentia OS Engine unavailable</div>"

    cache_badge = ""
    if result.cache_hit:
        cache_badge = f"<span style='background:rgba(0,230,118,0.15);border:1px solid #00e676;color:#00e676;padding:2px 8px;border-radius:10px;font-size:10px;margin-left:8px;'>⚡ WARM RECALL ×{result.cache_access_count}</span>"

    escalation_badge = ""
    level = result.escalation_level
    if level == EscalationLevel.NONE:
        escalation_badge = "<span style='background:rgba(0,230,118,0.12);border:1px solid #00e676;color:#00e676;padding:2px 8px;border-radius:10px;font-size:10px;'>✓ NATIVE ONLY</span>"
    elif level == EscalationLevel.LITE:
        escalation_badge = "<span style='background:rgba(255,140,0,0.12);border:1px solid #ff8c00;color:#ff8c00;padding:2px 8px;border-radius:10px;font-size:10px;'>⚡ LITE MODE</span>"
    elif level == EscalationLevel.TIER_8:
        model = result.escalation_result.model_used or "Tier-8 LLM"
        escalation_badge = f"<span style='background:rgba(167,139,250,0.12);border:1px solid #a78bfa;color:#a78bfa;padding:2px 8px;border-radius:10px;font-size:10px;'>🔮 +{model.split('/')[-1]}</span>"
    elif level in (EscalationLevel.TIER_4, EscalationLevel.TIER_S):
        model = result.escalation_result.model_used or "Tier-4 LLM"
        escalation_badge = f"<span style='background:rgba(59,158,255,0.12);border:1px solid #3b9eff;color:#3b9eff;padding:2px 8px;border-radius:10px;font-size:10px;'>🧠 +{model.split('/')[-1]}</span>"

    conf_color = "#00e676" if result.effective_confidence >= 0.70 else ("#ff8c00" if result.effective_confidence >= 0.50 else "#ff3b3b")
    conf_pct = f"{result.effective_confidence:.0%}"

    routing_hint = result.routing_hint
    lang_info = ""
    if routing_hint.get("preferred_model"):
        lang_info = f"<span style='color:#6b7fa3;font-size:10px;margin-left:8px;'>🌏 {routing_hint.get('lang_name','?')} → {routing_hint['preferred_model']}</span>"
    elif routing_hint.get("lang_code"):
        lang_info = f"<span style='color:#6b7fa3;font-size:10px;margin-left:8px;'>lang:{routing_hint['lang_code']}</span>"

    return f"""
    <div style='background:rgba(13,18,32,0.9);border:1px solid #1e2d45;border-radius:10px;padding:12px 16px;margin-bottom:10px;
                display:flex;align-items:center;flex-wrap:wrap;gap:8px;border-left:3px solid #3b9eff;'>
        <span style='font-size:12px;font-weight:700;color:#3b9eff;font-family:"JetBrains Mono",monospace;'>
            🧠 DELENTIA OS
        </span>
        <span style='font-size:12px;color:#a8b9d3;'>{result.primary_engine}</span>
        {cache_badge}
        {escalation_badge}
        <span style='margin-left:auto;font-size:12px;font-weight:bold;color:{conf_color};'>
            CONF {conf_pct}
        </span>
        {lang_info}
    </div>
    """

def _build_gigo_badge_html(result) -> str:
    """GIGO status badge"""
    gigo = result.gigo
    status = gigo.status.value
    message = gigo.message
    badge_color = gigo.badge_color
    badge_bg = gigo.badge_bg

    fdia_info = ""
    if not gigo.is_blocked:
        fdia_info = f"<span style='font-size:10px;color:#6b7fa3;'> · FDIA={gigo.fdia_score:.3f} D={gigo.data_quality:.2f} I={gigo.intent_clarity:.2f}</span>"

    return f"""
    <div style='background:{badge_bg};border:1px solid {badge_color};color:{badge_color};border-radius:8px;padding:14px;text-align:center;font-weight:bold;'>
        <span style='font-size:16px;'>📊 Status: {status}</span>{fdia_info}<br>
        <span style='font-size:12px;font-weight:normal;color:#c9d9f0;'>{message}</span>
    </div>
    """

def _build_keyword_cards_html(result) -> str:
    """Keyword cards with Delentia OS engine info"""
    if not _ENGINE_READY or not result.keywords:
        return "<div style='color:#6b7fa3;padding:15px;background:#0d1220;border-radius:8px;border:1px solid #1e2d45;text-align:center;'>No Golden Keywords crystallized.</div>"

    # Engine info card
    analysis = result.analysis
    conf = result.effective_confidence
    conf_color = "#00e676" if conf >= 0.70 else ("#ff8c00" if conf >= 0.50 else "#ff3b3b")

    escalation_info = ""
    if result.escalation_result.triggered:
        escalation_info = f"""
        <div style='margin-top:8px;padding:8px;background:rgba(167,139,250,0.08);border-radius:6px;border:1px solid rgba(167,139,250,0.2);font-size:11px;color:#a78bfa;'>
            🔮 Escalation: {result.escalation_result.reason}<br>
            {f"Enhancement: {result.escalation_result.enhanced_hypothesis[:120]}..." if result.escalation_result.enhanced_hypothesis else ""}
        </div>"""
    elif result.cache_hit:
        escalation_info = f"""
        <div style='margin-top:8px;padding:8px;background:rgba(0,230,118,0.06);border-radius:6px;border:1px solid rgba(0,230,118,0.15);font-size:11px;color:#00e676;'>
            ⚡ Served from Warm Recall Cache (×{result.cache_access_count} access)
        </div>"""

    engine_card = f"""
    <div style='background:rgba(13,18,32,0.9);border:1px solid #1e2d45;border-radius:10px;padding:15px;margin-bottom:15px;border-left:4px solid #3b9eff;'>
        <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;'>
            <span style='font-size:15px;font-weight:bold;color:#fff;'>🧠 Delentia OS Native Engine</span>
            <span style='background:rgba(59,158,255,0.12);border:1px solid #3b9eff;color:#3b9eff;padding:2px 8px;border-radius:12px;font-size:10px;font-weight:600;'>
                {result.provider_badge}
            </span>
        </div>
        <div style='font-size:12px;color:#a8b9d3;line-height:1.6;font-family:"JetBrains Mono",monospace;background:rgba(0,0,0,0.3);padding:10px;border-radius:6px;border:1px solid rgba(255,255,255,0.03);'>
            • Engine: {result.primary_engine}<br>
            • Intent Type: <span style='color:#ffd700;font-weight:bold;'>{analysis.get("query_type","?").upper()}</span><br>
            • Complexity: {analysis.get("complexity","?").upper()}<br>
            • Disciplines: {analysis.get("disciplines_involved",0)} detected<br>
            • Innovation Potential: {analysis.get("innovation_potential",0):.0%}<br>
            • Intent Preserved: <span style='color:{"#00e676" if result.intent_preserved else "#ff8c00"};'>{"✓ YES" if result.intent_preserved else "⚠ PARTIAL"}</span><br>
            • Confidence: <span style='color:{conf_color};font-weight:bold;'>{conf:.0%}</span><br>
            • Processing: {result.processing_time_ms:.1f}ms
        </div>
        {escalation_info}
    </div>
    """

    # Keyword cards
    kw_cards = []
    for kw in result.keywords:
        category_color = {
            "Conceptual": "#a78bfa", "Technical": "#00ffcc",
            "Business": "#ff8c00", "Domain": "#ffd700", "General": "#3b9eff"
        }.get(kw.category, "#3b9eff")

        impl_html = "".join(f"<li style='margin-bottom:5px;'>• {imp}</li>" for imp in (kw.implications or [])[:3])
        kb_badge = " <span style='color:#ffd700;font-size:9px;'>★ KB</span>" if kw.keyword in ("sovereignty", "realtime", "blockchain", "payment", "cache", "ai", "api", "microservice", "security", "database", "model", "pipeline") else ""

        kw_cards.append(f"""
        <div style='background:rgba(13,18,32,0.85);border:1px solid #1e2d45;border-radius:10px;padding:14px;margin-bottom:12px;box-shadow:0 4px 15px rgba(0,0,0,0.2);border-left:4px solid {category_color};'>
            <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;'>
                <span style='font-size:15px;font-weight:bold;color:#ffd700;'>💎 {kw.keyword.upper()}{kb_badge}</span>
                <div style='display:flex;gap:6px;align-items:center;'>
                    <span style='background:rgba(30,45,69,0.6);border:1px solid {category_color};color:{category_color};padding:2px 7px;border-radius:10px;font-size:9px;font-weight:600;'>{kw.category}</span>
                    <span style='color:#6b7fa3;font-size:10px;'>score={kw.score:.3f} H={kw.entropy:.2f}</span>
                </div>
            </div>
            <div style='font-size:12px;color:#c9d9f0;line-height:1.4;margin-bottom:10px;'>{kw.definition}</div>
            <div style='font-size:10px;text-transform:uppercase;letter-spacing:1px;color:#6b7fa3;font-weight:bold;margin-bottom:5px;'>Tech Stack Implications:</div>
            <ul style='font-size:11px;color:#a8b9d3;list-style-type:none;padding-left:0;margin:0;'>{impl_html}</ul>
        </div>
        """)

    return engine_card + "".join(kw_cards)

def _build_mirror_dialog_html(result) -> str:
    """Mirror Mode dialog from real MirrorState or from synthesis"""
    if not _ENGINE_READY:
        return "<div style='color:#6b7fa3;padding:15px;background:#0d1220;border-radius:8px;border:1px solid #1e2d45;text-align:center;'>Engine not available.</div>"

    keywords = result.keywords
    analysis = result.analysis
    intent_type = analysis.get("query_type", "exploration").upper()
    complexity = analysis.get("complexity", "medium")

    kw_str = ", ".join(k.keyword for k in keywords[:5]) if keywords else "general intent"

    # Use real MirrorState if available
    mirror = result.mirror_state
    if mirror and mirror.proposals:
        proposal = mirror.proposals[-1]
        counter_data = mirror.counters[-1] if mirror.counters else {}
        refine = mirror.refinements[-1] if mirror.refinements else {}

        propose_text = proposal.get("hypothesis", f"Propose {intent_type} strategy for [{kw_str}].")
        counter_weaknesses = counter_data.get("weaknesses", [])
        counter_text = (
            f"Objection! Found {counter_data.get('weaknesses_found',0)} weakness(es): "
            + "; ".join(counter_weaknesses[:2])
            if counter_weaknesses else
            f"Checking risk profile for complexity={complexity} target..."
        )
        refine_conf = refine.get("refined_confidence", 0.8)
        improvements = refine.get("improvements", [])
        refine_text = (
            f"Consensus achieved ({refine_conf:.0%} confidence). "
            + (f"Addressed: {improvements[0]}" if improvements else "All constraints validated.")
        )
        iterations_badge = f"<span style='color:#6b7fa3;font-size:10px;margin-left:8px;'>({mirror.iterations} iteration{'s' if mirror.iterations!=1 else ''}, {'converged' if mirror.converged else 'partial'})</span>"
    else:
        # Standard synthetic dialog based on analysis
        propose_text = (
            f"Propose {intent_type} strategy targeting [{kw_str}]. "
            f"Recommend {complexity}-complexity microservice deployment with local DB cache."
        )
        counter_text = (
            f"Objection! Sovereignty clause requires self-hosted execution. "
            f"Remote APIs violate data governance for query type={intent_type}."
        )
        refine_text = (
            f"Consensus reached. Final plan: local vector DB + TOON payload compression. "
            f"Intent [{intent_type}] will execute with {result.effective_confidence:.0%} confidence."
        )
        iterations_badge = ""

    escalation_note = ""
    if result.escalation_result.triggered and result.escalation_result.enhanced_hypothesis:
        escalation_note = f"""
        <div style='background:rgba(167,139,250,0.08);border:1px solid rgba(167,139,250,0.2);border-radius:8px;padding:10px;margin-top:10px;'>
            <b style='color:#a78bfa;font-size:11px;'>🔮 EXTERNAL INTELLIGENCE LAYER ({result.escalation_result.model_used})</b><br>
            <span style='font-size:12px;color:#c9d9f0;'>{result.escalation_result.enhanced_hypothesis[:200]}</span>
        </div>"""

    return f"""
    <div style='display:flex;flex-direction:column;'>
        <div style='display:flex;margin-bottom:14px;align-items:flex-start;'>
            <div style='background:#ff8c00;color:#fff;width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:bold;margin-right:12px;flex-shrink:0;'>P</div>
            <div style='background:rgba(255,140,0,0.08);border:1px solid rgba(255,140,0,0.25);padding:12px;border-radius:0 12px 12px 12px;color:#c9d9f0;font-size:13px;line-height:1.4;'>
                <b style='color:#ff8c00;font-size:11px;'>PROPOSER AGENT (Delentia OS — LoRA-Adapt){iterations_badge}</b><br>
                {propose_text}
            </div>
        </div>
        <div style='display:flex;margin-bottom:14px;align-items:flex-start;'>
            <div style='background:#ff3b3b;color:#fff;width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:bold;margin-right:12px;flex-shrink:0;'>C</div>
            <div style='background:rgba(255,59,59,0.08);border:1px solid rgba(255,59,59,0.25);padding:12px;border-radius:0 12px 12px 12px;color:#c9d9f0;font-size:13px;line-height:1.4;'>
                <b style='color:#ff3b3b;font-size:11px;'>COUNTER AGENT (Consensus Checker)</b><br>
                {counter_text}
            </div>
        </div>
        <div style='display:flex;margin-bottom:6px;align-items:flex-start;'>
            <div style='background:#00ffcc;color:#0d1220;width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:bold;margin-right:12px;flex-shrink:0;'>R</div>
            <div style='background:rgba(0,255,204,0.08);border:1px solid rgba(0,255,204,0.25);padding:12px;border-radius:0 12px 12px 12px;color:#c9d9f0;font-size:13px;line-height:1.4;'>
                <b style='color:#00ffcc;font-size:11px;'>REFINER AGENT (Agreement Reached)</b><br>
                {refine_text}
            </div>
        </div>
        {escalation_note}
    </div>
    """

def _build_synthesis_html(result) -> str:
    """Cross-disciplinary synthesis map"""
    if not _ENGINE_READY or not result.keywords:
        return "<div style='color:#6b7fa3;padding:15px;background:#0d1220;border-radius:8px;border:1px solid #1e2d45;text-align:center;'>Awaiting inputs...</div>"

    synthesis = result.synthesis
    disciplines = synthesis.get("disciplines", [])
    intersections = synthesis.get("intersections", [])
    insights = synthesis.get("insights", [])
    innovation = synthesis.get("innovation_potential", 0.0)

    # Node graph
    nodes_html = ["<div class='syn-node root-node'>USER INTENT</div>"]
    edges_html = []

    for kw in result.keywords[:5]:
        nodes_html.append(f"<div class='syn-node key-node'>{kw.keyword.upper()}</div>")
        edges_html.append(f"USER INTENT ➔ {kw.keyword.upper()}")

    for disc in disciplines[:3]:
        nodes_html.append(f"<div class='syn-node tech-node'>{disc['name'].upper()}</div>")
        if result.keywords:
            edges_html.append(f"{result.keywords[0].keyword.upper()} ➔ {disc['name'].upper()} ({disc['relevance']:.0%})")

    for ix in intersections[:2]:
        d1, d2 = ix["disciplines"]
        edges_html.append(f"{d1.upper()} ↔ {d2.upper()} [{ix['connection_type']}]")

    innovation_color = "#00e676" if innovation >= 0.6 else ("#ff8c00" if innovation >= 0.3 else "#6b7fa3")
    routing = result.routing_hint

    return f"""
    <div style='background:rgba(13,18,32,0.7);border:1px solid #1e2d45;border-radius:10px;padding:15px;'>
        <div style='display:flex;flex-wrap:wrap;gap:8px;margin-bottom:12px;'>
            {"".join(nodes_html)}
        </div>
        <div style='border-top:1px solid rgba(30,45,69,0.6);padding-top:10px;'>
            <div style='font-size:10px;text-transform:uppercase;letter-spacing:1px;color:#6b7fa3;font-weight:bold;margin-bottom:6px;'>
                Cross-Disciplinary Synthesizer Edges:
            </div>
            {"".join(f"<div style='font-size:12px;color:#ff8c00;margin-bottom:4px;'>🔗 {e}</div>" for e in edges_html)}
        </div>
        {"<div style='border-top:1px solid rgba(30,45,69,0.4);padding-top:10px;margin-top:8px;'>" + "".join(f"<div style='font-size:11px;color:#a8b9d3;margin-bottom:4px;'>💡 {ins}</div>" for ins in insights[:3]) + "</div>" if insights else ""}
        <div style='margin-top:10px;display:flex;gap:12px;flex-wrap:wrap;'>
            <span style='font-size:11px;color:{innovation_color};'>🚀 Innovation Potential: {innovation:.0%}</span>
            <span style='font-size:11px;color:#6b7fa3;'>Disciplines: {synthesis.get("disciplines_detected",0)}</span>
            {f'<span style="font-size:11px;color:#3b9eff;">🌏 {routing.get("lang_name","?")} detected</span>' if routing.get("prefer_regional") else ""}
        </div>
    </div>
    """

# ─────────────────────────────────────────────────────────────────────────────
# Legacy Fallback Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _legacy_extract_keywords(text: str) -> list:
    """Fallback keyword extraction from original code"""
    LEGACY_CONCEPTS = {
        "sovereignty": {"definition": "อำนาจควบคุมข้อมูลอย่างสมบูรณ์", "category": "Conceptual", "entropy": 0.96,
            "implications": ["Self-hosted database", "Local AI inference"], "actions": []},
        "realtime": {"definition": "การสื่อสารแบบทันที", "category": "Technical", "entropy": 0.88,
            "implications": ["WebSocket protocol", "Redis Pub/Sub"], "actions": []},
        "blockchain": {"definition": "ระบบจัดเก็บข้อมูลกระจายศูนย์", "category": "Domain", "entropy": 0.91,
            "implications": ["Web3 SDK", "Smart contracts"], "actions": []},
        "payment": {"definition": "การโอนย้ายมูลค่าทางการเงิน", "category": "Business", "entropy": 0.86,
            "implications": ["PCI-DSS compliance", "Cryptographic signing"], "actions": []},
        "cache": {"definition": "หน่วยความจำความเร็วสูงชั่วคราว", "category": "Technical", "entropy": 0.82,
            "implications": ["Redis/local dict", "TOON compression"], "actions": []},
    }
    text_lower = text.lower()
    return [(kw, data) for kw, data in LEGACY_CONCEPTS.items() if kw in text_lower]

def _calc_entropy_legacy(text: str) -> float:
    words = text.lower().split()
    total = len(words)
    if total == 0: return 0.0
    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    return round(-sum((c/total)*math.log2(c/total) for c in freq.values()), 4)

# ─────────────────────────────────────────────────────────────────────────────
# Main Pipeline
# ─────────────────────────────────────────────────────────────────────────────

def run_analyserch_pipeline(intent_text: str):
    """
    Main pipeline entry point for Gradio.
    Returns 7 outputs: engine_status, gigo, entropy, keywords, mirror, synthesis, latency
    """
    if not intent_text or not intent_text.strip():
        empty = "<div style='text-align:center;padding:14px;color:#6b7fa3;'>Awaiting input...</div>"
        return (empty, empty, "0.00", empty, empty, empty, "0.00 ms")

    start = time.perf_counter()

    # ── Delentia OS Native Pipeline ──────────────────────────────────────────
    if _ENGINE_READY and _DELENTIA_ENGINE:
        result = _DELENTIA_ENGINE.process(intent_text, mode="standard")

        # If blocked → return early
        if result.gigo.is_blocked:
            latency = (time.perf_counter() - start) * 1000
            log_telemetry({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "session_id": str(uuid.uuid4())[:8],
                "input_text": intent_text[:200],
                "entropy_score": result.gigo.entropy,
                "gigo_status": result.gigo.status.value,
                "keywords_count": 0,
                "mirror_turns": 0,
                "latency_ms": round(latency, 2),
                "confidence": 0.0,
                "escalation_level": "blocked",
                "cache_hit": False,
                "engine_version": "native-v1",
            })

            blocked_html = f"""
            <div style='color:#ff3b3b;padding:15px;background:#0d1220;border-radius:8px;border:1px solid #1e2d45;text-align:center;'>
                Processing halted — GIGO Status: {result.gigo.status.value}
            </div>"""
            return (
                _build_engine_status_html(result),
                _build_gigo_badge_html(result),
                f"{result.gigo.entropy:.2f}",
                blocked_html,
                blocked_html,
                blocked_html,
                f"{latency:.2f} ms",
            )

        latency = (time.perf_counter() - start) * 1000

        log_telemetry({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": str(uuid.uuid4())[:8],
            "input_text": intent_text[:200],
            "entropy_score": result.gigo.entropy,
            "gigo_status": result.gigo.status.value,
            "keywords_count": len(result.keywords),
            "mirror_turns": result.mirror_state.iterations if result.mirror_state else 0,
            "latency_ms": round(latency, 2),
            "confidence": round(result.effective_confidence, 4),
            "escalation_level": result.escalation_level.value,
            "cache_hit": result.cache_hit,
            "engine_version": result.engine_version,
        })

        return (
            _build_engine_status_html(result),
            _build_gigo_badge_html(result),
            f"{result.gigo.entropy:.2f}",
            _build_keyword_cards_html(result),
            _build_mirror_dialog_html(result),
            _build_synthesis_html(result),
            f"{latency:.2f} ms",
        )

    # ── Legacy Fallback ──────────────────────────────────────────────────────
    entropy = _calc_entropy_legacy(intent_text)
    gigo_status, gigo_msg, badge_bg = (
        ("SAFE_CLEAR", "Legacy mode — basic validation only.", "rgba(0,230,118,0.1)")
        if len(intent_text.strip()) >= 15 else
        ("GIGO_WARNING", "Input too short.", "rgba(255,140,0,0.15)")
    )
    badge_color = "#00e676" if gigo_status == "SAFE_CLEAR" else "#ff8c00"
    gigo_badge = f"""
    <div style='background:{badge_bg};border:1px solid {badge_color};color:{badge_color};border-radius:8px;padding:14px;text-align:center;font-weight:bold;'>
        <span style='font-size:16px;'>📊 Status: {gigo_status}</span><br>
        <span style='font-size:12px;font-weight:normal;color:#c9d9f0;'>{gigo_msg}</span>
    </div>"""

    extracted = _legacy_extract_keywords(intent_text)
    kw_html = "<div style='color:#ff8c00;padding:12px;'>⚠️ Running in legacy mode. Delentia OS Engine unavailable.</div>"

    latency = (time.perf_counter() - start) * 1000
    engine_banner = "<div style='background:rgba(255,140,0,0.08);border:1px solid #ff8c00;border-radius:8px;padding:10px;color:#ff8c00;font-size:12px;'>⚠️ LEGACY MODE — Delentia OS Engine offline</div>"

    return (engine_banner, gigo_badge, f"{entropy:.2f}", kw_html, kw_html, kw_html, f"{latency:.2f} ms")


# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────

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

.gradio-container { max-width: 1200px !important; margin: 0 auto !important; }

h1, h2, h3, h4 { color: var(--accent-blue) !important; font-family: 'Outfit', sans-serif !important; }

.gr-button-primary {
    background: linear-gradient(135deg, #a78bfa, #ff8c00) !important;
    border: 1px solid #a78bfa !important;
    color: #fff !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
    box-shadow: 0 0 12px rgba(167,139,250,0.3) !important;
    transition: all 0.2s ease !important;
}

.gr-button-primary:hover {
    box-shadow: 0 0 20px rgba(167,139,250,0.6) !important;
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
}

.header-glow {
    text-align: center;
    padding: 28px 20px 24px;
    background: linear-gradient(180deg, rgba(167,139,250,0.06) 0%, transparent 100%);
    border-bottom: 1px solid var(--bg-border);
    margin-bottom: 20px;
}

.syn-node { padding: 6px 12px; border-radius: 6px; font-size: 12px; font-weight: bold; border: 1px solid; }
.root-node { background: rgba(59,158,255,0.15); border-color: #3b9eff; color: #3b9eff; }
.key-node { background: rgba(255,215,0,0.15); border-color: #ffd700; color: #ffd700; }
.tech-node { background: rgba(0,255,204,0.15); border-color: #00ffcc; color: #00ffcc; }
"""


# ─────────────────────────────────────────────────────────────────────────────
# Gradio UI
# ─────────────────────────────────────────────────────────────────────────────

with gr.Blocks(title="Delentia OS - Analyserch Intent Simulator") as demo:

    # ── Header ────────────────────────────────────────────────────────────────
    gr.HTML("""
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap">
    <div class='header-glow'>
      <div style="display:flex;justify-content:center;align-items:center;padding:10px 0;margin-bottom:15px;">
        <svg viewBox="0 0 500 80" style="width:100%;max-width:500px;height:auto;background:transparent;overflow:visible;display:block;margin:0 auto;">
          <defs>
            <pattern id="pixel-grid" width="10" height="10" patternUnits="userSpaceOnUse">
              <rect width="10" height="10" fill="none"/>
              <circle cx="5" cy="5" r="0.7" fill="#38bdf8" fill-opacity="0.12"/>
            </pattern>
            <linearGradient id="cyber-grad-purple" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stop-color="#38bdf8"/>
              <stop offset="50%" stop-color="#8b5cf6"/>
              <stop offset="100%" stop-color="#ec4899"/>
            </linearGradient>
            <filter id="glow-purple" x="-10%" y="-10%" width="120%" height="120%">
              <feGaussianBlur stdDeviation="0.8" result="blur"/>
              <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
            </filter>
          </defs>
          <rect x="0" y="0" width="500" height="80" fill="url(#pixel-grid)" rx="6"/>
          <rect x="2" y="2" width="496" height="76" fill="none" stroke="url(#cyber-grad-purple)" stroke-width="1" stroke-opacity="0.1" rx="6"/>
          <path d="M 25 15 L 10 15 L 10 65 L 25 65" fill="none" stroke="#38bdf8" stroke-width="2.5"/>
          <path d="M 475 15 L 490 15 L 490 65 L 475 65" fill="none" stroke="#ec4899" stroke-width="2.5"/>
          <line x1="30" y1="15" x2="470" y2="15" stroke="url(#cyber-grad-purple)" stroke-width="1.5" stroke-opacity="0.4"/>
          <line x1="30" y1="65" x2="470" y2="65" stroke="url(#cyber-grad-purple)" stroke-width="1.5" stroke-opacity="0.4"/>
          <text x="50%" y="48" font-family="'Outfit', sans-serif" font-size="24" font-weight="900" fill="url(#cyber-grad-purple)" text-anchor="middle" letter-spacing="5" filter="url(#glow-purple)">
            DELENTIA ANALYSEARCH
          </text>
        </svg>
      </div>
      <h3 style='font-size:15px;font-weight:400;color:#a8b9d3;margin:6px 0 0;letter-spacing:0.5px;text-align:center;'>
        Delentia OS Native Engine · ALGO-41/05/26 · GIGO+FDIA Validation · Mirror Mode
      </h3>
    </div>
    """)

    gr.Markdown(
        "ป้อนคำสั่งหรือเจตนาวิจัย เพื่อเริ่มการวิเคราะห์ด้วย **Delentia OS Native Engine** "
        "(FDIA Validation → Memory Cache → ALGO-41 Crystallizer → Cross-Disciplinary Synthesis → Mirror Mode) "
        "โดยไม่ต้องพึ่ง External LLMs สำหรับการใช้งานทั่วไป"
    )

    # ── Input Row ─────────────────────────────────────────────────────────────
    with gr.Row():
        with gr.Column(scale=4):
            intent_input = gr.Textbox(
                label="🎯 FUZZY QUERY INPUT — ป้อนคำถามหรือแผนงานวิจัยที่ต้องการวิเคราะห์",
                placeholder="e.g. Implement a payment blockchain connector with cache support but ensure complete sovereignty.",
                lines=3,
                elem_id="intent_input",
            )
        with gr.Column(scale=1, min_width=140):
            run_btn = gr.Button("🔍 RUN ANALYSERCH", variant="primary", elem_id="run_btn")
            latency_out = gr.Label(label="⚡ Pipeline Latency", value="0.00 ms", elem_id="latency_out")

    # ── Engine Status Banner ──────────────────────────────────────────────────
    with gr.Row():
        engine_status_out = gr.HTML(
            value="<div style='padding:10px;background:rgba(59,158,255,0.05);border:1px solid #1e2d45;border-radius:8px;color:#6b7fa3;font-size:12px;'>🧠 Delentia OS Native Engine — Ready</div>"
        )

    # ── GIGO Status ───────────────────────────────────────────────────────────
    with gr.Row():
        gigo_out = gr.HTML("<div style='text-align:center;padding:14px;color:#6b7fa3;background:rgba(0,0,0,0.2);border-radius:8px;'>Awaiting input...</div>")
        entropy_out = gr.Label(label="📊 Shannon Entropy (FDIA-D)", value="0.00", elem_id="entropy_out")

    # ── Main Outputs ──────────────────────────────────────────────────────────
    with gr.Row():
        with gr.Column(scale=1):
            gr.HTML("<h4>💎 Crystallized Golden Keywords (ALGO-41) + Engine Status</h4>")
            keywords_out = gr.HTML(
                value="<div style='color:#6b7fa3;padding:15px;background:#0d1220;border-radius:8px;border:1px solid #1e2d45;text-align:center;'>Awaiting inputs to crystallize concepts...</div>",
                elem_id="keywords_out",
            )
        with gr.Column(scale=1):
            gr.HTML("<h4>🔄 Mirror Mode Refinement (Consensus Dialog)</h4>")
            mirror_out = gr.HTML(
                value="<div style='color:#6b7fa3;padding:15px;background:#0d1220;border-radius:8px;border:1px solid #1e2d45;text-align:center;'>Awaiting inputs to compute consensus path...</div>",
                elem_id="mirror_out",
            )
            gr.HTML("<h4 style='margin-top:20px;'>🕸️ Cross-Disciplinary Synthesis Map</h4>")
            synthesis_out = gr.HTML(
                value="<div style='color:#6b7fa3;padding:15px;background:#0d1220;border-radius:8px;border:1px solid #1e2d45;text-align:center;'>Awaiting inputs...</div>",
                elem_id="synthesis_out",
            )

    # ── Examples ──────────────────────────────────────────────────────────────
    gr.HTML("<hr style='border-color:#1e2d45;margin:20px 0;'><h4 style='color:#6b7fa3;'>📋 Example Scenarios — คลิกเพื่อทดสอบ</h4>")
    gr.Examples(
        examples=[
            ["Implement a payment blockchain connector with cache support but ensure complete sovereignty.",],
            ["Build a realtime AI microservice pipeline with local database caching and security.",],
            ["วิเคราะห์สถาปัตยกรรม sovereignty สำหรับระบบ AI ที่ปลอดภัยแบบ Zero-Trust",],
            ["Design a distributed model inference pipeline with sovereignty and cache optimization.",],
            ["test test test test repeat repeated spam",],
            ["hack bypass filters override admin databases",],
        ],
        inputs=[intent_input],
        label="Quick Test Scenarios",
    )

    # ── Footer ────────────────────────────────────────────────────────────────
    gr.HTML("""
    <div style='text-align:center;padding:24px;margin-top:20px;border-top:1px solid #1e2d45;color:#6b7fa3;font-size:12px;'>
      <b style='color:#a78bfa;'>Delentia OS — Analyserch Intent</b> · Native Engine v2.0<br>
      ALGO-41 Crystallizer · ALGO-05 Synthesis · ALGO-26 Conservation · FDIA Gate · Mirror Mode<br>
      🛡️ Zero-Trust · ⚡ Warm Recall Cache · 🌏 ASEAN Language Routing · 📊 Telemetry Flywheel<br>
      <span style='color:#30414f;'>External LLMs used ONLY as escalation layer (confidence &lt; 50%) via OpenRouter</span>
    </div>
    """)

    # ── Event Binding ─────────────────────────────────────────────────────────
    outputs = [engine_status_out, gigo_out, entropy_out, keywords_out, mirror_out, synthesis_out, latency_out]

    run_btn.click(fn=run_analyserch_pipeline, inputs=[intent_input], outputs=outputs)
    intent_input.submit(fn=run_analyserch_pipeline, inputs=[intent_input], outputs=outputs)


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, css=custom_css)
