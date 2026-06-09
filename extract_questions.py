#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parse C++ quiz questions from PDF and convert to JSON
"""
import pdfplumber
import json
import re
from pathlib import Path

pdf_path = "c:\\Users\\ADMIN\\Downloads\\LAP TRINH C++ (co DA).pdf"

if not Path(pdf_path).exists():
    print(f"File not found: {pdf_path}")
    exit(1)

all_text = []
char_highlights = {}  # Store highlighted characters

try:
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                all_text.append(text)
            
            # Try to extract highlighted text using chars
            if hasattr(page, 'chars'):
                for char in page.chars:
                    # Check for yellow highlight (some PDFs mark highlights)
                    if char.get('top') is not None:
                        char_highlights[f"{page_num}_{char.get('top')}_{char.get('x0')}"] = char

except Exception as e:
    print(f"Error extracting: {e}")

full_text = "\n".join(all_text)

# Parse questions - pattern: "Câu N: question"
# Answers: A, B, C, D options
# Correct answer is identified by checking if it's marked as answer in the original structure

questions = []
question_pattern = r'Câu\s+(\d+):\s*(.+?)(?=Câu\s+\d+:|$)'

matches = re.finditer(question_pattern, full_text, re.DOTALL | re.MULTILINE)

for match in matches:
    q_num = match.group(1)
    q_content = match.group(2).strip()
    
    # Split into question text and options
    lines = q_content.split('\n')
    
    # Find question text (until first option)
    question_text = ""
    option_start_idx = 0
    
    for i, line in enumerate(lines):
        if re.match(r'^[A-D]\.\s', line):
            option_start_idx = i
            break
        if line.strip() and not re.match(r'^[A-D]\.\s', line):
            question_text += line + " "
    
    question_text = re.sub(r'\s+', ' ', question_text).strip()
    
    # Extract options A, B, C, D
    options = []
    option_letters = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
    correct_idx = 0
    
    current_option_idx = -1
    for i in range(option_start_idx, len(lines)):
        line = lines[i].strip()
        match_opt = re.match(r'^([A-D])\.\s+(.+)$', line)
        
        if match_opt:
            letter = match_opt.group(1)
            text = match_opt.group(2).strip()
            options.append({"text": text})
            current_option_idx = option_letters[letter]
        elif current_option_idx >= 0 and line and not re.match(r'^[A-D]\.', line):
            # Continuation of previous option
            if options:
                options[len(options) - 1]["text"] += " " + line
    
    if question_text and len(options) == 4:
        # For now, assume first correct option is A (index 0)
        # This will be manually verified later
        questions.append({
            "question": f"{q_num}. {question_text}",
            "options": options,
            "answer": 0  # Default to A - will need manual correction
        })
        print(f"Parsed Câu {q_num}")

print(f"\nTotal questions parsed: {len(questions)}")

# Save to file
output_file = "d:\\game\\questions_parsed.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)

print(f"Saved to {output_file}")
