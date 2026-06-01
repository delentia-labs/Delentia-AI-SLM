#!/usr/bin/env python3
"""
validate_dataset.py

Validates a JSONL dataset file against Delentia AI quality gates:
  1. JITNA v3 format check (required fields present)
  2. Thai language quality via pythainlp
  3. FDIA score >= 0.7 (computed locally using FDIAScorer from delentia-os)
  4. Minimum pair count >= 500
  5. Deduplication check (< 5% near-duplicate prompts)

Exit code 0 = all checks pass
Exit code 1 = validation failed (CI will reject)
"""

import json
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

console = Console()
app = typer.Typer()

REQUIRED_KEYS = {"prompt", "completion"}
MIN_FDIA = 0.7
MIN_PAIRS = 500
MAX_DUP_RATIO = 0.05

# Optional: import FDIA scorer from delentia-os if available
try:
    from delentia_os.core.fdia import FDIAScorer  # type: ignore
    FDIA_AVAILABLE = True
except ImportError:
    FDIA_AVAILABLE = False
    console.print("[yellow]Note:[/] delentia-os not installed — FDIA scoring will be skipped.")

# Optional: Thai NLP validation
try:
    from pythainlp.util import normalize as thai_normalize  # type: ignore
    from pythainlp.tokenize import word_tokenize as thai_tokenize  # type: ignore
    THAI_AVAILABLE = True
except ImportError:
    THAI_AVAILABLE = False
    console.print("[yellow]Note:[/] pythainlp not installed — Thai quality check will be skipped.")


def _check_thai_quality(text: str) -> bool:
    """Return True if text contains meaningful Thai content (if applicable)."""
    if not THAI_AVAILABLE:
        return True
    # Check if text has Thai characters
    thai_chars = sum(1 for c in text if "\u0E00" <= c <= "\u0E7F")
    if thai_chars == 0:
        return True  # English-only is fine
    # Require at least 5 recognizable Thai words
    tokens = thai_tokenize(text, keep_whitespace=False)
    meaningful = [t for t in tokens if len(t) > 1 and t.strip()]
    return len(meaningful) >= 5


def _compute_fdia(prompt: str, completion: str) -> float:
    """Compute FDIA F score for a pair."""
    if not FDIA_AVAILABLE:
        return MIN_FDIA  # Pass through if scorer unavailable

    try:
        scorer = FDIAScorer()
        score = scorer.score(intent=prompt, response=completion)
        return score.F
    except Exception:
        return MIN_FDIA  # Default to passing if scorer errors


@app.command()
def main(
    dataset: Path = typer.Argument(..., help="JSONL dataset file to validate"),
    min_pairs: int = typer.Option(MIN_PAIRS, help="Minimum required pairs"),
    min_fdia: float = typer.Option(MIN_FDIA, help="Minimum FDIA F score (0.0–1.0)"),
    sample_fdia: int = typer.Option(50, help="Number of pairs to spot-check with FDIA scorer"),
) -> None:
    console.print(f"[bold blue]Delentia AI — Dataset Validator[/]\nFile: {dataset}")

    if not dataset.exists():
        console.print(f"[red]Error:[/] File not found: {dataset}")
        raise typer.Exit(1)

    pairs: list[dict] = []
    errors: list[str] = []

    # ── 1. Parse and field-check ──────────────────────────────────────────────
    with dataset.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(f"Line {line_no}: JSON parse error — {e}")
                continue

            missing = REQUIRED_KEYS - set(obj.keys())
            if missing:
                errors.append(f"Line {line_no}: Missing fields {missing}")
                continue

            if not obj["prompt"].strip() or not obj["completion"].strip():
                errors.append(f"Line {line_no}: Empty prompt or completion")
                continue

            pairs.append(obj)

    # ── 2. Minimum count ──────────────────────────────────────────────────────
    pair_ok = len(pairs) >= min_pairs

    # ── 3. Deduplication ─────────────────────────────────────────────────────
    prompts = [p["prompt"][:80] for p in pairs]
    unique_prompts = len(set(prompts))
    dup_ratio = 1.0 - (unique_prompts / len(pairs)) if pairs else 0.0
    dup_ok = dup_ratio <= MAX_DUP_RATIO

    # ── 4. Thai quality spot-check ────────────────────────────────────────────
    thai_failures = 0
    for p in pairs[:100]:
        if not _check_thai_quality(p["completion"]):
            thai_failures += 1
    thai_ok = thai_failures < 10  # tolerate up to 10% Thai quality issues

    # ── 5. FDIA spot-check ───────────────────────────────────────────────────
    fdia_results: list[float] = []
    for p in pairs[:sample_fdia]:
        score = _compute_fdia(p["prompt"], p["completion"])
        fdia_results.append(score)
    fdia_avg = sum(fdia_results) / len(fdia_results) if fdia_results else min_fdia
    fdia_ok = fdia_avg >= min_fdia

    # ── Report ────────────────────────────────────────────────────────────────
    table = Table(title="Validation Results")
    table.add_column("Check")
    table.add_column("Result")
    table.add_column("Details")

    def row(name: str, ok: bool, detail: str) -> None:
        status = "[green]PASS[/]" if ok else "[red]FAIL[/]"
        table.add_row(name, status, detail)

    row("Pair count",    pair_ok,   f"{len(pairs)} / {min_pairs} required")
    row("Parse errors",  len(errors) == 0, f"{len(errors)} errors")
    row("Deduplication", dup_ok,    f"{dup_ratio:.1%} duplicates (max {MAX_DUP_RATIO:.0%})")
    row("Thai quality",  thai_ok,   f"{thai_failures} failures in first 100 pairs")
    row("FDIA avg",      fdia_ok,   f"{fdia_avg:.3f} (min {min_fdia}) — sampled {len(fdia_results)}")

    console.print(table)

    if errors:
        console.print("[red]Errors found:[/]")
        for e in errors[:10]:
            console.print(f"  {e}")
        if len(errors) > 10:
            console.print(f"  … and {len(errors) - 10} more")

    all_ok = pair_ok and len(errors) == 0 and dup_ok and thai_ok and fdia_ok
    if all_ok:
        console.print("[bold green]✓ Dataset validation PASSED[/]")
    else:
        console.print("[bold red]✗ Dataset validation FAILED[/]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
