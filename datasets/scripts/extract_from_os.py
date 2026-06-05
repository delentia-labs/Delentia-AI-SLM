#!/usr/bin/env python3
"""
extract_from_os.py

Extracts JITNA-format training pairs from the delentia-os repository.
Sources:
  - delentia-os/tests/          (1,791 test assertions → prompt/completion)
  - delentia-os/examples/       (usage examples → prompt/completion)
  - delentia-os/rct_control_plane/  (intent templates if present)

Output:
  - datasets/processed/jitna_pairs.jsonl         (standard JSON format)
  - datasets/processed/jitna_pairs_toon.jsonl    (TOON v0.2 format — token-optimized)

Target: 500–1000 high-quality pairs minimum.

Format per line (standard):
  {"prompt": "<system_context>\n\n<user_intent>", "completion": "<expected_output>"}

Format per line (TOON v0.2):
  {"prompt": "<system_context>\n\n<user_intent>", "completion": "<TOON-formatted output>"}
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
DELENTIA_OS = REPO_ROOT / "Delentia-OS"

OUTPUT_DIR = Path(__file__).parents[1] / "processed"

SYSTEM_CONTEXT = (
    "You are Delentia OS — a constitutional AI operating under RCT v5 governance. "
    "You process intents through the JITNA v3 protocol. "
    "Your responses must be factual, safe, and PDPA-compliant. "
    "Always provide FDIA scores when applicable (F = D^I × A)."
)

SYSTEM_CONTEXT_TOON = (
    "You are Delentia OS v0.2 — a constitutional AI operating under RCT v5 governance. "
    "You process intents through the JITNA v3 protocol. "
    "You respond in TOON format (Token-Oriented Object Notation) for token efficiency. "
    "Your responses must be factual, safe, and PDPA-compliant. "
    "Always provide FDIA scores when applicable (F = D^I × A)."
)


def _emit(prompt: str, completion: str, use_toon: bool = False) -> dict:
    ctx = SYSTEM_CONTEXT_TOON if use_toon else SYSTEM_CONTEXT
    comp = _completion_to_toon(completion) if use_toon else completion.strip()
    return {
        "prompt": f"{ctx}\n\nUser intent: {prompt.strip()}",
        "completion": comp,
    }


def _completion_to_toon(completion: str) -> str:
    """
    Convert a completion string to TOON format.
    
    If the completion looks like structured data (dict-like), parse and convert.
    Otherwise, wrap it in a minimal TOON structure with 'output' key.
    """
    try:
        # Attempt to import TOON formatter from Delentia-OS
        sys.path.insert(0, str(REPO_ROOT / "Delentia-OS"))
        from rct_control_plane.toon_formatter import toon_serialize
        
        # Try parsing as JSON-like structure
        import ast
        try:
            data = ast.literal_eval(completion.strip())
            if isinstance(data, dict):
                return toon_serialize(data)
        except (ValueError, SyntaxError):
            pass
            
        return toon_serialize({"output": completion.strip()[:512]})
    except Exception:
        # Fallback if anything goes wrong
        escaped = completion.strip()[:512].replace("\n", "\\n")
        return f"output: {escaped}"



def _extract_from_tests(pairs: list[dict]) -> int:
    """Parse pytest test files for intent→assertion pairs."""
    test_dirs = [
        DELENTIA_OS / "tests",
        DELENTIA_OS / "rct_control_plane" / "tests",
        DELENTIA_OS / "microservices" / "intent-loop" / "tests",
    ]

    count = 0
    for test_dir in test_dirs:
        if not test_dir.exists():
            continue
        for py_file in track(list(test_dir.rglob("test_*.py")), description=f"Scanning tests in {test_dir.name}…"):
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
    toon: bool = typer.Option(False, "--toon", help="Generate TOON v0.2 format output"),
) -> None:
    fmt_label = "TOON v0.2" if toon else "standard"
    console.print(f"[bold blue]Delentia AI — Dataset Extractor ({fmt_label})[/]")
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
        key = p["prompt"]
        if key not in seen:
            seen.add(key)
            unique_pairs.append(p)


    # If TOON mode, re-emit all pairs with TOON formatting
    if toon:
        toon_pairs = []
        for p in unique_pairs:
            # Re-extract original intent from the prompt
            intent_marker = "User intent: "
            idx = p["prompt"].find(intent_marker)
            if idx >= 0:
                intent = p["prompt"][idx + len(intent_marker):]
            else:
                intent = p["prompt"]
            toon_pairs.append(_emit(intent, p["completion"], use_toon=True))
        unique_pairs = toon_pairs
        # Update output filename
        if output == OUTPUT_DIR / "jitna_pairs.jsonl":
            output = OUTPUT_DIR / "jitna_pairs_toon.jsonl"

    total = len(unique_pairs)
    console.print(
        f"\n[green]Extracted:[/] {n_tests} tests + {n_examples} examples + "
        f"{n_notebooks} notebook pairs = [bold]{total}[/] unique ({fmt_label})"
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
