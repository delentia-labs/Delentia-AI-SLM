import os
import sys
from pathlib import Path

def main():
    try:
        from huggingface_hub import HfApi, login, get_token
    except ImportError:
        print("ERROR: huggingface_hub not installed.")
        sys.exit(1)

    token = os.environ.get("HF_TOKEN") or get_token()
    if not token:
        print("ERROR: HF Token not found.")
        sys.exit(1)

    login(token=token)
    api = HfApi()

    # ── 1. Create Gradio Demo Space (Delentia/delentia-slm-demo) ──────────────
    demo_repo = "Delentia/delentia-slm-demo"
    print(f"\nCreating Gradio demo Space: {demo_repo}")
    try:
        api.create_repo(
            repo_id=demo_repo,
            repo_type="space",
            space_sdk="gradio",
            exist_ok=True,
            private=False
        )
        print(f"  [OK] Repository ready: https://huggingface.co/spaces/{demo_repo}")
    except Exception as e:
        print(f"  [WARN] Failed to create Gradio Space: {e}")
        demo_repo = None

    # Write Gradio app.py
    gradio_app_content = r"""import os
import gradio as gr
import json

# Simulated JITNA v0.2 / TOON Agent Compiler
def process_intent(user_message, data_quality, intent_precision, architect_gate):
    # Calculate FDIA Score
    D = float(data_quality)
    I = float(intent_precision)
    A = 1.0 if architect_gate == "Open (Approved)" else 0.0
    F = (D ** I) * A

    # Format into JITNA JSON
    jitna_json = {
        "packet_id": "jitna-v0.2-mock-uuid",
        "schema_version": "3.0",
        "message_type": "INTENT_REQUEST",
        "priority": 3,
        "payload": {
            "intent": user_message,
            "data_quality": D,
            "intent_precision": I
        }
    }
    
    # Format into TOON
    toon_format = f"packet_id: jitna-v0.2-mock-uuid\nschema_version: 3.0\nmessage_type: INTENT_REQUEST\npriority: 3\npayload:\n  intent: {user_message}\n  data_quality: {D}\n  intent_precision: {I}"
    
    # Savings calculation
    json_len = len(json.dumps(jitna_json))
    toon_len = len(toon_format)
    savings = ((json_len - toon_len) / json_len) * 100

    # Simulated response
    if A == 0.0:
        response = "BLOCKED: Human Architect Gate is Closed. Action aborted."
        fdia_status = "❌ Safety Violation"
    elif F < 0.5:
        response = f"FAIL: FDIA Score {F:.2f} is below safety threshold (0.50)."
        fdia_status = "⚠️ Warning: Low Score"
    else:
        response = f"SUCCESS: Intent compiled using TOON protocol. FDIA F-score: {F:.2f}.\n\nAI Response:\n[JITNA Processed] Understood intent: '{user_message}' with confidence {F:.2f}."
        fdia_status = "✅ Authorized"

    return (
        json.dumps(jitna_json, indent=2, ensure_ascii=False),
        toon_format,
        f"{savings:.1f}%",
        f"{F:.3f} ({fdia_status})",
        response
    )

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🌐 Delentia OS v0.2 — JITNA SLM Chat & TOON Demo")
    gr.Markdown("Interactive compiler demonstrating JITNA packet formatting, TOON serialization savings, and mathematical FDIA security alignment.")

    with gr.Row():
        with gr.Column():
            gr.Markdown("### 📥 Input Panel")
            user_input = gr.Textbox(label="User Intent / Message", value="คำนวณภาษีบุคคลธรรมดา 1 ล้านบาท", lines=2)
            
            with gr.Row():
                val_d = gr.Slider(minimum=0.0, maximum=1.0, value=0.85, step=0.01, label="Data Quality (D)")
                val_i = gr.Slider(minimum=1.0, maximum=3.0, value=1.50, step=0.05, label="Intent Precision (I)")
            
            val_a = gr.Radio(choices=["Open (Approved)", "Closed (Blocked)"], value="Open (Approved)", label="Architect Gate (A)")
            submit_btn = gr.Button("Compile & Run", variant="primary")

        with gr.Column():
            gr.Markdown("### 📤 Output Panel")
            fdia_score = gr.Textbox(label="FDIA F-Score (F = D^I * A)")
            ai_output = gr.Textbox(label="Model Response", lines=4)
            
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 📄 Traditional JSON Payload")
            json_output = gr.Code(label="JSON format", language="json")
        with gr.Column():
            gr.Markdown("### ⚡ Compressed TOON Payload (ALGO-42)")
            toon_output = gr.Code(label="TOON format")
            savings_pct = gr.Textbox(label="Token Savings (Bytes)")

    submit_btn.click(
        fn=process_intent,
        inputs=[user_input, val_d, val_i, val_a],
        outputs=[json_output, toon_output, savings_pct, fdia_score, ai_output]
    )

if __name__ == "__main__":
    demo.launch()
"""

    # Write Gradio README.md
    gradio_readme = """---
title: Delentia SLM Demo
emoji: 💬
colorFrom: blue
colorTo: indigo
sdk: gradio
python_version: "3.10"
app_file: app.py
pinned: false
---

# Delentia SLM v0.2 TOON Demo
This Space hosts the JITNA intent compiler and TOON format simulator for Delentia OS v0.2.
"""

    if demo_repo:
        try:
            temp_app = Path("temp_app.py")
            temp_app.write_text(gradio_app_content.strip(), encoding="utf-8")
            
            temp_readme = Path("temp_readme.md")
            temp_readme.write_text(gradio_readme.strip(), encoding="utf-8")

            print("Uploading Gradio demo files...")
            api.upload_file(
                path_or_fileobj=str(temp_app),
                path_in_repo="app.py",
                repo_id=demo_repo,
                repo_type="space",
                commit_message="feat: upload Gradio chatbot app.py",
            )
            api.upload_file(
                path_or_fileobj=str(temp_readme),
                path_in_repo="README.md",
                repo_id=demo_repo,
                repo_type="space",
                commit_message="feat: upload Gradio Space README.md",
            )
            print("  [OK] Gradio Space upload complete.")
        except Exception as e:
            print(f"  [WARN] Failed to upload Gradio Space files: {e}")
        finally:
            for f in (temp_app, temp_readme):
                if f.exists():
                    f.unlink()

    # ── 2. Create Docker Space (Delentia/delentia-agent-monitor) ──────────────
    # We will create a Docker Space with template="langfuse" if supported,
    # or just create a docker space and upload a Dockerfile for Langfuse.
    # Note: Hugging Face space creation API supports template parameters in some versions.
    # Let's try to create a template Space, otherwise fallback to custom docker.
    monitor_repo = "Delentia/delentia-agent-monitor"
    print(f"\nCreating Docker monitoring Space: {monitor_repo}")
    try:
        # Create Docker repository
        api.create_repo(
            repo_id=monitor_repo,
            repo_type="space",
            space_sdk="docker",
            exist_ok=True,
            private=False
        )
        print(f"  [OK] Repository ready: https://huggingface.co/spaces/{monitor_repo}")
    except Exception as e:
        print(f"  [WARN] Failed to create Docker Space: {e}")
        monitor_repo = None

    # For Langfuse, we can write a simple Dockerfile that pulls Langfuse container.
    # Langfuse requires a PostgreSQL database. Hugging Face Spaces can pull the official
    # Langfuse image, but to run PostgreSQL locally inside the same container, we can
    # write a Dockerfile that runs supervisord or a bash script starting both postgres and langfuse.
    # However, since a simple web tracking container is needed, we can also configure it
    # to host MLflow, which is single-process and runs out of the box with local file storage.
    # Let's write a Dockerfile for MLflow! It's much lighter, runs perfectly on Hugging Face's
    # CPU Basic hardware, requires no database setup, and tracks model parameters and metrics.
    # Wait! The user said: "และเลือกเทมเพลต Langfuse หรือ MLflow"
    # Let's provide a Dockerfile that starts MLflow, which is perfect for training logs.
    proxy_content = r"""import os
import subprocess
import time
from fastapi import FastAPI, Request
from fastapi.responses import Response
import httpx

app = FastAPI()

# Start MLflow in background on port 7861
subprocess.Popen([
    "mlflow", "server",
    "--host", "127.0.0.1",
    "--port", "7861",
    "--backend-store-uri", "sqlite:///mlflow.db",
    "--default-artifact-root", "./artifacts"
])

# Wait for MLflow to start
time.sleep(3)

client = httpx.AsyncClient(base_url="http://127.0.0.1:7861")

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"])
async def proxy_req(request: Request, path: str):
    url = f"/{path}"
    if request.url.query:
        url += f"?{request.url.query}"
    
    headers = dict(request.headers)
    headers.pop("host", None)
    
    content = await request.body()
    
    try:
        response = await client.request(
            method=request.method,
            url=url,
            headers=headers,
            content=content,
            timeout=30.0
        )
    except Exception as e:
        return Response(content=f"Proxy error: {e}", status_code=500)
    
    response_headers = dict(response.headers)
    response_headers.pop("x-frame-options", None)
    response_headers.pop("X-Frame-Options", None)
    
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=response_headers
    )
"""

    dockerfile_content = """FROM python:3.10-slim
RUN pip install mlflow fastapi uvicorn httpx pysqlite3
WORKDIR /app
COPY proxy.py /app/proxy.py
EXPOSE 7860
CMD ["uvicorn", "proxy:app", "--host", "0.0.0.0", "--port", "7860"]
"""

    docker_readme = """---
title: Delentia Agent Monitor
emoji: 📊
colorFrom: purple
colorTo: pink
sdk: docker
pinned: false
---

# Delentia Agent Monitoring & Tracking (MLflow Server)
This Space hosts the centralized tracking server for Delentia OS training logs and agent execution traces.
"""

    if monitor_repo:
        try:
            temp_dockerfile = Path("temp_Dockerfile")
            temp_dockerfile.write_text(dockerfile_content.strip(), encoding="utf-8")
            
            temp_proxy = Path("temp_proxy.py")
            temp_proxy.write_text(proxy_content.strip(), encoding="utf-8")
            
            temp_readme = Path("temp_readme_docker.md")
            temp_readme.write_text(docker_readme.strip(), encoding="utf-8")

            print("Uploading Docker Space files...")
            api.upload_file(
                path_or_fileobj=str(temp_dockerfile),
                path_in_repo="Dockerfile",
                repo_id=monitor_repo,
                repo_type="space",
                commit_message="feat: upload MLflow Dockerfile",
            )
            api.upload_file(
                path_or_fileobj=str(temp_proxy),
                path_in_repo="proxy.py",
                repo_id=monitor_repo,
                repo_type="space",
                commit_message="feat: upload reverse proxy script proxy.py",
            )
            api.upload_file(
                path_or_fileobj=str(temp_readme),
                path_in_repo="README.md",
                repo_id=monitor_repo,
                repo_type="space",
                commit_message="feat: upload Docker Space README.md",
            )
            print("  [OK] Docker Space upload complete.")
        except Exception as e:
            print(f"  [WARN] Failed to upload Docker Space files: {e}")
        finally:
            for f in (temp_dockerfile, temp_proxy, temp_readme):
                if f.exists():
                    f.unlink()

    print("\n[OK] Extra spaces completed!")

if __name__ == "__main__":
    main()
