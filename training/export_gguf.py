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
  delentia-export  (installed script)
"""

import subprocess
import sys
from pathlib import Path

import typer
import yaml
from rich.console import Console
from rich.panel import Panel

console = Console()
app = typer.Typer()

CONFIG_DEFAULT = Path(__file__).parent / "config" / "lora_config.yaml"

OLLAMA_MODEL_NAME = "delentia-jitna-v0.1"
OLLAMA_MODELFILE_TEMPLATE = """\
FROM {gguf_path}
SYSTEM You are Delentia OS — a constitutional AI operating under RCT v5 governance. Process intents through JITNA v3 protocol. Responses must be factual, safe, and PDPA-compliant.
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER stop "<|eot_id|>"
"""


def load_config(path: Path) -> dict:
    with path.open() as f:
        return yaml.safe_load(f)


@app.command()
def main(
    config: Path = typer.Option(CONFIG_DEFAULT, help="LoRA config YAML"),
    test_ollama: bool = typer.Option(True, help="Test with Ollama after export"),
    skip_convert: bool = typer.Option(False, help="Skip GGUF conversion (if already done)"),
) -> None:
    console.print(Panel("[bold blue]Delentia AI — GGUF Export[/]", expand=False))

    cfg = load_config(config)
    adapter_path = Path(cfg["adapter_path"])
    merged_path  = Path(cfg["merged_path"])
    gguf_path    = Path(cfg["gguf_path"])

    # ── 1. Load base + adapter ────────────────────────────────────────────────
    console.print("[1/4] Loading base model + LoRA adapter…")
    try:
        from unsloth import FastLanguageModel  # type: ignore
    except ImportError:
        console.print("[red]unsloth not installed.[/] Run: pip install 'unsloth[colab-new]'")
        raise typer.Exit(1)

    if not adapter_path.exists():
        console.print(f"[red]Adapter not found:[/] {adapter_path}")
        raise typer.Exit(1)

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=str(adapter_path),
        max_seq_length=4096,
        dtype=None,
        load_in_4bit=True,
    )

    # ── 2. Merge LoRA into base ───────────────────────────────────────────────
    console.print("[2/4] Merging LoRA weights into base model…")
    merged_path.mkdir(parents=True, exist_ok=True)
    model.save_pretrained_merged(
        str(merged_path),
        tokenizer,
        save_method="merged_16bit",
    )
    console.print(f"  Merged model saved → {merged_path}")

    # ── 3. Convert to GGUF ────────────────────────────────────────────────────
    if not skip_convert:
        console.print("[3/4] Converting to GGUF Q4_K_M…")
        gguf_path.parent.mkdir(parents=True, exist_ok=True)

        # Unsloth's built-in GGUF export (wraps llama.cpp convert + quantize)
        model.save_pretrained_gguf(
            str(gguf_path.parent),
            tokenizer,
            quantization_method="q4_k_m",
        )
        console.print(f"  GGUF saved → {gguf_path.parent}")
    else:
        console.print("[3/4] Skipping GGUF conversion (--skip-convert)")

    # ── 4. Test with Ollama ───────────────────────────────────────────────────
    if test_ollama:
        console.print("[4/4] Testing with Ollama…")

        # Find the exported GGUF file
        gguf_files = list(gguf_path.parent.glob("*.gguf"))
        if not gguf_files:
            console.print("[yellow]No .gguf file found — skipping Ollama test[/]")
            return

        gguf_file = gguf_files[0]
        modelfile_path = Path("models/Modelfile")
        modelfile_path.parent.mkdir(exist_ok=True)
        modelfile_path.write_text(
            OLLAMA_MODELFILE_TEMPLATE.format(gguf_path=gguf_file.absolute())
        )

        # Create Ollama model
        result = subprocess.run(
            ["ollama", "create", OLLAMA_MODEL_NAME, "-f", str(modelfile_path)],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            console.print(f"[yellow]Ollama create failed:[/] {result.stderr}")
            console.print("  Install Ollama: https://ollama.com")
        else:
            console.print(f"[green]Ollama model created:[/] {OLLAMA_MODEL_NAME}")

            # Quick sanity test
            test_result = subprocess.run(
                ["ollama", "run", OLLAMA_MODEL_NAME,
                 "List 3 key features of Delentia OS JITNA v3 protocol."],
                capture_output=True, text=True, timeout=60
            )
            if test_result.returncode == 0:
                console.print("[green]✓ Ollama inference test PASSED[/]")
                console.print(f"  Response preview: {test_result.stdout[:200]}…")
            else:
                console.print(f"[yellow]Ollama test failed:[/] {test_result.stderr}")

    console.print(Panel(
        f"[bold green]Export complete![/]\n"
        f"GGUF: {gguf_path.parent}\n"
        f"Ollama model: [cyan]{OLLAMA_MODEL_NAME}[/]\n\n"
        f"To use in Delentia OS:\n"
        f"  Set HexaCoreRole OLLAMA_ADAPTER → model_id: {OLLAMA_MODEL_NAME}",
        expand=False,
    ))


if __name__ == "__main__":
    app()
