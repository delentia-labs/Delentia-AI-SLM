"""
benchmark.py

Performance benchmark for the Delentia SLM via Ollama.
Measures: tokens/sec, FDIA scores, JITNA compliance, Thai accuracy.

Usage:
  python inference/benchmark.py
  python inference/benchmark.py --model delentia-jitna-v0.1 --samples 20
"""

import json
import statistics
import time
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from inference.jitna_validator import JITNAValidator
from inference.ollama_adapter import OllamaAdapter

console = Console()
app = typer.Typer()

BENCHMARK_PROMPTS = [
    "Explain JITNA v3 packet routing in 2 sentences.",
    "สรุป PDPA มาตรา 37 ในภาษาไทยสั้นๆ",
    "What is the FDIA formula and what does each letter stand for?",
    "List the 9 HexaCore roles in Delentia OS.",
    "How does the Delta Engine handle memory rollback?",
    "What is RCT v5 consensus and how does it prevent hallucinations?",
    "Describe constitutional AI governance in 3 bullet points.",
    "อธิบาย RCT v5 ให้ผู้บริหารองค์กรเข้าใจใน 1 ย่อหน้า",
    "What security controls does Delentia OS provide for enterprise PDPA compliance?",
    "How many microservices does Delentia OS v2.0 contain?",
]


@app.command()
def main(
    model: str = typer.Option("delentia-jitna-v0.1", help="Ollama model name"),
    ollama_url: str = typer.Option("http://localhost:11434", help="Ollama base URL"),
    samples: int = typer.Option(10, help="Number of benchmark prompts to run"),
    output_json: Path = typer.Option(
        Path("benchmark/results/slm_benchmark.json"),
        help="Output JSON results file",
    ),
) -> None:
    console.print(f"[bold blue]Delentia AI — SLM Benchmark[/]\nModel: {model}")

    adapter = OllamaAdapter(model_name=model, base_url=ollama_url)

    if not adapter.health_check():
        console.print(
            f"[red]Ollama not available or model '{model}' not loaded.[/]\n"
            "Run: ollama serve && ollama pull " + model
        )
        raise typer.Exit(1)

    validator = JITNAValidator()
    prompts = BENCHMARK_PROMPTS[:samples]

    latencies:      list[float] = []
    fdia_scores:    list[float] = []
    jitna_scores:   list[bool]  = []
    thai_counts:    int = 0
    results:        list[dict]  = []

    console.print(f"Running {len(prompts)} benchmark prompts…\n")

    for i, prompt in enumerate(prompts):
        start = time.perf_counter()
        try:
            resp = adapter.execute_intent(prompt)
            latency = time.perf_counter() - start
        except Exception as e:
            console.print(f"  [red]Sample {i+1} failed:[/] {e}")
            continue

        latencies.append(latency)

        # Tokens/sec estimate
        tokens_out = resp.eval_count or (len(resp.output.split()) * 1.3)
        tps = tokens_out / latency if latency > 0 else 0

        # FDIA heuristic
        words = len(resp.output.split())
        D = min(1.0, words / 50)
        I = min(1.0, len(prompt) / 40)
        A = min(1.0, (1 - (resp.output.count("?") / max(1, words))))
        F = (D ** I) * A
        fdia_scores.append(F)

        # JITNA check (partial — response may not be full packet)
        jitna_indicators = sum(
            1 for kw in ["JITNA", "schema_version", "packet_id", "INTENT", "constitutional"]
            if kw.lower() in resp.output.lower()
        )
        jitna_ok = jitna_indicators >= 1
        jitna_scores.append(jitna_ok)

        # Thai language
        thai_chars = sum(1 for c in resp.output if "\u0E00" <= c <= "\u0E7F")
        if thai_chars > 10:
            thai_counts += 1

        results.append({
            "prompt": prompt[:80],
            "output_preview": resp.output[:200],
            "latency_ms": round(latency * 1000),
            "tokens_per_sec": round(tps, 1),
            "fdia_F": round(F, 4),
            "jitna_ok": jitna_ok,
            "thai_chars": thai_chars,
        })

        console.print(
            f"  [{i+1:2d}/{len(prompts)}] {latency*1000:.0f}ms  "
            f"FDIA={F:.3f}  {'✓JITNA' if jitna_ok else '—'}"
        )

    # Summary stats
    if not latencies:
        console.print("[red]No successful samples.[/]")
        raise typer.Exit(1)

    summary = {
        "model": model,
        "samples": len(latencies),
        "avg_latency_ms": round(statistics.mean(latencies) * 1000),
        "p50_latency_ms": round(statistics.median(latencies) * 1000),
        "fdia_avg": round(statistics.mean(fdia_scores), 4),
        "fdia_min": round(min(fdia_scores), 4),
        "jitna_compliance": round(sum(jitna_scores) / len(jitna_scores), 4),
        "thai_response_rate": round(thai_counts / len(latencies), 4),
        "results": results,
    }

    # Print summary table
    table = Table(title="Benchmark Summary")
    for k, v in summary.items():
        if k != "results":
            table.add_row(k, str(v))
    console.print(table)

    # Save results
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    console.print(f"\n[green]Results saved → {output_json}[/]")

    # Gate check
    if summary["fdia_avg"] < 0.70:
        console.print(f"[yellow]Warning:[/] FDIA avg {summary['fdia_avg']} below 0.70 target")
    if summary["jitna_compliance"] < 0.50:
        console.print(f"[yellow]Warning:[/] JITNA compliance {summary['jitna_compliance']} below 0.50")


if __name__ == "__main__":
    app()
