#!/usr/bin/env python3
"""
prepare_rag_corpus.py

Parses DELENTIA_OS_PUBLIC_WHITEPAPER_v2.2.0_DRAFT.md by markdown headers (## and ###)
and chunks it into a tabular CSV structure (chunk_id, topic, text_content).
Also outputs the full raw document copy.
"""

import csv
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Setup paths
SCRIPT_DIR = Path(__file__).parent
DATASETS_DIR = SCRIPT_DIR.parent
PROCESSED_DIR = DATASETS_DIR / "processed"
RAG_OUTPUT_DIR = PROCESSED_DIR / "rag_corpus"

WHITEPAPER_PATH = (
    SCRIPT_DIR.parents[2] / "Delentia-Private-OS" / "whitepapers" / "01_foundation" / "DELENTIA_OS_PUBLIC_WHITEPAPER_v2.2.0_TH.md"
)

def chunk_markdown(content: str) -> list[dict]:
    """Parse markdown by ## and ### headers and return structured chunk dictionaries."""
    lines = content.splitlines()
    chunks = []
    
    current_header = "0. Document Info"
    current_lines = []
    chunk_count = 1
    
    header_pattern = re.compile(r"^#{2,3}\s+(.+)$")
    
    for line in lines:
        match = header_pattern.match(line)
        if match:
            # Save previous chunk
            if current_lines:
                text = "\n".join(current_lines).strip()
                if text:
                    chunks.append({
                        "chunk_id": f"chunk_{chunk_count:03d}",
                        "topic": current_header.strip(),
                        "text_content": text
                    })
                    chunk_count += 1
            current_header = match.group(1)
            current_lines = [line] # include the header line itself in the chunk
        else:
            current_lines.append(line)
            
    # Save the final chunk
    if current_lines:
        text = "\n".join(current_lines).strip()
        if text:
            chunks.append({
                "chunk_id": f"chunk_{chunk_count:03d}",
                "topic": current_header.strip(),
                "text_content": text
            })
            
    return chunks

def main():
    print("=" * 60)
    print("Delentia OS Whitepaper RAG Corpus Processor")
    print("=" * 60)
    
    if not WHITEPAPER_PATH.exists():
        print(f"❌ Error: Whitepaper file not found at {WHITEPAPER_PATH}")
        return
        
    print(f"Reading whitepaper: {WHITEPAPER_PATH}")
    content = WHITEPAPER_PATH.read_text(encoding="utf-8")
    
    # 1. Create output dir
    RAG_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 2. Write full raw md file
    full_md_dest = RAG_OUTPUT_DIR / "whitepaper_full.md"
    full_md_dest.write_text(content, encoding="utf-8")
    print(f"✅ Saved full markdown copy: {full_md_dest}")
    
    # 3. Chunk markdown content
    chunks = chunk_markdown(content)
    print(f"Parsed {len(chunks)} chunks from document.")
    
    # 4. Write tabular CSV file
    csv_dest = RAG_OUTPUT_DIR / "whitepaper_chunks.csv"
    with csv_dest.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["chunk_id", "topic", "text_content"])
        writer.writeheader()
        writer.writerows(chunks)
        
    print(f"✅ Saved structured RAG chunks CSV: {csv_dest}")

if __name__ == "__main__":
    main()
