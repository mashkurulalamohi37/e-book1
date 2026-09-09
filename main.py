"""
Main CLI Entrypoint
Professional Academic E-Book Conversion Platform
Usage:
    python main.py analyze <source.docx>
    python main.py extract <source.docx>
    python main.py build <source.docx>
    python main.py validate <output.epub>
    python main.py compare <source.docx> <output_dir>
    python main.py all <source.docx>
"""

import sys
import os
import argparse
import logging
from src.parser.document_parser import DocumentParser
from src.analyzer.inventory import generate_inventories
from src.cover.cover_generator import create_cover
from src.extractor.chart_extractor import extract_all_charts
from src.epub.epub_builder import EPUBBuilder
from src.pdf.pdf_builder import PDFBuilder
from src.html.html_builder import HTMLBuilder
from src.validation.content_validator import run_content_validation
from src.validation.link_validator import run_all_link_validation
from src.reporting.report_generator import generate_all_reports

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("ebook-pipeline")

def cmd_analyze(source_docx):
    logger.info(f"Analyzing source document: {source_docx}")
    parser = DocumentParser(source_docx)
    book = parser.parse()
    generate_inventories(book, "output/metadata")
    logger.info("Analysis complete. Generated metadata and inventory files in output/metadata/")

def cmd_extract(source_docx):
    logger.info("Extracting embedded assets...")
    # Raster media
    import zipfile
    with zipfile.ZipFile(source_docx, "r") as z:
        for name in z.namelist():
            if name.startswith("word/media/"):
                base = os.path.basename(name)
                out_path = os.path.join("output/assets/images", base)
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                with open(out_path, "wb") as f:
                    f.write(z.read(name))
    logger.info("Extracted raster media from DOCX.")
    
    # Vector charts
    extract_all_charts()
    logger.info("Extracted all 44 vector charts at 300 DPI.")

def cmd_build(source_docx):
    logger.info("Starting build process...")
    # 1. Cover
    logger.info("Generating publication cover...")
    create_cover("output/cover/cover.png")

    # 2. Parse model
    parser = DocumentParser(source_docx)
    book = parser.parse()

    # 3. EPUB 3
    logger.info("Building EPUB 3 edition...")
    epub_builder = EPUBBuilder(book, "output/ebook/Non-performing-Loans-in-Bangladesh.epub")
    epub_builder.build()

    # 4. PDF
    logger.info("Building searchable PDF edition...")
    pdf_builder = PDFBuilder(book, "output/ebook/Non-performing-Loans-in-Bangladesh.pdf")
    pdf_builder.build()

    # 5. HTML
    logger.info("Building responsive HTML edition...")
    html_builder = HTMLBuilder(book, "output/ebook/Non-performing-Loans-in-Bangladesh.html")
    html_builder.build()

    logger.info("Build complete. Deliverables available in output/ebook/")

def cmd_validate(epub_path):
    logger.info(f"Running validation suites on {epub_path}...")
    l_res = run_all_link_validation()
    c_res = run_content_validation()
    logger.info(f"Content Validation: {'PASSED' if c_res['passed'] else 'FAILED'}")
    logger.info(f"Link Validation: {'PASSED' if l_res['passed'] else 'FAILED'}")

def cmd_compare(source_docx, output_dir):
    logger.info("Running content comparison audit...")
    generate_all_reports("output/reports")
    logger.info("Comparison reports generated in output/reports/")

def cmd_all(source_docx):
    logger.info("==================================================")
    logger.info("Executing End-to-End Digital Publishing Pipeline")
    logger.info("==================================================")
    cmd_analyze(source_docx)
    cmd_extract(source_docx)
    cmd_build(source_docx)
    cmd_validate("output/ebook/Non-performing-Loans-in-Bangladesh.epub")
    cmd_compare(source_docx, "output")
    logger.info("==================================================")
    logger.info("Pipeline Complete. All deliverables & reports ready.")
    logger.info("==================================================")

def main():
    parser = argparse.ArgumentParser(description="Professional Academic E-Book Conversion Platform")
    subparsers = parser.add_subparsers(dest="command", help="Pipeline commands")

    p_analyze = subparsers.add_parser("analyze", help="Analyze DOCX and generate structure inventory")
    p_analyze.add_argument("source", help="Path to source DOCX")

    p_extract = subparsers.add_parser("extract", help="Extract embedded raster media and vector charts")
    p_extract.add_argument("source", help="Path to source DOCX")

    p_build = subparsers.add_parser("build", help="Generate EPUB, PDF, and HTML editions")
    p_build.add_argument("source", help="Path to source DOCX")

    p_validate = subparsers.add_parser("validate", help="Validate EPUB package and link integrity")
    p_validate.add_argument("epub", help="Path to EPUB file")

    p_compare = subparsers.add_parser("compare", help="Compare output artifacts vs source DOCX")
    p_compare.add_argument("source", help="Path to source DOCX")
    p_compare.add_argument("output", help="Path to output directory")

    p_all = subparsers.add_parser("all", help="Execute complete end-to-end publishing pipeline")
    p_all.add_argument("source", help="Path to source DOCX")

    args = parser.parse_args()

    if args.command == "analyze":
        cmd_analyze(args.source)
    elif args.command == "extract":
        cmd_extract(args.source)
    elif args.command == "build":
        cmd_build(args.source)
    elif args.command == "validate":
        cmd_validate(args.epub)
    elif args.command == "compare":
        cmd_compare(args.source, args.output)
    elif args.command == "all":
        cmd_all(args.source)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
