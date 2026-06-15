"""
upload_trace_ecosystem.py

Upload the Unified Delentia OS Trace Ecosystem Space to Hugging Face.
This replaces all previous individual Spaces (gatekeeper/scribe/executor).

Usage:
    python upload_trace_ecosystem.py
    python upload_trace_ecosystem.py --dry-run   # Preview only, no upload
"""

import argparse
import os
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Upload Delentia Trace Ecosystem Space to HF")
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without uploading")
    args = parser.parse_args()

    try:
        from huggingface_hub import HfApi, get_token, login
    except ImportError:
        print("ERROR: huggingface_hub not installed. Run: pip install huggingface_hub")
        sys.exit(1)

    token = os.environ.get("HF_TOKEN") or get_token()
    if not token:
        print("ERROR: HF Token not found. Set HF_TOKEN env var or run: huggingface-cli login")
        sys.exit(1)

    print("=" * 60)
    print("  Delentia OS — Trace Ecosystem Space Uploader v1.0")
    print("=" * 60)

    if not args.dry_run:
        login(token=token)
        api = HfApi()
    else:
        print("[DRY RUN MODE] No files will be uploaded.")
        api = None

    base_dir = Path(__file__).parent
    space_dir = base_dir / "spaces" / "trace_ecosystem"

    # Copy rct_control_plane from Delentia-OS to space directory before uploading
    import shutil
    source_cp = base_dir.parent / "Delentia-OS" / "rct_control_plane"
    target_cp = space_dir / "rct_control_plane"

    if source_cp.exists():
        print(f"[PREP] Copying rct_control_plane from {source_cp} to {target_cp}...")
        if target_cp.exists():
            try:
                shutil.rmtree(target_cp)
            except Exception as e:
                print(f"[WARN] Failed to remove existing target directory: {e}")
        try:
            shutil.copytree(
                source_cp,
                target_cp,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache", "tests", "*.db", "telemetry_log.csv")
            )
            print("[PREP] Copy complete.")
        except Exception as e:
            print(f"[ERROR] Failed to copy rct_control_plane: {e}")
    else:
        print(f"[WARN] Source rct_control_plane not found at {source_cp}!")

    # Dynamic file listing to upload everything recursively
    files_to_upload = []
    for path in space_dir.rglob("*"):
        if path.is_file() and "__pycache__" not in path.parts and ".pytest_cache" not in path.parts:
            repo_path = path.relative_to(space_dir).as_posix()
            files_to_upload.append((path, repo_path))

    # Target repo candidates (org first, fallback to personal)
    repo_candidates = [
        "Delentia/delentia-trace-ecosystem",
        "Ittirit-delentia/delentia-trace-ecosystem",
    ]

    # ── Validate local files ────────────────────────────────────────────────
    print("\n[1/3] Validating local files...")
    for local_path, _ in files_to_upload:
        if local_path.exists():
            size_kb = local_path.stat().st_size / 1024
            print(f"  [OK]  {local_path.name:<25} ({size_kb:.1f} KB)")
        else:
            print(f"  [!!]  {local_path.name:<25} NOT FOUND")
            if local_path.name == "app.py":
                print("      CRITICAL: app.py is required. Aborting.")
                sys.exit(1)

    if args.dry_run:
        print("\n[DRY RUN] Would upload to:", repo_candidates[0])
        print("[DRY RUN] Space URL would be: https://huggingface.co/spaces/Delentia/delentia-trace-ecosystem")
        print("\n[OK] Dry run complete. Use without --dry-run to upload.")
        return

    # ── Create / verify repo ────────────────────────────────────────────────
    print("\n[2/3] Creating / verifying Space repository...")
    repo_id = None
    for candidate in repo_candidates:
        try:
            api.create_repo(
                repo_id=candidate,
                repo_type="space",
                space_sdk="gradio",
                exist_ok=True,
                private=False,
            )
            repo_id = candidate
            print(f"  [OK]  Repository OK: {repo_id}")
            break
        except Exception as e:
            print(f"  [WARN] Failed for {candidate}: {e}")

    if repo_id is None:
        print("  [!!]  Could not create Space in any namespace. Aborting.")
        sys.exit(1)

    # ── Upload files ────────────────────────────────────────────────────────
    print(f"\n[3/3] Uploading files to {repo_id}...")
    success_count = 0
    for local_path, repo_path in files_to_upload:
        if not local_path.exists():
            print(f"  [SKIP]  Skipping {repo_path} (not found locally)")
            continue
        try:
            api.upload_file(
                path_or_fileobj=str(local_path),
                path_in_repo=repo_path,
                repo_id=repo_id,
                repo_type="space",
                commit_message=f"Upload {repo_path} -- Delentia OS Trace Ecosystem v0.4",
            )
            print(f"  [OK]  {repo_path} uploaded successfully.")
            success_count += 1
        except Exception as e:
            print(f"  [!!]  Failed to upload {repo_path}: {e}")

    # ── Summary ─────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"  Upload complete: {success_count}/{len(files_to_upload)} files")
    print(f"  Space URL: https://huggingface.co/spaces/{repo_id}")
    print(f"  API URL:   https://{repo_id.replace('/', '-').lower()}.hf.space")
    print("=" * 60)

    if success_count > 0:
        print("\n[SUCCESS] Space is building on Hugging Face -- check the URL above.")
        print("   It may take 2-5 minutes to restart and become available.")
    else:
        print("\n[WARN]  No files were uploaded successfully.")


if __name__ == "__main__":
    main()
