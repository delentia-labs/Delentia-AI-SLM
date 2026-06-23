import os
import sys
from pathlib import Path

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

def main():
    try:
        from huggingface_hub import HfApi, get_token, login
    except ImportError:
        print("ERROR: huggingface_hub not installed.")
        sys.exit(1)

    token = os.environ.get("HF_TOKEN") or get_token()
    if not token:
        print("ERROR: HF Token not found.")
        sys.exit(1)

    login(token=token)
    api = HfApi()

    # Paths
    base_dir = Path(__file__).parent
    spaces_dir = base_dir / "spaces"

    # Define the 3 spaces to upload
    spaces_to_upload = [
        {
            "name": "delentia-gatekeeper",
            "emoji": "🛡️",
            "color_from": "blue",
            "color_to": "indigo",
            "local_path": spaces_dir / "gatekeeper"
        },
        {
            "name": "delentia-scribe",
            "emoji": "🗜️",
            "color_from": "green",
            "color_to": "green",
            "local_path": spaces_dir / "scribe"
        },
        {
            "name": "delentia-executor",
            "emoji": "⚡",
            "color_from": "yellow",
            "color_to": "red",
            "local_path": spaces_dir / "executor"
        }
    ]

    for space in spaces_to_upload:
        repo_id = f"Delentia/{space['name']}"
        print(f"\n[+] Processing Space: {repo_id}")
        
        # Create Space repo if not exists
        try:
            api.create_repo(
                repo_id=repo_id,
                repo_type="space",
                space_sdk="gradio",
                exist_ok=True,
                private=False
            )
            print(f"    [OK] Repository created / verified.")
        except Exception as e:
            # Fallback to personal namespace if org access fails
            personal_repo_id = f"Ittirit-delentia/{space['name']}"
            print(f"    [WARN] Failed to create in Delentia organization: {e}")
            print(f"    [+] Trying fallback to personal namespace: {personal_repo_id}")
            try:
                api.create_repo(
                    repo_id=personal_repo_id,
                    repo_type="space",
                    space_sdk="gradio",
                    exist_ok=True,
                    private=False
                )
                repo_id = personal_repo_id
                print(f"    [OK] Repository created / verified in personal namespace.")
            except Exception as ex:
                print(f"    [ERROR] Failed to create Space: {ex}")
                continue

        # Write README.md with Gradio frontmatter
        readme_content = f"""---
title: {space['name'].replace('-', ' ').title()}
emoji: {space['emoji']}
colorFrom: {space['color_from']}
colorTo: {space['color_to']}
sdk: gradio
sdk_version: 4.44.1
python_version: "3.10"
app_file: app.py
pinned: false
---

# {space['name'].replace('-', ' ').title()}
Official interactive Gradio showroom for Delentia OS v0.4.
"""
        
        # Write files locally in temp then upload
        local_app = space["local_path"] / "app.py"
        local_req = space["local_path"] / "requirements.txt"
        
        if not local_app.exists():
            print(f"    [ERROR] app.py not found at {local_app}")
            continue

        temp_readme = space["local_path"] / "README.md"
        temp_readme.write_text(readme_content.strip(), encoding="utf-8")

        try:
            # Upload app.py
            api.upload_file(
                path_or_fileobj=str(local_app),
                path_in_repo="app.py",
                repo_id=repo_id,
                repo_type="space"
            )
            print("    [OK] app.py uploaded successfully.")

            # Upload requirements.txt if exists
            if local_req.exists():
                api.upload_file(
                    path_or_fileobj=str(local_req),
                    path_in_repo="requirements.txt",
                    repo_id=repo_id,
                    repo_type="space"
                )
                print("    [OK] requirements.txt uploaded successfully.")

            # Upload README.md
            api.upload_file(
                path_or_fileobj=str(temp_readme),
                path_in_repo="README.md",
                repo_id=repo_id,
                repo_type="space"
            )
            print("    [OK] README.md uploaded successfully.")
            print(f"    [SUCCESS] Space is live: https://huggingface.co/spaces/{repo_id}")

        except Exception as upload_err:
            print(f"    [ERROR] Failed uploading files to {repo_id}: {upload_err}")
        finally:
            if temp_readme.exists():
                temp_readme.unlink()

if __name__ == "__main__":
    main()
