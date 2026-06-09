#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract quiz questions from PDF with highlighted answers
"""
import pdfplumber
import json
import re
from pathlib import Path

pdf_path = "c:\\Users\\ADMIN\\Downloads\\LAP TRINH C++ (co DA).pdf"

# Check if file exists
if not Path(pdf_path).exists():
    print(f"File not found: {pdf_path}")
    exit(1)

questions = []

try:
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total pages: {len(pdf.pages)}")
        
        for page_num, page in enumerate(pdf.pages):
            print(f"\nExtracting page {page_num + 1}...")
            
            # Get text with layout
            text = page.extract_text()
            if not text:
                continue
            
            print(f"Page {page_num + 1} raw text (first 500 chars):\n{text[:500]}\n")
            
            # Try to extract highlights/annotations
            rects = page.rects
            print(f"Found {len(rects)} rectangles/highlights on page {page_num + 1}")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
