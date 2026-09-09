"""
EPUB 3 Builder Module
Constructs a standards-compliant, publication-grade EPUB 3.3 package
with clean XHTML5, CSS3 typography, responsive tables, complete navigation,
cover image registration, and landmark semantics.
"""

import os
import zipfile
import html
from datetime import datetime
from src.parser.document_model import Book

CSS_CONTENT = """
@charset "utf-8";

:root {
  --font-serif: "Georgia", "Source Serif", "Noto Serif", "Times New Roman", serif;
  --font-sans: "Inter", "Source Sans Pro", "Segoe UI", "Helvetica Neue", sans-serif;
  --color-primary: #0f2b48;
  --color-secondary: #4a5d6e;
  --color-accent: #c5a059;
  --color-text: #1f2429;
  --color-bg: #ffffff;
  --color-bg-alt: #f8fafc;
  --color-border: #cbd5e1;
  --line-height: 1.65;
}

@media (prefers-color-scheme: dark) {
  :root {
    --color-primary: #8cb4d9;
    --color-secondary: #94a3b8;
    --color-accent: #e5c158;
    --color-text: #e2e8f0;
    --color-bg: #0f172a;
    --color-bg-alt: #1e293b;
    --color-border: #334155;
  }
}

body {
  font-family: var(--font-serif);
  font-size: 1.05em;
  line-height: var(--line-height);
  color: var(--color-text);
  background-color: var(--color-bg);
  margin: 1.5rem 1.2rem;
  padding: 0;
  text-rendering: optimizeLegibility;
}

h1, h2, h3, h4 {
  font-family: var(--font-serif);
  color: var(--color-primary);
  font-weight: bold;
  line-height: 1.3;
  margin-top: 1.8rem;
  margin-bottom: 0.8rem;
}

h1 {
  font-size: 1.85em;
  text-align: center;
  border-bottom: 2px solid var(--color-accent);
  padding-bottom: 0.5rem;
  margin-bottom: 1.5rem;
}

.chapter-number {
  display: block;
  font-family: var(--font-sans);
  font-size: 0.65em;
  letter-spacing: 2px;
  color: var(--color-accent);
  text-transform: uppercase;
  margin-bottom: 0.3rem;
}

h2 {
  font-size: 1.35em;
  margin-top: 1.6rem;
  border-left: 4px solid var(--color-accent);
  padding-left: 0.6rem;
}

h3 {
  font-size: 1.15em;
  margin-top: 1.2rem;
  font-style: italic;
}

p {
  margin: 0.8rem 0;
  text-align: justify;
  hyphens: auto;
}

.p-center {
  text-align: center;
}

.table-container {
  width: 100%;
  overflow-x: auto;
  margin: 1.5rem 0;
  border: 1px solid var(--color-border);
  border-radius: 4px;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-family: var(--font-sans);
  font-size: 0.88em;
  line-height: 1.4;
}

th, td {
  padding: 8px 10px;
  border: 1px solid var(--color-border);
  text-align: left;
}

th {
  background-color: var(--color-primary);
  color: #ffffff;
  font-weight: 600;
  text-align: center;
}

tr:nth-child(even) td {
  background-color: var(--color-bg-alt);
}

.caption {
  font-family: var(--font-sans);
  font-weight: bold;
  font-size: 0.92em;
  color: var(--color-primary);
  margin-top: 1rem;
  margin-bottom: 0.4rem;
  text-align: center;
}

.source-note {
  font-family: var(--font-sans);
  font-size: 0.8em;
  font-style: italic;
  color: var(--color-secondary);
  text-align: center;
  margin-top: 0.3rem;
  margin-bottom: 1.2rem;
}

figure {
  margin: 1.8rem 0;
  text-align: center;
}

figure img {
  max-width: 100%;
  height: auto;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

figcaption {
  font-family: var(--font-sans);
  font-weight: 600;
  font-size: 0.9em;
  color: var(--color-primary);
  margin-top: 0.6rem;
}

.cover-container {
  text-align: center;
  margin: 0;
  padding: 0;
}

.cover-container img {
  max-width: 100%;
  height: auto;
}

.title-page {
  text-align: center;
  padding: 4rem 1rem;
}

.book-title {
  font-size: 2.2em;
  color: var(--color-primary);
  margin-bottom: 1rem;
}

.book-subtitle {
  font-size: 1.2em;
  color: var(--color-secondary);
  margin-bottom: 2.5rem;
}

.book-author {
  font-size: 1.4em;
  color: var(--color-text);
  font-weight: bold;
  margin-bottom: 3rem;
}

.book-publisher {
  font-size: 1.1em;
  color: var(--color-accent);
  font-weight: bold;
}

.dedication {
  text-align: center;
  padding: 6rem 2rem;
  font-style: italic;
}

.author-bio {
  margin-top: 1.5rem;
}

.author-portrait {
  text-align: center;
  margin-bottom: 1.5rem;
}

.author-portrait img {
  border-radius: 50%;
  max-width: 180px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.reference-list {
  list-style-type: none;
  padding-left: 0;
}

.reference-item {
  margin-bottom: 1rem;
  padding-left: 1.5rem;
  text-indent: -1.5rem;
  font-size: 0.95em;
}

.reference-item a {
  color: var(--color-primary);
  word-break: break-all;
  text-decoration: underline;
}
"""

class EPUBBuilder:
    def __init__(self, book: Book, output_path: str = "output/ebook/Non-performing-Loans-in-Bangladesh.epub"):
        self.book = book
        self.output_path = output_path
        self.manifest_items = [] # (id, href, media_type, properties)
        self.spine_items = []    # id
        self.toc_entries = []    # (title, href, children)

    def _clean(self, text: str) -> str:
        return html.escape(str(text or ""))

    def build(self):
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        
        # Temp build dictionary: relative_path -> bytes
        files = {}

        # 1. mimetype (MUST be first file in ZIP, uncompressed)
        mimetype_bytes = b"application/epub+zip"

        # 2. META-INF/container.xml
        container_xml = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="EPUB/package.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>"""
        files["META-INF/container.xml"] = container_xml.encode("utf-8")

        # 3. Stylesheet
        files["EPUB/css/stylesheet.css"] = CSS_CONTENT.encode("utf-8")
        self.manifest_items.append(("css", "css/stylesheet.css", "text/css", None))

        # 4. Assets: Cover & Images
        cover_path = "output/cover/cover.png"
        if os.path.exists(cover_path):
            with open(cover_path, "rb") as f:
                files["EPUB/images/cover.png"] = f.read()
            self.manifest_items.append(("cover-image", "images/cover.png", "image/png", "cover-image"))

        # Embedded images
        for img in ["image1.jpeg", "image2.jpeg", "image3.jpeg", "image4.jpeg", "image5.png"]:
            p = os.path.join("output/assets/images", img)
            if os.path.exists(p):
                with open(p, "rb") as f:
                    files[f"EPUB/images/{img}"] = f.read()
                mtype = "image/png" if img.endswith(".png") else "image/jpeg"
                self.manifest_items.append((img.replace(".", "-"), f"images/{img}", mtype, None))

        # Vector charts
        for fnum in [
            "1.2", "1.3", "1.4", "3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7",
            "5.1", "5.2", "5.3", "5.4", "5.5", "5.6", "5.7", "5.8", "5.9", "5.10",
            "6.1", "6.2", "6.3", "6.4", "6.5", "6.6", "6.7", "6.8", "6.9", "6.10",
            "6.11", "6.12", "6.13", "6.14", "6.15", "6.16", "6.17", "6.18", "6.19", "6.20", "6.21",
            "10.1", "10.2", "10.3"
        ]:
            fname = f"figure_{fnum.replace('.', '_')}.png"
            cp = os.path.join("output/assets/charts", fname)
            if os.path.exists(cp):
                with open(cp, "rb") as f:
                    files[f"EPUB/charts/{fname}"] = f.read()
                self.manifest_items.append((f"chart-{fnum.replace('.', '-')}", f"charts/{fname}", "image/png", None))

        # 5. XHTML Pages
        # Cover Page
        cover_html = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="en">
<head>
  <title>Cover</title>
  <link rel="stylesheet" type="text/css" href="css/stylesheet.css"/>
</head>
<body class="cover-container" epub:type="cover">
  <img src="images/cover.png" alt="Book Cover: Non-performing Loans in Bangladesh"/>
</body>
</html>"""
        files["EPUB/cover.xhtml"] = cover_html.encode("utf-8")
        self.manifest_items.append(("cover", "cover.xhtml", "application/xhtml+xml", None))
        self.spine_items.append("cover")

        # Title Page
        title_html = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="en">
<head>
  <title>Title Page</title>
  <link rel="stylesheet" type="text/css" href="css/stylesheet.css"/>
</head>
<body epub:type="frontmatter titlepage">
  <div class="title-page">
    <h1 class="book-title">{self._clean(self.book.metadata.title.split(':')[0])}</h1>
    <div class="book-subtitle">{self._clean(self.book.metadata.subtitle)}</div>
    <div class="book-author">{self._clean(self.book.metadata.author)}</div>
    <div style="margin-top: 2rem;">
      <img src="images/image1.jpeg" alt="Hakkani Publishers Logo" style="max-height: 80px;"/>
    </div>
    <div class="book-publisher">{self._clean(self.book.metadata.publisher)}</div>
  </div>
</body>
</html>"""
        files["EPUB/titlepage.xhtml"] = title_html.encode("utf-8")
        self.manifest_items.append(("titlepage", "titlepage.xhtml", "application/xhtml+xml", None))
        self.spine_items.append("titlepage")
        self.toc_entries.append(("Title Page", "titlepage.xhtml", []))

        # Copyright Page
        copy_lines = "".join(f"<p>{self._clean(p)}</p>" for p in self.book.front_matter.copyright_page)
        copy_html = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="en">
<head>
  <title>Copyright</title>
  <link rel="stylesheet" type="text/css" href="css/stylesheet.css"/>
</head>
<body epub:type="frontmatter copyright-page">
  <section>
    <h2>Publication Details</h2>
    {copy_lines}
  </section>
</body>
</html>"""
        files["EPUB/copyright.xhtml"] = copy_html.encode("utf-8")
        self.manifest_items.append(("copyright", "copyright.xhtml", "application/xhtml+xml", None))
        self.spine_items.append("copyright")

        # Dedication
        ded_lines = "".join(f"<p class='p-center'>{self._clean(d)}</p>" for d in self.book.front_matter.dedication)
        ded_html = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="en">
<head>
  <title>Dedication</title>
  <link rel="stylesheet" type="text/css" href="css/stylesheet.css"/>
</head>
<body epub:type="frontmatter dedication">
  <div class="dedication">
    <h2>Dedication</h2>
    {ded_lines}
  </div>
</body>
</html>"""
        files["EPUB/dedication.xhtml"] = ded_html.encode("utf-8")
        self.manifest_items.append(("dedication", "dedication.xhtml", "application/xhtml+xml", None))
        self.spine_items.append("dedication")
        self.toc_entries.append(("Dedication", "dedication.xhtml", []))

        # About Author
        bio_lines = "".join(f"<p>{self._clean(p.text)}</p>" for p in self.book.front_matter.about_author)
        about_html = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="en">
<head>
  <title>About the Author</title>
  <link rel="stylesheet" type="text/css" href="css/stylesheet.css"/>
</head>
<body epub:type="frontmatter">
  <section>
    <h1>About the Author</h1>
    <div class="author-portrait">
      <img src="images/image3.jpeg" alt="Photograph of Dr. Md. Ariful Islam"/>
    </div>
    <div class="author-bio">
      {bio_lines}
    </div>
  </section>
</body>
</html>"""
        files["EPUB/about-author.xhtml"] = about_html.encode("utf-8")
        self.manifest_items.append(("about-author", "about-author.xhtml", "application/xhtml+xml", None))
        self.spine_items.append("about-author")
        self.toc_entries.append(("About the Author", "about-author.xhtml", []))

        # Preface
        preface_lines = "".join(f"<p>{self._clean(p)}</p>" for p in self.book.front_matter.preface)
        pref_html = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="en">
<head>
  <title>Preface</title>
  <link rel="stylesheet" type="text/css" href="css/stylesheet.css"/>
</head>
<body epub:type="frontmatter preface">
  <section>
    <h1>Preface</h1>
    {preface_lines}
    <p style="text-align: right; font-weight: bold; margin-top: 2rem;">— Dr. Md. Ariful Islam</p>
  </section>
</body>
</html>"""
        files["EPUB/preface.xhtml"] = pref_html.encode("utf-8")
        self.manifest_items.append(("preface", "preface.xhtml", "application/xhtml+xml", None))
        self.spine_items.append("preface")
        self.toc_entries.append(("Preface", "preface.xhtml", []))

        # Acronyms Table
        if self.book.front_matter.table_of_acronyms:
            acr_html = self._render_table_page(self.book.front_matter.table_of_acronyms, "Table of Acronyms")
            files["EPUB/acronyms.xhtml"] = acr_html.encode("utf-8")
            self.manifest_items.append(("acronyms", "acronyms.xhtml", "application/xhtml+xml", None))
            self.spine_items.append("acronyms")
            self.toc_entries.append(("Table of Acronyms", "acronyms.xhtml", []))

        # Chapters 1 to 10
        for chapter in self.book.chapters:
            c_html, c_subsections = self._render_chapter(chapter)
            fname = f"chapter-{chapter.number}.xhtml"
            files[f"EPUB/{fname}"] = c_html.encode("utf-8")
            cid = f"chapter-{chapter.number}"
            self.manifest_items.append((cid, fname, "application/xhtml+xml", None))
            self.spine_items.append(cid)
            self.toc_entries.append((f"Chapter {chapter.number}: {chapter.title}", fname, c_subsections))

        # References
        ref_html = self._render_references()
        files["EPUB/references.xhtml"] = ref_html.encode("utf-8")
        self.manifest_items.append(("references", "references.xhtml", "application/xhtml+xml", None))
        self.spine_items.append("references")
        self.toc_entries.append(("Reference", "references.xhtml", []))

        # Appendices I to XIV
        for app in self.book.appendices:
            a_html = self._render_appendix(app)
            fname = f"appendix-{app.number.lower()}.xhtml"
            files[f"EPUB/{fname}"] = a_html.encode("utf-8")
            aid = f"appendix-{app.number.lower()}"
            self.manifest_items.append((aid, fname, "application/xhtml+xml", None))
            self.spine_items.append(aid)
            self.toc_entries.append((f"Appendix {app.number}: {app.title}", fname, []))

        # Key Words Index Table
        if self.book.keywords_table:
            kw_html = self._render_table_page(self.book.keywords_table, "Key Words Index")
            files["EPUB/keywords.xhtml"] = kw_html.encode("utf-8")
            self.manifest_items.append(("keywords", "keywords.xhtml", "application/xhtml+xml", None))
            self.spine_items.append("keywords")
            self.toc_entries.append(("Key Words", "keywords.xhtml", []))

        # 6. Navigation Document (nav.xhtml)
        nav_html = self._render_nav_doc()
        files["EPUB/nav.xhtml"] = nav_html.encode("utf-8")
        self.manifest_items.append(("nav", "nav.xhtml", "application/xhtml+xml", "nav"))

        # 7. Package Document (package.opf)
        opf_xml = self._render_package_opf()
        files["EPUB/package.opf"] = opf_xml.encode("utf-8")

        # 8. NCX Fallback (toc.ncx)
        ncx_xml = self._render_ncx()
        files["EPUB/toc.ncx"] = ncx_xml.encode("utf-8")
        self.manifest_items.append(("ncx", "toc.ncx", "application/x-dtbncx+xml", None))

        # 9. Write ZIP archive
        with zipfile.ZipFile(self.output_path, "w") as z:
            # 1. mimetype (first, uncompressed)
            z.writestr("mimetype", mimetype_bytes, compress_type=zipfile.ZIP_STORED)
            # 2. rest of files (compressed)
            for path, data in files.items():
                z.writestr(path, data, compress_type=zipfile.ZIP_DEFLATED)

        print(f"Built valid EPUB 3 at {self.output_path} ({os.path.getsize(self.output_path)} bytes)")
        return self.output_path

    def _render_chapter(self, chapter):
        subsections = []
        body_parts = []
        for elem in chapter.elements:
            if elem.elem_type == "heading":
                if elem.level == 2:
                    body_parts.append(f"<h2 id='{elem.id}'>{self._clean(elem.text)}</h2>")
                    subsections.append((elem.text, f"chapter-{chapter.number}.xhtml#{elem.id}"))
                elif elem.level == 3:
                    body_parts.append(f"<h3 id='{elem.id}'>{self._clean(elem.text)}</h3>")
            elif elem.elem_type == "paragraph":
                align_cls = " class='p-center'" if elem.align == "center" else ""
                body_parts.append(f"<p{align_cls} id='{elem.id}'>{self._clean(elem.text)}</p>")
            elif elem.elem_type == "figure":
                f_img = f"charts/figure_{elem.number.replace('.', '_')}.png" if elem.number != "1.1" else "images/image4.jpeg"
                body_parts.append(f"""<figure id='{elem.id}'>
  <img src='{f_img}' alt='{self._clean(elem.caption)}'/>
  <figcaption>{self._clean(elem.caption)}</figcaption>
</figure>""")
            elif elem.elem_type == "table":
                body_parts.append(self._render_table_html(elem))

        content_html = "\n".join(body_parts)
        doc_html = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="en">
<head>
  <title>Chapter {chapter.number}: {self._clean(chapter.title)}</title>
  <link rel="stylesheet" type="text/css" href="css/stylesheet.css"/>
</head>
<body epub:type="bodymatter chapter">
  <section id="chapter-{chapter.number}">
    <h1>
      <span class="chapter-number">Chapter {chapter.number}</span>
      {self._clean(chapter.title)}
    </h1>
    {content_html}
  </section>
</body>
</html>"""
        return doc_html, subsections

    def _render_appendix(self, app):
        body_parts = []
        for elem in app.elements:
            if elem.elem_type == "heading":
                body_parts.append(f"<h2 id='{elem.id}'>{self._clean(elem.text)}</h2>")
            elif elem.elem_type == "paragraph":
                body_parts.append(f"<p id='{elem.id}'>{self._clean(elem.text)}</p>")
            elif elem.elem_type == "table":
                body_parts.append(self._render_table_html(elem))

        content_html = "\n".join(body_parts)
        return f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="en">
<head>
  <title>Appendix {app.number}: {self._clean(app.title)}</title>
  <link rel="stylesheet" type="text/css" href="css/stylesheet.css"/>
</head>
<body epub:type="backmatter appendix">
  <section id="{app.id}">
    <h1>
      <span class="chapter-number">Appendix {app.number}</span>
      {self._clean(app.title)}
    </h1>
    {content_html}
  </section>
</body>
</html>"""

    def _render_references(self):
        items = []
        for r in self.book.references:
            cite = self._clean(r.citation)
            if r.url:
                # make clickable
                url_clean = self._clean(r.url)
                cite = cite.replace(url_clean, f"<a href='{url_clean}' target='_blank'>{url_clean}</a>")
            items.append(f"<li class='reference-item' id='{r.id}'>{cite}</li>")
        list_html = "\n".join(items)
        return f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="en">
<head>
  <title>Reference</title>
  <link rel="stylesheet" type="text/css" href="css/stylesheet.css"/>
</head>
<body epub:type="backmatter bibliography">
  <section id="references">
    <h1>References</h1>
    <ul class="reference-list">
      {list_html}
    </ul>
  </section>
</body>
</html>"""

    def _render_table_page(self, tbl, page_title):
        tbl_html = self._render_table_html(tbl)
        return f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="en">
<head>
  <title>{self._clean(page_title)}</title>
  <link rel="stylesheet" type="text/css" href="css/stylesheet.css"/>
</head>
<body epub:type="frontmatter">
  <section>
    <h1>{self._clean(page_title)}</h1>
    {tbl_html}
  </section>
</body>
</html>"""

    def _render_table_html(self, tbl):
        parts = ["<div class='table-container'>", f"<table id='{tbl.id}'>"]
        if tbl.caption:
            parts.append(f"<caption>{self._clean(tbl.caption)}</caption>")
        if tbl.headers:
            parts.append("<thead>")
            for hrow in tbl.headers:
                parts.append("<tr>")
                for cell in hrow:
                    parts.append(f"<th>{self._clean(cell.text)}</th>")
                parts.append("</tr>")
            parts.append("</thead>")
        parts.append("<tbody>")
        for row in tbl.rows:
            parts.append("<tr>")
            for cell in row:
                parts.append(f"<td>{self._clean(cell.text)}</td>")
            parts.append("</tr>")
        parts.append("</tbody>")
        parts.append("</table>")
        parts.append("</div>")
        if tbl.source_note:
            parts.append(f"<p class='source-note'>{self._clean(tbl.source_note)}</p>")
        return "\n".join(parts)

    def _render_nav_doc(self):
        def render_ol(entries):
            items = []
            for title, href, children in entries:
                if children:
                    child_ol = render_ol([(t, h, []) for t, h in children])
                    items.append(f"<li><a href='{href}'>{self._clean(title)}</a>{child_ol}</li>")
                else:
                    items.append(f"<li><a href='{href}'>{self._clean(title)}</a></li>")
            return f"<ol>\n" + "\n".join(items) + "\n</ol>"

        ol_html = render_ol(self.toc_entries)
        return f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="en">
<head>
  <title>Table of Contents</title>
  <link rel="stylesheet" type="text/css" href="css/stylesheet.css"/>
</head>
<body>
  <nav epub:type="toc" id="toc">
    <h1>Table of Contents</h1>
    {ol_html}
  </nav>
  <nav epub:type="landmarks" id="landmarks" hidden="">
    <h2>Landmarks</h2>
    <ol>
      <li><a epub:type="cover" href="cover.xhtml">Cover</a></li>
      <li><a epub:type="titlepage" href="titlepage.xhtml">Title Page</a></li>
      <li><a epub:type="bodymatter" href="chapter-1.xhtml">Start of Content</a></li>
      <li><a epub:type="bibliography" href="references.xhtml">References</a></li>
    </ol>
  </nav>
</body>
</html>"""

    def _render_package_opf(self):
        items_xml = []
        for i_id, href, mtype, prop in self.manifest_items:
            prop_attr = f' properties="{prop}"' if prop else ""
            items_xml.append(f'    <item id="{i_id}" href="{href}" media-type="{mtype}"{prop_attr}/>')

        spine_xml = []
        for s_id in self.spine_items:
            spine_xml.append(f'    <itemref idref="{s_id}"/>')

        now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="pub-id" xml:lang="en">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="pub-id">urn:isbn:{self.book.metadata.isbn}</dc:identifier>
    <dc:title>{self._clean(self.book.metadata.title)}</dc:title>
    <dc:creator>{self._clean(self.book.metadata.author)}</dc:creator>
    <dc:publisher>{self._clean(self.book.metadata.publisher)}</dc:publisher>
    <dc:date>{self.book.metadata.publication_date}</dc:date>
    <dc:language>en</dc:language>
    <meta property="dcterms:modified">{now}</meta>
    <meta name="cover" content="cover-image"/>
  </metadata>
  <manifest>
{chr(10).join(items_xml)}
  </manifest>
  <spine toc="ncx">
{chr(10).join(spine_xml)}
  </spine>
</package>"""

    def _render_ncx(self):
        nav_points = []
        order = 1
        for title, href, children in self.toc_entries:
            nav_points.append(f"""    <navPoint id="np-{order}" playOrder="{order}">
      <navLabel><text>{self._clean(title)}</text></navLabel>
      <content src="{href}"/>
    </navPoint>""")
            order += 1

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="urn:isbn:{self.book.metadata.isbn}"/>
    <meta name="dtb:depth" content="2"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNumber" content="0"/>
  </head>
  <docTitle><text>{self._clean(self.book.metadata.title)}</text></docTitle>
  <navMap>
{chr(10).join(nav_points)}
  </navMap>
</ncx>"""

if __name__ == "__main__":
    from src.parser.document_parser import DocumentParser
    p = DocumentParser()
    b = p.parse()
    builder = EPUBBuilder(b)
    builder.build()
