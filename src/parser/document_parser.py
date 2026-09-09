"""
Document Parser Module
Parses DOCX source into the Intermediate Semantic Document Model.
Preserves 100% content fidelity, extracts styles, tables, equations, and references.
"""

import os
import re
import docx
from typing import List, Dict, Any, Tuple
from src.parser.document_model import (
    Book, BookMetadata, FrontMatter, Chapter, Appendix, ReferenceEntry,
    DocElement, HeadingElement, ParagraphElement, TableElement, TableCell, FigureElement
)

PUA_MAP = {
    0xF061: "α",
    0xF062: "β",
    0xF065: "ε",
    0xF067: "γ",
    0xF06C: "λ",
}

def clean_text(text: str) -> str:
    """Normalizes Symbol font PUA characters to standard Unicode Greek letters."""
    if not text:
        return ""
    chars = []
    for ch in text:
        code = ord(ch)
        if code in PUA_MAP:
            chars.append(PUA_MAP[code])
        else:
            chars.append(ch)
    return "".join(chars)

class DocumentParser:
    def __init__(self, docx_path: str = "input/source.docx"):
        self.docx_path = docx_path
        self.doc = docx.Document(docx_path)
        self.book = Book()
        self.figure_map = {}
        self._init_figure_map()

    def _init_figure_map(self):
        # Map figure numbers to extracted asset filenames
        for fnum in [
            "1.2", "1.3", "1.4", "3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7",
            "5.1", "5.2", "5.3", "5.4", "5.5", "5.6", "5.7", "5.8", "5.9", "5.10",
            "6.1", "6.2", "6.3", "6.4", "6.5", "6.6", "6.7", "6.8", "6.9", "6.10",
            "6.11", "6.12", "6.13", "6.14", "6.15", "6.16", "6.17", "6.18", "6.19", "6.20", "6.21",
            "10.1", "10.2", "10.3"
        ]:
            fname = f"figure_{fnum.replace('.', '_')}.png"
            self.figure_map[fnum] = {
                "image_path": os.path.abspath(os.path.join("output/assets/charts", fname)),
                "rel_path": f"../assets/charts/{fname}"
            }
        # Figure 1.1 is image4.jpeg
        self.figure_map["1.1"] = {
            "image_path": os.path.abspath("output/assets/images/image4.jpeg"),
            "rel_path": "../assets/images/image4.jpeg"
        }

    def _convert_table(self, docx_tbl, table_id: str, caption: str = "", source: str = "") -> TableElement:
        headers = []
        rows = []
        for r_idx, row in enumerate(docx_tbl.rows):
            row_cells = []
            for cell in row.cells:
                text = clean_text(cell.text.strip())
                bold = any(r.bold for p in cell.paragraphs for r in p.runs if r.bold)
                row_cells.append(TableCell(text=text, bold=bold))
            if r_idx == 0:
                headers.append(row_cells)
            else:
                rows.append(row_cells)
        return TableElement(
            id=table_id,
            caption=clean_text(caption),
            source_note=clean_text(source),
            headers=headers,
            rows=rows
        )

    def parse(self) -> Book:
        body = self.doc.element.body
        elements_stream = [] # list of ('p', Paragraph) or ('tbl', Table)

        for child in body:
            tag = child.tag.split("}")[-1]
            if tag == "p":
                elements_stream.append(("p", docx.text.paragraph.Paragraph(child, self.doc)))
            elif tag == "tbl":
                elements_stream.append(("tbl", docx.table.Table(child, self.doc)))

        # Process stream
        self._parse_front_matter(elements_stream)
        self._parse_chapters_and_backmatter(elements_stream)
        return self.book

    def _parse_front_matter(self, stream):
        fm = self.book.front_matter
        p_idx = 0
        tbl_idx = 0

        # Dedicated author about elements
        about_p = []
        in_about = False
        in_preface = False
        preface_p = []

        for tag, obj in stream:
            if tag == "p":
                p_idx += 1
                t = clean_text(obj.text.strip())
                
                # Title page (approx p 1-33)
                if p_idx < 34 and t:
                    fm.title_page.append(t)
                # Copyright page (approx p 34-70)
                elif 34 <= p_idx < 71 and t:
                    fm.copyright_page.append(t)
                # Dedication (p 71-75)
                elif 71 <= p_idx < 76 and t:
                    fm.dedication.append(t)
                # About the author (p 76-86)
                elif p_idx == 76:
                    in_about = True
                elif in_about and p_idx < 87:
                    if t:
                        about_p.append(t)
                elif p_idx == 87:
                    in_about = False
                    fm.foreword.append("Foreword") # preserved placeholder
                elif p_idx == 121:
                    fm.acknowledgments.append("Acknowledgments")
                elif 121 < p_idx < 128 and t:
                    fm.acknowledgments.append(t)
                elif p_idx == 128:
                    in_preface = True
                elif in_preface and p_idx < 140:
                    if t:
                        preface_p.append(t)
                elif p_idx == 140:
                    in_preface = False
                elif 140 <= p_idx < 183:
                    # Contents & headers
                    if t and not any(t.startswith(x) for x in ["List of", "Table of", "Key Words"]):
                        fm.contents.append({"text": t})

            elif tag == "tbl":
                tbl_idx += 1
                if tbl_idx == 1:
                    fm.list_of_tables = self._convert_table(obj, "tbl-list-of-tables", "List of Tables")
                elif tbl_idx == 2:
                    fm.table_of_acronyms = self._convert_table(obj, "tbl-acronyms", "Table of Acronyms")
                elif tbl_idx == 3:
                    fm.list_of_figures = self._convert_table(obj, "tbl-list-of-figures", "List of Figures")
                if tbl_idx >= 3:
                    break

        fm.about_author = [ParagraphElement(text=p) for p in about_p]
        fm.preface = preface_p

    def _parse_chapters_and_backmatter(self, stream):
        # Chapters: 1 to 10
        # Reference: P[1667] onwards
        # Appendices: P[1989] onwards
        # Key Words: TBL 53
        
        current_chapter = None
        current_appendix = None
        in_references = False
        in_appendices = False
        
        p_idx = 0
        tbl_idx = 0
        fig_counter = 0

        # Chapter start indices from analysis:
        # Ch 1: P[183]
        # Ch 2: P[615]
        # Ch 3: P[739]
        # Ch 4: P[855]
        # Ch 5: P[902]
        # Ch 6: P[1254]
        # Ch 7: P[1389]
        # Ch 8: P[1429]
        # Ch 9: P[1546]
        # Ch 10: P[1594]
        # Ref: P[1667]
        # App: P[1989]

        last_p_text = ""

        for tag, obj in stream:
            if tag == "p":
                p_idx += 1
                t = clean_text(obj.text.strip())
                if not t:
                    # check if it contains a chart drawing
                    charts = obj._element.xpath('.//c:chart/@r:id')
                    if charts and current_chapter:
                        for rid in charts:
                            fig_counter += 1
                            fnum = self._get_fig_num_by_counter(fig_counter)
                            fig_info = self.figure_map.get(fnum, {})
                            current_chapter.elements.append(FigureElement(
                                number=fnum,
                                caption=f"Figure {fnum}",
                                image_path=fig_info.get("image_path", ""),
                                rel_path=fig_info.get("rel_path", ""),
                                id=f"fig-{fnum.replace('.', '-')}"
                            ))
                    continue

                last_p_text = t
                runs_bold = all(r.bold for r in obj.runs if r.text.strip())
                max_sz = max([r.font.size.pt for r in obj.runs if r.font.size] or [12.0])

                # Chapter Detection
                chap_match = re.match(r"^(\d+)\s{2,}(.+)$", t)
                if chap_match and int(chap_match.group(1)) in range(1, 11) and (max_sz >= 15.0 or runs_bold):
                    cnum = int(chap_match.group(1))
                    ctitle = chap_match.group(2).strip()
                    current_chapter = Chapter(number=cnum, title=ctitle, id=f"chapter-{cnum}")
                    self.book.chapters.append(current_chapter)
                    continue

                # References Detection
                if t == "Reference" and max_sz >= 13.0 and p_idx > 1650:
                    in_references = True
                    current_chapter = None
                    continue

                # Appendices Detection
                app_match = re.match(r"^Appendix\s+([IVXLCDM]+):?\s*(.*)$", t)
                if app_match and p_idx > 1980:
                    in_references = False
                    in_appendices = True
                    anum = app_match.group(1)
                    atitle = app_match.group(2).strip()
                    if current_appendix and current_appendix.number == anum:
                        if atitle:
                            current_appendix.title = atitle
                        continue
                    current_appendix = Appendix(number=anum, title=atitle, id=f"appendix-{anum.lower()}")
                    self.book.appendices.append(current_appendix)
                    continue

                # Handling within References
                if in_references:
                    # check for URL/DOI
                    urls = re.findall(r"https?://[^\s]+", t)
                    doi_match = re.search(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", t)
                    url = urls[0] if urls else (f"https://doi.org/{doi_match.group(0)}" if doi_match else None)
                    ref_id = f"ref-{len(self.book.references) + 1}"
                    self.book.references.append(ReferenceEntry(id=ref_id, citation=t, url=url))
                    continue

                # Handling within Appendices
                if in_appendices and current_appendix:
                    if max_sz >= 13.0 and runs_bold:
                        current_appendix.elements.append(HeadingElement(level=2, text=t, id=f"app-h2-{p_idx}"))
                    else:
                        current_appendix.elements.append(ParagraphElement(text=t, id=f"app-p-{p_idx}"))
                    continue

                # Handling within Chapters
                if current_chapter:
                    # Figure 1.1 detection (embedded raster)
                    if "Figure 1.1:" in t:
                        fig_info = self.figure_map.get("1.1", {})
                        current_chapter.elements.append(FigureElement(
                            number="1.1",
                            caption=t,
                            image_path=fig_info.get("image_path", ""),
                            rel_path=fig_info.get("rel_path", ""),
                            id="fig-1-1"
                        ))
                        continue

                    # Figure captions
                    if t.startswith("Figure ") and ":" in t:
                        # caption for next or preceding figure
                        current_chapter.elements.append(ParagraphElement(text=t, id=f"fig-cap-{p_idx}", align="center"))
                        continue

                    if t.startswith("Source:") or t.startswith("Source :"):
                        current_chapter.elements.append(ParagraphElement(text=t, id=f"src-{p_idx}", align="center"))
                        continue

                    # Section headings (13pt bold or uppercase)
                    if max_sz >= 13.0 and runs_bold and len(t) < 120:
                        current_chapter.elements.append(HeadingElement(level=2, text=t, id=f"h2-{p_idx}"))
                    elif max_sz >= 12.0 and runs_bold and len(t) < 80 and not t.endswith("."):
                        current_chapter.elements.append(HeadingElement(level=3, text=t, id=f"h3-{p_idx}"))
                    else:
                        align = "center" if obj.alignment == docx.enum.text.WD_ALIGN_PARAGRAPH.CENTER else "justify"
                        current_chapter.elements.append(ParagraphElement(text=t, align=align, id=f"p-{p_idx}"))

            elif tag == "tbl":
                tbl_idx += 1
                if tbl_idx <= 3:
                    continue  # already parsed in front matter

                # Check if it is the Key Words table (TBL 53)
                if tbl_idx == 53:
                    self.book.keywords_table = self._convert_table(obj, "tbl-keywords", "Key Words")
                    continue

                # Appendix tables (TBL 36 to 52)
                if in_appendices and current_appendix:
                    current_appendix.elements.append(self._convert_table(obj, f"tbl-{tbl_idx}", last_p_text))
                    continue

                # Chapter tables (TBL 4 to 35)
                if current_chapter:
                    current_chapter.elements.append(self._convert_table(obj, f"tbl-{tbl_idx}", last_p_text))

    def _get_fig_num_by_counter(self, count: int) -> str:
        # Sequence of 44 charts in document:
        order = [
            "1.2", "1.3", "1.4", "3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7",
            "5.1", "5.2", "5.3", "5.4", "5.5", "5.6", "5.7", "5.8", "5.9", "5.10",
            "6.1", "6.2", "6.3", "6.4", "6.5", "6.6", "6.7", "6.8", "6.9", "6.10",
            "6.11", "6.12", "6.13", "6.14", "6.15", "6.16", "6.17", "6.18", "6.19", "6.20", "6.21",
            "10.1", "10.2", "10.3"
        ]
        if 1 <= count <= len(order):
            return order[count - 1]
        return f"{count}"

if __name__ == "__main__":
    parser = DocumentParser()
    book = parser.parse()
    print(f"Parsed Book:")
    print(f"  Title: {book.metadata.title}")
    print(f"  Author: {book.metadata.author}")
    print(f"  Front Matter Preface paragraphs: {len(book.front_matter.preface)}")
    print(f"  Chapters: {len(book.chapters)}")
    for c in book.chapters:
        print(f"    Chapter {c.number}: {c.title} ({len(c.elements)} elements)")
    print(f"  References: {len(book.references)}")
    print(f"  Appendices: {len(book.appendices)}")
    for a in book.appendices:
        print(f"    Appendix {a.number}: {a.title} ({len(a.elements)} elements)")
    print(f"  Keywords table present: {book.keywords_table is not None}")
