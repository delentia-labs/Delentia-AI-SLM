"""
Upload Delentia SLM model card to HuggingFace Hub.
Usage:
    $env:HF_TOKEN = "hf_xxxxxxxxxxxxxxxx"
    python upload_model_card.py
"""
import os
import sys

def main():
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    if not token:
        print("ERROR: Set HF_TOKEN environment variable first:")
        print('  $env:HF_TOKEN = "hf_xxxxxxxxxxxxxxxx"')
        sys.exit(1)

    try:
        from huggingface_hub import HfApi, login
    except ImportError:
        print("ERROR: huggingface_hub not installed.")
        print("Run: pip install huggingface_hub")
        sys.exit(1)

    login(token=token)

    REPO_ID = "Ittirit-delentia/delentia-slm-jitna-v0.1"
    REPO_ID_ORG = "Delentia/delentia-slm-jitna-v0.1"
    api = HfApi()

    readme_path = os.path.join(os.path.dirname(__file__), "README_MODEL.md")
    if not os.path.exists(readme_path):
        print("ERROR: README_MODEL.md not found")
        sys.exit(1)

    for repo_id in [REPO_ID, REPO_ID_ORG]:
        # Create repo (idempotent)
        print(f"\nCreating/verifying repo: {repo_id}")
        try:
            api.create_repo(repo_id=repo_id, repo_type="model", exist_ok=True, private=False)
            print(f"  ✓ Repo ready: https://huggingface.co/{repo_id}")
        except Exception as e:
            print(f"  ⚠ Could not create {repo_id}: {e}")
            print(f"  Skipping {repo_id} — check org write permission")
            continue

        # Upload README_MODEL.md → README.md (model card)
        print(f"Uploading model card → README.md ...")
        api.upload_file(
            path_or_fileobj=readme_path,
            path_in_repo="README.md",
            repo_id=repo_id,
            repo_type="model",
            commit_message="fix: update FDIA canonical definition (F=Future D=Data I=Intent A=Architect)",
        )
        print(f"  ✓ Model card live: https://huggingface.co/{repo_id}")

    # Upload training config for reproducibility (personal repo only)
    config_dir = os.path.join(os.path.dirname(__file__), "training", "config")
    if os.path.isdir(config_dir):
        import glob
        for config_file in glob.glob(os.path.join(config_dir, "*.yaml")):
            fname = os.path.basename(config_file)
            print(f"Uploading training config: {fname} → {REPO_ID}...")
            api.upload_file(
                path_or_fileobj=config_file,
                path_in_repo=f"training_config/{fname}",
                repo_id=REPO_ID,
                repo_type="model",
                commit_message=f"Add training config: {fname}",
            )
            print(f"  ✓ https://huggingface.co/{REPO_ID}/blob/main/training_config/{fname}")

    print(f"\n✅ Done! Model cards published:")
    print(f"   Personal:  https://huggingface.co/{REPO_ID}")
    print(f"   Org:       https://huggingface.co/{REPO_ID_ORG}")
    print(f"\nTo download the model with Ollama (after GGUF upload):")
    print(f"   ollama run {REPO_ID}")

if __name__ == "__main__":
    main()
