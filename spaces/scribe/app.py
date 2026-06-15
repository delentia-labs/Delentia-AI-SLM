import gradio as gr
import time
import random
import json

def compress_context(long_text, api_price_per_million):
    start_time = time.perf_counter()
    words = long_text.split()
    orig_tokens = int(len(words) * 1.3)  # rough estimation of token count
    
    if orig_tokens < 10:
        return "กรุณาใส่ข้อความที่มีความยาวอย่างน้อย 1 ย่อหน้าเพื่อทวนสอบ", {}, "0x", 0, 0, "$0.00", "$0.00", "0.0%"

    # Simulate compression ratio
    comp_ratio = random.uniform(3.5, 4.5)
    comp_tokens = int(orig_tokens / comp_ratio)
    tokens_saved = orig_tokens - comp_tokens
    savings_pct = (tokens_saved / orig_tokens) * 100
    
    # Extract topics & key points mock based on content
    topic = "Extracted System Specifications"
    points = [
        "JITNA v3 security parameters require isolated memory allocations",
        "VRAM consumption is restricted to 6.84GB under active multi-LoRA loads",
        "Consensus voting requires signatures from a minimum of 4 validator cores"
    ]
    
    if "pdpa" in long_text.lower() or "personal data" in long_text.lower():
        topic = "PDPA Compliance Rules Summary"
        points = [
            "Explicit user consent is mandatory prior to personal data ingestion",
            "Breach notification window is strictly capped at 72 hours",
            "Regulatory penalties scale up to 5,000,000 THB for structural negligence"
        ]
    elif "rct" in long_text.lower() or "constitution" in long_text.lower():
        topic = "RCT v7 Governance Principles"
        points = [
            "Boundary enforcement restricts arbitrary execution of user payloads",
            "Zero-trust override validates every state mutation cryptographically",
            "Architect approval A=0 halts all execution nodes instantly"
        ]

    summary = {
        "topic": topic,
        "key_points": points,
        "compression_ratio": round(comp_ratio, 2),
        "original_tokens": orig_tokens,
        "compressed_tokens": comp_tokens,
        "token_savings_pct": f"{savings_pct:.1f}%"
    }
    
    # Calculate costs (Standard price vs Delentia Scribe compressed price)
    # Average daily inputs: 50,000 prompts
    daily_runs = 50000
    cost_original = (orig_tokens * daily_runs / 1000000) * api_price_per_million
    cost_compressed = (comp_tokens * daily_runs / 1000000) * api_price_per_million
    cost_saved = cost_original - cost_compressed
    
    latency = (time.perf_counter() - start_time) * 1000 + random.uniform(15, 25)
    
    trace_tree = (
        f"Trace Tree - context_compression\n"
        f"+-- [Intent Received] | Actor: system | Source: rag_pipeline\n"
        f"`-- [Scribe Context Compressor] | Ratio: {comp_ratio:.2f}x | Saved: {tokens_saved} "
        f"({orig_tokens} -> {comp_tokens}) | Latency: {latency:.2f}ms"
    )
    
    return (
        json.dumps(summary, indent=2, ensure_ascii=False),
        f"{comp_ratio:.2f}x",
        tokens_saved,
        f"${cost_original:.2f}",
        f"${cost_compressed:.2f}",
        f"${cost_saved:.2f} ({savings_pct:.1f}% Savings)",
        trace_tree
    )

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
    background: linear-gradient(135deg, #ffd700, #ff8c00) !important;
    border: 1px solid #ffd700 !important;
    color: #111 !important;
    font-weight: 700 !important;
    font-family: 'Outfit', sans-serif !important;
    border-radius: 8px !important;
    box-shadow: 0 0 12px rgba(255, 215, 0, 0.3) !important;
    transition: all 0.2s ease !important;
}

.gr-button-primary:hover {
    box-shadow: 0 0 20px rgba(255, 215, 0, 0.6) !important;
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
    background: linear-gradient(180deg, rgba(255,215,0,0.06) 0%, transparent 100%);
    border-bottom: 1px solid var(--bg-border);
    margin-bottom: 20px;
}

.ascii-logo {
    font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace !important;
    font-size: 10px !important;
    line-height: 1.25 !important;
    letter-spacing: 0px !important;
    margin: 0 auto 12px !important;
    background: linear-gradient(135deg, #a78bfa 0%, #ffd700 50%, #00ffcc 100%);
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    display: inline-block !important;
    font-weight: bold !important;
    white-space: pre !important;
    text-align: left !important;
}
"""

with gr.Blocks(css=custom_css, title="Delentia Scribe Compressor") as demo:
    gr.HTML("""
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap">
    <div class='header-glow'>
      <div style="display: flex; justify-content: center; align-items: center; padding: 10px 0; margin-bottom: 15px;">
        <svg viewBox="0 0 450 60" style="width: 100%; max-width: 450px; height: auto; background: transparent; overflow: visible; display: block; margin: 0 auto;">
          <defs>
            <linearGradient id="scribe-grad" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stop-color="#a78bfa" />
              <stop offset="50%" stop-color="#ffd700" />
              <stop offset="100%" stop-color="#00ffcc" />
            </linearGradient>
            <filter id="scribe-glow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>
          <line x1="0" y1="5" x2="450" y2="5" stroke="url(#scribe-grad)" stroke-width="1.5" stroke-opacity="0.3" />
          <line x1="0" y1="55" x2="450" y2="55" stroke="url(#scribe-grad)" stroke-width="1.5" stroke-opacity="0.3" />
          <path d="M 15 15 L 5 15 L 5 45 L 15 45" fill="none" stroke="#a78bfa" stroke-width="2" />
          <path d="M 435 15 L 445 15 L 445 45 L 435 45" fill="none" stroke="#00ffcc" stroke-width="2" />
          <text x="50%" y="38" font-family="'Outfit', sans-serif" font-size="24" font-weight="900" fill="url(#scribe-grad)" text-anchor="middle" letter-spacing="3" filter="url(#scribe-glow)">
            🗜️ DELENTIA SCRIBE
          </text>
        </svg>
      </div>
      <h3 style='font-size:15px;font-weight:400;color:#a8b9d3;margin:6px 0 0;letter-spacing:0.5px;text-align:center;'>
        Recursive Context Compression Engine · Memory Efficiency Engine (MEE)
      </h3>
      
      <div style='margin-top:12px;display:flex;gap:12px;justify-content:center;flex-wrap:wrap;font-size:12px;'>
        <span style='background:#1a2a40;padding:4px 12px;border-radius:20px;border:1px solid #ffd700;color:#ffd700;'>🗜️ Scribe Pillar</span>
        <span style='background:#1a2a40;padding:4px 12px;border-radius:20px;border:1px solid #a78bfa;color:#a78bfa;'>💾 VRAM Optimization</span>
        <span style='background:#1a2a40;padding:4px 12px;border-radius:20px;border:1px solid #00ffcc;color:#00ffcc;'>📉 Context Compression</span>
      </div>
    </div>
    """)
    
    gr.Markdown(
        "จำลองประสิทธิภาพการทำงานของเสาหลักที่ 3 **The Scribe** ที่ใช้ในการย่อส่วนแชทการประทับความจำระยะยาว (Context History) "
        "ให้เหลือเฉพาะแกนความรู้ระดับ High-Signal เพื่อป้องกันปัญหาแรมหมดขีดจำกัด (Context Rot) และลดต้นทุนค่า API ของโมเดลใหญ่ลงแบบสัมผัสได้จริง"
    )
    
    with gr.Row():
        with gr.Column(scale=2):
            long_text = gr.Textbox(
                label="ป้อนเนื้อหาบริบท RAG หรือ Chat History ขนาดใหญ่ที่จะทดสอบบีบอัด",
                placeholder="Paste your long text document or logs here...",
                lines=8
            )
            api_price = gr.Slider(
                minimum=1.0, maximum=15.0, value=2.5, step=0.5,
                label="สมมติฐานราคาค่า API โมเดลหลัก ($ ต่อ 1 ล้านโทเค็น)"
            )
            btn = gr.Button("Compress Context & Calculate ROI", variant="primary")
            
        with gr.Column(scale=2):
            gr.HTML("<h4>✍️ Scribe High-Signal Output Summary</h4>")
            compressed_out = gr.Code(label="Compressed JSON Output", language="json", interactive=False, lines=12)

    with gr.Row():
        ratio_out = gr.Label(label="อัตราการบีบอัด (Ratio)", value="0x")
        tokens_saved_out = gr.Label(label="จำนวนโทเค็นที่ประหยัดได้ (Tokens Saved)", value="0")
        
    with gr.Row():
        with gr.Column():
            gr.HTML("<h3>💡 ผลวิเคราะห์ ROI ค่าใช้จ่าย (ต่อ 50,000 การเรียกใช้งานต่อวัน)</h3>")
            with gr.Row():
                cost_orig_out = gr.Textbox(label="ค่าบริการ API ราคาปกติ", interactive=False)
                cost_comp_out = gr.Textbox(label="ค่าบริการ API หลังประมวลผลผ่าน Scribe", interactive=False)
                cost_saved_out = gr.Textbox(label="ต้นทุนที่ประหยัดเงินได้จริง", interactive=False)

    with gr.Row():
        with gr.Column():
            gr.HTML("<h4>📊 Distributed Tracing - Console Trace Tree</h4>")
            trace_tree_out = gr.Code(label="OTel Staircase Visualizer", language=None, interactive=False, lines=4)

    gr.Examples(
        examples=[
            [
                "The Personal Data Protection Act (PDPA) of Thailand was published in the Government Gazette in May 2019. It governs the protection of personal data in the digital economy. Organizations must assign Data Protection Officers (DPO), request explicit user consent before processing, and notify authorities about breaches within 72 hours. Violations could result in severe administrative fines scaling up to 5,000,000 THB.",
                2.5
            ],
            [
                "The RCT v7 Governance framework establishes constitutional security rules. Rule 1 sets strict boundary conditions for runtime executions. Rule 2 sets zero-trust permission models for ledger storage nodes. Rule 3 enforces override approvals for manual recovery procedures. Calculated scores below 0.70 via the FDIA formula are immediately blocked.",
                2.5
            ]
        ],
        inputs=[long_text, api_price]
    )

    btn.click(
        fn=compress_context,
        inputs=[long_text, api_price],
        outputs=[compressed_out, ratio_out, tokens_saved_out, cost_orig_out, cost_comp_out, cost_saved_out, trace_tree_out]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)

