#!/usr/bin/env python3
"""
save_checkpoint_to_drive.py

Run this at any point during or after training to save all Delentia v0.4.1
checkpoints to Google Drive.

Usage in Colab:
    !python training/save_checkpoint_to_drive.py

Or paste the content into a Colab cell to run interactively.
"""

import glob
import json
import os
import shutil
from datetime import datetime

REPO_DIR = "/content/Delentia-AI-SLM"
if os.path.exists(REPO_DIR):
    os.chdir(REPO_DIR)

# ── 1. Ensure Google Drive is mounted ─────────────────────────────────────────
drive_mounted = os.path.exists("/content/drive/MyDrive")
if not drive_mounted:
    try:
        from google.colab import drive  # type: ignore
        drive.mount("/content/drive")
        drive_mounted = True
        print("✅ Google Drive mounted.")
    except Exception as e:
        print(f"❌ Could not mount Google Drive: {e}")
        print("   → Checkpoint NOT saved. Please mount manually and re-run.")
        raise SystemExit(1)
else:
    print("✅ Google Drive already mounted.")

# ── 2. Create timestamped checkpoint folder ────────────────────────────────────
timestamp = datetime.now().strftime("%Y%m%d_%H%M")
DRIVE_ROOT = f"/content/drive/MyDrive/Delentia_Checkpoints/v0.4.1_{timestamp}"
os.makedirs(DRIVE_ROOT, exist_ok=True)
print(f"📁 Checkpoint folder: {DRIVE_ROOT}")
print("-" * 65)

saved_files: list[str] = []
skipped: list[str] = []


def safe_copy(src: str, dst_dir: str, label: str = "") -> bool:
    """Copy a file or directory to Drive. Returns True on success."""
    try:
        os.makedirs(dst_dir, exist_ok=True)
        if os.path.isdir(src):
            dst = os.path.join(dst_dir, os.path.basename(src))
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst_dir)
        saved_files.append(label or src)
        return True
    except Exception as e:
        skipped.append(f"{label or src}: {e}")
        return False


# ── 3. Save LoRA Adapters (4 Pillars) ─────────────────────────────────────────
print("\n[1/5] Saving LoRA Adapters...")
adapter_dst = os.path.join(DRIVE_ROOT, "adapters")
for pillar in ["executor", "router", "guardian", "scribe"]:
    adapter_path = f"models/adapters/jitna_{pillar}_v0.4"
    if os.path.exists(adapter_path):
        if safe_copy(adapter_path, adapter_dst, f"adapter/{pillar}"):
            print(f"  ✅ {pillar} adapter saved")
        else:
            print(f"  ⚠️  {pillar} adapter save failed")
    else:
        print(f"  ─  {pillar} adapter not found (not yet trained — skipped)")

# ── 4. Save GGUF Export Files ──────────────────────────────────────────────────
print("\n[2/5] Saving GGUF files...")
gguf_dst = os.path.join(DRIVE_ROOT, "gguf")
gguf_files = glob.glob("models/gguf/*.gguf")
if gguf_files:
    for f in gguf_files:
        if safe_copy(f, gguf_dst, os.path.basename(f)):
            print(f"  ✅ {os.path.basename(f)}")
else:
    print("  ─  No GGUF files found (run Cell 9 to export first)")

# ── 5. Save Evaluation Results ─────────────────────────────────────────────────
print("\n[3/5] Saving evaluation results...")
eval_dst = os.path.join(DRIVE_ROOT, "eval")
eval_files = glob.glob("models/eval_*.json")
if eval_files:
    for f in eval_files:
        if safe_copy(f, eval_dst, os.path.basename(f)):
            print(f"  ✅ {os.path.basename(f)}")
else:
    print("  ─  No eval JSON files found (run Cell 8 to evaluate first)")

# ── 6. Save VRAM Graph + Logs ──────────────────────────────────────────────────
print("\n[4/5] Saving VRAM graph and logs...")
vram_graph = "docs/vram_comparison_100_turns.png"
if os.path.exists(vram_graph):
    if safe_copy(vram_graph, os.path.join(DRIVE_ROOT, "docs"), "vram_comparison_100_turns.png"):
        print("  ✅ vram_comparison_100_turns.png")
else:
    print("  ─  VRAM graph not found (run Cell 8.2 with --plot-vram-cost)")

log_files = glob.glob("logs/*.json") + glob.glob("logs/*.txt")
for f in log_files:
    if safe_copy(f, os.path.join(DRIVE_ROOT, "logs"), os.path.basename(f)):
        print(f"  ✅ {os.path.basename(f)}")

# ── 7. Save session manifest ───────────────────────────────────────────────────
print("\n[5/5] Writing session manifest...")
manifest = {
    "timestamp": timestamp,
    "checkpoint_dir": DRIVE_ROOT,
    "saved": saved_files,
    "skipped": skipped,
    "resume_instructions": {
        "step_1": "Open colab_4_pillars_v041.ipynb in a new Colab session",
        "step_2": "Run Cell 1 to mount Drive and reload repos from the ZIPs",
        "step_3": "Run Cell 2 to install dependencies",
        "step_4": "Skip cells for already-trained pillars",
        "step_5": f"Load adapter from:  {DRIVE_ROOT}/adapters/jitna_PILLAR_v0.4/",
        "step_6": "Continue from the next untrained pillar OR jump straight to Cell 8",
    },
}
manifest_path = os.path.join(DRIVE_ROOT, "checkpoint_manifest.json")
with open(manifest_path, "w", encoding="utf-8") as mf:
    json.dump(manifest, mf, indent=2, ensure_ascii=False)
print("  ✅ checkpoint_manifest.json written")

# ── Summary ────────────────────────────────────────────────────────────────────
print()
print("=" * 65)
print("💾 CHECKPOINT COMPLETE")
print(f"   Saved  : {len(saved_files)} items")
print(f"   Skipped: {len(skipped)} items")
print(f"   Location: {DRIVE_ROOT}")
print("=" * 65)
print()
print("📋 How to resume next session:")
print("  1. Open this notebook in a new Colab session")
print("  2. Run Cell 1 (mounts Drive + loads repos)")
print("  3. Run Cell 2 (install dependencies)")
print("  4. Skip cells for already-trained pillars")
print(f"  5. Load adapters from: {DRIVE_ROOT}/adapters/")
print("  6. Continue from the next untrained pillar or Cell 8 evaluation")
