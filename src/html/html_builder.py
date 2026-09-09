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
  --font-serif: "Georgia", "Cambria", "Times New Roman", serif;
  --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  --color-primary: #0b1d33;
  --color-secondary: #475569;
  --color-accent: #c5a059;
  --color-accent-hover: #b08d48;
  --color-text: #1e293b;
  --color-bg: #ffffff;
  --color-bg-rgb: 255, 255, 255;
  --color-bg-alt: #f8fafc;
  --color-border: #e2e8f0;
  --sidebar-w: 320px;
  --topbar-h: 56px;
  --reader-font-size: 17px;
  --content-max-w: 860px;
}

body[data-theme="sepia"] {
  --color-primary: #433422;
  --color-secondary: #63523f;
  --color-accent: #a07830;
  --color-accent-hover: #8c6724;
  --color-text: #2d241e;
  --color-bg: #fbf0d9;
  --color-bg-rgb: 251, 240, 217;
  --color-bg-alt: #f4e5c8;
  --color-border: #e6d5b8;
}

body[data-theme="dark"] {
  --color-primary: #93c5fd;
  --color-secondary: #94a3b8;
  --color-accent: #fcd34d;
  --color-accent-hover: #fde047;
  --color-text: #f1f5f9;
  --color-bg: #0f172a;
  --color-bg-rgb: 15, 23, 42;
  --color-bg-alt: #1e293b;
  --color-border: #334155;
}

@media (prefers-color-scheme: dark) {
  body:not([data-theme="light"]):not([data-theme="sepia"]) {
    --color-primary: #93c5fd;
    --color-secondary: #94a3b8;
    --color-accent: #fcd34d;
    --color-accent-hover: #fde047;
    --color-text: #f1f5f9;
    --color-bg: #0f172a;
    --color-bg-rgb: 15, 23, 42;
    --color-bg-alt: #1e293b;
    --color-border: #334155;
  }
}

* { box-sizing: border-box; margin: 0; padding: 0; }

html {
  scroll-behavior: smooth;
  scroll-padding-top: calc(var(--topbar-h) + 1rem);
}

body {
  font-family: var(--font-serif);
  font-size: var(--reader-font-size);
  line-height: 1.75;
  color: var(--color-text);
  background-color: var(--color-bg);
  transition: background-color 0.2s ease, color 0.2s ease;
  min-height: 100vh;
}

/* Sticky Top Navigation Bar */
#reader-topbar {
  position: sticky;
  top: 0;
  left: 0;
  right: 0;
  height: var(--topbar-h);
  background: rgba(var(--color-bg-rgb), 0.94);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1rem;
  z-index: 1000;
  font-family: var(--font-sans);
}

.topbar-left, .topbar-right {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.topbar-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.45rem 0.75rem;
  border-radius: 6px;
  border: 1px solid var(--color-border);
  background: var(--color-bg-alt);
  color: var(--color-text);
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.15s ease;
}

.topbar-btn:hover {
  background: var(--color-border);
  color: var(--color-primary);
}

.topbar-btn svg {
  flex-shrink: 0;
}

.chapter-indicator {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-primary);
  max-width: 320px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-left: 0.5rem;
}

@media (max-width: 800px) {
  .chapter-indicator { display: none; }
  .btn-text { display: none; }
  .topbar-btn { padding: 0.4rem 0.55rem; }
}

.font-controls, .theme-controls {
  display: flex;
  align-items: center;
  gap: 0.2rem;
  background: var(--color-bg-alt);
  padding: 2px 4px;
  border-radius: 6px;
  border: 1px solid var(--color-border);
}

.tool-btn {
  background: transparent;
  border: none;
  color: var(--color-text);
  padding: 0.25rem 0.5rem;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.15s;
}

.tool-btn:hover, .tool-btn.active {
  background: var(--color-border);
  color: var(--color-primary);
}

/* Reading Progress Bar */
#reading-progress-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 3px;
  width: 0%;
  background: var(--color-accent);
  transition: width 0.1s ease-out;
}

/* Main Layout Wrapper */
.layout-wrapper {
  display: flex;
  width: 100%;
}

/* Sidebar Navigation */
#sidebar {
  width: var(--sidebar-w);
  height: calc(100vh - var(--topbar-h));
  position: sticky;
  top: var(--topbar-h);
  background: var(--color-bg-alt);
  border-right: 1px solid var(--color-border);
  overflow-y: auto;
  padding: 1.25rem 1rem;
  font-family: var(--font-sans);
  font-size: 0.88rem;
  flex-shrink: 0;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 1050;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 2px solid var(--color-accent);
  padding-bottom: 0.6rem;
  margin-bottom: 1rem;
}

.sidebar-header h2 {
  font-size: 1.05rem;
  color: var(--color-primary);
  margin: 0;
  border: none;
  padding: 0;
}

.close-sidebar-btn {
  display: none;
  background: transparent;
  border: none;
  font-size: 1.25rem;
  cursor: pointer;
  color: var(--color-secondary);
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
}

.close-sidebar-btn:hover {
  background: var(--color-border);
  color: var(--color-primary);
}

#sidebar ul {
  list-style: none;
  padding-left: 0;
  margin: 0;
}

#sidebar li {
  margin: 0.3rem 0;
}

#sidebar a {
  color: var(--color-text);
  text-decoration: none;
  display: block;
  padding: 6px 8px;
  border-radius: 6px;
  line-height: 1.35;
  transition: background 0.15s, color 0.15s;
}

#sidebar a:hover {
  background: var(--color-border);
  color: var(--color-primary);
}

#sidebar a.active {
  background: rgba(197, 160, 89, 0.15);
  color: var(--color-primary);
  font-weight: 700;
  border-left: 3px solid var(--color-accent);
}

#sidebar-backdrop {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  z-index: 1040;
  opacity: 0;
  transition: opacity 0.3s ease;
}

/* Off-canvas Responsive Sidebar for Tablets & Mobile */
@media (max-width: 920px) {
  #sidebar {
    position: fixed;
    top: 0;
    left: 0;
    width: min(85vw, 340px);
    height: 100vh;
    transform: translateX(-100%);
    box-shadow: 6px 0 24px rgba(0, 0, 0, 0.25);
  }
  #sidebar.open {
    transform: translateX(0);
  }
  .close-sidebar-btn {
    display: block;
  }
  #sidebar-backdrop.open {
    display: block;
    opacity: 1;
  }
}

/* Main Content Container */
#content {
  flex: 1;
  max-width: var(--content-max-w);
  margin: 0 auto;
  padding: 2.5rem 2rem 6rem;
  overflow-x: hidden;
}

@media (max-width: 920px) {
  #content {
    padding: 1.5rem 1.25rem 5rem;
  }
}

@media (max-width: 480px) {
  #content {
    padding: 1.25rem 0.85rem 4rem;
  }
}

/* Typography */
h1, h2, h3, h4 {
  font-family: var(--font-serif);
  color: var(--color-primary);
  line-height: 1.3;
}

h1 {
  font-size: clamp(1.75rem, 4vw, 2.3rem);
  text-align: center;
  border-bottom: 2px solid var(--color-accent);
  padding-bottom: 0.6rem;
  margin-top: 3rem;
  margin-bottom: 2rem;
}

.chapter-number {
  display: block;
  font-family: var(--font-sans);
  font-size: 0.88rem;
  letter-spacing: 2px;
  color: var(--color-accent);
  text-transform: uppercase;
  margin-bottom: 0.4rem;
}

h2 {
  font-size: clamp(1.3rem, 2.5vw, 1.6rem);
  margin-top: 2.2rem;
  margin-bottom: 0.8rem;
  border-left: 4px solid var(--color-accent);
  padding-left: 0.8rem;
}

h3 {
  font-size: clamp(1.1rem, 2vw, 1.25rem);
  margin-top: 1.6rem;
  margin-bottom: 0.6rem;
  font-style: italic;
}

p {
  margin: 1.15rem 0;
  text-align: justify;
  text-justify: inter-word;
  overflow-wrap: break-word;
  word-wrap: break-word;
  hyphens: auto;
}

@media (max-width: 600px) {
  p {
    text-align: left;
  }
}

.p-center {
  text-align: center;
}

/* Responsive Figures & Lightbox */
figure {
  margin: 2.5rem 0;
  text-align: center;
  position: relative;
}

.figure-wrapper {
  position: relative;
  display: inline-block;
  max-width: 100%;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
  border: 1px solid var(--color-border);
  cursor: pointer;
  background: #ffffff;
}

figure img {
  display: block;
  max-width: 100%;
  height: auto;
  transition: transform 0.2s ease;
}

.figure-wrapper:hover img {
  transform: scale(1.015);
}

.zoom-badge {
  position: absolute;
  bottom: 8px;
  right: 8px;
  background: rgba(15, 43, 72, 0.85);
  color: #ffffff;
  font-family: var(--font-sans);
  font-size: 0.75rem;
  padding: 3px 8px;
  border-radius: 4px;
  backdrop-filter: blur(4px);
  pointer-events: none;
  opacity: 0.85;
}

figcaption {
  font-family: var(--font-sans);
  font-size: 0.92rem;
  font-weight: 600;
  color: var(--color-primary);
  margin-top: 0.8rem;
  padding: 0 0.5rem;
}

/* Lightbox Modal */
.image-modal {
  display: none;
  position: fixed;
  inset: 0;
  z-index: 3000;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}

.image-modal.open {
  display: flex;
}

.modal-backdrop {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.modal-content {
  position: relative;
  max-width: 95vw;
  max-height: 90vh;
  z-index: 3010;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.modal-content img {
  max-width: 100%;
  max-height: 80vh;
  object-fit: contain;
  border-radius: 8px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5);
  background: #ffffff;
}

.modal-caption {
  color: #ffffff;
  font-family: var(--font-sans);
  font-size: 0.95rem;
  margin-top: 0.85rem;
  text-align: center;
  max-width: 800px;
}

.modal-close-btn {
  position: absolute;
  top: -40px;
  right: 0;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: #ffffff;
  font-size: 1.5rem;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
}

.modal-close-btn:hover {
  background: rgba(255, 255, 255, 0.4);
}

/* Responsive Tables */
.table-container {
  width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  margin: 2rem 0;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.03);
  position: relative;
  background: var(--color-bg);
}

.table-scroll-hint {
  font-family: var(--font-sans);
  font-size: 0.74rem;
  color: var(--color-secondary);
  background: var(--color-bg-alt);
  padding: 4px 10px;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-family: var(--font-sans);
  font-size: clamp(0.78rem, 1.8vw, 0.88rem);
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
  position: sticky;
  top: 0;
  z-index: 10;
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
  max-width: min(100%, 450px);
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.18);
  height: auto;
}

.title-page {
  text-align: center;
  padding: 3rem 1rem;
}

.title-page h1 {
  font-size: clamp(1.8rem, 4.5vw, 2.6rem);
  margin-bottom: 1rem;
}

.author-portrait {
  text-align: center;
  margin: 1.5rem 0;
}

.author-portrait img {
  border-radius: 50%;
  max-width: 160px;
  height: auto;
  box-shadow: 0 4px 14px rgba(0,0,0,0.15);
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
  line-height: 1.6;
}

.reference-item a {
  color: var(--color-primary);
  word-break: break-all;
}

/* Floating Back-to-Top Button */
#btn-back-to-top {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--color-accent);
  color: #0b1d33;
  border: none;
  box-shadow: 0 4px 16px rgba(0,0,0,0.25);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  visibility: hidden;
  transition: all 0.25s ease;
  z-index: 990;
}

#btn-back-to-top.visible {
  opacity: 1;
  visibility: visible;
}

#btn-back-to-top:hover {
  background: var(--color-accent-hover);
  transform: translateY(-3px);
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
  <div class="figure-wrapper" title="Click to view full size">
    <img src='{fpath}' alt='{self._clean(elem.caption)}' loading='lazy'/>
    <span class="zoom-badge">🔍 Tap to enlarge</span>
  </div>
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
  <!-- Sticky Topbar Navigation -->
  <header id="reader-topbar">
    <div class="topbar-left">
      <button id="btn-toggle-sidebar" class="topbar-btn" aria-label="Toggle Table of Contents" title="Table of Contents">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>
        <span class="btn-text">Contents</span>
      </button>
      <a href="/" class="topbar-btn" title="Back to Portal">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>
        <span class="btn-text">Portal</span>
      </a>
      <span id="current-chapter-indicator" class="chapter-indicator">Non-performing Loans in Bangladesh</span>
    </div>
    <div class="topbar-right">
      <div class="font-controls">
        <button id="btn-font-dec" class="tool-btn" title="Decrease Font Size">A-</button>
        <button id="btn-font-inc" class="tool-btn" title="Increase Font Size">A+</button>
      </div>
      <div class="theme-controls">
        <button id="theme-light-btn" class="tool-btn" title="Light Theme">☀️</button>
        <button id="theme-sepia-btn" class="tool-btn" title="Sepia Theme">📜</button>
        <button id="theme-dark-btn" class="tool-btn" title="Dark Theme">🌙</button>
      </div>
    </div>
    <div id="reading-progress-bar"></div>
  </header>

  <!-- Responsive Layout -->
  <div class="layout-wrapper">
    <div id="sidebar-backdrop"></div>
    <nav id="sidebar">
      <div class="sidebar-header">
        <h2>Contents</h2>
        <button id="btn-close-sidebar" class="close-sidebar-btn" aria-label="Close Table of Contents">✕</button>
      </div>
      <ul>
        {sidebar_items}
      </ul>
    </nav>
    <main id="content">
      {"\n".join(content_sections)}
    </main>
  </div>

  <!-- Image Zoom Lightbox Modal -->
  <div id="image-modal" class="image-modal" role="dialog" aria-hidden="true">
    <div class="modal-backdrop" id="modal-backdrop"></div>
    <div class="modal-content">
      <button id="modal-close" class="modal-close-btn" aria-label="Close image">✕</button>
      <img id="modal-img" src="" alt="Enlarged figure"/>
      <div id="modal-caption" class="modal-caption"></div>
    </div>
  </div>

  <!-- Floating Back to Top Button -->
  <button id="btn-back-to-top" title="Scroll to Top" aria-label="Scroll to top">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="18 15 12 9 6 15"></polyline></svg>
  </button>

  <script>
    // Responsive Sidebar Drawer
    const sidebar = document.getElementById('sidebar');
    const backdrop = document.getElementById('sidebar-backdrop');
    const btnToggleSidebar = document.getElementById('btn-toggle-sidebar');
    const btnCloseSidebar = document.getElementById('btn-close-sidebar');

    function openSidebar() {{
      sidebar.classList.add('open');
      backdrop.classList.add('open');
      if (window.innerWidth <= 920) document.body.style.overflow = 'hidden';
    }}

    function closeSidebar() {{
      sidebar.classList.remove('open');
      backdrop.classList.remove('open');
      document.body.style.overflow = '';
    }}

    if (btnToggleSidebar) btnToggleSidebar.addEventListener('click', () => {{
      sidebar.classList.contains('open') ? closeSidebar() : openSidebar();
    }});
    if (btnCloseSidebar) btnCloseSidebar.addEventListener('click', closeSidebar);
    if (backdrop) backdrop.addEventListener('click', closeSidebar);

    // Auto-close on link click (mobile)
    document.querySelectorAll('#sidebar a').forEach(a => {{
      a.addEventListener('click', () => {{
        if (window.innerWidth <= 920) closeSidebar();
      }});
    }});

    // Reading Progress & Floating Back to Top
    const progressBar = document.getElementById('reading-progress-bar');
    const backToTopBtn = document.getElementById('btn-back-to-top');

    window.addEventListener('scroll', () => {{
      const scrollTop = window.scrollY;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      if (docHeight > 0 && progressBar) {{
        const pct = Math.min(100, Math.max(0, (scrollTop / docHeight) * 100));
        progressBar.style.width = pct + '%';
      }}
      if (backToTopBtn) {{
        if (scrollTop > 350) backToTopBtn.classList.add('visible');
        else backToTopBtn.classList.remove('visible');
      }}
    }});

    if (backToTopBtn) {{
      backToTopBtn.addEventListener('click', () => {{
        window.scrollTo({{ top: 0, behavior: 'smooth' }});
      }});
    }}

    // Dynamic Font Sizing
    let currentFontSize = parseInt(localStorage.getItem('reader-font-size') || '17', 10);
    function setFontSize(sz) {{
      currentFontSize = Math.min(24, Math.max(14, sz));
      document.documentElement.style.setProperty('--reader-font-size', currentFontSize + 'px');
      localStorage.setItem('reader-font-size', currentFontSize);
    }}
    setFontSize(currentFontSize);

    document.getElementById('btn-font-dec')?.addEventListener('click', () => setFontSize(currentFontSize - 1));
    document.getElementById('btn-font-inc')?.addEventListener('click', () => setFontSize(currentFontSize + 1));

    // Theme Switcher (Light / Sepia / Dark)
    function setTheme(theme) {{
      document.body.setAttribute('data-theme', theme);
      localStorage.setItem('reader-theme', theme);
      document.querySelectorAll('.theme-controls .tool-btn').forEach(b => b.classList.remove('active'));
      const activeBtn = document.getElementById('theme-' + theme + '-btn');
      if (activeBtn) activeBtn.classList.add('active');
    }}
    const savedTheme = localStorage.getItem('reader-theme') || 'default';
    if (savedTheme !== 'default') setTheme(savedTheme);

    document.getElementById('theme-light-btn')?.addEventListener('click', () => setTheme('light'));
    document.getElementById('theme-sepia-btn')?.addEventListener('click', () => setTheme('sepia'));
    document.getElementById('theme-dark-btn')?.addEventListener('click', () => setTheme('dark'));

    // Lightbox Modal for Figures & Charts
    const modal = document.getElementById('image-modal');
    const modalImg = document.getElementById('modal-img');
    const modalCaption = document.getElementById('modal-caption');
    const modalClose = document.getElementById('modal-close');
    const modalBackdrop = document.getElementById('modal-backdrop');

    function openModal(src, caption) {{
      if (!modal || !modalImg) return;
      modalImg.src = src;
      if (modalCaption) modalCaption.textContent = caption || '';
      modal.classList.add('open');
      modal.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
    }}

    function closeModal() {{
      if (!modal) return;
      modal.classList.remove('open');
      modal.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
    }}

    document.querySelectorAll('figure .figure-wrapper, figure img').forEach(el => {{
      el.addEventListener('click', () => {{
        const img = el.tagName === 'IMG' ? el : el.querySelector('img');
        if (!img) return;
        const fig = el.closest('figure');
        const cap = fig ? fig.querySelector('figcaption')?.textContent : '';
        openModal(img.src, cap);
      }});
    }});

    if (modalClose) modalClose.addEventListener('click', closeModal);
    if (modalBackdrop) modalBackdrop.addEventListener('click', closeModal);
    document.addEventListener('keydown', (e) => {{
      if (e.key === 'Escape') closeModal();
    }});

    // Active Chapter Highlighting
    const sections = document.querySelectorAll('main section, main article');
    const navLinks = document.querySelectorAll('#sidebar a');
    const currentIndicator = document.getElementById('current-chapter-indicator');

    if ('IntersectionObserver' in window) {{
      const observer = new IntersectionObserver((entries) => {{
        entries.forEach(entry => {{
          if (entry.isIntersecting) {{
            const id = entry.target.id;
            navLinks.forEach(link => {{
              if (link.getAttribute('href') === '#' + id) {{
                navLinks.forEach(l => l.classList.remove('active'));
                link.classList.add('active');
                if (currentIndicator) {{
                  currentIndicator.textContent = link.textContent;
                }}
              }}
            }});
          }}
        }});
      }}, {{ rootMargin: '-20% 0px -65% 0px' }});

      sections.forEach(s => observer.observe(s));
    }}
  </script>
</body>
</html>"""

        with open(self.output_path, "w", encoding="utf-8") as f:
            f.write(full_html)

        print(f"Built responsive HTML edition at {self.output_path} ({os.path.getsize(self.output_path)} bytes)")
        return self.output_path

    def _render_table_html(self, tbl):
        parts = [
            "<div class='table-container'>",
            "<div class='table-scroll-hint'><span>📊 Data Table</span><span>↔ Scroll horizontally to view full table</span></div>",
            f"<table id='{tbl.id}'>"
        ]
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
