#!/usr/bin/env python3
"""
PDF Merger for SonicBuilder
Supports both command-line merging and PRO manual assembly
"""
import argparse
import sys
from pathlib import Path
from pypdf import PdfReader, PdfWriter

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"

def merge_manual_inputs(inputs, output):
    """Simple merge of provided PDFs"""
    writer = PdfWriter()
    for path in inputs:
        try:
            r = PdfReader(path)
            for page in r.pages:
                writer.add_page(page)
        except Exception as e:
            print("WARN: skipping", path, "->", e)
    with open(output, "wb") as f:
        writer.write(f)

def merge_pro_manual(theme="dark"):
    """Merge all component PDFs into final PRO manual"""
    # List of PDFs to merge (in order)
    pdf_components = [
        "SonicBuilder_Pro_Cover.pdf",
        "SonicBuilder_Parts_Sheet.pdf",
        "SonicBuilder_Supersonic_Manual_v2.1.0-SB-4P.pdf",
        "SonicBuilder_Appendix_Wiring.pdf",
        "NextGen_Appendix_v2.2.0-SB-NEXTGEN.pdf"
    ]
    
    writer = PdfWriter()
    merged_count = 0
    
    for pdf_name in pdf_components:
        pdf_path = OUT / pdf_name
        if pdf_path.exists():
            try:
                reader = PdfReader(pdf_path)
                for page in reader.pages:
                    writer.add_page(page)
                merged_count += 1
                print(f"✓ Merged: {pdf_name} ({len(reader.pages)} pages)")
            except Exception as e:
                print(f"✗ Skipped {pdf_name}: {e}")
        else:
            print(f"⚠ Missing: {pdf_name} (skipping)")
    
    if merged_count == 0:
        print("Error: No PDFs found to merge")
        sys.exit(1)
    
    # Write final PRO manual
    output_file = f"SonicBuilder_PRO_Manual_Complete_{theme}.pdf"
    output_path = OUT / output_file
    with open(output_path, "wb") as f:
        writer.write(f)
    
    print(f"\n✅ Final PRO manual created: {output_path}")
    print(f"   Total components merged: {merged_count}/{len(pdf_components)}")
    print(f"   Total pages: {len(writer.pages)}")
    
    # Stamp metadata
    try:
        import pikepdf
        from pikepdf import Pdf, String
        with Pdf.open(output_path, allow_overwriting_input=True) as pdf:
            info = pdf.docinfo
            info["/Title"] = String("SonicBuilder Professional Installation Manual")
            info["/Author"] = String("SonicBuilder Engineering")
            info["/Subject"] = String("2014 Chevy Sonic LTZ Android Head Unit Installation")
            info["/Keywords"] = String("SonicBuilder,Sonic,EOENKK,Maestro,RR2,GMLAN,Teensy")
            info["/Creator"] = String("SonicBuilder PRO Pipeline")
            info["/Producer"] = String("pikepdf + pypdf")
            pdf.save(output_path)
        print("   Metadata stamped successfully")
    except Exception as e:
        print(f"   Metadata stamp warning: {e}")
    
    return output_path

def main():
    p = argparse.ArgumentParser()
    p.add_argument("inputs", nargs="*", help="PDFs to merge in order")
    p.add_argument("-o", "--output", help="Output PDF file")
    p.add_argument("--theme", default="dark", choices=["dark", "light"])
    p.add_argument("--pro", action="store_true", help="Build complete PRO manual")
    args = p.parse_args()
    
    if args.pro:
        merge_pro_manual(theme=args.theme)
    else:
        if not args.inputs or not args.output:
            p.error("inputs and --output required (or use --pro)")
        merge_manual_inputs(args.inputs, args.output)

if __name__ == "__main__":
    main()
