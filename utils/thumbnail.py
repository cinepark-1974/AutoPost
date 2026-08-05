
from PIL import Image, ImageDraw, ImageFont
import textwrap

def create_thumbnail(text="넷플릭스 액션 추천 TOP 7", out_path="/tmp/thumb.jpg"):
    W, H = 1280, 720
    img = Image.new("RGB", (W,H), "#0A0A0A")
    draw = ImageDraw.Draw(img)
    # black box
    draw.rectangle([40, 120, W-40, H-120], fill="#141414", outline="#FFD60A", width=4)
    # yellow quote
    draw.text((80, 140), '“', fill="#FFD60A", font=ImageFont.load_default())
    # title - use default font, wrap
    lines = textwrap.wrap(text, width=18)
    y=200
    for line in lines[:3]:
        draw.text((100, y), line, fill="white", font=ImageFont.load_default())
        y+=80
    draw.text((100, H-180), "CINEPARK | 2026.08", fill="#888888", font=ImageFont.load_default())
    img.save(out_path, quality=95)
    return out_path
