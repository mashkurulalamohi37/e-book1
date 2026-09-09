"""
HTML Builder Module
Constructs a single-file, highly responsive, semantic HTML5 publication
complete with sidebar navigation, dark mode support, accessible landmarks,
scrollable financial tables, and interactive table of contents.
"""

import os
import html
from src.parser.document_model import Book

HTML_STYLES = """
:root {
  --font-serif: "Georgia", "Source Serif", "Noto Serif", "Times New Roman", serif;
  --font-sans: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --color-primary: #0f2b48;
  --color-secondary: #4a5d6e;
  --color-accent: #c5a059;
  --color-text: #1f2429;
  --color-bg: #ffffff;
  --color-bg-alt: #f8fafc;
  --color-border: #cbd5e1;
  --sidebar-w: 320px;
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

* { box-sizing: border-box; }

body {
  font-family: var(--font-serif);
  font-size: 17px;
  line-height: 1.7;
  color: var(--color-text);
  background-color: var(--color-bg);
  margin: 0;
  padding: 0;
  display: flex;
}

/* Sidebar Navigation */
#sidebar {
  width: var(--sidebar-w);
  height: 100vh;
  position: sticky;
  top: 0;
  background: var(--color-bg-alt);
  border-right: 1px solid var(--color-border);
  overflow-y: auto;
  padding: 1.5rem 1rem;
  font-family: var(--font-sans);
  font-size: 0.88rem;
  flex-shrink: 0;
}

#sidebar h2 {
  font-size: 1.1rem;
  color: var(--color-primary);
  margin-top: 0;
  border-bottom: 2px solid var(--color-accent);
  padding-bottom: 0.4rem;
}

#sidebar ul {
  list-style: none;
  padding-left: 0;
  margin: 0;
}

#sidebar li {
  margin: 0.4rem 0;
}

#sidebar a {
  color: var(--color-text);
  text-decoration: none;
  display: block;
  padding: 4px 6px;
  border-radius: 4px;
  transition: background 0.15s;
}

#sidebar a:hover {
  background: var(--color-border);
  color: var(--color-primary);
}

#sidebar .nav-ch {
  font-weight: 600;
  color: var(--color-primary);
}

/* Main Content Container */
#content {
  flex: 1;
  max-width: 900px;
  margin: 0 auto;
  padding: 2.5rem 2rem;
}

@media (max-width: 900px) {
  body { display: block; }
  #sidebar {
    position: relative;
    width: 100%;
    height: auto;
    border-right: none;
    border-bottom: 1px solid var(--color-border);
  }
  #content { padding: 1.5rem 1rem; }
}

/* Typography */
h1, h2, h3, h4 {
  font-family: var(--font-serif);
  color: var(--color-primary);
  line-height: 1.3;
}

h1 {
  font-size: 2.2rem;
  text-align: center;
  border-bottom: 2px solid var(--color-accent);
  padding-bottom: 0.6rem;
  margin-top: 3rem;
  margin-bottom: 2rem;
}

.chapter-number {
  display: block;
  font-family: var(--font-sans);
  font-size: 0.9rem;
  letter-spacing: 2px;
  color: var(--color-accent);
  text-transform: uppercase;
  margin-bottom: 0.4rem;
}

h2 {
  font-size: 1.5rem;
  margin-top: 2.2rem;
  border-left: 4px solid var(--color-accent);
  padding-left: 0.8rem;
}

h3 {
  font-size: 1.2rem;
  margin-top: 1.5rem;
  font-style: italic;
}

p {
  margin: 1rem 0;
  text-align: justify;
}

.p-center {
  text-align: center;
}

/* Figures */
figure {
  margin: 2.5rem 0;
  text-align: center;
}

figure img {
  max-width: 100%;
  height: auto;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

figcaption {
  font-family: var(--font-sans);
  font-size: 0.92rem;
  font-weight: 600;
  color: var(--color-primary);
  margin-top: 0.8rem;
}

/* Tables */
.table-container {
  width: 100%;
  overflow-x: auto;
  margin: 2rem 0;
  border: 1px solid var(--color-border);
  border-radius: 6px;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-family: var(--font-sans);
  font-size: 0.88rem;
  line-height: 1.4;
}

th, td {
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  text-align: left;
}

th {
  background: var(--color-primary);
  color: #ffffff;
  font-weight: 600;
}

tr:nth-child(even) td {
  background: var(--color-bg-alt);
}

.source-note {
  font-family: var(--font-sans);
  font-size: 0.82rem;
  font-style: italic;
  color: var(--color-secondary);
  text-align: center;
  margin-top: 0.4rem;
  margin-bottom: 1.5rem;
}

/* Front Matter Sections */
.cover-hero {
  text-align: center;
  margin-bottom: 3rem;
}

.cover-hero img {
  max-width: 480px;
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.18);
}

.title-page {
  text-align: center;
  padding: 3rem 1rem;
}

.title-page h1 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.author-portrait {
  text-align: center;
  margin: 1.5rem 0;
}

.author-portrait img {
  border-radius: 50%;
  max-width: 180px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.reference-list {
  list-style: none;
  padding-left: 0;
}

.reference-item {
  margin-bottom: 1.2rem;
  padding-left: 1.8rem;
  text-indent: -1.8rem;
  font-size: 0.95rem;
}

.reference-item a {
  color: var(--color-primary);
  word-break: break-all;
}

.back-to-top {
  display: block;
  text-align: center;
  margin: 3rem 0;
  font-family: var(--font-sans);
  font-size: 0.9rem;
  color: var(--color-secondary);
}
"""

class HTMLBuilder:
    def __init__(self, book: Book, output_path: str = "output/ebook/Non-performing-Loans-in-Bangladesh.html"):
        self.book = book
        self.output_path = output_path

    def _clean(self, text: str) -> str:
        return html.escape(str(text or ""))

    def build(self):
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        
        # Sidebar Links
        nav_links = [
            ("Cover", "#cover"),
            ("Title Page", "#titlepage"),
            ("Publication Details", "#copyright"),
            ("Dedication", "#dedication"),
            ("About the Author", "#about-author"),
            ("Preface", "#preface"),
            ("Table of Acronyms", "#acronyms")
        ]
        for c in self.book.chapters:
            nav_links.append((f"Chapter {c.number}: {c.title}", f"#chapter-{c.number}"))
        nav_links.append(("References", "#references"))
        for a in self.book.appendices:
            nav_links.append((f"Appendix {a.number}: {a.title[:35]}...", f"#{a.id}"))
        if self.book.keywords_table:
            nav_links.append(("Key Words", "#keywords"))

        sidebar_items = "\n".join(f"<li><a href='{href}' class='nav-ch'>{self._clean(title)}</a></li>" for title, href in nav_links)

        # Body Sections
        content_sections = []

        # 1. Cover
        content_sections.append("""<section id="cover" class="cover-hero">
  <img src="../cover/cover.png" alt="Book Cover: Non-performing Loans in Bangladesh"/>
</section>""")

        # 2. Title Page
        content_sections.append(f"""<section id="titlepage" class="title-page">
  <h1>{self._clean(self.book.metadata.title.split(':')[0])}</h1>
  <p style="font-size: 1.3rem; color: var(--color-secondary);">{self._clean(self.book.metadata.subtitle)}</p>
  <p style="font-size: 1.5rem; font-weight: bold; margin: 2rem 0;">{self._clean(self.book.metadata.author)}</p>
  <p><img src="../assets/images/image1.jpeg" alt="Hakkani Publishers Logo" style="max-height: 80px;"/></p>
  <p style="font-size: 1.2rem; font-weight: bold; color: var(--color-accent);">{self._clean(self.book.metadata.publisher)}</p>
</section>""")

        # 3. Copyright Page
        copy_p = "".join(f"<p>{self._clean(l)}</p>" for l in self.book.front_matter.copyright_page)
        content_sections.append(f"""<section id="copyright">
  <h2>Publication Information</h2>
  {copy_p}
</section>""")

        # 4. Dedication
        ded_p = "".join(f"<p class='p-center' style='font-style: italic;'>{self._clean(l)}</p>" for l in self.book.front_matter.dedication)
        content_sections.append(f"""<section id="dedication" style="padding: 4rem 1rem; text-align: center;">
  <h2>Dedication</h2>
  {ded_p}
</section>""")

        # 5. About Author
        bio_p = "".join(f"<p>{self._clean(p.text)}</p>" for p in self.book.front_matter.about_author)
        content_sections.append(f"""<section id="about-author">
  <h1>About the Author</h1>
  <div class="author-portrait">
    <img src="../assets/images/image3.jpeg" alt="Dr. Md. Ariful Islam Portrait"/>
  </div>
  {bio_p}
</section>""")

        # 6. Preface
        pref_p = "".join(f"<p>{self._clean(p)}</p>" for p in self.book.front_matter.preface)
        content_sections.append(f"""<section id="preface">
  <h1>Preface</h1>
  {pref_p}
  <p style="text-align: right; font-weight: bold; margin-top: 2rem;">— Dr. Md. Ariful Islam</p>
</section>""")

        # 7. Table of Acronyms
        if self.book.front_matter.table_of_acronyms:
            content_sections.append(f"""<section id="acronyms">
  <h1>Table of Acronyms</h1>
  {self._render_table_html(self.book.front_matter.table_of_acronyms)}
</section>""")

        # 8. Chapters 1 to 10
        for chapter in self.book.chapters:
            c_parts = []
            for elem in chapter.elements:
                if elem.elem_type == "heading":
                    tag = "h2" if elem.level == 2 else "h3"
                    c_parts.append(f"<{tag} id='{elem.id}'>{self._clean(elem.text)}</{tag}>")
                elif elem.elem_type == "paragraph":
                    cls = " class='p-center'" if elem.align == "center" else ""
                    c_parts.append(f"<p{cls} id='{elem.id}'>{self._clean(elem.text)}</p>")
                elif elem.elem_type == "figure":
                    fpath = f"../assets/charts/figure_{elem.number.replace('.', '_')}.png" if elem.number != "1.1" else "../assets/images/image4.jpeg"
                    c_parts.append(f"""<figure id='{elem.id}'>
  <img src='{fpath}' alt='{self._clean(elem.caption)}'/>
  <figcaption>{self._clean(elem.caption)}</figcaption>
</figure>""")
                elif elem.elem_type == "table":
                    c_parts.append(self._render_table_html(elem))

            chap_body = "\n".join(c_parts)
            content_sections.append(f"""<article id="chapter-{chapter.number}">
  <h1>
    <span class="chapter-number">Chapter {chapter.number}</span>
    {self._clean(chapter.title)}
  </h1>
  {chap_body}
  <a href="#sidebar" class="back-to-top">↑ Back to Navigation</a>
</article>""")

        # 9. References
        ref_items = []
        for r in self.book.references:
            cite = self._clean(r.citation)
            if r.url:
                url_clean = self._clean(r.url)
                cite = cite.replace(url_clean, f"<a href='{url_clean}' target='_blank' rel='noopener'>{url_clean}</a>")
            ref_items.append(f"<li class='reference-item' id='{r.id}'>{cite}</li>")
        content_sections.append(f"""<section id="references">
  <h1>References</h1>
  <ul class="reference-list">
    {"".join(ref_items)}
  </ul>
  <a href="#sidebar" class="back-to-top">↑ Back to Navigation</a>
</section>""")

        # 10. Appendices
        for app in self.book.appendices:
            a_parts = []
            for elem in app.elements:
                if elem.elem_type == "heading":
                    a_parts.append(f"<h2 id='{elem.id}'>{self._clean(elem.text)}</h2>")
                elif elem.elem_type == "paragraph":
                    a_parts.append(f"<p id='{elem.id}'>{self._clean(elem.text)}</p>")
                elif elem.elem_type == "table":
                    a_parts.append(self._render_table_html(elem))
            app_body = "\n".join(a_parts)
            content_sections.append(f"""<section id="{app.id}">
  <h1>
    <span class="chapter-number">Appendix {app.number}</span>
    {self._clean(app.title)}
  </h1>
  {app_body}
  <a href="#sidebar" class="back-to-top">↑ Back to Navigation</a>
</section>""")

        # 11. Key Words
        if self.book.keywords_table:
            content_sections.append(f"""<section id="keywords">
  <h1>Key Words</h1>
  {self._render_table_html(self.book.keywords_table)}
  <a href="#sidebar" class="back-to-top">↑ Back to Navigation</a>
</section>""")

        full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{self._clean(self.book.metadata.title)}</title>
  <style>
{HTML_STYLES}
  </style>
</head>
<body>
  <nav id="sidebar">
    <h2>Contents</h2>
    <ul>
      {sidebar_items}
    </ul>
  </nav>
  <main id="content">
    {"\n".join(content_sections)}
  </main>
</body>
</html>"""

        with open(self.output_path, "w", encoding="utf-8") as f:
            f.write(full_html)

        print(f"Built responsive HTML edition at {self.output_path} ({os.path.getsize(self.output_path)} bytes)")
        return self.output_path

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

if __name__ == "__main__":
    from src.parser.document_parser import DocumentParser
    p = DocumentParser()
    b = p.parse()
    builder = HTMLBuilder(b)
    builder.build()
