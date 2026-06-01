#!/usr/bin/env python3
"""
extract_from_os.py

Extracts JITNA-format training pairs from the delentia-os repository.
Sources:
  - delentia-os/tests/          (1,791 test assertions → prompt/completion)
  - delentia-os/examples/       (usage examples → prompt/completion)
  - delentia-os/rct_control_plane/  (intent templates if present)

Output: datasets/processed/jitna_pairs.jsonl
Target: 500–1000 high-quality pairs minimum.

Format per line:
  {"prompt": "<system_context>\n\n<user_intent>", "completion": "<expected_output>"}
"""

import json
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import track

console = Console()
app = typer.Typer()

# Relative path from this file to delentia-os root
REPO_ROOT = Path(__file__).parents[3]
DELENTIA_OS = REPO_ROOT / "delentia-os"
OUTPUT_DIR = Path(__file__).parents[1] / "processed"

SYSTEM_CONTEXT = (
    "You are Delentia OS — a constitutional AI operating under RCT v5 governance. "
    "You process intents through the JITNA v3 protocol. "
    "Your responses must be factual, safe, and PDPA-compliant. "
    "Always provide FDIA scores when applicable (F = D^I × A)."
)


def _emit(prompt: str, completion: str) -> dict:
    return {
        "prompt": f"{SYSTEM_CONTEXT}\n\nUser intent: {prompt.strip()}",
        "completion": completion.strip(),
    }


def _extract_from_tests(pairs: list[dict]) -> int:
    """Parse pytest test files for intent→assertion pairs."""
    test_dir = DELENTIA_OS / "tests"
    if not test_dir.exists():
        console.print(f"[yellow]Warning:[/] tests/ not found at {test_dir}")
        return 0

    count = 0
    for py_file in track(list(test_dir.rglob("test_*.py")), description="Scanning tests…"):
        text = py_file.read_text(encoding="utf-8", errors="ignore")
        lines = text.splitlines()
        for i, line in enumerate(lines):
            if "def test_" in line:
                # Collect docstring or next assert as completion
                func_block = "\n".join(lines[i : i + 20])
                if '"""' in func_block or "assert" in func_block:
                    # Use function name as intent hint
                    intent = (
                        line.strip()
                        .replace("def test_", "")
                        .replace("(self):", "")
                        .replace("():", "")
                        .replace("_", " ")
                        .strip()
                    )
                    pairs.append(_emit(intent, func_block.strip()[:512]))
                    count += 1
    return count


def _extract_from_examples(pairs: list[dict]) -> int:
    """Extract from delentia-os/examples/ directory."""
    examples_dir = DELENTIA_OS / "examples"
    if not examples_dir.exists():
        console.print(f"[yellow]Warning:[/] examples/ not found at {examples_dir}")
        return 0

    count = 0
    for py_file in track(list(examples_dir.rglob("*.py")), description="Scanning examples…"):
        text = py_file.read_text(encoding="utf-8", errors="ignore")
        # Look for # INTENT: ... comments followed by code
        lines = text.splitlines()
        for i, line in enumerate(lines):
            if line.strip().startswith("# INTENT:") or line.strip().startswith("# intent:"):
                intent = line.split(":", 1)[-1].strip()
                completion = "\n".join(lines[i + 1 : i + 15]).strip()
                if len(completion) > 20:
                    pairs.append(_emit(intent, completion[:512]))
                    count += 1
    return count


def _extract_from_notebooks(pairs: list[dict]) -> int:
    """Extract from delentia-os/notebooks/ .ipynb files."""
    nb_dir = DELENTIA_OS / "notebooks"
    if not nb_dir.exists():
        return 0

    count = 0
    for nb_file in nb_dir.rglob("*.ipynb"):
        try:
            nb = json.loads(nb_file.read_text(encoding="utf-8"))
            cells = nb.get("cells", [])
            for j, cell in enumerate(cells):
                if cell.get("cell_type") == "markdown":
                    md = "".join(cell.get("source", []))
                    if j + 1 < len(cells) and cells[j + 1].get("cell_type") == "code":
                        code = "".join(cells[j + 1].get("source", []))
                        if len(md) > 15 and len(code) > 20:
                            pairs.append(_emit(md[:200], code[:512]))
                            count += 1
        except (json.JSONDecodeError, KeyError):
            continue
    return count


@app.command()
def main(
    output: Path = typer.Option(
        OUTPUT_DIR / "jitna_pairs.jsonl",
        help="Output JSONL file path",
    ),
    min_pairs: int = typer.Option(500, help="Minimum pairs required"),
) -> None:
    console.print("[bold blue]Delentia AI — Dataset Extractor[/]")
    console.print(f"Source: {DELENTIA_OS}")
    console.print(f"Output: {output}")

    pairs: list[dict] = []
    n_tests    = _extract_from_tests(pairs)
    n_examples = _extract_from_examples(pairs)
    n_notebooks = _extract_from_notebooks(pairs)

    # Deduplicate by prompt
    seen: set[str] = set()
    unique_pairs = []
    for p in pairs:
        key = p["prompt"][:100]
        if key not in seen:
            seen.add(key)
            unique_pairs.append(p)

    total = len(unique_pairs)
    console.print(
        f"\n[green]Extracted:[/] {n_tests} tests + {n_examples} examples + "
        f"{n_notebooks} notebook pairs = [bold]{total}[/] unique"
    )

    if total < min_pairs:
        console.print(
            f"[yellow]Warning:[/] Only {total} pairs extracted — target is {min_pairs}. "
            "Consider adding more examples to delentia-os/examples/."
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as f:
        for pair in unique_pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")

    console.print(f"[bold green]Done.[/] Written {total} pairs to {output}")

    if total < min_pairs:
        sys.exit(1)


if __name__ == "__main__":
    app()
