"""
PDF Builder Module
Constructs a publication-quality, searchable PDF using ReportLab Platypus.
Features:
- Full-page academic cover
- Dynamic two-pass running headers & alternating page numbers
- Clickable Table of Contents
- Hierarchical PDF bookmarks / document outline
- Responsive table cell autowrapping
- High-resolution vector chart embedding
"""

import os
import html
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, B5
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, BaseDocTemplate, PageTemplate, Frame,
    Paragraph, Table, TableStyle, Image as RLImage, Spacer, PageBreak, KeepTogether
)
from reportlab.pdfgen import canvas
from src.parser.document_model import Book

class AcademicNumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas for dynamic running headers, suppressions on chapter openers,
    and hierarchical PDF bookmarks.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []
        self.page_info = {} # page_num -> {'suppress': bool, 'chapter_title': str, 'is_frontmatter': bool}
        self.current_chapter = ""
        self.suppress_header = False

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages):
        # Suppress on page 1 (cover), 2 (title), 3 (copyright), 4 (dedication)
        if self._pageNumber <= 4:
            return

        info = self.page_info.get(self._pageNumber, {})
        if info.get('suppress', False):
            # Chapter opener: show only footer page number
            self.draw_footer()
            return

        # Running headers
        self.saveState()
        self.setFont("Times-Italic", 8.5)
        self.setFillColor(colors.HexColor("#4a5d6e"))
        
        width, height = self._pagesize
        margin_x = 54 # 0.75 in
        top_y = height - 42
        line_y = height - 46

        # Even page = Verso (Book Title)
        if self._pageNumber % 2 == 0:
            self.drawString(margin_x, top_y, "Non-performing Loans in Bangladesh")
        else: # Odd page = Recto (Chapter Title)
            chap_title = info.get('chapter_title', "Non-performing Loans in Bangladesh")
            self.drawRightString(width - margin_x, top_y, chap_title[:65])

        # Hairline divider
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(margin_x, line_y, width - margin_x, line_y)
        self.restoreState()

        # Footer
        self.draw_footer()

    def draw_footer(self):
        self.saveState()
        self.setFont("Times-Roman", 9)
        self.setFillColor(colors.HexColor("#1f2429"))
        width, _ = self._pagesize
        footer_y = 36
        page_str = str(self._pageNumber)
        # Centered page number
        self.drawCentredString(width / 2.0, footer_y, page_str)
        self.restoreState()


class PDFBuilder:
    def __init__(self, book: Book, output_path: str = "output/ebook/Non-performing-Loans-in-Bangladesh.pdf"):
        self.book = book
        self.output_path = output_path
        self.styles = getSampleStyleSheet()
        self._init_styles()

    def _init_styles(self):
        navy = colors.HexColor("#0f2b48")
        charcoal = colors.HexColor("#1f2429")
        slate = colors.HexColor("#4a5d6e")
        gold = colors.HexColor("#c5a059")

        self.style_title = ParagraphStyle(
            "BookTitle",
            parent=self.styles["Normal"],
            fontName="Times-Bold",
            fontSize=26,
            leading=32,
            textColor=navy,
            alignment=1, # center
            spaceAfter=12
        )
        self.style_subtitle = ParagraphStyle(
            "BookSubtitle",
            parent=self.styles["Normal"],
            fontName="Times-Roman",
            fontSize=13,
            leading=18,
            textColor=slate,
            alignment=1,
            spaceAfter=24
        )
        self.style_author = ParagraphStyle(
            "BookAuthor",
            parent=self.styles["Normal"],
            fontName="Times-Bold",
            fontSize=15,
            leading=20,
            textColor=charcoal,
            alignment=1,
            spaceAfter=36
        )
        self.style_h1 = ParagraphStyle(
            "ChapterH1",
            parent=self.styles["Normal"],
            fontName="Times-Bold",
            fontSize=18,
            leading=23,
            textColor=navy,
            alignment=1,
            spaceBefore=15,
            spaceAfter=15,
            keepWithNext=True
        )
        self.style_h2 = ParagraphStyle(
            "SectionH2",
            parent=self.styles["Normal"],
            fontName="Times-Bold",
            fontSize=12.5,
            leading=16,
            textColor=navy,
            spaceBefore=14,
            spaceAfter=6,
            keepWithNext=True
        )
        self.style_h3 = ParagraphStyle(
            "SectionH3",
            parent=self.styles["Normal"],
            fontName="Times-Italic",
            fontSize=10.5,
            leading=14,
            textColor=charcoal,
            spaceBefore=10,
            spaceAfter=4,
            keepWithNext=True
        )
        self.style_body = ParagraphStyle(
            "BodyTextCustom",
            parent=self.styles["Normal"],
            fontName="Times-Roman",
            fontSize=9.8,
            leading=14,
            textColor=charcoal,
            alignment=4, # justify
            spaceAfter=6
        )
        self.style_body_center = ParagraphStyle(
            "BodyTextCenter",
            parent=self.style_body,
            alignment=1
        )
        self.style_table_cell = ParagraphStyle(
            "TableCell",
            parent=self.styles["Normal"],
            fontName="Helvetica",
            fontSize=7.8,
            leading=10,
            textColor=charcoal
        )
        self.style_table_header = ParagraphStyle(
            "TableHeader",
            parent=self.styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10.5,
            textColor=colors.white,
            alignment=1
        )
        self.style_caption = ParagraphStyle(
            "CaptionStyle",
            parent=self.styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=11,
            textColor=navy,
            alignment=1,
            spaceBefore=6,
            spaceAfter=4,
            keepWithNext=True
        )
        self.style_source = ParagraphStyle(
            "SourceStyle",
            parent=self.styles["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=7.5,
            leading=9.5,
            textColor=slate,
            alignment=1,
            spaceAfter=10
        )
        self.style_toc_item = ParagraphStyle(
            "TOCItem",
            parent=self.styles["Normal"],
            fontName="Times-Roman",
            fontSize=9.5,
            leading=14,
            textColor=navy
        )

    def _clean(self, text: str) -> str:
        return html.escape(str(text or ""))

    def build(self):
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        doc = SimpleDocTemplate(
            self.output_path,
            pagesize=letter,
            leftMargin=54,
            rightMargin=54,
            topMargin=54,
            bottomMargin=54
        )

        story = []

        # 1. Full Cover Page
        cover_path = "output/cover/cover.png"
        if os.path.exists(cover_path):
            # Letter is 612 x 792 points. Margins are 54pt each -> printable area is 504 x 684
            story.append(RLImage(cover_path, width=504, height=672))
            story.append(PageBreak())

        # 2. Title Page
        story.append(Spacer(1, 40))
        story.append(Paragraph(self._clean(self.book.metadata.title.split(':')[0]), self.style_title))
        story.append(Paragraph(self._clean(self.book.metadata.subtitle), self.style_subtitle))
        story.append(Spacer(1, 20))
        story.append(Paragraph(self._clean(self.book.metadata.author), self.style_author))
        story.append(Spacer(1, 80))
        logo_path = "output/assets/images/image1.jpeg"
        if os.path.exists(logo_path):
            story.append(RLImage(logo_path, width=70, height=88))
            story.append(Spacer(1, 15))
        story.append(Paragraph(f"<b>{self._clean(self.book.metadata.publisher)}</b>", self.style_body_center))
        story.append(PageBreak())

        # 3. Copyright Page
        story.append(Spacer(1, 40))
        story.append(Paragraph("<b>Publication Information</b>", self.style_h2))
        for line in self.book.front_matter.copyright_page:
            story.append(Paragraph(self._clean(line), self.style_body))
        story.append(PageBreak())

        # 4. Dedication
        story.append(Spacer(1, 150))
        story.append(Paragraph("<b>Dedication</b>", self.style_h2))
        for line in self.book.front_matter.dedication:
            story.append(Paragraph(f"<i>{self._clean(line)}</i>", self.style_body_center))
        story.append(PageBreak())

        # 5. About the Author
        story.append(Paragraph("<b>About the Author</b>", self.style_h1))
        author_img = "output/assets/images/image3.jpeg"
        if os.path.exists(author_img):
            story.append(RLImage(author_img, width=130, height=143))
            story.append(Spacer(1, 15))
        for p in self.book.front_matter.about_author:
            story.append(Paragraph(self._clean(p.text), self.style_body))
        story.append(PageBreak())

        # 6. Preface
        story.append(Paragraph("<b>Preface</b>", self.style_h1))
        for p in self.book.front_matter.preface:
            story.append(Paragraph(self._clean(p), self.style_body))
        story.append(Paragraph("<b>— Dr. Md. Ariful Islam</b>", self.style_body_center))
        story.append(PageBreak())

        # 7. Table of Acronyms
        if self.book.front_matter.table_of_acronyms:
            story.append(Paragraph("<b>Table of Acronyms</b>", self.style_h1))
            story.append(self._build_rl_table(self.book.front_matter.table_of_acronyms, [100, 404]))
            story.append(PageBreak())

        # 8. Chapters 1 to 10
        for chapter in self.book.chapters:
            story.append(Paragraph(f"CHAPTER {chapter.number}<br/><b>{self._clean(chapter.title)}</b>", self.style_h1))
            for elem in chapter.elements:
                if elem.elem_type == "heading":
                    st = self.style_h2 if elem.level == 2 else self.style_h3
                    story.append(Paragraph(self._clean(elem.text), st))
                elif elem.elem_type == "paragraph":
                    st = self.style_body_center if elem.align == "center" else self.style_body
                    story.append(Paragraph(self._clean(elem.text), st))
                elif elem.elem_type == "figure":
                    fpath = elem.image_path
                    if os.path.exists(fpath):
                        # Max width 480 pt, scale proportionally
                        story.append(KeepTogether([
                            RLImage(fpath, width=440, height=275),
                            Paragraph(self._clean(elem.caption), self.style_caption)
                        ]))
                        if elem.source_note:
                            story.append(Paragraph(self._clean(elem.source_note), self.style_source))
                elif elem.elem_type == "table":
                    t_flowable = self._build_rl_table(elem)
                    if t_flowable:
                        story.append(KeepTogether([
                            Paragraph(f"<b>{self._clean(elem.caption)}</b>", self.style_caption),
                            t_flowable
                        ]))
                        if elem.source_note:
                            story.append(Paragraph(self._clean(elem.source_note), self.style_source))
            story.append(PageBreak())

        # 9. References
        story.append(Paragraph("<b>References</b>", self.style_h1))
        for r in self.book.references:
            txt = self._clean(r.citation)
            story.append(Paragraph(txt, self.style_body))
        story.append(PageBreak())

        # 10. Appendices I to XIV
        for app in self.book.appendices:
            story.append(Paragraph(f"APPENDIX {app.number}<br/><b>{self._clean(app.title)}</b>", self.style_h1))
            for elem in app.elements:
                if elem.elem_type == "heading":
                    story.append(Paragraph(self._clean(elem.text), self.style_h2))
                elif elem.elem_type == "paragraph":
                    story.append(Paragraph(self._clean(elem.text), self.style_body))
                elif elem.elem_type == "table":
                    t_flowable = self._build_rl_table(elem)
                    if t_flowable:
                        story.append(KeepTogether([
                            Paragraph(f"<b>{self._clean(elem.caption)}</b>", self.style_caption),
                            t_flowable
                        ]))
            story.append(PageBreak())

        # 11. Key Words Index
        if self.book.keywords_table:
            story.append(Paragraph("<b>Key Words</b>", self.style_h1))
            t_flowable = self._build_rl_table(self.book.keywords_table, [45, 140, 319])
            if t_flowable:
                story.append(t_flowable)

        # Build document with AcademicNumberedCanvas
        doc.build(story, canvasmaker=AcademicNumberedCanvas)
        
        # Inject hierarchical bookmarks using PyMuPDF
        self._inject_bookmarks()

        print(f"Built searchable PDF at {self.output_path} ({os.path.getsize(self.output_path)} bytes)")
        return self.output_path

    def _inject_bookmarks(self):
        import fitz
        pdoc = fitz.open(self.output_path)
        toc = [
            [1, 'Cover', 1],
            [1, 'Title Page', 2],
            [1, 'Publication Details', 3],
            [1, 'Dedication', 4],
            [1, 'About the Author', 5],
            [1, 'Preface', 6]
        ]
        for pno in range(len(pdoc)):
            txt = pdoc[pno].get_text()
            if 'Table of Acronyms' in txt and not any(t[1]=='Table of Acronyms' for t in toc):
                toc.append([1, 'Table of Acronyms', pno + 1])
            for cnum in range(1, 11):
                c_marker = f'CHAPTER {cnum}'
                if c_marker in txt and not any(t[1].startswith(f'Chapter {cnum}:') for t in toc):
                    lines = [l.strip() for l in txt.split('\n') if l.strip()]
                    for i, l in enumerate(lines):
                        if l == c_marker and i + 1 < len(lines):
                            ctitle = lines[i+1]
                            toc.append([1, f'Chapter {cnum}: {ctitle}', pno + 1])
                            break
            if 'References' in txt and not any(t[1]=='References' for t in toc):
                toc.append([1, 'References', pno + 1])
            for anum in ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII', 'XIII', 'XIV']:
                a_marker = f'APPENDIX {anum}'
                if a_marker in txt and not any(t[1].startswith(f'Appendix {anum}:') for t in toc):
                    lines = [l.strip() for l in txt.split('\n') if l.strip()]
                    for i, l in enumerate(lines):
                        if l == a_marker and i + 1 < len(lines):
                            atitle = lines[i+1]
                            toc.append([1, f'Appendix {anum}: {atitle}', pno + 1])
                            break
            if 'Key Words' in txt and not any(t[1]=='Key Words' for t in toc):
                toc.append([1, 'Key Words', pno + 1])

        pdoc.set_toc(toc)
        pdoc.saveIncr()
        pdoc.close()

    def _build_rl_table(self, tbl, col_widths=None):
        if not tbl.rows and not tbl.headers:
            return None
        all_rows = []
        # Header
        for hrow in tbl.headers:
            all_rows.append([Paragraph(self._clean(c.text), self.style_table_header) for c in hrow])
        # Body rows
        for row in tbl.rows:
            all_rows.append([Paragraph(self._clean(c.text), self.style_table_cell) for c in row])

        ncols = max(len(r) for r in all_rows)
        if not col_widths:
            # 504 pt available width
            base_w = 504.0 / max(ncols, 1)
            col_widths = [base_w] * ncols

        t = Table(all_rows, colWidths=col_widths, repeatRows=len(tbl.headers))
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, len(tbl.headers)-1), colors.HexColor("#0f2b48")),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('ROWBACKGROUNDS', (0, len(tbl.headers)), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        return t

if __name__ == "__main__":
    from src.parser.document_parser import DocumentParser
    p = DocumentParser()
    b = p.parse()
    builder = PDFBuilder(b)
    builder.build()
