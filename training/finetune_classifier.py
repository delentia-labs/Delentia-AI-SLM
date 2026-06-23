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

# Monkeypatch PEFT to prevent gradient errors on non-float tensors (specifically for QLoRA classification)
try:
    import peft.utils.other
    def safe_set_layer_requires_grad(layer, requires_grad=True):
        for param in layer.parameters():
            if param.is_leaf:
                if torch.is_tensor(param) and param.is_floating_point():
                    param.requires_grad_(requires_grad)
                else:
                    param.requires_grad = False
    peft.utils.other._set_layer_requires_grad = safe_set_layer_requires_grad
    print("✅ Applied PEFT gradient safety monkeypatch.")
except Exception as e:
    print(f"⚠️ PEFT monkeypatch warning: {e}")

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
    push_to_hub: bool = typer.Option(False, "--push-to-hub", help="Push checkpoints to HF Hub"),  # noqa: B008
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
            llm_int8_skip_modules=["score", "classifier"],
        )

        import torch.nn.init as torch_init
        import transformers.initialization as hf_init

        # Save original init functions
        orig_normal = torch_init.normal_
        orig_uniform = torch_init.uniform_

        def safe_normal(tensor, mean=0.0, std=1.0, generator=None):
            if tensor.dtype in [torch.uint8, torch.int8, torch.int16, torch.int32, torch.int64]:
                return tensor
            return orig_normal(tensor, mean=mean, std=std, generator=generator)

        def safe_uniform(tensor, a=0.0, b=1.0, generator=None):
            if tensor.dtype in [torch.uint8, torch.int8, torch.int16, torch.int32, torch.int64]:
                return tensor
            return orig_uniform(tensor, a=a, b=b, generator=generator)

        # Apply patches
        torch_init.normal_ = safe_normal
        torch_init.uniform_ = safe_uniform
        if hasattr(hf_init, "TORCH_INIT_FUNCTIONS"):
            if "normal_" in hf_init.TORCH_INIT_FUNCTIONS:
                hf_init.TORCH_INIT_FUNCTIONS["normal_"] = safe_normal
            if "uniform_" in hf_init.TORCH_INIT_FUNCTIONS:
                hf_init.TORCH_INIT_FUNCTIONS["uniform_"] = safe_uniform

        orig_llama_init_weights = None
        LlamaPreTrainedModel = None
        try:
            from transformers.models.llama.modeling_llama import LlamaPreTrainedModel
            orig_llama_init_weights = LlamaPreTrainedModel._init_weights

            def safe_llama_init_weights(self, module):
                try:
                    orig_llama_init_weights(self, module)
                except Exception as e:
                    if "not implemented for" in str(e) or "Byte" in str(e) or "normal_kernel_cuda" in str(e):
                        pass
                    else:
                        raise e

            LlamaPreTrainedModel._init_weights = safe_llama_init_weights
        except Exception:
            pass

        try:
            model = AutoModelForSequenceClassification.from_pretrained(
                model_cfg["base_model"],
                num_labels=class_cfg["num_labels"],
                quantization_config=quantization_config,
                device_map="auto",
            )
        finally:
            # Restore original functions and methods
            torch_init.normal_ = orig_normal
            torch_init.uniform_ = orig_uniform
            if hasattr(hf_init, "TORCH_INIT_FUNCTIONS"):
                if "normal_" in hf_init.TORCH_INIT_FUNCTIONS:
                    hf_init.TORCH_INIT_FUNCTIONS["normal_"] = orig_normal
                if "uniform_" in hf_init.TORCH_INIT_FUNCTIONS:
                    hf_init.TORCH_INIT_FUNCTIONS["uniform_"] = orig_uniform
            if LlamaPreTrainedModel is not None and orig_llama_init_weights is not None:
                LlamaPreTrainedModel._init_weights = orig_llama_init_weights

        # Replace Linear4bit/quantized heads with standard float32 nn.Linear
        import torch.nn as nn
        for head_name in ["score", "classifier"]:
            if hasattr(model, head_name):
                orig_head = getattr(model, head_name)
                if not isinstance(orig_head, nn.Linear) or type(orig_head).__name__ != 'Linear':
                    in_features = orig_head.in_features
                    out_features = orig_head.out_features
                    has_bias = getattr(orig_head, "bias", None) is not None
                    new_head = nn.Linear(in_features, out_features, bias=has_bias)
                    new_head = new_head.to(torch.float32)
                    setattr(model, head_name, new_head)
                    console.print(f"✅ Replaced quantized {head_name} head with standard float32 nn.Linear.")

        model.config.pad_token_id = tokenizer.pad_token_id
    else:
        from unittest.mock import MagicMock
        model = MagicMock()
        model.config = MagicMock()
        model.config.pad_token_id = tokenizer.pad_token_id

    # ── Apply SEQ_CLS LoRA adapter ────────────────────────────────────────────
    console.print("[3/5] Applying Sequence Classification LoRA adapter…")
    if not dry_run:
        from peft import prepare_model_for_kbit_training
        model = prepare_model_for_kbit_training(model)
        
        # Cast classification head explicitly to float32 to prevent PEFT gradient error
        if hasattr(model, "score"):
            model.score = model.score.to(torch.float32)

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

    if dataset_path.suffix == ".parquet":
        raw = load_dataset("parquet", data_files=str(dataset_path), split="train")
    else:
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
            hub_model_id = "delentia-labs/delentia-slm-jitna-router"
            console.print(f"  Hub Repository ID: [cyan]{hub_model_id}[/]")
        except Exception as e:
            console.print(f"  [red]Failed to login to Hugging Face Hub:[/] {e}")
            raise typer.Exit(1)

    import inspect
    sig = inspect.signature(TrainingArguments.__init__)
    eval_strategy_key = "eval_strategy" if "eval_strategy" in sig.parameters else "evaluation_strategy"

    training_args_kwargs = {
        "output_dir": train_cfg["output_dir"],
        "num_train_epochs": train_cfg["num_train_epochs"],
        "per_device_train_batch_size": train_cfg["per_device_train_batch_size"],
        "gradient_accumulation_steps": train_cfg["gradient_accumulation_steps"],
        "learning_rate": float(train_cfg["learning_rate"]),
        "lr_scheduler_type": train_cfg["lr_scheduler_type"],
        "warmup_ratio": train_cfg["warmup_ratio"],
        "bf16": use_bf16,
        "fp16": use_fp16,
        "optim": train_cfg.get("optim", "adamw_8bit"),
        "weight_decay": train_cfg.get("weight_decay", 0.01),
        "max_grad_norm": train_cfg.get("max_grad_norm", 1.0),
        "save_strategy": "steps" if push_to_hub else train_cfg.get("save_strategy", "epoch"),
        "save_steps": 100 if push_to_hub else train_cfg.get("save_steps", 500),
        "save_total_limit": train_cfg.get("save_total_limit", 3),
        "logging_steps": train_cfg.get("logging_steps", 10),
        eval_strategy_key: train_cfg.get("evaluation_strategy", "epoch"),
        "load_best_model_at_end": train_cfg.get("load_best_model_at_end", True) if not push_to_hub else False,
        "metric_for_best_model": train_cfg.get("metric_for_best_model", "eval_accuracy"),
        "report_to": report_to_list,
        "remove_unused_columns": False,
        "push_to_hub": push_to_hub,
        "hub_model_id": hub_model_id,
        "hub_strategy": "every_save" if push_to_hub else "every_save",
        "hub_token": hf_token if push_to_hub else None,
    }
    training_args = TrainingArguments(**training_args_kwargs)

    from transformers import DataCollatorWithPadding
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer, pad_to_multiple_of=8)

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=eval_ds,
        compute_metrics=compute_metrics,
        data_collator=data_collator,
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
        adapter_path = Path(cfg.get("adapter_save_path", "models/adapters/jitna_router_v0.4"))
    else:
        adapter_path = Path(adapter_path)
        
    model.save_pretrained(str(adapter_path))
    tokenizer.save_pretrained(str(adapter_path))
    console.print(f"[bold green]Classifier Adapter saved → {adapter_path}[/]")
    if push_to_hub:
        console.print("[bold blue]Pushing final classifier weights to Hugging Face Hub…[/]")
        try:
            trainer.push_to_hub()
            console.print("🎉 Final classifier weights pushed to Hugging Face Hub successfully!")
        except Exception as e:
            console.print(f"  [red]Failed to push final weights to Hugging Face Hub:[/] {e}")


if __name__ == "__main__":
    app()
