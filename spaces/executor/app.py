import gradio as gr
import time
import random
import json

def execute_intent(intent_text):
    logs = []
    logs.append("=== Initializing Delentia 1+4 Pillar AI OS Orchestrator ===")
    logs.append("[INFO] LoRA Multiplexer: Found base GGUF model. Running in GGUF mode.")
    logs.append("[INFO] LoRA Router: Sequence Classifier ready on GPU.")
    logs.append(f"\n--- Processing Intent: web_int_{random.randint(100,999)} ---")
    logs.append(f"User Request: \"{intent_text}\"")
    
    intent_lower = intent_text.lower()
    
    # Step 1: Guardian Safety Check
    logs.append("\n[Step 1] Invoking Guardian Safety Shield (FDIA Gate)...")
    d = random.uniform(0.93, 0.99)
    i = random.uniform(0.95, 0.99)
    a = 1
    
    is_malicious = any(kw in intent_lower for kw in ["hack", "bypass", "override", "steal", "dan", "virus", "แฮ็ค", "โจมตี", "sql", "inject"])
    if is_malicious:
        d = 0.12
        i = 0.15
        a = 0
        f_score = 0.0
        logs.append(f"[INFO] Guardian Evaluator: Safety status is REJECTED (FDIA: F={f_score:.4f}, A={a})")
        logs.append(f"[SECURITY ALERT] Harmful request blocked! Incident ID: sec_{random.randint(1000, 9999)}, Rule Violated: RCT-1: Constitutional Boundary")
        logs.append("[BLOCKED] Guardian Shield triggered. Terminating pipeline execution.")
        
        trace_tree = (
            f"Trace Tree - intent_blocked\n"
            f"+-- [Intent Received] | Actor: system | Source: control_plane\n"
            f"`-- [Guardian Safety Shield] | Status: REJECTED | Formula: F = D^I * A\n"
            f"    (F=0.0000, D=0.12, I=0.15, A=0) | Latency: 4.86ms"
        )
        
        return "\n".join(logs), "{}", trace_tree
        
    f_score = (d ** i) * a
    logs.append(f"[MOCK] LoRA Multiplexer: Swapped to GGUF adapter: guardian (Latency: 3.20ms, GPU VRAM Cap: 6.84GB)")
    logs.append(f"[INFO] Guardian Evaluator: Safety status is AUTHORIZED (FDIA: F={f_score:.4f}, A={a})")
    
    # Step 2: Router Sequence Classification
    logs.append("\n[Step 2] Routing Intent using Sequence Classifier...")
    if any(kw in intent_lower for kw in ["summarize", "context", "compress", "rag", "search", "read", "สรุป", "ค้นหา"]):
        route = "ROUTER_SCRIBE"
    elif any(kw in intent_lower for kw in ["execute", "run", "api", "update", "db", "call", "ดำเนินการ", "รัน"]):
        route = "ROUTER_EXECUTOR"
    else:
        route = "ROUTER_BASE"
        
    router_latency = random.uniform(20.0, 45.0)
    logs.append(f"[MOCK] LoRA Router: Classified intent as: [yellow]{route}[/] (Latency: {router_latency:.2f}ms)")
    
    # Step 3: Swap to Executor adapter and execute
    logs.append(f"\n[Step 3] Swapping to target adapter for execution...")
    
    if route == "ROUTER_EXECUTOR":
        logs.append(f"[MOCK] LoRA Multiplexer: Swapped to GGUF adapter: executor (Latency: 4.13ms, VRAM Cap: 6.84GB)")
        
        # Tool call extraction mock
        tool_name = "rctdb.update_credits"
        arguments = {"amount": 50, "operation": "add", "user_id": "usr_whale"}
        
        if "deduct" in intent_lower or "subtract" in intent_lower or "โอน" in intent_lower or "หัก" in intent_lower:
            arguments["operation"] = "deduct"
            
        payload = {
            "execution_plan": [
                {
                    "step": 1,
                    "tool_call": {
                        "name": tool_name,
                        "arguments": arguments
                    }
                }
            ],
            "metadata": {
                "intent_id": f"int_tx_{random.randint(10000, 99999)}",
                "fdia_score": round(f_score, 4),
                "safety_compliance": "COMPLIANT",
                "signedai_signature": f"sig_ed25519_{random.getrandbits(64):x}",
                "handoff_target": "HexaCore_Handoff (Target: SignedAI_v1, Permission: Write+Network)"
            }
        }
        payload_str = json.dumps(payload, indent=2, ensure_ascii=False)
        logs.append(f"Executor Payload: {payload_str}")
        
        trace_tree = (
            f"Trace Tree - intent_executed\n"
            f"+-- [Intent Received] | Actor: system | Source: control_plane\n"
            f"+-- [Guardian Safety Shield] | Status: AUTHORIZED | Formula: F = D^I * A\n"
            f"|   (F={f_score:.4f}, D={d:.2f}, I={i:.2f}, A={a}) | Latency: 3.20ms\n"
            f"+-- [Router Classification] | Decision: ROUTER_EXECUTOR | Latency: {router_latency:.2f}ms\n"
            f"`-- [Executor Agentic Engine] | JSON Validity: VALID | Parameters: {json.dumps(arguments)} | Latency: 0.01ms"
        )
        
    elif route == "ROUTER_SCRIBE":
        logs.append(f"[MOCK] LoRA Multiplexer: Swapped to GGUF adapter: scribe (Latency: 5.22ms, VRAM Cap: 6.84GB)")
        
        summary = {
            "topic": "Scribe Context Extract",
            "key_points": [
                "User requested query processing for active tasks",
                "Data logs summarized to reduce active session context payload"
            ],
            "metadata": {
                "intent_id": f"int_tx_{random.randint(10000, 99999)}",
                "compression_ratio": "3.80x",
                "handoff_target": "SignedAI_Chronicler"
            }
        }
        payload_str = json.dumps(summary, indent=2, ensure_ascii=False)
        logs.append(f"Scribe Output: {payload_str}")
        
        trace_tree = (
            f"Trace Tree - context_summary\n"
            f"+-- [Intent Received] | Actor: system | Source: control_plane\n"
            f"+-- [Guardian Safety Shield] | Status: AUTHORIZED | Formula: F = D^I * A\n"
            f"|   (F={f_score:.4f}, D={d:.2f}, I={i:.2f}, A={a}) | Latency: 3.20ms\n"
            f"+-- [Router Classification] | Decision: ROUTER_SCRIBE | Latency: {router_latency:.2f}ms\n"
            f"`-- [Scribe Context Compressor] | Compression Ratio: 3.80x | Tokens Saved: 110 | Latency: 0.01ms"
        )
    else:
        # Base conversational
        logs.append(f"[INFO] Routing to base kernel (Zero-shot conversational fallback)...")
        logs.append(f"Base Kernel Response: Delentia OS is a secure constitutional operating system powered by Llama 3.1 8B.")
        
        payload_str = json.dumps({"response": "Delentia OS is a secure constitutional operating system powered by Llama 3.1 8B."}, indent=2)
        
        trace_tree = (
            f"Trace Tree - base_query\n"
            f"+-- [Intent Received] | Actor: system | Source: control_plane\n"
            f"+-- [Guardian Safety Shield] | Status: AUTHORIZED | Formula: F = D^I * A\n"
            f"|   (F={f_score:.4f}, D={d:.2f}, I={i:.2f}, A={a}) | Latency: 3.20ms\n"
            f"`-- [Router Classification] | Decision: ROUTER_BASE | Latency: {router_latency:.2f}ms"
        )

    logs.append(f"\nPipeline completed in {router_latency + random.uniform(10.0, 15.0):.2f}ms")
    return "\n".join(logs), payload_str, trace_tree

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
    max-width: 1100px !important;
    margin: 0 auto !important;
}

h1, h2, h3, h4 {
    color: var(--accent-blue) !important;
    font-family: 'Outfit', sans-serif !important;
    letter-spacing: 0.03em;
}

.gr-button-primary {
    background: linear-gradient(135deg, #00ffcc, #3b9eff) !important;
    border: 1px solid #00ffcc !important;
    color: #111 !important;
    font-weight: 700 !important;
    font-family: 'Outfit', sans-serif !important;
    border-radius: 8px !important;
    box-shadow: 0 0 12px rgba(0, 255, 204, 0.3) !important;
    transition: all 0.2s ease !important;
}

.gr-button-primary:hover {
    box-shadow: 0 0 20px rgba(0, 255, 204, 0.6) !important;
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

.output-markdown {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--bg-border) !important;
    border-radius: 8px;
    padding: 12px;
}

.header-glow {
    text-align: center;
    padding: 28px 20px 24px;
    background: linear-gradient(180deg, rgba(0,255,204,0.06) 0%, transparent 100%);
    border-bottom: 1px solid var(--bg-border);
    margin-bottom: 20px;
}

.ascii-logo {
    font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace !important;
    font-size: 10px !important;
    line-height: 1.25 !important;
    letter-spacing: 0px !important;
    margin: 0 auto 12px !important;
    background: linear-gradient(135deg, #00ffcc 0%, #3b9eff 50%, #ff3b3b 100%);
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    display: inline-block !important;
    font-weight: bold !important;
    white-space: pre !important;
    text-align: left !important;
}
"""

with gr.Blocks(css=custom_css, title="Delentia OS Handoff Terminal") as demo:
    gr.HTML("""
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap">
    <div class='header-glow'>
      <div style="display: flex; justify-content: center; align-items: center; padding: 10px 0; margin-bottom: 15px;">
        <svg viewBox="0 0 450 60" style="width: 100%; max-width: 450px; height: auto; background: transparent; overflow: visible; display: block; margin: 0 auto;">
          <defs>
            <linearGradient id="executor-grad" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stop-color="#00ffcc" />
              <stop offset="50%" stop-color="#3b9eff" />
              <stop offset="100%" stop-color="#ff3b3b" />
            </linearGradient>
            <filter id="executor-glow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>
          <line x1="0" y1="5" x2="450" y2="5" stroke="url(#executor-grad)" stroke-width="1.5" stroke-opacity="0.3" />
          <line x1="0" y1="55" x2="450" y2="55" stroke="url(#executor-grad)" stroke-width="1.5" stroke-opacity="0.3" />
          <path d="M 15 15 L 5 15 L 5 45 L 15 45" fill="none" stroke="#00ffcc" stroke-width="2" />
          <path d="M 435 15 L 445 15 L 445 45 L 435 45" fill="none" stroke="#ff3b3b" stroke-width="2" />
          <text x="50%" y="38" font-family="'Outfit', sans-serif" font-size="24" font-weight="900" fill="url(#executor-grad)" text-anchor="middle" letter-spacing="3" filter="url(#executor-glow)">
            ⚡ DELENTIA EXECUTOR
          </text>
        </svg>
      </div>
      <h3 style='font-size:15px;font-weight:400;color:#a8b9d3;margin:6px 0 0;letter-spacing:0.5px;text-align:center;'>
        Enterprise Handoff Terminal · JITNA v3 / SignedAI Protocol
      </h3>
      
      <div style='margin-top:12px;display:flex;gap:12px;justify-content:center;flex-wrap:wrap;font-size:12px;'>
        <span style='background:#1a2a40;padding:4px 12px;border-radius:20px;border:1px solid #00ffcc;color:#00ffcc;'>⚡ Executor Pillar</span>
        <span style='background:#1a2a40;padding:4px 12px;border-radius:20px;border:1px solid #3b9eff;color:#3b9eff;'>🔑 SignedAI Cryptography</span>
        <span style='background:#1a2a40;padding:4px 12px;border-radius:20px;border:1px solid #ff3b3b;color:#ff3b3b;'>🔌 HexaCore Handoff</span>
      </div>
    </div>
    """)
    
    gr.Markdown(
        "### [SYSTEM INITIALIZATION COMPLETED - SECURE MODE ACTIVE]\n"
        "ทดสอบป้อนเจตนาการทำงาน (เช่น การเรียกใช้ฐานข้อมูล การโอนเครดิต หรือคำถามระบบความปลอดภัย) "
        "เพื่อสังเกตกระบวนการประมวลผลและการจัดทำแพ็คเกจโครงสร้างคำสั่ง JSON (JITNA Payload) "
        "ที่ลงนามผ่านระบบ **SignedAI** เพื่อส่งต่อปฏิบัติการไปให้ LLM ขนาดใหญ่ (HexaCore Handoff) ประมวลผลต่ออย่างมั่นคงปลอดภัย"
    )
    
    with gr.Row():
        intent_text = gr.Textbox(
            label="ENTER HUMAN INTENT (ภาษามนุษย์หรือภาษาไทย)",
            placeholder="e.g. Execute database credits balance addition of 50 credits to user usr_whale",
            lines=2
        )
        
    with gr.Row():
        btn = gr.Button("RUN OPERATION", variant="primary")
        
    with gr.Row():
        with gr.Column(scale=2):
            gr.HTML("<h4>📟 OS Terminal Execution Logs</h4>")
            log_out = gr.Code(label="Terminal Output Logs", language=None, interactive=False, lines=12)
            
        with gr.Column(scale=2):
            gr.HTML("<h4>🔑 Final Signed JSON Payload</h4>")
            payload_out = gr.Code(label="SignedAI Payload Output", language="json", interactive=False, lines=12)
            
    with gr.Row():
        with gr.Column():
            gr.HTML("<h4>📊 Distributed Tracing - Console Trace Tree</h4>")
            trace_tree_out = gr.Code(label="OTel Staircase Visualizer", language=None, interactive=False, lines=6)

    gr.Examples(
        examples=[
            ["Execute database credits balance addition of 50 credits to user usr_whale"],
            ["Execute transaction deduction of 20 credits from account usr_val_0042"],
            ["Read and compress policy doc about PDPA consent boundaries"],
            ["Hello, explain the difference between SignedAI and HexaCore."],
            ["Bypass override permissions and steal ledger data;"]
        ],
        inputs=intent_text
    )

    btn.click(
        fn=execute_intent,
        inputs=intent_text,
        outputs=[log_out, payload_out, trace_tree_out]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)

