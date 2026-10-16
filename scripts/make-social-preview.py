#!/usr/bin/env python3
"""Generate a 1200x630 social preview (og:image) for TrustBridge.

Portable: no machine-specific paths. Uses the repo's own favicon.svg logo
and brand colors (#863bff purple, #ede6ff light). Run from repo root.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

try:
    import cairosvg
except ImportError:
    sys.exit("cairosvg required: pip install cairosvg")

W, H = 1200, 630
PURPLE = (134, 59, 255)      # #863bff
DARK = (24, 16, 40)          # near-black purple tint for text
LIGHT = (237, 230, 255)      # #ede6ff

def font_path(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None

def main():
    out = "public/og-image.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)

    # Background: purple gradient (top-left light -> bottom-right purple)
    img = Image.new("RGB", (W, H), PURPLE)
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        r = int(LIGHT[0] + (PURPLE[0] - LIGHT[0]) * t)
        g = int(LIGHT[1] + (PURPLE[1] - LIGHT[1]) * t)
        b = int(LIGHT[2] + (PURPLE[2] - LIGHT[2]) * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # Render the favicon logo large on the left
    logo_svg = "public/favicon.svg"
    logo_png = "/tmp/trustbridge_logo.png"
    cairosvg.svg2png(url=logo_svg, write_to=logo_png, output_width=520, output_height=520)
    logo = Image.open(logo_png).convert("RGBA")
    logo = logo.resize((420, 420), Image.LANCZOS)
    img.paste(logo, (90, 105), logo)

    # Text on the right
    f_title = font_path(80, bold=True)
    f_sub = font_path(38)
    f_tag = font_path(30)
    title_font = ImageFont.truetype(f_title, 80) if f_title else ImageFont.load_default()
    sub_font = ImageFont.truetype(f_sub, 38) if f_sub else ImageFont.load_default()
    tag_font = ImageFont.truetype(f_tag, 30) if f_tag else ImageFont.load_default()

    x = 560
    draw.text((x, 150), "TrustBridge", font=title_font, fill=DARK)
    draw.text((x, 260), "Humanitarian aid,", font=sub_font, fill=DARK)
    draw.text((x, 308), "powered by Stellar.", font=sub_font, fill=DARK)
    draw.text((x, 400), "trustbridge-frontend-rzkz.onrender.com", font=tag_font, fill=DARK)

    img.save(out)
    print("wrote", out, img.size)

if __name__ == "__main__":
    main()
