"""
upload_analyserch_intent.py

Upload the Delentia Analyserch Intent Space to Hugging Face.
Usage:
    python upload_analyserch_intent.py
    python upload_analyserch_intent.py --dry-run   # Preview only, no upload
"""

import argparse
import os
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Upload Delentia Analyserch Space to HF")
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
    print("  Delentia OS — Analyserch Space Uploader v1.0")
    print("=" * 60)

    if not args.dry_run:
        login(token=token)
        api = HfApi()
    else:
        print("[DRY RUN MODE] No files will be uploaded.")
        api = None

    base_dir = Path(__file__).parent
    space_dir = base_dir / "spaces" / "analyserch_intent"

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
        "Delentia/delentia-analyserch-intent",
        "Ittirit-delentia/delentia-analyserch-intent",
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
        print("[DRY RUN] Space URL would be: https://huggingface.co/spaces/Delentia/delentia-analyserch-intent")
        print("\n[OK] Dry run complete. Use without --dry-run to upload.")
        sys.exit(0)

    # ── Upload Phase ────────────────────────────────────────────────────────
    print("\n[2/3] Uploading files to Hugging Face...")
    target_repo = None
    for candidate in repo_candidates:
        try:
            print(f"  Attempting to upload to {candidate}...")
            # Create Space repo if not exists
            api.create_repo(
                repo_id=candidate,
                repo_type="space",
                space_sdk="gradio",
                exist_ok=True
            )
            target_repo = candidate
            print(f"  [OK] Repo target confirmed: {target_repo}")
            break
        except Exception as e:
            print(f"  [WARN] Failed to access/create repo {candidate}: {e}")

    if not target_repo:
        print("\n[ERROR] All repository targets failed. Verify permissions or set HF_TOKEN properly.")
        sys.exit(1)

    # Parallel upload using huggingface_hub
    print(f"\n[3/3] Uploading all {len(files_to_upload)} files...")
    uploaded_count = 0
    for local_path, repo_path in files_to_upload:
        try:
            api.upload_file(
                path_or_fileobj=str(local_path),
                path_in_repo=repo_path,
                repo_id=target_repo,
                repo_type="space"
            )
            print(f"  Uploaded: {repo_path}")
            uploaded_count += 1
        except Exception as e:
            print(f"  [ERROR] Failed to upload {repo_path}: {e}")

    print(f"\n[OK] Upload complete. {uploaded_count}/{len(files_to_upload)} files processed.")
    print(f"Space URL: https://huggingface.co/spaces/{target_repo}")
    print("=" * 60)


if __name__ == "__main__":
    main()
