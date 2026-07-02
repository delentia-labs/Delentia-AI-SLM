#!/usr/bin/env python3
"""
upload_auditor_notebook.py

Uploads the verified DELENTIA_4_PILLAR_AUDITOR.ipynb notebook to the 4 Pillar
repositories on Hugging Face Hub under the '/verification_notebooks/' folder.
This ensures a static verification snapshot is persisted to prevent Link Rot.

Usage:
    $env:HF_TOKEN = "hf_xxxxxxxxxxxxxxxx"
    python training/upload_auditor_notebook.py
"""

import os
import sys
from pathlib import Path

# Repository names for the 4 pillars
PILLAR_REPOS = [
    "Delentia/delentia-slm-jitna-router-v0.4",
    "Delentia/delentia-slm-jitna-executor-v0.4",
    "Delentia/delentia-slm-jitna-guardian-v0.4",
    "Delentia/delentia-slm-jitna-scribe-v0.4",
]


def main():
    try:
        from huggingface_hub import HfApi, get_token, login
    except ImportError:
        print("ERROR: huggingface_hub not installed.")
        print("Run: pip install huggingface_hub")
        sys.exit(1)

    # Get HuggingFace token
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN") or get_token()
    if not token:
        print("ERROR: Set HF_TOKEN environment variable first or login using 'huggingface-cli login'.")
        sys.exit(1)

    login(token=token)
    api = HfApi()

    # Path to local auditor notebook
    notebook_path = Path("notebooks/DELENTIA_4_PILLAR_AUDITOR.ipynb")
    if not notebook_path.exists():
        print(f"ERROR: Local notebook '{notebook_path}' not found.")
        print("Please create the notebook before running this script.")
        sys.exit(1)

    print("🚀 Publishing Static Auditor Notebook to Hugging Face...")
    print("=" * 65)

    for repo_id in PILLAR_REPOS:
        print(f"\n📂 Target Repo: {repo_id}")
        print("   Uploading DELENTIA_4_PILLAR_AUDITOR.ipynb to /verification_notebooks/ ...")
        try:
            api.upload_file(
                path_or_fileobj=str(notebook_path),
                path_in_repo="verification_notebooks/DELENTIA_4_PILLAR_AUDITOR.ipynb",
                repo_id=repo_id,
                repo_type="model",
                commit_message="docs: upload static auditor notebook snapshot to prevent link rot",
            )
            print(f"   [OK] Notebook uploaded successfully to {repo_id}.")
        except Exception as e:
            print(f"   [WARN] Failed to upload to {repo_id}: {e}")
            print("          Verify write permissions for the repository.")

    print("\n✅ Static snapshot publishing complete.")


if __name__ == "__main__":
    main()
