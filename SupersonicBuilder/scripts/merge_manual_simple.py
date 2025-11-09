#!/usr/bin/env python3
"""
Simple PDF merger for manual + appendix
"""
from pypdf import PdfReader, PdfWriter
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='Merge SonicBuilder manual with appendix')
    parser.add_argument('--main', required=True, help='Main manual PDF')
    parser.add_argument('--appendix', required=True, help='Appendix PDF')
    parser.add_argument('--out', required=True, help='Output merged PDF')
    
    args = parser.parse_args()
    
    # Create PDF writer
    writer = PdfWriter()
    
    # Add pages from main manual
    print(f"Reading main manual: {args.main}")
    main_reader = PdfReader(args.main)
    for page in main_reader.pages:
        writer.add_page(page)
    
    # Add pages from appendix
    print(f"Reading appendix: {args.appendix}")
    appendix_reader = PdfReader(args.appendix)
    for page in appendix_reader.pages:
        writer.add_page(page)
    
    # Write merged PDF
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, 'wb') as f:
        writer.write(f)
    
    print(f"✅ Merged -> {args.out}")
    print(f"   Main: {len(main_reader.pages)} pages")
    print(f"   Appendix: {len(appendix_reader.pages)} pages")
    print(f"   Total: {len(main_reader.pages) + len(appendix_reader.pages)} pages")

if __name__ == '__main__':
    main()
