#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract all 200 C++ quiz questions from PDF
"""
import pdfplumber
import json
import re
from pathlib import Path

pdf_path = "c:\\Users\\ADMIN\\Downloads\\LAP TRINH C++ (co DA).pdf"

if not Path(pdf_path).exists():
    print(f"File not found: {pdf_path}")
    exit(1)

# Collect all text from PDF
all_text = []
try:
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                all_text.append(text)
except Exception as e:
    print(f"Error reading PDF: {e}")
    exit(1)

full_text = "\n".join(all_text)

# Parse questions using regex
questions = []
# Pattern: Câu N: [question text]\nA. [option]\nB. [option]\nC. [option]\nD. [option]

# Split by question numbers
question_blocks = re.split(r'(?=Câu\s+\d+:)', full_text)

for block in question_blocks:
    if not block.strip():
        continue
    
    # Extract question number
    q_match = re.match(r'Câu\s+(\d+):', block)
    if not q_match:
        continue
    
    q_num = q_match.group(1)
    
    # Extract question text (from after "Câu N:" until first option)
    q_text_match = re.search(r'Câu\s+\d+:\s*(.+?)(?=\n[A-D]\.)', block, re.DOTALL)
    if not q_text_match:
        continue
    
    q_text = re.sub(r'\s+', ' ', q_text_match.group(1)).strip()
    
    # Extract options A, B, C, D
    options = []
    option_pattern = r'^([A-D])\.\s+(.+?)(?=\n[A-D]\.|$)'
    
    for opt_match in re.finditer(option_pattern, block, re.MULTILINE | re.DOTALL):
        letter = opt_match.group(1)
        text = opt_match.group(2).strip()
        # Clean up text - remove extra newlines
        text = re.sub(r'\s+', ' ', text)
        options.append({"text": text})
    
    # Only add if we have all 4 options
    if len(options) == 4:
        # For now, default answer to A (index 0) - this needs manual review
        questions.append({
            "question": f"{q_num}. {q_text}",
            "options": options,
            "answer": 0  # Default - needs to be verified against PDF highlights
        })
        print(f"✓ Parsed Câu {q_num}")
    else:
        print(f"✗ Câu {q_num} - Expected 4 options, got {len(options)}")

print(f"\n✅ Total questions extracted: {len(questions)}")

# Save to file
output_file = "d:\\game\\questions_all.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)

print(f"Saved to {output_file}")

# Also show first few questions for verification
if questions:
    print("\n--- First question sample ---")
    print(json.dumps(questions[0], ensure_ascii=False, indent=2))
