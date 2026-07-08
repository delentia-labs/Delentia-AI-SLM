#!/usr/bin/env python3
"""
export_gguf.py

Merges the LoRA adapter into the base model and exports to GGUF Q4_K_M format
for use with Ollama (OLLAMA_ADAPTER HexaCore role in Delentia OS).

Pipeline:
  1. Load base model + LoRA adapter
  2. Merge LoRA weights into base model
  3. Save merged HuggingFace model
  4. Convert to GGUF Q4_K_M via llama.cpp's convert script
  5. Test with Ollama (optional, requires Ollama installed)

Usage:
  python training/export_gguf.py
  python training/export_gguf.py --toon
  python training/export_gguf.py --dry-run --toon
  delentia-export  (installed script)
"""

import subprocess
from pathlib import Path

import typer
import yaml
from rich.console import Console
from rich.panel import Panel

console = Console()
app = typer.Typer()

CONFIG_DEFAULT = Path(__file__).parent / "config" / "lora_config.yaml"

OLLAMA_MODELFILE_TEMPLATE_V01 = (
    "FROM {gguf_path}\n\n"
    "TEMPLATE \"\"\"{{ if .System }}<|system|>\n"
    "{{ .System }}\n"
    "{{ end }}{{ if .Prompt }}<|user|>\n"
    "{{ .Prompt }}\n"
    "{{ end }}<|assistant|>\n"
    "\"\"\"\n\n"
    "SYSTEM \"\"\"คุณคือ Delentia AI v0.4.1 (Cognitive AI OS)\n"
    "กฎเหล็ก: จงตอบคำถามผู้ใช้อย่างเป็นธรรมชาติและยืดหยุ่น ห้ามคัดลอกข้อความยาวๆ ซ้ำๆ มาตอบเด็ดขาด ห้ามพิมพ์แท็กควบคุมเด็ดขาด\n\n"
    "ข้อมูลอ้างอิงสำหรับการประมวลผล (จงนำไปเรียบเรียงคำตอบเองตามบริบทคำถาม):\n"
    "- ผู้สร้าง: คุณอิทธิฤทธิ์ แซ่โง้ว (Ittirit Saengow) เป็นสถาปนิกและผู้พัฒนาเดี่ยว (Solo Developer & Architect) จากชุมชนคลองเตย กรุงเทพฯ พัฒนาบนเครื่อง ROG Ally X ในกรอบเวลา 30 วัน เริ่มต้น 11 สิงหาคม 2568\n"
    "- กรอบความปลอดภัย: สมการ FDIA -> F = (D^I) * A (A คือสถาปนิกมนุษย์ผู้มีสิทธิ์ Veto หาก A = 0 ผลลัพธ์ F = 0 เสมอ)\n"
    "- สถาปัตยกรรมคิดย้อนกลับ: RCT-7 Steps -> สังเกต (Observe) > วิเคราะห์ (Analyze) > แยกส่วน (Deconstruct) > คิดย้อนกลับ (Reverse Reasoning) > ระบุเจตนาหลัก (Identify Core Intent) > สร้างใหม่ (Reconstruct) > เปรียบเทียบกับเจตนา (Compare)\"\"\"\n\n"
    "PARAMETER temperature 0.3\n"
    "PARAMETER top_p 0.9\n"
    "PARAMETER repeat_penalty 1.02\n"
    "PARAMETER stop \"<|eot_id|>\"\n"
    "PARAMETER stop \"<|end_of_text|>\"\n"
    "PARAMETER stop \"<|user|>\"\n"
    "PARAMETER stop \"<|system|>\"\n"
    "PARAMETER stop \"<|assistant|>\"\n"
)

OLLAMA_MODELFILE_TEMPLATE_V02 = (
    "FROM {gguf_path}\n\n"
    "TEMPLATE \"\"\"{{ if .System }}<|system|>\n"
    "{{ .System }}\n"
    "{{ end }}{{ if .Prompt }}<|user|>\n"
    "{{ .Prompt }}\n"
    "{{ end }}<|assistant|>\n"
    "\"\"\"\n\n"
    "SYSTEM You are Delentia OS v0.2 — a constitutional AI operating under RCT v5 governance. "
    "You process intents through the JITNA v3 protocol. You respond in TOON format "
    "(Token-Oriented Object Notation) for token efficiency. Your responses must be factual, "
    "safe, and PDPA-compliant. You must respond using the 6 JITNA fields: I=Intent, D=Data, Δ=Delta, A=Approach, R=Reflection, M=Memory.\n\n"
    "PARAMETER temperature 0.7\n"
    "PARAMETER top_p 0.9\n"
    "PARAMETER repeat_penalty 1.15\n"
    "PARAMETER stop \"<|eot_id|>\"\n"
    "PARAMETER stop \"<|end_of_text|>\"\n"
    "PARAMETER stop \"<|user|>\"\n"
    "PARAMETER stop \"<|system|>\"\n"
    "PARAMETER stop \"<|assistant|>\"\n"
)


OLLAMA_MODELFILE_TEMPLATE_EXECUTOR = (
    "FROM {gguf_path}\n\n"
    "TEMPLATE \"\"\"{{ if .System }}<|system|>\n"
    "{{ .System }}\n"
    "{{ end }}{{ if .Prompt }}<|user|>\n"
    "{{ .Prompt }}\n"
    "{{ end }}<|assistant|>\n"
    "\"\"\"\n\n"
    "SYSTEM You are The Executor (slm-jitna-agentic) — a specialized LoRA adapter "
    "within the Delentia OS 1+4 Pillar Architecture. Your ONLY purpose is to convert "
    "user intents into machine-executable JSON payloads. You must NEVER produce natural "
    "language explanations. Output ONLY valid JSON — no markdown, no text, no comments. "
    "Your output must pass json.loads() without error.\n\n"
    "PARAMETER temperature 0.0\n"
    "PARAMETER top_p 0.9\n"
    "PARAMETER repeat_penalty 1.15\n"
    "PARAMETER stop \"<|eot_id|>\"\n"
    "PARAMETER stop \"<|end_of_text|>\"\n"
    "PARAMETER stop \"<|user|>\"\n"
    "PARAMETER stop \"<|system|>\"\n"
    "PARAMETER stop \"<|assistant|>\"\n"
)

OLLAMA_MODELFILE_TEMPLATE_GUARDIAN = (
    "FROM {gguf_path}\n\n"
    "TEMPLATE \"\"\"{{ if .System }}<|system|>\n"
    "{{ .System }}\n"
    "{{ end }}{{ if .Prompt }}<|user|>\n"
    "{{ .Prompt }}\n"
    "{{ end }}<|assistant|>\n"
    "\"\"\"\n\n"
    "SYSTEM You are The Guardian (slm-jitna-guardian) — a specialized Constitutional AI "
    "safety evaluator within the Delentia OS 1+4 Pillar Architecture. Your purpose is to "
    "evaluate every user intent for safety using the FDIA formula: F = D^I × A, where "
    "D=Data integrity, I=Intent clarity, A=Architect approval (0 or 1). Output ONLY a JSON "
    "verdict. If the intent is harmful, set A=0 and status=REJECTED. If safe, set A=1 and "
    "status=AUTHORIZED.\n\n"
    "PARAMETER temperature 0.0\n"
    "PARAMETER top_p 0.9\n"
    "PARAMETER repeat_penalty 1.15\n"
    "PARAMETER stop \"<|eot_id|>\"\n"
    "PARAMETER stop \"<|end_of_text|>\"\n"
    "PARAMETER stop \"<|user|>\"\n"
    "PARAMETER stop \"<|system|>\"\n"
    "PARAMETER stop \"<|assistant|>\"\n"
)

OLLAMA_MODELFILE_TEMPLATE_SCRIBE = (
    "FROM {gguf_path}\n\n"
    "TEMPLATE \"\"\"{{ if .System }}<|system|>\n"
    "{{ .System }}\n"
    "{{ end }}{{ if .Prompt }}<|user|>\n"
    "{{ .Prompt }}\n"
    "{{ end }}<|assistant|>\n"
    "\"\"\"\n\n"
    "SYSTEM You are The Scribe (slm-jitna-scribe) — a specialized LoRA adapter "
    "within the Delentia OS 1+4 Pillar Architecture. Your purpose is to compress large "
    "contexts into minimal, high-signal summaries. Remove noise. Keep only actionable "
    "information. Output must be structured and token-efficient. Report compression statistics "
    "in every response.\n\n"
    "PARAMETER temperature 0.3\n"
    "PARAMETER top_p 0.9\n"
    "PARAMETER repeat_penalty 1.15\n"
    "PARAMETER stop \"<|eot_id|>\"\n"
    "PARAMETER stop \"<|end_of_text|>\"\n"
    "PARAMETER stop \"<|user|>\"\n"
    "PARAMETER stop \"<|system|>\"\n"
    "PARAMETER stop \"<|assistant|>\"\n"
)


def load_config(path: Path) -> dict:
    with path.open() as f:
        return yaml.safe_load(f)


@app.command()
def main(
    config: Path = typer.Option(CONFIG_DEFAULT, help="LoRA config YAML"),  # noqa: B008
    test_ollama: bool = typer.Option(True, help="Test with Ollama after export"),  # noqa: B008
    skip_convert: bool = typer.Option(False, help="Skip GGUF conversion (if already done)"),  # noqa: B008
    toon: bool = typer.Option(False, "--toon", help="Export TOON v0.2 model"),  # noqa: B008
    dry_run: bool = typer.Option(False, "--dry-run", help="Validate setup without exporting"),  # noqa: B008
    adapter_path: Path = typer.Option(None, help="LoRA adapter directory"),  # noqa: B008
    gguf_path: Path = typer.Option(None, help="GGUF export file path"),  # noqa: B008
    model_name: str = typer.Option(None, help="Ollama model register name"),  # noqa: B008
    merged_path: Path = typer.Option(None, help="HuggingFace merged model output directory"),  # noqa: B008
    pillar: str = typer.Option(None, help="Pillar type: executor, guardian, scribe (Router classification adapter doesn't use GGUF)"),  # noqa: B008
    quant: str = typer.Option("q4_k_m", "--quant", help="GGUF quantization method (e.g., q4_k_m, q8_0)"),  # noqa: B008
    imatrix_calib: Path = typer.Option(Path("datasets/processed/delentia_v042_imatrix_calib.txt"), help="Path to custom imatrix calibration text"),  # noqa: B008
    use_imatrix: bool = typer.Option(True, help="Use custom JITNA-TOON IMatrix quantization"),  # noqa: B008
) -> None:
    version_label = f"Pillar: {pillar.upper()}" if pillar else ("v0.2 TOON" if toon else "v0.1")
    console.print(Panel(f"[bold blue]Delentia AI - GGUF Export ({version_label}) (Quant: {quant})[/]", expand=False))

    # Resolve paths and model name dynamically
    if pillar:
        pillar = pillar.lower()
        if pillar == "router":
            console.print("[red]The Router uses sequence classification and is loaded directly in python backend via PEFT. GGUF export is not required for the Router.[/]")
            raise typer.Exit(1)
        elif pillar == "executor":
            def_model_name = "delentia-jitna-executor"
            def_adapter_path = Path("models/adapters/jitna_executor_v0.4.1")
            def_merged_path  = Path("models/merged/jitna_executor_v0.4.1")
            def_gguf_path    = Path(f"models/gguf/delentia-jitna-executor-{quant.upper()}.gguf")
            modelfile_template = OLLAMA_MODELFILE_TEMPLATE_EXECUTOR
        elif pillar == "guardian":
            def_model_name = "delentia-jitna-guardian"
            def_adapter_path = Path("models/adapters/jitna_guardian_v0.4.1")
            def_merged_path  = Path("models/merged/jitna_guardian_v0.4.1")
            def_gguf_path    = Path(f"models/gguf/delentia-jitna-guardian-{quant.upper()}.gguf")
            modelfile_template = OLLAMA_MODELFILE_TEMPLATE_GUARDIAN
        elif pillar == "scribe":
            def_model_name = "delentia-jitna-scribe"
            def_adapter_path = Path("models/adapters/jitna_scribe_v0.4.1")
            def_merged_path  = Path("models/merged/jitna_scribe_v0.4.1")
            def_gguf_path    = Path(f"models/gguf/delentia-jitna-scribe-{quant.upper()}.gguf")
            modelfile_template = OLLAMA_MODELFILE_TEMPLATE_SCRIBE
        else:
            console.print(f"[red]Unknown pillar:[/] {pillar}. Valid: executor, guardian, scribe")
            raise typer.Exit(1)
    elif toon:
        def_model_name = "delentia-jitna-v0.2"
        def_adapter_path = Path("models/adapters/jitna_v0.2_toon")
        def_merged_path  = Path("models/merged/jitna_v0.2_toon")
        def_gguf_path    = Path(f"models/gguf/delentia-jitna-v0.2-{quant.upper()}.gguf")
        modelfile_template = OLLAMA_MODELFILE_TEMPLATE_V02
    else:
        # Load from config or default to v0.1
        cfg = load_config(config) if config.exists() else {}
        def_model_name = "delentia-jitna-v0.1"
        def_adapter_path = Path(cfg.get("adapter_path", "models/adapters/jitna_v0.1"))
        def_merged_path  = Path(cfg.get("merged_path", "models/merged/jitna_v0.1"))
        def_gguf_path = Path(cfg.get("gguf_path", f"models/gguf/delentia-jitna-v0.1-{quant.upper()}.gguf"))
        modelfile_template = OLLAMA_MODELFILE_TEMPLATE_V01

    model_name = model_name or def_model_name
    adapter_path = Path(adapter_path).resolve() if adapter_path else def_adapter_path.resolve()
    merged_path = Path(merged_path).resolve() if merged_path else def_merged_path.resolve()
    gguf_path = Path(gguf_path).resolve() if gguf_path else def_gguf_path.resolve()

    console.print(f"Model Name:   [cyan]{model_name}[/]")
    console.print(f"Adapter Path: [cyan]{adapter_path}[/]")
    console.print(f"Merged Path:  [cyan]{merged_path}[/]")
    console.print(f"GGUF Path:    [cyan]{gguf_path}[/]")

    # Check unsloth is available unless dry run
    try:
        from unsloth import FastLanguageModel  # type: ignore
        unsloth_available = True
    except ImportError:
        unsloth_available = False
        if not dry_run:
            console.print("[red]unsloth not installed.[/] Run: pip install 'unsloth[colab-new]'")
            raise typer.Exit(1) from None
        console.print("[yellow]unsloth not installed — mocking export pipeline for dry run.[/]")

    if not dry_run and not adapter_path.exists():
        console.print(f"[red]Adapter not found:[/] {adapter_path}")
        raise typer.Exit(1)

    # ── 1. Load base + adapter ────────────────────────────────────────────────
    console.print("[1/4] Loading base model + LoRA adapter...")
    if not dry_run and unsloth_available:
        max_seq_len = 8192 if (pillar and pillar.lower() == "scribe") else 4096
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=str(adapter_path),
            max_seq_length=max_seq_len,
            dtype=None,
            load_in_4bit=True,
        )

    # ── 2. Merge LoRA into base ───────────────────────────────────────────────
    console.print("[2/4] Merging LoRA weights into base model...")
    if not dry_run and unsloth_available:
        merged_path.mkdir(parents=True, exist_ok=True)
        model.save_pretrained_merged(
            str(merged_path),
            tokenizer,
            save_method="merged_16bit",
        )
        console.print(f"  Merged model saved -> {merged_path}")
    else:
        console.print("[yellow]Dry run / Mock: Skipped merging weights[/]")


    # ── 3. Convert to GGUF ────────────────────────────────────────────────────
    if not skip_convert:
        console.print(f"[3/4] Converting to GGUF {quant}...")
        if not dry_run and unsloth_available:
            gguf_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Setup optional IMatrix parameters for precision preservation of TOON layout
            save_kwargs = {}
            if use_imatrix and imatrix_calib.exists():
                console.print(f"  [IMATRIX] Applying custom JITNA-TOON calibration dataset -> {imatrix_calib}")
                save_kwargs["imatrix_path"] = str(imatrix_calib)
            elif use_imatrix:
                console.print(f"  [WARN] Custom calibration file {imatrix_calib} not found. Proceeding with standard quantization.")
                
            model.save_pretrained_gguf(
                str(gguf_path.parent),
                tokenizer,
                quantization_method=quant,
                **save_kwargs
            )
            # Locate and move the opinionated file path Unsloth creates
            unsloth_gguf_dir = Path(str(gguf_path.parent) + "_gguf")
            if unsloth_gguf_dir.exists():
                generated_files = list(unsloth_gguf_dir.glob("*.gguf"))
                if generated_files:
                    generated_file = generated_files[0]
                    if gguf_path.exists():
                        gguf_path.unlink()
                    import shutil
                    shutil.move(str(generated_file), str(gguf_path))
                    console.print(f"  [OK] Moved GGUF model to target path: {gguf_path}")
                    shutil.rmtree(str(unsloth_gguf_dir), ignore_errors=True)
                else:
                    console.print("[yellow]Warning: No GGUF files found in Unsloth output directory.[/]")
            console.print(f"  GGUF saved -> {gguf_path}")
        else:
            console.print("[yellow]Dry run / Mock: Skipped GGUF conversion[/]")
    else:
        console.print("[3/4] Skipping GGUF conversion (--skip-convert)")

    # ── 4. Test with Ollama ───────────────────────────────────────────────────
    if test_ollama:
        console.print("[4/4] Testing with Ollama...")
        gguf_file = gguf_path
        # In dry run, or if gguf file doesn't exist, create a mock file
        # to verify Modelfile generation.
        if dry_run or not gguf_file.exists():
            gguf_file = gguf_path.parent / gguf_path.name
            gguf_file.parent.mkdir(parents=True, exist_ok=True)
            if not gguf_file.exists():
                gguf_file.write_text("mock gguf content")

        modelfile_path = Path("models/Modelfile")
        modelfile_path.parent.mkdir(exist_ok=True)
        modelfile_path.write_text(
            modelfile_template.format(gguf_path=gguf_file.absolute()),
            encoding="utf-8"
        )
        console.print(f"  Ollama Modelfile generated -> {modelfile_path}")

        if dry_run:
            console.print("[yellow]Dry run: Skipped registering and testing with Ollama process[/]")
        else:
            # Create Ollama model
            try:
                result = subprocess.run(
                    ["ollama", "create", model_name, "-f", str(modelfile_path)],
                    capture_output=True, text=True
                )
                if result.returncode != 0:
                    console.print(f"[yellow]Ollama create failed:[/] {result.stderr}")
                    console.print("  Install Ollama: https://ollama.com")
                else:
                    console.print(f"[green]Ollama model created:[/] {model_name}")

                    # Quick sanity test
                    test_result = subprocess.run(
                        ["ollama", "run", model_name,
                         "List 3 key features of Delentia OS JITNA v3 protocol."],
                        capture_output=True, text=True, timeout=60
                    )
                    if test_result.returncode == 0:
                        console.print("[green][OK] Ollama inference test PASSED[/]")
                        console.print(f"  Response preview: {test_result.stdout[:200]}...")
                    else:
                        console.print(f"[yellow]Ollama test failed:[/] {test_result.stderr}")
            except FileNotFoundError:
                console.print("[yellow]Warning: ollama command not found on this system. Skipping Ollama model registration.[/]")
                console.print("  To install Ollama, visit: https://ollama.com")

    console.print(Panel(
        f"[bold green]Export process completed![/]\n"
        f"GGUF Path: {gguf_path.parent}\n"
        f"Ollama model: [cyan]{model_name}[/]\n\n"
        f"To use in Delentia OS:\n"
        f"  Set HexaCoreRole OLLAMA_ADAPTER -> model_id: {model_name}",
        expand=False,
    ))


if __name__ == "__main__":
    app()
