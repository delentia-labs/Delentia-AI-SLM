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
    api = HfApi()

    # Create repo (idempotent)
    print(f"Creating/verifying repo: {REPO_ID}")
    api.create_repo(repo_id=REPO_ID, repo_type="model", exist_ok=True, private=False)
    print(f"  ✓ Repo ready: https://huggingface.co/{REPO_ID}")

    # Upload README_MODEL.md → README.md (model card)
    readme_path = os.path.join(os.path.dirname(__file__), "README_MODEL.md")
    if os.path.exists(readme_path):
        print(f"\nUploading model card (README_MODEL.md → README.md)...")
        api.upload_file(
            path_or_fileobj=readme_path,
            path_in_repo="README.md",
            repo_id=REPO_ID,
            repo_type="model",
            commit_message="Add HuggingFace model card for Delentia SLM JITNA v0.1",
        )
        print(f"  ✓ Model card live: https://huggingface.co/{REPO_ID}")
    else:
        print("ERROR: README_MODEL.md not found")
        sys.exit(1)

    # Upload training config for reproducibility
    config_dir = os.path.join(os.path.dirname(__file__), "training", "config")
    if os.path.isdir(config_dir):
        import glob
        for config_file in glob.glob(os.path.join(config_dir, "*.yaml")):
            fname = os.path.basename(config_file)
            print(f"Uploading training config: {fname}...")
            api.upload_file(
                path_or_fileobj=config_file,
                path_in_repo=f"training_config/{fname}",
                repo_id=REPO_ID,
                repo_type="model",
                commit_message=f"Add training config: {fname}",
            )
            print(f"  ✓ https://huggingface.co/{REPO_ID}/blob/main/training_config/{fname}")

    print(f"\n✅ Done! Model card published at:")
    print(f"   https://huggingface.co/{REPO_ID}")
    print(f"\nTo download the model with Ollama (after GGUF upload):")
    print(f"   ollama run {REPO_ID}")

if __name__ == "__main__":
    main()
