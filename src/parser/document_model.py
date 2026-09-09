"""
Intermediate Semantic Document Model
Defines the unified AST used across EPUB, PDF, and HTML generators.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class BookMetadata:
    title: str = "Non-performing Loans in Bangladesh: A Comparative Study of Selected State-owned and Private Commercial Banks"
    subtitle: str = "A Comparative Study of Selected State-owned and Private Commercial Banks"
    author: str = "Dr. Md. Ariful Islam"
    publisher: str = "Hakkani Publishers"
    publication_date: str = "15 May 2022"
    isbn: str = "984-70214-0179-6"
    price: str = "TK 1000.00"
    copyright: str = "@ Author"
    cover_designer: str = "Md. Ebrahim Bappy"
    printer: str = "Faria Printers, Khans Mansion, 215/A, Fakirapool (1st Lane), Motijheel, Dhaka-1000"
    publisher_address: str = "House-7 Road-4 Dhanmondi Dhaka-1205"
    publisher_contact: Dict[str, Any] = field(default_factory=lambda: {
        "phones": ["(+8802) 9661141", "(+88) 01811 416026", "(+88) 01811 416027"],
        "email": "info@hakkanipublishers.com",
        "ecommerce": "www.paramabooks.com",
        "web": "www.hakkanipublishers.com"
    })
    language: str = "en-US"

@dataclass
class DocElement:
    elem_type: str  # 'heading', 'paragraph', 'table', 'figure', 'equation', 'divider'

@dataclass
class HeadingElement(DocElement):
    level: int = 2  # 1=Chapter, 2=Section, 3=Subsection
    text: str = ""
    id: str = ""
    elem_type: str = "heading"

@dataclass
class ParagraphElement(DocElement):
    text: str = ""
    runs: List[Dict[str, Any]] = field(default_factory=list) # [{'text': ..., 'bold': ..., 'italic': ..., 'sub': ..., 'sup': ...}]
    align: str = "left"  # left, center, justify
    id: str = ""
    elem_type: str = "paragraph"

@dataclass
class TableCell:
    text: str = ""
    bold: bool = False
    col_span: int = 1
    row_span: int = 1
    align: str = "left"

@dataclass
class TableElement(DocElement):
    caption: str = ""
    headers: List[List[TableCell]] = field(default_factory=list)
    rows: List[List[TableCell]] = field(default_factory=list)
    source_note: str = ""
    id: str = ""
    elem_type: str = "table"

@dataclass
class FigureElement(DocElement):
    number: str = ""       # e.g. "1.1", "1.2"
    caption: str = ""
    source_note: str = ""
    image_path: str = ""
    rel_path: str = ""
    width: int = 0
    height: int = 0
    id: str = ""
    elem_type: str = "figure"

@dataclass
class ReferenceEntry:
    id: str = ""
    citation: str = ""
    url: Optional[str] = None
    doi: Optional[str] = None

@dataclass
class Chapter:
    number: int = 1
    title: str = ""
    id: str = ""
    elements: List[DocElement] = field(default_factory=list)

@dataclass
class Appendix:
    number: str = ""       # "I", "II", ...
    title: str = ""
    id: str = ""
    elements: List[DocElement] = field(default_factory=list)

@dataclass
class FrontMatter:
    title_page: List[str] = field(default_factory=list)
    copyright_page: List[str] = field(default_factory=list)
    dedication: List[str] = field(default_factory=list)
    about_author: List[DocElement] = field(default_factory=list)
    foreword: List[str] = field(default_factory=list)
    acknowledgments: List[str] = field(default_factory=list)
    preface: List[str] = field(default_factory=list)
    contents: List[Dict[str, Any]] = field(default_factory=list)
    list_of_tables: Optional[TableElement] = None
    table_of_acronyms: Optional[TableElement] = None
    list_of_figures: Optional[TableElement] = None

@dataclass
class Book:
    metadata: BookMetadata = field(default_factory=BookMetadata)
    front_matter: FrontMatter = field(default_factory=FrontMatter)
    chapters: List[Chapter] = field(default_factory=list)
    references: List[ReferenceEntry] = field(default_factory=list)
    appendices: List[Appendix] = field(default_factory=list)
    keywords_table: Optional[TableElement] = None
