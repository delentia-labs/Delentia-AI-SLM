#!/usr/bin/env python3
"""
delete_legacy_models.py
Deletes the 12 duplicate personal mirror repositories from Ittirit-delentia on Hugging Face.
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
        sys.exit(1)
        
    api = HfApi(token=token)
    
    legacy_repos = [
        "Ittirit-delentia/delentia-slm-jitna-v0.1",
        "Ittirit-delentia/delentia-slm-jitna-v0.2",
        "Ittirit-delentia/delentia-slm-jitna-router",
        "Ittirit-delentia/delentia-slm-jitna-executor",
        "Ittirit-delentia/delentia-slm-jitna-guardian",
        "Ittirit-delentia/delentia-slm-jitna-scribe",
        "Ittirit-delentia/delentia-slm-jitna-v0.3",
        "Ittirit-delentia/delentia-slm-jitna-router-v0.4",
        "Ittirit-delentia/delentia-slm-jitna-executor-v0.4",
        "Ittirit-delentia/delentia-slm-jitna-guardian-v0.4",
        "Ittirit-delentia/delentia-slm-jitna-scribe-v0.4",
        "Ittirit-delentia/delentia-slm-jitna-v0.4",
    ]
    
    print("Starting deletion of duplicate legacy personal models...")
    success_count = 0
    fail_count = 0
    
    for repo_id in legacy_repos:
        print(f"Deleting repository: {repo_id}...")
        try:
            api.delete_repo(repo_id=repo_id, repo_type="model")
            print(f"  ✓ Successfully deleted {repo_id}")
            success_count += 1
        except Exception as e:
            # Check if the repo already doesn't exist
            if "404" in str(e) or "Repo not found" in str(e):
                print(f"  ✓ {repo_id} does not exist (already deleted)")
                success_count += 1
            else:
                print(f"  ⚠ Failed to delete {repo_id}: {e}")
                fail_count += 1
                
    print(f"\nDeletion finished. Success: {success_count}/{len(legacy_repos)}, Failed: {fail_count}")

if __name__ == "__main__":
    main()
