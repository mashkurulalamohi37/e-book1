"""
Cover Generator Module
Generates a premium, publication-quality academic book cover (1800x2700, 300 DPI)
for 'Non-performing Loans in Bangladesh' by Dr. Md. Ariful Islam.
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_cover(output_path="output/cover/cover.png", width=1800, height=2700):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 1. Base Image with Deep Navy Gradient
    img = Image.new("RGBA", (width, height), (11, 29, 51, 255))
    draw = ImageDraw.Draw(img)
    
    # Gradient overlay (top dark navy to bottom deeper midnight)
    for y in range(height):
        ratio = y / height
        r = int(14 * (1 - ratio) + 6 * ratio)
        g = int(32 * (1 - ratio) + 16 * ratio)
        b = int(58 * (1 - ratio) + 30 * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    # 2. Abstract Financial Network / Geometric Motif in Center-Background
    # Muted geometric lines suggesting financial risk trends & banking nodes
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    
    # Subtle financial grid
    grid_color = (40, 75, 115, 45)
    for x in range(100, width - 100, 80):
        overlay_draw.line([(x, 700), (x, 1900)], fill=grid_color, width=1)
    for y in range(700, 1901, 80):
        overlay_draw.line([(100, y), (width - 100, y)], fill=grid_color, width=1)
        
    # Stylized financial risk trend lines (representing macroeconomic cycles)
    trend_pts_1 = []
    trend_pts_2 = []
    trend_pts_3 = []
    for x in range(120, width - 120, 20):
        nx = (x - 120) / (width - 240)
        y1 = 1450 - math.sin(nx * math.pi * 2.2) * 180 - nx * 140
        y2 = 1520 - math.cos(nx * math.pi * 2.8) * 130 + math.sin(nx * 5) * 40
        y3 = 1380 + math.sin(nx * math.pi * 1.6) * 110 - nx * 80
        trend_pts_1.append((x, y1))
        trend_pts_2.append((x, y2))
        trend_pts_3.append((x, y3))

    overlay_draw.line(trend_pts_1, fill=(197, 160, 89, 70), width=4)
    overlay_draw.line(trend_pts_2, fill=(80, 140, 200, 60), width=3)
    overlay_draw.line(trend_pts_3, fill=(197, 160, 89, 45), width=2)
    
    # Banking nodes / data points
    for pt in trend_pts_1[::4]:
        overlay_draw.ellipse([pt[0]-6, pt[1]-6, pt[0]+6, pt[1]+6], fill=(212, 175, 55, 120), outline=(255, 255, 255, 150))
    for pt in trend_pts_2[::5]:
        overlay_draw.ellipse([pt[0]-5, pt[1]-5, pt[0]+5, pt[1]+5], fill=(70, 130, 180, 100), outline=(200, 220, 255, 120))

    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)

    # 3. Fonts
    fonts_dir = r"C:\Windows\Fonts"
    font_badge = ImageFont.truetype(os.path.join(fonts_dir, "segoeuib.ttf"), 38)
    font_title_main = ImageFont.truetype(os.path.join(fonts_dir, "georgiab.ttf"), 102)
    font_title_sub = ImageFont.truetype(os.path.join(fonts_dir, "georgia.ttf"), 44)
    font_subtitle = ImageFont.truetype(os.path.join(fonts_dir, "segoeui.ttf"), 48)
    font_by = ImageFont.truetype(os.path.join(fonts_dir, "georgia.ttf"), 36)
    font_author = ImageFont.truetype(os.path.join(fonts_dir, "georgiab.ttf"), 66)
    font_pub = ImageFont.truetype(os.path.join(fonts_dir, "segoeuib.ttf"), 48)
    font_isbn = ImageFont.truetype(os.path.join(fonts_dir, "segoeui.ttf"), 32)

    # 4. Top Decorative Borders & Header Badge
    gold = (212, 175, 55, 255)
    soft_gold = (197, 160, 89, 230)
    white = (255, 255, 255, 255)
    off_white = (235, 240, 245, 255)
    slate_blue = (165, 190, 215, 255)

    # Outer elegant frame
    draw.rectangle([(80, 80), (width - 80, height - 80)], outline=(197, 160, 89, 140), width=3)
    draw.rectangle([(96, 96), (width - 96, height - 96)], outline=(255, 255, 255, 40), width=1)

    # Corner ornaments
    corner_len = 60
    for cx, cy in [(80, 80), (width-80, 80), (80, height-80), (width-80, height-80)]:
        dx = 1 if cx == 80 else -1
        dy = 1 if cy == 80 else -1
        draw.line([(cx, cy), (cx + dx * corner_len, cy)], fill=gold, width=4)
        draw.line([(cx, cy), (cx, cy + dy * corner_len)], fill=gold, width=4)

    # Header Badge
    badge_text = "ACADEMIC MONOGRAPH  •  FINANCIAL ECONOMICS"
    badge_bbox = draw.textbbox((0, 0), badge_text, font=font_badge)
    badge_w = badge_bbox[2] - badge_bbox[0]
    draw.text(((width - badge_w) // 2, 220), badge_text, font=font_badge, fill=soft_gold)

    # Thin divider under badge
    draw.line([(width//2 - 250, 290), (width//2 + 250, 290)], fill=soft_gold, width=2)
    draw.ellipse([width//2 - 5, 287, width//2 + 5, 293], fill=gold)

    # 5. Book Title
    # "NON-PERFORMING LOANS"
    # "IN BANGLADESH"
    title_line1 = "Non-performing Loans"
    title_line2 = "in Bangladesh"
    
    t1_bbox = draw.textbbox((0, 0), title_line1, font=font_title_main)
    t1_w = t1_bbox[2] - t1_bbox[0]
    draw.text(((width - t1_w) // 2, 380), title_line1, font=font_title_main, fill=white)

    t2_bbox = draw.textbbox((0, 0), title_line2, font=font_title_main)
    t2_w = t2_bbox[2] - t2_bbox[0]
    draw.text(((width - t2_w) // 2, 510), title_line2, font=font_title_main, fill=gold)

    # Decorative Gold Divider
    div_y = 670
    draw.line([(width//2 - 450, div_y), (width//2 + 450, div_y)], fill=gold, width=3)
    draw.rectangle([(width//2 - 8, div_y - 8), (width//2 + 8, div_y + 8)], fill=gold)

    # Subtitle
    sub_line1 = "A Comparative Study of Selected"
    sub_line2 = "State-owned and Private Commercial Banks"

    s1_bbox = draw.textbbox((0, 0), sub_line1, font=font_subtitle)
    s1_w = s1_bbox[2] - s1_bbox[0]
    draw.text(((width - s1_w) // 2, 730), sub_line1, font=font_subtitle, fill=off_white)

    s2_bbox = draw.textbbox((0, 0), sub_line2, font=font_subtitle)
    s2_w = s2_bbox[2] - s2_bbox[0]
    draw.text(((width - s2_w) // 2, 805), sub_line2, font=font_subtitle, fill=off_white)

    # Central Crest / Shield / Institutional Insignia
    crest_cy = 1350
    crest_r = 130
    draw.ellipse([(width//2 - crest_r, crest_cy - crest_r), (width//2 + crest_r, crest_cy + crest_r)], 
                 outline=(197, 160, 89, 180), width=3)
    draw.ellipse([(width//2 - crest_r + 15, crest_cy - crest_r + 15), (width//2 + crest_r - 15, crest_cy + crest_r - 15)], 
                 outline=(255, 255, 255, 80), width=1)
    
    # Monogram inside crest
    font_mono = ImageFont.truetype(os.path.join(fonts_dir, "georgiab.ttf"), 76)
    mono_text = "NPL"
    m_bbox = draw.textbbox((0, 0), mono_text, font=font_mono)
    m_w = m_bbox[2] - m_bbox[0]
    m_h = m_bbox[3] - m_bbox[1]
    draw.text(((width - m_w) // 2, crest_cy - m_h // 2 - 10), mono_text, font=font_mono, fill=gold)

    # 6. Author Section
    auth_y = 1880
    by_text = "— AUTHOR —"
    by_bbox = draw.textbbox((0, 0), by_text, font=font_by)
    by_w = by_bbox[2] - by_bbox[0]
    draw.text(((width - by_w) // 2, auth_y), by_text, font=font_by, fill=soft_gold)

    auth_name = "Dr. Md. Ariful Islam"
    a_bbox = draw.textbbox((0, 0), auth_name, font=font_author)
    a_w = a_bbox[2] - a_bbox[0]
    draw.text(((width - a_w) // 2, auth_y + 70), auth_name, font=font_author, fill=white)

    # Author Credentials / Affiliation
    cred_text = "Doctor of Business Administration (DBA) • University of Dhaka"
    font_cred = ImageFont.truetype(os.path.join(fonts_dir, "segoeui.ttf"), 34)
    c_bbox = draw.textbbox((0, 0), cred_text, font=font_cred)
    c_w = c_bbox[2] - c_bbox[0]
    draw.text(((width - c_w) // 2, auth_y + 165), cred_text, font=font_cred, fill=slate_blue)

    # 7. Publisher Section (Bottom Banner)
    pub_div_y = 2280
    draw.line([(width//2 - 350, pub_div_y), (width//2 + 350, pub_div_y)], fill=soft_gold, width=2)
    draw.ellipse([width//2 - 5, pub_div_y - 4, width//2 + 5, pub_div_y + 4], fill=gold)

    # Hakkani Publishers logo overlay if available
    logo_path = "output/assets/images/image1.jpeg"
    pub_text_y = 2360
    if os.path.exists(logo_path):
        try:
            logo_img = Image.open(logo_path).convert("RGBA")
            # Resize slightly
            logo_img.thumbnail((120, 120), Image.Resampling.LANCZOS)
            # Create white/gold tinted logo or place on badge
            logo_x = width // 2 - logo_img.width // 2
            logo_y = 2320
            img.paste(logo_img, (logo_x, logo_y), mask=logo_img if "A" in logo_img.getbands() else None)
            pub_text_y = logo_y + logo_img.height + 25
        except Exception:
            pass

    pub_name = "HAKKANI PUBLISHERS"
    p_bbox = draw.textbbox((0, 0), pub_name, font=font_pub)
    p_w = p_bbox[2] - p_bbox[0]
    draw.text(((width - p_w) // 2, pub_text_y), pub_name, font=font_pub, fill=gold)

    isbn_text = "ISBN: 984-70214-0179-6"
    i_bbox = draw.textbbox((0, 0), isbn_text, font=font_isbn)
    i_w = i_bbox[2] - i_bbox[0]
    draw.text(((width - i_w) // 2, pub_text_y + 70), isbn_text, font=font_isbn, fill=slate_blue)

    # Save final RGB cover
    final_rgb = img.convert("RGB")
    final_rgb.save(output_path, "PNG", dpi=(300, 300), optimize=True)
    print(f"Cover generated successfully at {output_path} ({width}x{height} @ 300 DPI)")
    return output_path

if __name__ == "__main__":
    create_cover()
