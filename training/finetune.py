#!/usr/bin/env python3
"""
finetune.py

Unsloth-accelerated QLoRA fine-tuning for the Delentia SLM.
Supports Base Kernel (v0.1/v0.2/v0.3) and 4-Pillar LoRA adapters.

Usage:
  python training/finetune.py
  python training/finetune.py --toon                              # TOON v0.2
  python training/finetune.py --pillar executor                   # The Executor
  python training/finetune.py --pillar guardian                   # The Guardian
  python training/finetune.py --pillar scribe                     # The Scribe
  python training/finetune.py --config training/config/slm_jitna_executor.yaml --pillar executor
  delentia-train  (if installed via pyproject.toml scripts)

Note: The Router uses finetune_classifier.py (Sequence Classification task).

Requirements:
  - GPU with >= 16 GB VRAM recommended (T4 16GB or A100 40GB)
  - Run: pip install -r requirements.txt
"""

from pathlib import Path

import mlflow
import typer
import yaml
from rich.console import Console
from rich.panel import Panel

from datasets import load_dataset

console = Console()
app = typer.Typer()

CONFIG_DEFAULT = Path(__file__).parent / "config" / "slm_jitna_v0.1.yaml"


def load_config(config_path: Path) -> dict:
    with config_path.open() as f:
        return yaml.safe_load(f)


# ── Pillar config auto-detection ──────────────────────────────────────────
PILLAR_CONFIGS = {
    "executor": Path(__file__).parent / "config" / "slm_jitna_executor.yaml",
    "guardian": Path(__file__).parent / "config" / "slm_jitna_guardian.yaml",
    "scribe":  Path(__file__).parent / "config" / "slm_jitna_scribe.yaml",
}

PILLAR_LABELS = {
    "executor": "The Executor (slm-jitna-agentic)",
    "guardian": "The Guardian (slm-jitna-guardian)",
    "scribe":  "The Scribe (slm-jitna-scribe)",
}
@app.command()
def main(
    config: Path = typer.Option(CONFIG_DEFAULT, help="YAML config file"),  # noqa: B008
    dry_run: bool = typer.Option(False, help="Validate setup without training"),  # noqa: B008
    toon: bool = typer.Option(False, "--toon", help="Train with TOON v0.2 format"),  # noqa: B008
    adapter_path: Path = typer.Option(None, help="LoRA adapter save directory"),  # noqa: B008
    pillar: str = typer.Option(None, help="Pillar type: executor, guardian, scribe (Router uses finetune_classifier.py)"),  # noqa: B008
    push_to_hub: bool = typer.Option(False, "--push-to-hub", help="Push checkpoints to HF Hub"),  # noqa: B008
):
    if pillar:
        pillar = pillar.lower()
        if pillar == "router":
            console.print("[red]The Router uses Sequence Classification. Use finetune_classifier.py instead.[/]")
            raise typer.Exit(1)
        if pillar not in PILLAR_CONFIGS:
            console.print(f"[red]Unknown pillar:[/] {pillar}. Valid: executor, guardian, scribe")
            raise typer.Exit(1)
        # Use pillar-specific config if user didn't provide a custom one
        if config == CONFIG_DEFAULT:
            config = PILLAR_CONFIGS[pillar]
        version_label = PILLAR_LABELS[pillar]
    elif toon:
        version_label = "v0.2 TOON"
    else:
        version_label = "v0.1"
    msg = f"[bold blue]Delentia AI — SLM Fine-tuning ({version_label})[/]"
    console.print(Panel(msg, expand=False))

    # ── Load config ───────────────────────────────────────────────────────────
    if not config.exists():
        console.print(f"[red]Config not found:[/] {config}")
        raise typer.Exit(1)

    cfg = load_config(config)
    model_cfg = cfg["model"]
    lora_cfg = cfg["lora"]
    train_cfg = cfg["training"]
    mlflow_cfg = cfg.get("mlflow", {})

    # Auto-redirect to local v0.4.1 base model if present (e.g. running on Google Colab after Step 9)
    local_base = Path("/content/delentia-base-v0.4.1-gguf")
    if local_base.exists() and (local_base / "config.json").exists():
        console.print(f"[yellow]Auto-redirecting base model from {model_cfg['base_model']} to local path {local_base}[/]")
        model_cfg["base_model"] = str(local_base)

    console.print(f"Base model: [cyan]{model_cfg['base_model']}[/]")
    console.print(f"Dataset:    [cyan]{train_cfg['dataset_path']}[/]")
    console.print(f"LoRA rank:  [cyan]{lora_cfg['r']}[/], alpha: [cyan]{lora_cfg['lora_alpha']}[/]")

    # ── Import Unsloth (lazy — heavy import) ─────────────────────────────────
    try:
        from unsloth import FastLanguageModel  # type: ignore
        unsloth_available = True
    except ImportError:
        unsloth_available = False
        if not dry_run:
            console.print("[red]unsloth not installed.[/] Run: pip install 'unsloth[colab-new]'")
            raise typer.Exit(1) from None
        console.print("[yellow]unsloth not installed — mocking FastLanguageModel for dry run.[/]")

    # ── Load base model ───────────────────────────────────────────────────────
    console.print("\n[1/5] Loading base model…")
    if unsloth_available:
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=model_cfg["base_model"],
            max_seq_length=model_cfg["max_seq_length"],
            dtype=model_cfg.get("dtype"),
            load_in_4bit=model_cfg.get("load_in_4bit", True),
        )
    else:
        from unittest.mock import MagicMock
        model = MagicMock()
        tokenizer = MagicMock()
        tokenizer.eos_token = "<|eot_id|>"

    # ── Apply LoRA adapter ────────────────────────────────────────────────────
    console.print("[2/5] Applying LoRA adapter…")
    if unsloth_available:
        model = FastLanguageModel.get_peft_model(
            model,
            r=lora_cfg["r"],
            lora_alpha=lora_cfg["lora_alpha"],
            lora_dropout=lora_cfg["lora_dropout"],
            bias=lora_cfg.get("bias", "none"),
            use_rslora=lora_cfg.get("use_rslora", True),
            target_modules=lora_cfg["target_modules"],
            use_gradient_checkpointing="unsloth",
        )
    else:
        pass


    # ── Load dataset ──────────────────────────────────────────────────────────
    console.print("[3/5] Loading dataset…")
    dataset_path = Path(train_cfg["dataset_path"])
    if not dataset_path.exists():
        console.print(
            f"[red]Dataset not found:[/] {dataset_path}\n"
            "Run: python datasets/scripts/extract_from_os.py"
        )
        raise typer.Exit(1)

    if dataset_path.suffix == ".parquet":
        raw = load_dataset("parquet", data_files=str(dataset_path), split="train")
    else:
        raw = load_dataset("json", data_files=str(dataset_path), split="train")
    if train_cfg.get("max_samples"):
        raw = raw.select(range(min(len(raw), train_cfg["max_samples"])))

    # Split train/validation
    val_split = train_cfg.get("validation_split", 0.05)
    split = raw.train_test_split(test_size=val_split, seed=42)
    train_ds = split["train"]
    eval_ds  = split["test"]
    console.print(f"  Train: {len(train_ds)}, Eval: {len(eval_ds)}")

    import re
    # Tokenize with TOON-aware chat template
    if toon:
        config_template = cfg.get("chat_template")
        if config_template:
            chat_template = re.sub(r'\{\{\s*(\w+)\s*\}\}', r'{\1}', config_template)
            if "{completion}" not in chat_template:
                chat_template = chat_template.rstrip() + "\n{completion}"
        else:
            chat_template = (
                "<|system|>\n"
                "You are Delentia OS v0.2 — a constitutional AI operating under RCT v5 governance. "
                "You process intents through the JITNA v3 protocol. "
                "You respond in TOON format (Token-Oriented Object Notation) for token efficiency. "
                "Your responses must be factual, safe, and PDPA-compliant. "
                "You must respond using the 6 JITNA fields: I=Intent, D=Data, Δ=Delta, A=Approach, R=Reflection, M=Memory.\n"
                "<|user|>\n{user_intent}\n"
                "<|assistant|>\n{completion}"
            )
    else:
        chat_template = cfg.get("chat_template", "{prompt}\n{completion}")
        chat_template = re.sub(r'\{\{\s*(\w+)\s*\}\}', r'{\1}', chat_template)

    def format_pair(example: dict) -> dict:
        if toon:
            prompt_str = example["prompt"]
            intent_marker = "User intent: "
            idx = prompt_str.find(intent_marker)
            if idx >= 0:
                raw_intent = prompt_str[idx + len(intent_marker):].strip()
            else:
                raw_intent = prompt_str.strip()

            text = chat_template.format(
                user_intent=raw_intent,
                completion=example["completion"],
            ) + tokenizer.eos_token
        else:
            prompt_str = example["prompt"]
            pillar_type = cfg.get("pillar_type")
            if pillar_type in ["executor", "guardian", "scribe"]:
                parts = prompt_str.split("\n\n", 1)
                if len(parts) > 1:
                    prompt_str = parts[1]
            text = chat_template.format(
                system_context=(
                    "You are Delentia OS — constitutional AI under RCT v5 governance."
                ),
                user_intent=prompt_str,
            ) + example["completion"] + tokenizer.eos_token
        return {"text": text}

    train_ds = train_ds.map(format_pair, batched=False)
    eval_ds  = eval_ds.map(format_pair, batched=False)

    if dry_run:
        console.print("[yellow]Dry run complete — skipping training.[/]")
        return

    # ── Train ─────────────────────────────────────────────────────────────────
    console.print("[4/5] Starting training…")
    import torch
    from trl import SFTConfig, SFTTrainer  # type: ignore

    # Auto-detect device and bfloat16 support
    supports_bf16 = False
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        supports_bf16 = torch.cuda.is_bf16_supported()
        console.print(f"  GPU detected: [cyan]{gpu_name}[/] (Supports BF16: [cyan]{supports_bf16}[/])")
    else:
        console.print("  [yellow]Warning:[/] No CUDA GPU detected. Using CPU fallback (Dry Run only).")

    # Override config precision based on GPU hardware capability
    use_bf16 = train_cfg.get("bf16", True) and supports_bf16
    use_fp16 = train_cfg.get("fp16", False) or (not use_bf16 and torch.cuda.is_available())
    console.print(f"  Training precision: bf16=[cyan]{use_bf16}[/], fp16=[cyan]{use_fp16}[/]")
    # MLflow tracking initialization
    mlflow_enabled = False
    mlflow_cfg = cfg.get("mlflow", {})
    tracking_uri = mlflow_cfg.get("tracking_uri", "http://localhost:5000")
    
    try:
        import os
        # Set authorization header if HF_TOKEN is available
        hf_token = os.environ.get("HF_TOKEN", "")
        if hf_token:
            os.environ["MLFLOW_TRACKING_HEADERS"] = f"Authorization: Bearer {hf_token}"
            
        mlflow.set_tracking_uri(tracking_uri)
        experiment_name = mlflow_cfg.get("experiment_name", "delentia-slm")
        mlflow.set_experiment(experiment_name)
        mlflow_enabled = True
        console.print(f"  MLflow tracking enabled on server: [cyan]{tracking_uri}[/]")
    except Exception as e:
        console.print(f"  [yellow]Warning:[/] Failed to initialize MLflow client ({e}). Training will proceed with local logging only.")

    report_to_list = ["mlflow"] if mlflow_enabled else []

    # Hugging Face Login for streaming checkpoints
    hf_token = os.environ.get("HF_TOKEN", "")
    hub_model_id = None
    if push_to_hub:
        if not hf_token:
            console.print("[red]Error: --push-to-hub is active but HF_TOKEN is not set.[/]")
            raise typer.Exit(1)
        try:
            from huggingface_hub import login
            login(token=hf_token)
            console.print("✅ Logged in to Hugging Face Hub successfully.")
            # Set Model ID
            if pillar:
                hub_model_id = f"delentia-labs/delentia-slm-jitna-{pillar}"
            elif toon:
                hub_model_id = "delentia-labs/delentia-slm-jitna-v0.2-toon"
            else:
                hub_model_id = "delentia-labs/delentia-slm-jitna-v0.1"
            console.print(f"  Hub Repository ID: [cyan]{hub_model_id}[/]")
        except Exception as e:
            console.print(f"  [red]Failed to login to Hugging Face Hub:[/] {e}")
            raise typer.Exit(1)

    import inspect
    sig = inspect.signature(SFTConfig.__init__)
    eval_strategy_key = "eval_strategy" if "eval_strategy" in sig.parameters else "evaluation_strategy"

    sft_config_kwargs = {
        "output_dir": train_cfg["output_dir"],
        "num_train_epochs": train_cfg["num_train_epochs"],
        "per_device_train_batch_size": train_cfg["per_device_train_batch_size"],
        "gradient_accumulation_steps": train_cfg["gradient_accumulation_steps"],
        "learning_rate": train_cfg["learning_rate"],
        "lr_scheduler_type": train_cfg["lr_scheduler_type"],
        "warmup_ratio": train_cfg["warmup_ratio"],
        "bf16": use_bf16,
        "fp16": use_fp16,
        "optim": train_cfg.get("optim", "adamw_8bit"),
        "weight_decay": train_cfg.get("weight_decay", 0.01),
        "max_grad_norm": train_cfg.get("max_grad_norm", 0.3),
        "save_strategy": "steps" if push_to_hub else train_cfg.get("save_strategy", "epoch"),
        "save_steps": 100 if push_to_hub else train_cfg.get("save_steps", 500),
        "save_total_limit": train_cfg.get("save_total_limit", 3),
        "logging_steps": train_cfg.get("logging_steps", 10),
        eval_strategy_key: train_cfg.get("eval_strategy") or train_cfg.get("evaluation_strategy", "epoch"),
        "load_best_model_at_end": train_cfg.get("load_best_model_at_end", True) if not push_to_hub else False,
        "metric_for_best_model": train_cfg.get("metric_for_best_model", "eval_loss"),
        "report_to": report_to_list,
        "dataset_text_field": "text",
        "max_seq_length": model_cfg["max_seq_length"],
        "push_to_hub": push_to_hub,
        "hub_model_id": hub_model_id,
        "hub_strategy": "every_save" if push_to_hub else "every_save",
        "hub_token": hf_token if push_to_hub else None,
        "packing": train_cfg.get("packing", False),
    }
    training_args = SFTConfig(**sft_config_kwargs)

    # Enable completion-only loss (loss masking) for specialized LoRA adapters
    data_collator = None
    if pillar in ["executor", "guardian", "scribe"]:
        try:
            from trl import DataCollatorForCompletionOnlyLM
            response_template = "<|assistant|>\n"
            data_collator = DataCollatorForCompletionOnlyLM(
                response_template=response_template,
                tokenizer=tokenizer,
                mlm=False
            )
            console.print("  [green]Enabled completion-only loss masking with response template '[cyan]<|assistant|>\\n[/]'[/]")
        except ImportError:
            console.print("  [yellow]Warning:[/] Could not import DataCollatorForCompletionOnlyLM. Standard loss will be used.")

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_ds,
        eval_dataset=eval_ds,
        data_collator=data_collator,
        args=training_args,
    )

    if mlflow_enabled:
        try:
            with mlflow.start_run():
                mlflow.log_params({
                    "base_model": model_cfg["base_model"],
                    "lora_r": lora_cfg["r"],
                    "lora_alpha": lora_cfg["lora_alpha"],
                    "epochs": train_cfg["num_train_epochs"],
                    "lr": train_cfg["learning_rate"],
                    "train_size": len(train_ds),
                    "toon_format": toon,
                    "version": version_label,
                })
                train_result = trainer.train()
                mlflow.log_metrics({
                    "train_loss": train_result.training_loss,
                    "train_steps": train_result.global_step,
                })
        except Exception as e:
            console.print(f"  [red]MLflow Error during logging:[/] {e}")
            console.print("  Proceeding to run training without MLflow tracking...")
            train_result = trainer.train()
    else:
        train_result = trainer.train()

    # ── Save adapter ──────────────────────────────────────────────────────────────────
    console.print("[5/5] Saving LoRA adapter…")
    if adapter_path is None:
        # Check config for pillar-specific save path
        adapter_save = cfg.get("adapter_save_path")
        if adapter_save:
            adapter_path = Path(adapter_save)
        elif toon:
            adapter_path = Path("models/adapters/jitna_v0.2_toon")
        else:
            adapter_path = Path("models/adapters/jitna_v0.1")
    else:
        adapter_path = Path(adapter_path)
    model.save_pretrained(str(adapter_path))
    tokenizer.save_pretrained(str(adapter_path))
    console.print(f"[bold green]Adapter saved → {adapter_path}[/]")
    if push_to_hub:
        console.print("[bold blue]Pushing final adapter weights to Hugging Face Hub…[/]")
        try:
            trainer.push_to_hub()
            console.print("🎉 Final adapter weights pushed to Hugging Face Hub successfully!")
        except Exception as e:
            console.print(f"  [red]Failed to push final weights to Hugging Face Hub:[/] {e}")
    console.print("\nNext steps:")
    if pillar:
        console.print(f"  python training/evaluate.py --pillar {pillar}")
        console.print(f"  python training/export_gguf.py --pillar {pillar}")
    else:
        console.print("  python training/evaluate.py")
        console.print("  python training/export_gguf.py")


if __name__ == "__main__":
    app()
