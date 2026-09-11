"""
Chart Extractor Module
Extracts all 44 DrawingML charts from the high-fidelity rendered reference document
at 300 DPI, saving clean, publication-quality PNG images.
"""

import os
import sys
import fitz

FIGURE_METADATA = [
    # Chapter 1
    {"num": "1.2", "page": 32, "name": "figure_1_2.png", "box": (50.0, 95.0, 345.0, 333.0)},
    {"num": "1.3", "page": 33, "name": "figure_1_3.png", "box": (50.0, 135.0, 355.0, 442.0)},
    {"num": "1.4", "page": 34, "name": "figure_1_4.png", "box": (50.0, 94.0, 345.0, 248.5)},

    # Chapter 3
    {"num": "3.1", "page": 91, "name": "figure_3_1.png", "box": (50.0, 110.0, 345.0, 525.0)},
    {"num": "3.2", "page": 92, "name": "figure_3_2.png", "box": (50.0, 185.0, 345.0, 525.0)},
    {"num": "3.3", "page": 97, "name": "figure_3_3.png", "box": (50.0, 330.0, 198.0, 485.0)},
    {"num": "3.4", "page": 97, "name": "figure_3_4.png", "box": (198.0, 330.0, 342.0, 480.0)},
    {"num": "3.5", "page": 102, "name": "figure_3_5.png", "box": (50.0, 310.0, 196.0, 465.0)},
    {"num": "3.6", "page": 102, "name": "figure_3_6.png", "box": (196.0, 310.0, 342.0, 465.0)},
    {"num": "3.7", "page": 104, "name": "figure_3_7.png", "box": (50.0, 260.0, 345.0, 475.0)},

    # Chapter 5
    {"num": "5.1", "page": 155, "name": "figure_5_1.png", "box": (50.0, 95.0, 345.0, 500.0)},
    {"num": "5.2", "page": 156, "name": "figure_5_2.png", "box": (50.0, 95.0, 345.0, 525.0)},
    {"num": "5.3", "page": 157, "name": "figure_5_3.png", "box": (50.0, 130.0, 345.0, 520.0)},
    {"num": "5.4", "page": 158, "name": "figure_5_4.png", "box": (50.0, 210.0, 345.0, 525.0)},
    {"num": "5.5", "page": 162, "name": "figure_5_5.png", "box": (50.0, 95.0, 345.0, 235.0)},
    {"num": "5.6", "page": 162, "name": "figure_5_6.png", "box": (50.0, 260.0, 345.0, 415.0)},
    {"num": "5.7", "page": 164, "name": "figure_5_7.png", "box": (50.0, 55.0, 345.0, 375.0)},
    {"num": "5.8", "page": 165, "name": "figure_5_8.png", "box": (50.0, 55.0, 345.0, 515.0)},
    {"num": "5.9", "page": 167, "name": "figure_5_9.png", "box": (50.0, 135.0, 345.0, 450.0)},
    {"num": "5.10", "page": 168, "name": "figure_5_10.png", "box": (50.0, 55.0, 345.0, 320.0)},

    # Chapter 6
    {"num": "6.1", "page": 189, "name": "figure_6_1.png", "box": (50.0, 80.0, 345.0, 275.0)},
    {"num": "6.2", "page": 189, "name": "figure_6_2.png", "box": (50.0, 305.0, 345.0, 510.0)},
    {"num": "6.3", "page": 190, "name": "figure_6_3.png", "box": (50.0, 245.0, 345.0, 525.0)},
    {"num": "6.4", "page": 192, "name": "figure_6_4.png", "box": (50.0, 55.0, 345.0, 405.0)},
    {"num": "6.5", "page": 193, "name": "figure_6_5.png", "box": (50.0, 58.0, 198.0, 200.0)},
    {"num": "6.6", "page": 193, "name": "figure_6_6.png", "box": (198.0, 58.0, 345.0, 200.0)},
    {"num": "6.7", "page": 193, "name": "figure_6_7.png", "box": (50.0, 240.0, 198.0, 405.0)},
    {"num": "6.8", "page": 193, "name": "figure_6_8.png", "box": (198.0, 240.0, 345.0, 405.0)},
    {"num": "6.9", "page": 194, "name": "figure_6_9.png", "box": (48.0, 145.0, 196.0, 320.0)},
    {"num": "6.10", "page": 194, "name": "figure_6_10.png", "box": (196.0, 145.0, 345.0, 320.0)},
    {"num": "6.11", "page": 200, "name": "figure_6_11.png", "box": (50.0, 90.0, 345.0, 445.0)},
    {"num": "6.12", "page": 201, "name": "figure_6_12.png", "box": (50.0, 305.0, 196.0, 410.0)},
    {"num": "6.13", "page": 201, "name": "figure_6_13.png", "box": (196.0, 305.0, 345.0, 415.0)},
    {"num": "6.14", "page": 202, "name": "figure_6_14.png", "box": (50.0, 285.0, 196.0, 375.0)},
    {"num": "6.15", "page": 202, "name": "figure_6_15.png", "box": (196.0, 285.0, 345.0, 375.0)},
    {"num": "6.16", "page": 203, "name": "figure_6_16.png", "box": (50.0, 100.0, 196.0, 185.0)},
    {"num": "6.17", "page": 203, "name": "figure_6_17.png", "box": (196.0, 100.0, 345.0, 185.0)},
    {"num": "6.18", "page": 203, "name": "figure_6_18.png", "box": (50.0, 230.0, 196.0, 335.0)},
    {"num": "6.19", "page": 203, "name": "figure_6_19.png", "box": (196.0, 230.0, 345.0, 340.0)},
    {"num": "6.20", "page": 204, "name": "figure_6_20.png", "box": (50.0, 105.0, 195.0, 218.0)},
    {"num": "6.21", "page": 204, "name": "figure_6_21.png", "box": (195.0, 105.0, 342.0, 218.0)},

    # Chapter 10
    {"num": "10.1", "page": 247, "name": "figure_10_1.png", "box": (50.0, 140.0, 345.0, 360.0)},
    {"num": "10.2", "page": 248, "name": "figure_10_2.png", "box": (50.0, 58.0, 345.0, 265.0)},
    {"num": "10.3", "page": 251, "name": "figure_10_3.png", "box": (50.0, 230.0, 345.0, 470.0)},
]

def extract_all_charts(pdf_path="reference_source.pdf", output_dir="output/assets/charts", dpi=300):
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    extracted = []

    for item in FIGURE_METADATA:
        pno = item["page"] - 1
        page = doc[pno]
        x0, y0, x1, y1 = item["box"]
        rect = fitz.Rect(x0, y0, x1, y1)
        pix = page.get_pixmap(clip=rect, dpi=dpi)
        out_path = os.path.join(output_dir, item["name"])
        pix.save(out_path)
        extracted.append({
            "figure": item["num"],
            "page": item["page"],
            "filename": item["name"],
            "path": out_path,
            "width": pix.width,
            "height": pix.height
        })

    print(f"Successfully extracted {len(extracted)} charts to {output_dir}")
    return extracted

if __name__ == "__main__":
    extract_all_charts()
