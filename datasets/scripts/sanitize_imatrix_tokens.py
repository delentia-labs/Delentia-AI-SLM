#!/usr/bin/env python3
"""
sanitize_imatrix_tokens.py

Converts legacy chat template tokens (<|system|>, etc.) to official Llama 3.1 templates:
  <|start_header_id|>system<|end_header_id|>\n\n
  etc.
"""
import re
import argparse
from pathlib import Path

LLAMA3_TEMPLATE_MAP = {
    r'<\|system\|>':    '<|start_header_id|>system<|end_header_id|>\n\n',
    r'<\|user\|>':      '<|start_header_id|>user<|end_header_id|>\n\n',
    r'<\|assistant\|>': '<|start_header_id|>assistant<|end_header_id|>\n\n',
    r'</s>':            '<|eot_id|>',
}

def sanitize_calib_file(input_path: str, output_path: str) -> dict:
    """Convert legacy token format to Llama 3.1 Cognitive Chat Template."""
    print(f"Reading input file from: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    stats = {}
    for old, new in LLAMA3_TEMPLATE_MAP.items():
        raw_pattern = old.replace('\\', '')
        count = content.count(raw_pattern)
        content = re.sub(old, new, content)
        stats[raw_pattern] = count
    
    print(f"Writing sanitized file to: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return stats

def main():
    parser = argparse.ArgumentParser(description="Sanitize imatrix legacy tokens to Llama 3.1 format")
    parser.add_argument("--input", type=str, default="datasets/processed/v0.4.3/delentia_v042_imatrix_calib.txt", help="Input file path")
    parser.add_argument("--output", type=str, default="datasets/processed/v0.4.3/delentia_v043_imatrix_calib.txt", help="Output file path")
    
    args = parser.parse_args()
    
    repo_dir = Path(__file__).parent.parent.parent
    input_file = repo_dir / args.input
    output_file = repo_dir / args.output
    
    if not input_file.exists():
        print(f"❌ Error: Input file {input_file} does not exist!")
        return
        
    stats = sanitize_calib_file(str(input_file), str(output_file))
    
    print("-" * 50)
    print("🎉 Token Sanitization Completed:")
    for token, count in stats.items():
        print(f"  Replacements of '{token}': {count}")
    print("-" * 50)

if __name__ == "__main__":
    main()
