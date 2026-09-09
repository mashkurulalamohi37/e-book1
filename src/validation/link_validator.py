"""
Link and Navigation Validator Module
Audits internal cross-references, navigation manifests, and anchor resolution
across EPUB, PDF, and HTML deliverables.
"""

import os
import re
import zipfile
import fitz
from bs4 import BeautifulSoup

def validate_epub_links(epub_path="output/ebook/Non-performing-Loans-in-Bangladesh.epub"):
    issues = []
    if not os.path.exists(epub_path):
        return {"passed": False, "issues": ["EPUB file does not exist"]}

    with zipfile.ZipFile(epub_path, "r") as z:
        # Check nav.xhtml
        nav_content = z.read("EPUB/nav.xhtml").decode("utf-8")
        soup = BeautifulSoup(nav_content, "html.parser")
        links = soup.find_all("a")
        
        all_files = set(z.namelist())
        for a in links:
            href = a.get("href")
            if not href:
                continue
            # target file and target anchor
            parts = href.split("#")
            target_file = f"EPUB/{parts[0]}" if parts[0] else ""
            if target_file and target_file not in all_files:
                issues.append(f"Nav link target file not found: {target_file}")
            elif len(parts) > 1 and target_file:
                # check anchor in file
                file_content = z.read(target_file).decode("utf-8")
                anchor = parts[1]
                if f"id=\"{anchor}\"" not in file_content and f"id='{anchor}'" not in file_content:
                    issues.append(f"Nav link anchor #{anchor} not found in {target_file}")

    return {
        "passed": len(issues) == 0,
        "total_nav_links": len(links),
        "issues": issues
    }

def validate_html_links(html_path="output/ebook/Non-performing-Loans-in-Bangladesh.html"):
    issues = []
    if not os.path.exists(html_path):
        return {"passed": False, "issues": ["HTML file does not exist"]}

    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    all_ids = {tag.get("id") for tag in soup.find_all(id=True)}
    nav_links = soup.select("#sidebar a")
    
    for a in nav_links:
        href = a.get("href")
        if href and href.startswith("#"):
            target_id = href[1:]
            if target_id not in all_ids:
                issues.append(f"Sidebar link #{target_id} has no matching element ID")

    return {
        "passed": len(issues) == 0,
        "total_sidebar_links": len(nav_links),
        "issues": issues
    }

def validate_pdf_bookmarks(pdf_path="output/ebook/Non-performing-Loans-in-Bangladesh.pdf"):
    issues = []
    if not os.path.exists(pdf_path):
        return {"passed": False, "issues": ["PDF file does not exist"]}

    doc = fitz.open(pdf_path)
    toc = doc.get_toc()
    total_pages = len(doc)

    for level, title, pageno in toc:
        if pageno < 1 or pageno > total_pages:
            issues.append(f"Bookmark '{title}' points to invalid page {pageno} (total {total_pages})")

    return {
        "passed": len(issues) == 0,
        "total_bookmarks": len(toc),
        "issues": issues
    }

def run_all_link_validation():
    e_res = validate_epub_links()
    h_res = validate_html_links()
    p_res = validate_pdf_bookmarks()
    return {
        "passed": e_res["passed"] and h_res["passed"] and p_res["passed"],
        "epub": e_res,
        "html": h_res,
        "pdf": p_res
    }

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    res = run_all_link_validation()
    print("Link & Navigation Validation:")
    print(f"  EPUB Nav Links ({res['epub'].get('total_nav_links', 0)}): {'PASSED' if res['epub']['passed'] else 'FAILED'}")
    print(f"  HTML Sidebar Links ({res['html'].get('total_sidebar_links', 0)}): {'PASSED' if res['html']['passed'] else 'FAILED'}")
    print(f"  PDF Bookmarks ({res['pdf'].get('total_bookmarks', 0)}): {'PASSED' if res['pdf']['passed'] else 'FAILED'}")
    print("Overall Status:", "PASSED" if res["passed"] else "FAILED")
