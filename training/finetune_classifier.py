#!/usr/bin/env python3
"""
finetune_classifier.py

Sequence Classification fine-tuning for The Router (slm-jitna-router) using Hugging Face PEFT.
Loads a base model in 4-bit, replaces the head with a classification head,
and trains a SEQ_CLS LoRA adapter to categorize user intents.

Usage:
  python training/finetune_classifier.py
  python training/finetune_classifier.py --dry-run
"""

from pathlib import Path

import mlflow
import numpy as np
import torch
import typer
import yaml
from peft import LoraConfig, TaskType, get_peft_model
from rich.console import Console
from rich.panel import Panel
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    BitsAndBytesConfig,
    Trainer,
    TrainingArguments,
)

from datasets import load_dataset

console = Console()
app = typer.Typer()

CONFIG_DEFAULT = Path(__file__).parent / "config" / "slm_jitna_router.yaml"


def load_config(config_path: Path) -> dict:
    with config_path.open() as f:
        return yaml.safe_load(f)


def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    preds = np.argmax(predictions, axis=1)
    acc = float((preds == labels).mean())
    
    # Compute manual macro F1 score
    f1s = []
    for c in range(4):  # We have exactly 4 routing labels
        tp = np.sum((preds == c) & (labels == c))
        fp = np.sum((preds == c) & (labels != c))
        fn = np.sum((preds != c) & (labels == c))
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        f1s.append(f1)
        
    f1_macro = float(np.mean(f1s))
    return {"accuracy": acc, "f1_macro": f1_macro}


@app.command()
def main(
    config: Path = typer.Option(CONFIG_DEFAULT, help="YAML config file"),  # noqa: B008
    dry_run: bool = typer.Option(False, help="Validate setup without training"),  # noqa: B008
    adapter_path: Path = typer.Option(None, help="LoRA adapter save directory"),  # noqa: B008
) -> None:
    msg = "[bold blue]Delentia AI — SLM Sequence Classification (The Router)[/]"
    console.print(Panel(msg, expand=False))

    # ── Load config ───────────────────────────────────────────────────────────
    if not config.exists():
        console.print(f"[red]Config not found:[/] {config}")
        raise typer.Exit(1)

    cfg = load_config(config)
    model_cfg = cfg["model"]
    lora_cfg = cfg["lora"]
    class_cfg = cfg["classification"]
    train_cfg = cfg["training"]
    mlflow_cfg = cfg.get("mlflow", {})

    console.print(f"Base model: [cyan]{model_cfg['base_model']}[/]")
    console.print(f"Dataset:    [cyan]{train_cfg['dataset_path']}[/]")
    console.print(f"LoRA rank:  [cyan]{lora_cfg['r']}[/], alpha: [cyan]{lora_cfg['lora_alpha']}[/]")
    console.print(f"Num labels: [cyan]{class_cfg['num_labels']}[/]")

    # ── Load Tokenizer ────────────────────────────────────────────────────────
    console.print("\n[1/5] Loading tokenizer…")
    tokenizer = AutoTokenizer.from_pretrained(model_cfg["tokenizer"])
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # ── Load base model for classification ────────────────────────────────────
    console.print("[2/5] Loading base model with Classification Head…")
    
    if not dry_run:
        # Configure 4-bit quantization config
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=model_cfg.get("load_in_4bit", True),
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16,
            bnb_4bit_use_double_quant=True,
        )

        model = AutoModelForSequenceClassification.from_pretrained(
            model_cfg["base_model"],
            num_labels=class_cfg["num_labels"],
            quantization_config=quantization_config,
            device_map="auto",
        )
        model.config.pad_token_id = tokenizer.pad_token_id
    else:
        from unittest.mock import MagicMock
        model = MagicMock()
        model.config = MagicMock()
        model.config.pad_token_id = tokenizer.pad_token_id

    # ── Apply SEQ_CLS LoRA adapter ────────────────────────────────────────────
    console.print("[3/5] Applying Sequence Classification LoRA adapter…")
    if not dry_run:
        peft_config = LoraConfig(
            task_type=TaskType.SEQ_CLS,
            inference_mode=False,
            r=lora_cfg["r"],
            lora_alpha=lora_cfg["lora_alpha"],
            lora_dropout=lora_cfg["lora_dropout"],
            target_modules=lora_cfg["target_modules"],
            bias=lora_cfg.get("bias", "none"),
        )
        model = get_peft_model(model, peft_config)
        model.print_trainable_parameters()
    else:
        pass

    # ── Load dataset ──────────────────────────────────────────────────────────
    console.print("[4/5] Loading dataset…")
    dataset_path = Path(train_cfg["dataset_path"])
    if not dataset_path.exists():
        console.print(f"[red]Dataset not found:[/] {dataset_path}")
        raise typer.Exit(1)

    raw = load_dataset("json", data_files=str(dataset_path), split="train")
    if train_cfg.get("max_samples"):
        raw = raw.select(range(min(len(raw), train_cfg["max_samples"])))

    # Split train/validation
    val_split = train_cfg.get("validation_split", 0.1)
    split = raw.train_test_split(test_size=val_split, seed=42)
    train_ds = split["train"]
    eval_ds  = split["test"]
    console.print(f"  Train samples: {len(train_ds)}, Eval samples: {len(eval_ds)}")

    label_map = class_cfg["label_map"]

    def preprocess_function(examples):
        result = tokenizer(
            examples["prompt"],
            truncation=True,
            max_length=model_cfg.get("max_seq_length", 2048),
            padding="max_length",  # Classification benefits from padded inputs
        )
        result["labels"] = [label_map[label] for label in examples["label"]]
        return result

    if not dry_run:
        train_ds = train_ds.map(preprocess_function, batched=True, remove_columns=["prompt", "completion", "label"])
        eval_ds  = eval_ds.map(preprocess_function, batched=True, remove_columns=["prompt", "completion", "label"])
    else:
        console.print("[yellow]Dry run complete — skipping training.[/]")
        return

    # ── Train ─────────────────────────────────────────────────────────────────
    console.print("[5/5] Starting training…")
    
    # Auto-detect precision based on GPU hardware capability
    supports_bf16 = torch.cuda.is_available() and torch.cuda.is_bf16_supported()
    use_bf16 = train_cfg.get("bf16", True) and supports_bf16
    use_fp16 = train_cfg.get("fp16", False) or (not use_bf16 and torch.cuda.is_available())
    console.print(f"  Training precision: bf16={use_bf16}, fp16={use_fp16}")

    # MLflow tracking initialization
    mlflow_enabled = False
    tracking_uri = mlflow_cfg.get("tracking_uri", "http://localhost:5000")
    
    try:
        import os
        hf_token = os.environ.get("HF_TOKEN", "")
        if hf_token:
            os.environ["MLFLOW_TRACKING_HEADERS"] = f"Authorization: Bearer {hf_token}"
            
        mlflow.set_tracking_uri(tracking_uri)
        experiment_name = mlflow_cfg.get("experiment_name", "delentia-slm-router-classifier")
        mlflow.set_experiment(experiment_name)
        mlflow_enabled = True
        console.print(f"  MLflow tracking enabled on server: {tracking_uri}")
    except Exception as e:
        console.print(f"  [yellow]Warning:[/] Failed to initialize MLflow client ({e}). Training will proceed with local logging only.")

    report_to_list = ["mlflow"] if mlflow_enabled else []

    training_args = TrainingArguments(
        output_dir=train_cfg["output_dir"],
        num_train_epochs=train_cfg["num_train_epochs"],
        per_device_train_batch_size=train_cfg["per_device_train_batch_size"],
        gradient_accumulation_steps=train_cfg["gradient_accumulation_steps"],
        learning_rate=float(train_cfg["learning_rate"]),
        lr_scheduler_type=train_cfg["lr_scheduler_type"],
        warmup_ratio=train_cfg["warmup_ratio"],
        bf16=use_bf16,
        fp16=use_fp16,
        optim=train_cfg.get("optim", "adamw_8bit"),
        weight_decay=train_cfg.get("weight_decay", 0.01),
        max_grad_norm=train_cfg.get("max_grad_norm", 1.0),
        save_strategy=train_cfg.get("save_strategy", "epoch"),
        save_total_limit=train_cfg.get("save_total_limit", 3),
        logging_steps=train_cfg.get("logging_steps", 10),
        eval_strategy=train_cfg.get("evaluation_strategy", "epoch"),
        load_best_model_at_end=train_cfg.get("load_best_model_at_end", True),
        metric_for_best_model=train_cfg.get("metric_for_best_model", "eval_accuracy"),
        report_to=report_to_list,
        remove_unused_columns=False,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=eval_ds,
        compute_metrics=compute_metrics,
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
                    "num_labels": class_cfg["num_labels"],
                    "task_type": "SEQ_CLS",
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

    # ── Save adapter ──────────────────────────────────────────────────────────
    console.print("\nSaving Sequence Classification adapter…")
    if adapter_path is None:
        adapter_path = Path(cfg.get("adapter_save_path", "models/adapters/jitna_router_v1"))
    else:
        adapter_path = Path(adapter_path)
        
    model.save_pretrained(str(adapter_path))
    tokenizer.save_pretrained(str(adapter_path))
    console.print(f"[bold green]Classifier Adapter saved → {adapter_path}[/]")


if __name__ == "__main__":
    app()
