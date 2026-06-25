#!/usr/bin/env python3
"""
create_stardew_drafts.py
Creates the 3 Stardew Valley modding adapter draft repositories under Ittirit-delentia
on Hugging Face and uploads their draft READMEs.
"""

import os
import sys
from pathlib import Path
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
    
    # Path to the brain folder drafts
    brain_dir = Path(r"C:\Users\whale\.gemini\antigravity-ide\brain\9ee3a396-2bf6-40bd-b65d-065651113cee")
    
    drafts = [
        {
            "repo_id": "Ittirit-delentia/delentia-stardew-npc-intent-lora",
            "file_name": "readme_stardew_npc.md",
            "description": "Autonomous NPC Brain"
        },
        {
            "repo_id": "Ittirit-delentia/delentia-rpg-lore-delta-lora",
            "file_name": "readme_lore_keeper.md",
            "description": "RPG Delta-Lore Keeper"
        },
        {
            "repo_id": "Ittirit-delentia/delentia-smapi-coder-lora",
            "file_name": "readme_smapi_coder.md",
            "description": "SMAPI Mod Coder"
        }
    ]
    
    print("Starting creation of Stardew Valley adapter draft repositories...")
    
    for item in drafts:
        repo_id = item["repo_id"]
        readme_path = brain_dir / item["file_name"]
        desc = item["description"]
        
        print(f"\nCreating repository for {desc}: {repo_id}...")
        try:
            # Create repository
            api.create_repo(repo_id=repo_id, repo_type="model", exist_ok=True)
            print(f"  ✓ Repository {repo_id} is ready")
            
            # Check draft README exists
            if not readme_path.exists():
                print(f"  ⚠ Error: Draft file {readme_path} not found.")
                continue
                
            # Upload README
            print(f"  Uploading README: {item['file_name']} -> {repo_id}...")
            api.upload_file(
                path_or_fileobj=str(readme_path),
                path_in_repo="README.md",
                repo_id=repo_id,
                repo_type="model",
                commit_message=f"docs: initialize online draft for {desc} lora adapter"
            )
            print(f"  ✓ README uploaded to {repo_id}")
        except Exception as e:
            print(f"  ✗ Failed for {repo_id}: {e}")
            
    print("\nDraft repositories initialization finished.")

if __name__ == "__main__":
    main()
