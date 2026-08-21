import os
from PIL import Image, ImageDraw, ImageFont

UPLOAD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "uploads")
os.makedirs(UPLOAD, exist_ok=True)
FONT = "C:/Windows/Fonts/arial.ttf"


def make_image(filename, label, bg, fg):
    img = Image.new("RGB", (800, 800), bg)
    d = ImageDraw.Draw(img)
    # subtle border
    d.rectangle([20, 20, 779, 779], outline=fg, width=6)
    try:
        fnt = ImageFont.truetype(FONT, 60)
    except Exception:
        fnt = ImageFont.load_default()
    # wrap label into lines
    words = label.split()
    lines, cur = [], ""
    for w in words:
        if len(cur + " " + w) <= 14:
            cur = (cur + " " + w).strip()
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    line_h = 70
    total_h = line_h * len(lines)
    y = 400 - total_h // 2
    for ln in lines:
        bbox = d.textbbox((0, 0), ln, font=fnt)
        w = bbox[2] - bbox[0]
        d.text(((800 - w) / 2, y), ln, font=fnt, fill=fg)
        y += line_h
    img.save(os.path.join(UPLOAD, filename))


cats = [
    ("COSMETIC", "cat_cosmetic.png"),
    ("SKINCARE", "cat_skincare.png"),
    ("PERSONAL CARE", "cat_personal.png"),
    ("CUSTOM OEM", "cat_oem.png"),
]

products = {
    "COSMETIC": ["Cosmetic Jar 30ml", "Cosmetic Bottle 100ml", "Lip Gloss Tube", "Compact Case"],
    "SKINCARE": ["Skincare Cream Jar", "Serum Dropper Bottle", "Lotion Pump Bottle", "Face Mask Pouch"],
    "PERSONAL CARE": ["Shampoo Bottle", "Body Wash Pump", "Deodorant Stick", "Soap Box"],
    "CUSTOM OEM": ["Custom Molded Jar", "Custom Bottle", "Custom Closure", "OEM Component"],
}

navy = (11, 59, 120)
blue = (22, 79, 145)
red = (197, 31, 31)
white = (255, 255, 255)

for name, fn in cats:
    make_image(fn, name, navy, white)

for ci, (cname, _) in enumerate(cats):
    for pi, pname in enumerate(products[cname], 1):
        bg = [navy, blue, red, blue][pi % 4]
        make_image(f"prod_{cname.split()[0].lower()}_{pi}.png", pname, bg, white)

print("generated images in", UPLOAD)
print(os.listdir(UPLOAD))
