"""
generate_icon.py
Auto-generates logo.png (blue lock icon) if not present.
Run: python3 generate_icon.py
"""
import os
from PIL import Image, ImageDraw

LOGO = "logo.png"

if os.path.exists(LOGO):
    print("Using existing logo.png")
else:
    print("Generating blue lock icon...")
    SIZE  = 512
    img   = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw  = ImageDraw.Draw(img)
    BG    = (24, 119, 242)
    DARK  = (10, 80, 180)
    WHITE = (255, 255, 255)
    cx, cy = SIZE // 2, SIZE // 2

    draw.ellipse([0, 0, SIZE, SIZE], fill=BG)
    draw.ellipse([18, 18, SIZE-18, SIZE-18], fill=DARK)
    draw.ellipse([32, 32, SIZE-32, SIZE-32], fill=BG)

    SW, ST = 110, 28
    sx = cx - SW // 2
    sy = cy - 80
    draw.rectangle([sx, sy+40, sx+ST, cy-20], fill=WHITE)
    draw.rectangle([sx+SW-ST, sy+40, sx+SW, cy-20], fill=WHITE)
    draw.arc([sx, sy, sx+SW, sy+int(SW*0.9)], start=180, end=0, fill=WHITE, width=ST)

    BW, BH = 180, 150
    bx, by = cx - BW//2, cy - 20
    draw.rounded_rectangle([bx, by, bx+BW, by+BH], radius=22, fill=WHITE)

    KR = 26
    draw.ellipse([cx-KR, by+40, cx+KR, by+40+KR*2], fill=BG)
    draw.rectangle([cx-12, by+40+KR, cx+12, by+40+KR*2+24], fill=BG)

    img.save(LOGO, "PNG")
    print("logo.png generated successfully!")
