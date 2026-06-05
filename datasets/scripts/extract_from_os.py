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


def _build_6field_jitna(prompt: str, body: str) -> dict:
    """Build a canonical 6-field JITNA Language schema dictionary (I/D/Δ/A/R/M)."""
    intent = prompt.strip()

    # Extract docstring if present in function/example body
    doc = ""
    if '"""' in body:
        parts = body.split('"""', 2)
        if len(parts) >= 3:
            doc = parts[1].strip()
    elif "'''" in body:
        parts = body.split("'''", 2)
        if len(parts) >= 3:
            doc = parts[1].strip()

    doc = doc.replace("\n", " ").strip()

    # D: Data
    if doc:
        d_val = f"ทดสอบกรณี {doc} โดยตรวจสอบความถูกต้องของระบบ"
    else:
        d_val = f"RCT OS local test parameters and validation variables for intent '{intent}'."

    # delta: Delta (change of state)
    if "assert " in body:
        delta_val = "ตรวจสอบเงื่อนไขและโครงสร้างระบบให้ผ่านการรับรอง"
    else:
        delta_val = "Verify execution outcomes and ensure zero state conflicts."

    # A: Approach
    body_lower = body.lower()
    if "scorer" in body_lower or "score" in body_lower or "fdia" in body_lower:
        a_val = "FDIAGatekeeper safety assessment using equation F = D^I * A."
    elif "signed" in body_lower or "consensus" in body_lower:
        a_val = "SignedAI HexaCore multi-node validation consensus execution."
    elif "toon" in body_lower:
        a_val = "ALGO-42 TOON syntax compression and token saving verification."
    elif "loop" in body_lower or "intake" in body_lower:
        a_val = "IntentLoopEngine JITNA natural action intake pipeline."
    else:
        a_val = "Deterministic RCT component unit verification."

    # R: Reflection
    r_val = "หากเงื่อนไขผิดพลาดหรือสิทธิ์สถาปนิก (A) ปิด ระบบจะต้องรีเซ็ต F เป็น 0 และป้องกันการบวมของข้อมูลผ่าน Delta Engine (91.5% saving)."

    # M: Memory
    m_val = "RCT v5 compliance, PDPA integrity guarantees, and local offline deployment limits under SignedAI rules."

    return {
        "I": intent,
        "D": d_val,
        "Δ": delta_val,
        "A": a_val,
        "R": r_val,
        "M": m_val,
    }


def _emit(prompt: str, completion_body: str, use_toon: bool = False) -> dict:
    ctx = SYSTEM_CONTEXT_TOON if use_toon else SYSTEM_CONTEXT
    jitna_dict = _build_6field_jitna(prompt, completion_body)

    if use_toon:
        sys.path.insert(0, str(DELENTIA_OS))
        from rct_control_plane.toon_formatter import toon_serialize
        comp = toon_serialize(jitna_dict)
    else:
        comp = json.dumps(jitna_dict, ensure_ascii=False, indent=2)

    return {
        "prompt": f"{ctx}\n\nUser intent: {prompt.strip()}",
        "completion": comp,
    }


def _extract_from_tests(pairs: list[dict], use_toon: bool = False) -> int:
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
                        pairs.append(_emit(intent, func_block.strip()[:512], use_toon=use_toon))
                        count += 1
    return count


def _extract_from_examples(pairs: list[dict], use_toon: bool = False) -> int:
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
                    pairs.append(_emit(intent, completion[:512], use_toon=use_toon))
                    count += 1
    return count


def _extract_from_notebooks(pairs: list[dict], use_toon: bool = False) -> int:
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
                            pairs.append(_emit(md[:200], code[:512], use_toon=use_toon))
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
    n_tests    = _extract_from_tests(pairs, use_toon=toon)
    n_examples = _extract_from_examples(pairs, use_toon=toon)
    n_notebooks = _extract_from_notebooks(pairs, use_toon=toon)

    # Deduplicate by prompt
    seen: set[str] = set()
    unique_pairs = []
    for p in pairs:
        key = p["prompt"]
        if key not in seen:
            seen.add(key)
            unique_pairs.append(p)

    # Update output filename if toon mode is on
    if toon and output == OUTPUT_DIR / "jitna_pairs.jsonl":
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
