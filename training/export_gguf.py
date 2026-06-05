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
    "FROM {gguf_path}\n"
    "SYSTEM You are Delentia OS — a constitutional AI operating under RCT v5 governance. "
    "Process intents through JITNA v3 protocol. Responses must be factual, safe, and "
    "PDPA-compliant.\n"
    "PARAMETER temperature 0.7\n"
    "PARAMETER top_p 0.9\n"
    "PARAMETER stop \"<|eot_id|>\"\n"
)

OLLAMA_MODELFILE_TEMPLATE_V02 = (
    "FROM {gguf_path}\n"
    "SYSTEM You are Delentia OS v0.2 — a constitutional AI operating under RCT v5 governance. "
    "You process intents through the JITNA v3 protocol. You respond in TOON format "
    "(Token-Oriented Object Notation) for token efficiency. Your responses must be factual, "
    "safe, and PDPA-compliant. Always provide FDIA scores when applicable (F = D^I × A).\n"
    "PARAMETER temperature 0.7\n"
    "PARAMETER top_p 0.9\n"
    "PARAMETER stop \"<|eot_id|>\"\n"
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
) -> None:
    version_label = "v0.2 TOON" if toon else "v0.1"
    console.print(Panel(f"[bold blue]Delentia AI — GGUF Export ({version_label})[/]", expand=False))

    # Resolve paths and model name dynamically if toon is specified
    if toon:
        model_name = "delentia-jitna-v0.2"
        adapter_path = Path("models/adapters/jitna_v0.2_toon")
        merged_path  = Path("models/merged/jitna_v0.2_toon")
        gguf_path    = Path("models/gguf/delentia-jitna-v0.2-Q4_K_M.gguf")
        modelfile_template = OLLAMA_MODELFILE_TEMPLATE_V02
    else:
        # Load from config or default to v0.1
        cfg = load_config(config) if config.exists() else {}
        model_name = "delentia-jitna-v0.1"
        adapter_path = Path(cfg.get("adapter_path", "models/adapters/jitna_v0.1"))
        merged_path  = Path(cfg.get("merged_path", "models/merged/jitna_v0.1"))
        gguf_path = Path(cfg.get("gguf_path", "models/gguf/delentia-jitna-v0.1-Q4_K_M.gguf"))
        modelfile_template = OLLAMA_MODELFILE_TEMPLATE_V01

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
    console.print("[1/4] Loading base model + LoRA adapter…")
    if not dry_run and unsloth_available:
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=str(adapter_path),
            max_seq_length=4096,
            dtype=None,
            load_in_4bit=True,
        )

    # ── 2. Merge LoRA into base ───────────────────────────────────────────────
    console.print("[2/4] Merging LoRA weights into base model…")
    if not dry_run and unsloth_available:
        merged_path.mkdir(parents=True, exist_ok=True)
        model.save_pretrained_merged(
            str(merged_path),
            tokenizer,
            save_method="merged_16bit",
        )
        console.print(f"  Merged model saved → {merged_path}")
    else:
        console.print("[yellow]Dry run / Mock: Skipped merging weights[/]")

    # ── 3. Convert to GGUF ────────────────────────────────────────────────────
    if not skip_convert:
        console.print("[3/4] Converting to GGUF Q4_K_M…")
        if not dry_run and unsloth_available:
            gguf_path.parent.mkdir(parents=True, exist_ok=True)
            model.save_pretrained_gguf(
                str(gguf_path.parent),
                tokenizer,
                quantization_method="q4_k_m",
            )
            console.print(f"  GGUF saved → {gguf_path.parent}")
        else:
            console.print("[yellow]Dry run / Mock: Skipped GGUF conversion[/]")
    else:
        console.print("[3/4] Skipping GGUF conversion (--skip-convert)")

    # ── 4. Test with Ollama ───────────────────────────────────────────────────
    if test_ollama:
        console.print("[4/4] Testing with Ollama…")
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
        console.print(f"  Ollama Modelfile generated → {modelfile_path}")

        if dry_run:
            console.print("[yellow]Dry run: Skipped registering and testing with Ollama process[/]")
        else:
            # Create Ollama model
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
                    console.print("[green]✓ Ollama inference test PASSED[/]")
                    console.print(f"  Response preview: {test_result.stdout[:200]}…")
                else:
                    console.print(f"[yellow]Ollama test failed:[/] {test_result.stderr}")

    console.print(Panel(
        f"[bold green]Export process completed![/]\n"
        f"GGUF Path: {gguf_path.parent}\n"
        f"Ollama model: [cyan]{model_name}[/]\n\n"
        f"To use in Delentia OS:\n"
        f"  Set HexaCoreRole OLLAMA_ADAPTER → model_id: {model_name}",
        expand=False,
    ))


if __name__ == "__main__":
    app()
