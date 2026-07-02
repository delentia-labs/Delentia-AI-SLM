#!/usr/bin/env python3
"""
delete_all_spaces.py
Deletes ALL 7 Spaces from Delentia organization on Hugging Face.
Spaces to delete:
  1. Delentia/delentia-trace-ecosystem  (Build Error - Pinned)
  2. Delentia/README                    (Running - Labs Landing)
  3. Delentia/delentia-analyserch-intent (Paused)
  4. Delentia/delentia-executor          (Sleeping)
  5. Delentia/delentia-scribe            (Paused)
  6. Delentia/delentia-gatekeeper        (Sleeping)
  7. Delentia/delentia-agent-monitor     (Sleeping)

NOTE: Only Spaces are deleted. Models and Datasets are NOT touched.
"""

import os
import sys
from huggingface_hub import HfApi, get_token

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


def main():
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN") or get_token()
    if not token:
        print("ERROR: Hugging Face API token not found.")
        print("Please run: huggingface-cli login")
        sys.exit(1)

    api = HfApi(token=token)

    # ALL 7 Spaces to delete — Spaces only, no models touched
    spaces_to_delete = [
        "Delentia/delentia-trace-ecosystem",   # Build Error (Pinned)
        "Delentia/README",                      # Running (Labs)
        "Delentia/delentia-analyserch-intent",  # Paused
        "Delentia/delentia-executor",           # Sleeping
        "Delentia/delentia-scribe",             # Paused
        "Delentia/delentia-gatekeeper",         # Sleeping
        "Delentia/delentia-agent-monitor",      # Sleeping
    ]

    print("=" * 60)
    print("  Delentia Organization — Space Cleanup Script")
    print("  Deleting ALL 7 legacy Spaces")
    print("  ⚠ Models and Datasets will NOT be touched")
    print("=" * 60)
    print(f"\nFound {len(spaces_to_delete)} Spaces to delete:\n")
    for s in spaces_to_delete:
        print(f"  - {s}")

    print("\nStarting deletion...")
    print("-" * 60)

    success_count = 0
    fail_count = 0

    for space_id in spaces_to_delete:
        print(f"\n[DELETING] {space_id} ...")
        try:
            api.delete_repo(repo_id=space_id, repo_type="space")
            print(f"  ✅ Successfully deleted: {space_id}")
            success_count += 1
        except Exception as e:
            if "404" in str(e) or "not found" in str(e).lower():
                print(f"  ✅ {space_id} — Already deleted or not found (OK)")
                success_count += 1
            else:
                print(f"  ❌ Failed to delete {space_id}: {e}")
                fail_count += 1

    print("\n" + "=" * 60)
    print(f"  DONE — Deleted: {success_count}/{len(spaces_to_delete)}, Failed: {fail_count}")
    print("=" * 60)
    print("\n✅ Hugging Face Organization is now clean and ready.")
    print("   Next step: Create 'Delentia/delenti-os-live-demo' Space")


if __name__ == "__main__":
    main()
