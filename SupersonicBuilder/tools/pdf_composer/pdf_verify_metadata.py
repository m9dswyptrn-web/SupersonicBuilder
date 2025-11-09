#!/usr/bin/env python3
import argparse
from pikepdf import Pdf
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="src", required=True)
    A = ap.parse_args()
    with Pdf.open(A.src) as pdf:
        info = pdf.docinfo
        print("Pages:", len(pdf.pages))
        print("Title:", info.get('/Title'))
        print("Author:", info.get('/Author'))
        print("Subject:", info.get('/Subject'))
        print("Keywords:", info.get('/Keywords'))
        print("Creator:", info.get('/Creator'))
        print("Producer:", info.get('/Producer'))
    print("✅ verified", A.src)
if __name__ == "__main__":
    main()
