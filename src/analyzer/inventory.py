"""
Inventory and Analysis Module
Generates the 4 standardized metadata and inventory JSON files:
- document-structure.json
- metadata.json
- content-inventory.json
- asset-inventory.json
"""

import os
import json
from src.parser.document_parser import DocumentParser

def generate_inventories(book=None, output_dir="output/metadata"):
    os.makedirs(output_dir, exist_ok=True)
    if book is None:
        parser = DocumentParser()
        book = parser.parse()

    # 1. metadata.json
    metadata_data = {
        "title": book.metadata.title,
        "subtitle": book.metadata.subtitle,
        "author": book.metadata.author,
        "publisher": book.metadata.publisher,
        "publication_date": book.metadata.publication_date,
        "isbn": book.metadata.isbn,
        "price": book.metadata.price,
        "copyright": book.metadata.copyright,
        "cover_designer": book.metadata.cover_designer,
        "printer": book.metadata.printer,
        "publisher_address": book.metadata.publisher_address,
        "publisher_contact": book.metadata.publisher_contact,
        "language": book.metadata.language,
    }
    with open(os.path.join(output_dir, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata_data, f, indent=2, ensure_ascii=False)

    # 2. document-structure.json
    structure_data = {
        "front_matter": [
            "Title Page",
            "Copyright Page",
            "Dedication",
            "About the Author",
            "Foreword",
            "Acknowledgments",
            "Preface",
            "Contents",
            "List of Tables",
            "Table of Acronyms",
            "List of Figures"
        ],
        "chapters": [
            {"number": c.number, "title": c.title, "element_count": len(c.elements)}
            for c in book.chapters
        ],
        "references": {
            "title": "Reference",
            "entry_count": len(book.references)
        },
        "appendices": [
            {"number": a.number, "title": a.title, "element_count": len(a.elements)}
            for a in book.appendices
        ],
        "back_matter": [
            "Key Words Index"
        ]
    }
    with open(os.path.join(output_dir, "document-structure.json"), "w", encoding="utf-8") as f:
        json.dump(structure_data, f, indent=2, ensure_ascii=False)

    # 3. content-inventory.json
    total_elements = sum(len(c.elements) for c in book.chapters) + sum(len(a.elements) for a in book.appendices)
    content_data = {
        "summary": {
            "total_chapters": len(book.chapters),
            "total_appendices": len(book.appendices),
            "total_reference_entries": len(book.references),
            "total_frontmatter_sections": len(structure_data["front_matter"]),
            "keywords_index_terms": len(book.keywords_table.rows) if book.keywords_table else 0
        },
        "chapters_detail": [
            {
                "chapter": c.number,
                "title": c.title,
                "paragraphs": sum(1 for e in c.elements if e.elem_type == "paragraph"),
                "headings": sum(1 for e in c.elements if e.elem_type == "heading"),
                "tables": sum(1 for e in c.elements if e.elem_type == "table"),
                "figures": sum(1 for e in c.elements if e.elem_type == "figure")
            }
            for c in book.chapters
        ]
    }
    with open(os.path.join(output_dir, "content-inventory.json"), "w", encoding="utf-8") as f:
        json.dump(content_data, f, indent=2, ensure_ascii=False)

    # 4. asset-inventory.json
    assets_data = {
        "raster_images": [
            {"file": "image1.jpeg", "role": "Publisher Logo", "path": "output/assets/images/image1.jpeg"},
            {"file": "image2.jpeg", "role": "Publisher Colophon", "path": "output/assets/images/image2.jpeg"},
            {"file": "image3.jpeg", "role": "Author Portrait", "path": "output/assets/images/image3.jpeg"},
            {"file": "image4.jpeg", "role": "Figure 1.1 Diagram", "path": "output/assets/images/image4.jpeg"},
            {"file": "image5.png", "role": "Cronbach Alpha Formula", "path": "output/assets/images/image5.png"},
            {"file": "cover.png", "role": "Book Cover", "path": "output/cover/cover.png"}
        ],
        "vector_charts": [
            {"figure": fnum, "file": f"figure_{fnum.replace('.', '_')}.png", "path": f"output/assets/charts/figure_{fnum.replace('.', '_')}.png"}
            for fnum in [
                "1.2", "1.3", "1.4", "3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7",
                "5.1", "5.2", "5.3", "5.4", "5.5", "5.6", "5.7", "5.8", "5.9", "5.10",
                "6.1", "6.2", "6.3", "6.4", "6.5", "6.6", "6.7", "6.8", "6.9", "6.10",
                "6.11", "6.12", "6.13", "6.14", "6.15", "6.16", "6.17", "6.18", "6.19", "6.20", "6.21",
                "10.1", "10.2", "10.3"
            ]
        ]
    }
    with open(os.path.join(output_dir, "asset-inventory.json"), "w", encoding="utf-8") as f:
        json.dump(assets_data, f, indent=2, ensure_ascii=False)

    print(f"Generated 4 inventory files in {output_dir}")

if __name__ == "__main__":
    generate_inventories()
