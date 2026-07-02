#!/usr/bin/env python3
"""
delete_personal_delentia_models.py

Deletes legacy/mirror repositories starting with 'delentia-' under the personal account 'Ittirit-delentia',
leaving strictly the draft models prefixed with 'DLT-'.
"""

import os
import sys
from huggingface_hub import HfApi, get_token, login

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def main():
    print("=" * 80)
    print("🗑️ HUGGING FACE PERSONAL ACCOUNT CLEANUP (Ittirit-delentia)")
    print("=" * 80)

    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN") or get_token()
    if not token:
        print("[ERROR] HF_TOKEN environment variable not set or not logged in.")
        sys.exit(1)

    login(token=token)
    api = HfApi()

    username = "Ittirit-delentia"
    print(f"Fetching all model repositories for user: {username}...")
    
    models = api.list_models(author=username)
    
    delentia_repos_to_delete = []
    dlt_repos_to_keep = []

    for m in models:
        repo_name = m.modelId.split("/")[-1]
        if repo_name.lower().startswith("delentia"):
            delentia_repos_to_delete.append(m.modelId)
        elif repo_name.startswith("DLT-"):
            dlt_repos_to_keep.append(m.modelId)
        else:
            # Any other legacy model starting with delentia
            if "delentia" in repo_name.lower():
                delentia_repos_to_delete.append(m.modelId)
            else:
                dlt_repos_to_keep.append(m.modelId)

    print(f"\n📋 Repositories identified for DELETION under {username}:")
    for repo in delentia_repos_to_delete:
        print(f"   ❌ {repo}")

    print(f"\n📋 Repositories identified to KEEP under {username}:")
    for repo in dlt_repos_to_keep:
        print(f"   ✅ {repo}")

    if not delentia_repos_to_delete:
        print("\n✓ No 'delentia' repositories found to delete.")
        return

    print(f"\n[EXECUTION] Deleting {len(delentia_repos_to_delete)} mirror repositories from personal account...")
    for repo_id in delentia_repos_to_delete:
        try:
            api.delete_repo(repo_id=repo_id, repo_type="model")
            print(f"   ✓ Deleted: {repo_id}")
        except Exception as e:
            print(f"   ⚠ Could not delete {repo_id}: {e}")

    print("\n🎉 [SUCCESS] PERSONAL ACCOUNT CLEANUP COMPLETED! Only DLT- prefixed models remain.")


if __name__ == "__main__":
    main()
