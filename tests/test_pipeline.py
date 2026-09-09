"""
Automated Pytest Pipeline Test Suite
Verifies source fidelity, asset extraction, EPUB validity, PDF searchability,
and data integrity across all generated outputs.
"""

import os
import zipfile
import pytest
import fitz
from PIL import Image
from src.parser.document_parser import DocumentParser
from src.validation.content_validator import run_content_validation
from src.validation.link_validator import run_all_link_validation

def test_source_document_and_model():
    parser = DocumentParser("input/source.docx")
    book = parser.parse()
    assert len(book.chapters) == 10, "Book must contain exactly 10 main chapters"
    assert len(book.appendices) == 14, "Book must contain exactly 14 appendices"
    assert len(book.references) >= 200, "Book must contain >= 200 bibliographic references"
    assert book.keywords_table is not None, "Book must contain Key Words index table"
    assert book.metadata.isbn == "984-70214-0179-6"

def test_extracted_assets():
    # 5 raster images
    for img in ["image1.jpeg", "image2.jpeg", "image3.jpeg", "image4.jpeg", "image5.png"]:
        p = os.path.join("output/assets/images", img)
        assert os.path.exists(p), f"Missing raster image: {p}"
        assert os.path.getsize(p) > 1000

    # 44 vector charts
    for fnum in [
        "1.2", "1.3", "1.4", "3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7",
        "5.1", "5.2", "5.3", "5.4", "5.5", "5.6", "5.7", "5.8", "5.9", "5.10",
        "6.1", "6.2", "6.3", "6.4", "6.5", "6.6", "6.7", "6.8", "6.9", "6.10",
        "6.11", "6.12", "6.13", "6.14", "6.15", "6.16", "6.17", "6.18", "6.19", "6.20", "6.21",
        "10.1", "10.2", "10.3"
    ]:
        fname = f"figure_{fnum.replace('.', '_')}.png"
        cp = os.path.join("output/assets/charts", fname)
        assert os.path.exists(cp), f"Missing vector chart: {cp}"
        assert os.path.getsize(cp) > 5000

def test_cover_dimensions():
    cover_path = "output/cover/cover.png"
    assert os.path.exists(cover_path)
    with Image.open(cover_path) as im:
        assert im.size == (1800, 2700)

def test_epub_package():
    epub_path = "output/ebook/Non-performing-Loans-in-Bangladesh.epub"
    assert os.path.exists(epub_path)
    with zipfile.ZipFile(epub_path, "r") as z:
        infolist = z.infolist()
        assert infolist[0].filename == "mimetype"
        assert infolist[0].compress_type == zipfile.ZIP_STORED
        assert z.read("mimetype") == b"application/epub+zip"
        assert "META-INF/container.xml" in z.namelist()
        assert "EPUB/package.opf" in z.namelist()
        assert "EPUB/nav.xhtml" in z.namelist()
        assert "EPUB/cover.xhtml" in z.namelist()

def test_pdf_searchability_and_bookmarks():
    pdf_path = "output/ebook/Non-performing-Loans-in-Bangladesh.pdf"
    assert os.path.exists(pdf_path)
    doc = fitz.open(pdf_path)
    assert len(doc) >= 150
    toc = doc.get_toc()
    assert len(toc) >= 30, "PDF bookmarks outline must contain all chapters and appendices"
    # Searchable text
    full_text = " ".join(page.get_text() for page in doc)
    assert "non-performing loans" in full_text.lower()
    assert "arellano and bond" in full_text.lower()
    assert "hakkani publishers" in full_text.lower()

def test_html_deliverable():
    html_path = "output/ebook/Non-performing-Loans-in-Bangladesh.html"
    assert os.path.exists(html_path)
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "<nav id=\"sidebar\">" in content
    assert "chapter-1" in content
    assert "chapter-10" in content
    assert "appendix-xiv" in content

def test_validation_suites():
    c_res = run_content_validation()
    assert c_res["passed"] is True, "Content validation suite must pass"
    l_res = run_all_link_validation()
    assert l_res["passed"] is True, "Link and navigation validation suite must pass"
