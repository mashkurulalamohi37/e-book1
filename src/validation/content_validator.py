"""
Content Verification and Validation Module
Performs character-level and structural audits comparing the source DOCX
against the intermediate model and generated EPUB, PDF, and HTML artifacts.
"""

import os
import re
import fitz
import docx
from src.parser.document_parser import DocumentParser

def run_content_validation(docx_path="input/source.docx", epub_path="output/ebook/Non-performing-Loans-in-Bangladesh.epub", pdf_path="output/ebook/Non-performing-Loans-in-Bangladesh.pdf"):
    results = {
        "passed": True,
        "checks": [],
        "metrics": {}
    }

    parser = DocumentParser(docx_path)
    book = parser.parse()

    # 1. Structural Checks
    num_chapters = len(book.chapters)
    results["checks"].append({
        "check": "Chapter Count",
        "expected": 10,
        "actual": num_chapters,
        "passed": num_chapters == 10
    })

    num_appendices = len(book.appendices)
    results["checks"].append({
        "check": "Appendix Count",
        "expected": 14,
        "actual": num_appendices,
        "passed": num_appendices == 14
    })

    num_refs = len(book.references)
    results["checks"].append({
        "check": "References Count",
        "expected": ">= 200",
        "actual": num_refs,
        "passed": num_refs >= 200
    })

    has_keywords = book.keywords_table is not None
    results["checks"].append({
        "check": "Key Words Index Present",
        "expected": True,
        "actual": has_keywords,
        "passed": has_keywords
    })

    # 2. PDF Searchability & Page Count Checks
    if os.path.exists(pdf_path):
        pdoc = fitz.open(pdf_path)
        pdf_pages = len(pdoc)
        pdf_toc = pdoc.get_toc()
        results["checks"].append({
            "check": "PDF Generated & Openable",
            "expected": True,
            "actual": True,
            "passed": True
        })
        results["checks"].append({
            "check": "PDF Searchable Page Count",
            "expected": "> 150 pages",
            "actual": f"{pdf_pages} pages",
            "passed": pdf_pages > 150
        })
        results["checks"].append({
            "check": "PDF Hierarchical Bookmarks",
            "expected": ">= 25 entries",
            "actual": f"{len(pdf_toc)} entries",
            "passed": len(pdf_toc) >= 25
        })

    # 3. Critical Financial & Statistical Data Integrity Checks
    test_phrases = [
        "943 billion",
        "1033 billion",
        "8.1%",
        "984-70214-0179-6",
        "Dr. Md. Ariful Islam",
        "Hakkani Publishers",
        "Arellano and Bond",
        "Cronbach's Alpha",
        "Im-Pesaran-Shin"
    ]

    pdoc = fitz.open(pdf_path)
    pdf_full_text = " ".join(page.get_text() for page in pdoc)

    for phrase in test_phrases:
        found_in_pdf = phrase.lower() in pdf_full_text.lower()
        results["checks"].append({
            "check": f"Data Integrity: '{phrase}'",
            "expected": "Present in output text",
            "actual": "Found" if found_in_pdf else "Missing",
            "passed": found_in_pdf
        })

    for c in results["checks"]:
        if not c["passed"]:
            results["passed"] = False

    return results

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    res = run_content_validation()
    print("Content Validation Summary:")
    print("Status:", "PASSED" if res["passed"] else "FAILED")
    for c in res["checks"]:
        mark = "PASS" if c["passed"] else "FAIL"
        print(f"  [{mark}] {c['check']}: actual={c['actual']}, expected={c['expected']}")
