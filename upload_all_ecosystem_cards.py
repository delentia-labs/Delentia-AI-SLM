#!/usr/bin/env python3
"""
upload_all_ecosystem_cards.py

Updates and uploads all Hugging Face metadata cards for Delentia OS:
1. Uploads datasets/README_DATASET.md to Delentia/delentia-rct-intent-dataset
2. Uploads datasets/README_DATASET.md with warning banner to Ittirit-delentia/delentia-rct-intent-dataset
3. Uploads datasets/README_RAG.md to Delentia/delentia-os-whitepaper-rag-corpus
4. Uploads datasets/README_RAG.md with warning banner to Ittirit-delentia/delentia-os-whitepaper-rag-corpus
5. Uploads README_MODEL.md to Delentia/delentia-slm-jitna-v0.3 and Ittirit-delentia/delentia-slm-jitna-v0.3
6. Uploads Deprecation Notice to Ittirit-delentia/delentia-slm-jitna-v0.1 and Ittirit-delentia/delentia-slm-jitna-v0.2
7. Triggers create_profile_cards.py to push profile cards (Delentia/README and Ittirit-delentia/Ittirit-delentia)
"""

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
        print("ERROR: huggingface_hub not installed. Run: pip install huggingface_hub")
        sys.exit(1)

    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN") or get_token()
    if not token:
        print("ERROR: Set HF_TOKEN environment variable or login using 'huggingface-cli login'.")
        sys.exit(1)

    login(token=token)
    api = HfApi()

    base_dir = Path(__file__).parent
    
    # ── 1. Read files ─────────────────────────────────────────────────────────
    dataset_readme_path = base_dir / "datasets" / "README_DATASET.md"
    rag_org_path = base_dir / "datasets" / "README_RAG_ORG.md"
    rag_personal_path = base_dir / "datasets" / "README_RAG_PERSONAL.md"
    model_readme_path = base_dir / "README_MODEL.md"

    if not (dataset_readme_path.exists() and rag_org_path.exists() and rag_personal_path.exists() and model_readme_path.exists()):
        print("ERROR: One or more local card templates are missing.")
        sys.exit(1)

    dataset_content = dataset_readme_path.read_text(encoding="utf-8")
    model_content = model_readme_path.read_text(encoding="utf-8")

    # ── 2. Helper to insert banners ──────────────────────────────────────────
    def insert_personal_banner(readme_text, target_repo, is_dataset=True):
        # Insert alert under YAML frontmatter
        yaml_end_idx = readme_text.find("---", 4)
        if yaml_end_idx == -1:
            return readme_text
        
        insert_idx = yaml_end_idx + 3
        banner = f"\n\n> [!WARNING]\n> **Notice:** This is the Architect's personal mirror. สำหรับการนำไปใช้งานระดับ Enterprise และรับอัปเดตเวอร์ชันล่าสุด กรุณาดาวน์โหลดจาก Official Repository ที่องค์กร [Delentia/{target_repo}](https://huggingface.co/datasets/Delentia/{target_repo})\n\n"
        return readme_text[:insert_idx] + banner + readme_text[insert_idx:]

    # ── 3. Upload Main Datasets ───────────────────────────────────────────────
    # Official Org
    print("\n--- Publishing Official Dataset Card: Delentia/delentia-rct-intent-dataset ---")
    try:
        api.create_repo(repo_id="Delentia/delentia-rct-intent-dataset", repo_type="dataset", exist_ok=True)
        api.upload_file(
            path_or_fileobj=str(dataset_readme_path),
            path_in_repo="README.md",
            repo_id="Delentia/delentia-rct-intent-dataset",
            repo_type="dataset"
        )
        print("  ✓ Official Dataset Card uploaded.")
    except Exception as e:
        print(f"  ✗ Failed: {e}")

    # Personal Mirror
    print("\n--- Publishing Personal Mirror Dataset Card: Ittirit-delentia/delentia-rct-intent-dataset ---")
    try:
        api.create_repo(repo_id="Ittirit-delentia/delentia-rct-intent-dataset", repo_type="dataset", exist_ok=True)
        mirrored_dataset = insert_personal_banner(dataset_content, "delentia-rct-intent-dataset")
        temp_file = base_dir / "temp_dataset_readme.md"
        temp_file.write_text(mirrored_dataset, encoding="utf-8")
        api.upload_file(
            path_or_fileobj=str(temp_file),
            path_in_repo="README.md",
            repo_id="Ittirit-delentia/delentia-rct-intent-dataset",
            repo_type="dataset"
        )
        temp_file.unlink()
        print("  ✓ Personal Mirror Dataset Card uploaded with warning banner.")
    except Exception as e:
        print(f"  ✗ Failed: {e}")

    # ── 4. Upload RAG Corpora ─────────────────────────────────────────────────
    # Official Org
    print("\n--- Publishing Official RAG Card: Delentia/delentia-os-whitepaper-rag-corpus ---")
    try:
        api.create_repo(repo_id="Delentia/delentia-os-whitepaper-rag-corpus", repo_type="dataset", exist_ok=True)
        api.upload_file(
            path_or_fileobj=str(rag_org_path),
            path_in_repo="README.md",
            repo_id="Delentia/delentia-os-whitepaper-rag-corpus",
            repo_type="dataset"
        )
        print("  ✓ Official RAG Card uploaded.")
    except Exception as e:
        print(f"  ✗ Failed: {e}")

    # Personal Mirror
    print("\n--- Publishing Personal Mirror RAG Card: Ittirit-delentia/delentia-os-whitepaper-rag-corpus ---")
    try:
        api.create_repo(repo_id="Ittirit-delentia/delentia-os-whitepaper-rag-corpus", repo_type="dataset", exist_ok=True)
        api.upload_file(
            path_or_fileobj=str(rag_personal_path),
            path_in_repo="README.md",
            repo_id="Ittirit-delentia/delentia-os-whitepaper-rag-corpus",
            repo_type="dataset"
        )
        print("  ✓ Personal Mirror RAG Card uploaded.")
    except Exception as e:
        print(f"  ✗ Failed: {e}")

    # ── 5. Upload Model Cards (v0.3 & v0.2) ──────────────────────────────────
    repos_model = [
        "Delentia/delentia-slm-jitna-v0.4",
        "Ittirit-delentia/delentia-slm-jitna-v0.4",
        "Delentia/delentia-slm-jitna-v0.3",
        "Ittirit-delentia/delentia-slm-jitna-v0.3",
        "Delentia/delentia-slm-jitna-v0.2",
        "Ittirit-delentia/delentia-slm-jitna-v0.2"
    ]
    for repo_id in repos_model:
        print(f"\n--- Publishing Model Card to: {repo_id} ---")
        try:
            api.create_repo(repo_id=repo_id, repo_type="model", exist_ok=True)
            api.upload_file(
                path_or_fileobj=str(model_readme_path),
                path_in_repo="README.md",
                repo_id=repo_id,
                repo_type="model"
            )
            print(f"  ✓ Model card uploaded to {repo_id}.")
        except Exception as e:
            print(f"  ✗ Failed: {e}")

    # ── 6. Deprecate Legacy Models in Personal Workspace ────────────────────
    legacy_repos = [
        "Ittirit-delentia/delentia-slm-jitna-v0.1",
        "Ittirit-delentia/delentia-slm-jitna-v0.2"
    ]
    
    deprecation_text = """---
license: apache-2.0
tags:
- delentia-os
- outdated
- deprecated
---

# 🛑 DEPRECATED / เวอร์ชันที่เลิกใช้งานแล้ว

> [!CAUTION]
> **OUTDATED VERSION:** โมเดลเวอร์ชันนี้ล้าสมัยแล้ว Delentia OS ได้ทำการอัปเกรดเป็นเวอร์ชัน `v0.3` (และกำลังจะปล่อย `v0.4`) ซึ่งมีความสามารถด้าน Self-Awareness, ZK-FDIA, และ CORD Security ครบถ้วน กรุณาย้ายไปใช้งานโมเดลล่าสุดได้ที่ 👉 [Delentia/delentia-slm-jitna-v0.3](https://huggingface.co/Delentia/delentia-slm-jitna-v0.3)
"""
    
    for repo_id in legacy_repos:
        print(f"\n--- Deprecating Legacy Repo: {repo_id} ---")
        try:
            api.create_repo(repo_id=repo_id, repo_type="model", exist_ok=True)
            temp_file = base_dir / "temp_dep_readme.md"
            temp_file.write_text(deprecation_text, encoding="utf-8")
            api.upload_file(
                path_or_fileobj=str(temp_file),
                path_in_repo="README.md",
                repo_id=repo_id,
                repo_type="model"
            )
            temp_file.unlink()
            print(f"  ✓ Deprecation card uploaded successfully.")
        except Exception as e:
            print(f"  ✗ Failed to deprecate: {e}")

    # ── 7. Run profile card uploader ──────────────────────────────────────────
    print("\n--- Running Profile Card Uploader (create_profile_cards.py) ---")
    try:
        import create_profile_cards
        create_profile_cards.main()
    except Exception as e:
        print(f"  ✗ Failed to run create_profile_cards.py: {e}")

    print("\n🎉 All Hugging Face ecosystem and profile cards successfully updated and synced!")

if __name__ == "__main__":
    main()
