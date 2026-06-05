#!/usr/bin/env python3
"""
finetune.py

Unsloth-accelerated QLoRA fine-tuning for the Delentia SLM.
Configuration: training/config/slm_jitna_v0.1.yaml (or v0.2 for TOON)

Usage:
  python training/finetune.py
  python training/finetune.py --toon           # TOON v0.2 format training
  python training/finetune.py --config training/config/slm_jitna_v0.2.yaml --toon
  delentia-train  (if installed via pyproject.toml scripts)

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


@app.command()
def main(
    config: Path = typer.Option(CONFIG_DEFAULT, help="YAML config file"),  # noqa: B008
    dry_run: bool = typer.Option(False, help="Validate setup without training"),  # noqa: B008
    toon: bool = typer.Option(False, "--toon", help="Train with TOON v0.2 format"),  # noqa: B008
) -> None:
    version_label = "v0.2 TOON" if toon else "v0.1"
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

    raw = load_dataset("json", data_files=str(dataset_path), split="train")
    if train_cfg.get("max_samples"):
        raw = raw.select(range(min(len(raw), train_cfg["max_samples"])))

    # Split train/validation
    val_split = train_cfg.get("validation_split", 0.05)
    split = raw.train_test_split(test_size=val_split, seed=42)
    train_ds = split["train"]
    eval_ds  = split["test"]
    console.print(f"  Train: {len(train_ds)}, Eval: {len(eval_ds)}")

    # Tokenize with TOON-aware chat template
    if toon:
        chat_template = (
            "<|system|>\n"
            "You are Delentia OS v0.2 — a constitutional AI under RCT v5 governance. "
            "You respond in TOON format (Token-Oriented Object Notation).\n"
            "<|user|>\n{user_intent}\n"
            "<|assistant|>\n{completion}"
        )
    else:
        chat_template = cfg.get("chat_template", "{prompt}\n{completion}")

    def format_pair(example: dict) -> dict:
        if toon:
            text = chat_template.format(
                user_intent=example["prompt"],
                completion=example["completion"],
            ) + tokenizer.eos_token
        else:
            text = chat_template.format(
                system_context=(
                    "You are Delentia OS — constitutional AI under RCT v5 governance."
                ),
                user_intent=example["prompt"],
            ) + example["completion"] + tokenizer.eos_token
        return {"text": text}

    train_ds = train_ds.map(format_pair, batched=False)
    eval_ds  = eval_ds.map(format_pair, batched=False)

    if dry_run:
        console.print("[yellow]Dry run complete — skipping training.[/]")
        return

    # ── Train ─────────────────────────────────────────────────────────────────
    console.print("[4/5] Starting training…")
    from transformers import TrainingArguments  # type: ignore
    from trl import SFTTrainer  # type: ignore

    training_args = TrainingArguments(
        output_dir=train_cfg["output_dir"],
        num_train_epochs=train_cfg["num_train_epochs"],
        per_device_train_batch_size=train_cfg["per_device_train_batch_size"],
        gradient_accumulation_steps=train_cfg["gradient_accumulation_steps"],
        learning_rate=train_cfg["learning_rate"],
        lr_scheduler_type=train_cfg["lr_scheduler_type"],
        warmup_ratio=train_cfg["warmup_ratio"],
        bf16=train_cfg.get("bf16", True),
        fp16=train_cfg.get("fp16", False),
        optim=train_cfg.get("optim", "adamw_8bit"),
        weight_decay=train_cfg.get("weight_decay", 0.01),
        max_grad_norm=train_cfg.get("max_grad_norm", 0.3),
        save_strategy=train_cfg.get("save_strategy", "epoch"),
        save_total_limit=train_cfg.get("save_total_limit", 3),
        logging_steps=train_cfg.get("logging_steps", 10),
        evaluation_strategy=train_cfg.get("evaluation_strategy", "epoch"),
        load_best_model_at_end=train_cfg.get("load_best_model_at_end", True),
        metric_for_best_model=train_cfg.get("metric_for_best_model", "eval_loss"),
        report_to="none",  # MLflow handled separately
    )

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_ds,
        eval_dataset=eval_ds,
        dataset_text_field="text",
        max_seq_length=model_cfg["max_seq_length"],
        args=training_args,
    )

    # MLflow tracking
    mlflow.set_tracking_uri(mlflow_cfg.get("tracking_uri", "http://localhost:5000"))
    mlflow.set_experiment(mlflow_cfg.get("experiment_name", "delentia-slm"))

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

    # ── Save adapter ──────────────────────────────────────────────────────────────────
    console.print("[5/5] Saving LoRA adapter…")
    adapter_version = "jitna_v0.2_toon" if toon else "jitna_v0.1"
    adapter_path = f"models/adapters/{adapter_version}"
    model.save_pretrained(adapter_path)
    tokenizer.save_pretrained(adapter_path)
    console.print(f"[bold green]Adapter saved → {adapter_path}[/]")
    console.print("\nNext steps:")
    console.print("  python training/evaluate.py")
    console.print("  python training/export_gguf.py")


if __name__ == "__main__":
    app()
