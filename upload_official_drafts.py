#!/usr/bin/env python3
"""
upload_official_drafts.py
Creates the 5 platform flagship adapter draft repositories under Ittirit-delentia (personal)
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
            "repo_id": "Ittirit-delentia/delentia-legal-pdpa-lora",
            "file_name": "readme_legal_pdpa.md",
            "description": "Legal & PDPA Specialist"
        },
        {
            "repo_id": "Ittirit-delentia/delentia-financial-auditor-lora",
            "file_name": "readme_financial_auditor.md",
            "description": "Financial Auditor"
        },
        {
            "repo_id": "Ittirit-delentia/delentia-ui-generator-lora",
            "file_name": "readme_ui_generator.md",
            "description": "ArtentAI / UI Generator"
        },
        {
            "repo_id": "Ittirit-delentia/delentia-medical-triage-lora",
            "file_name": "readme_medical_triage.md",
            "description": "Medical Triage & Healthcare"
        },
        {
            "repo_id": "Ittirit-delentia/delentia-system-devops-lora",
            "file_name": "readme_system_devops.md",
            "description": "System DevOps & RCT Analyst"
        }
    ]
    
    print("Starting creation of platform flagship adapter draft repositories on personal namespace...")
    
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
                commit_message=f"docs: initialize online draft for {desc} platform adapter"
            )
            print(f"  ✓ README uploaded to {repo_id}")
        except Exception as e:
            print(f"  ✗ Failed for {repo_id}: {e}")
            
    print("\nPlatform drafts initialization finished.")

if __name__ == "__main__":
    main()
