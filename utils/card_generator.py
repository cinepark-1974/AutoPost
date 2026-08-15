from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random, os
from pathlib import Path
from config import CARD_SIZE

def get_font(size=60, bold=True):
    from config import FONT_BOLD, FONT_REGULAR
    try:
        path = FONT_BOLD if bold else FONT_REGULAR
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    except:
        pass
    return ImageFont.load_default()

def pick_background(bg_path=None):
    if bg_path and Path(bg_path).exists():
        return Image.open(bg_path).convert("RGB")
    bg_dir = Path("assets/backgrounds")
    if bg_dir.exists():
        files = list(bg_dir.glob("*.jpg")) + list(bg_dir.glob("*.png"))
        if files:
            return Image.open(random.choice(files)).convert("RGB")
    return Image.new("RGB", CARD_SIZE, (18,18,18))

def create_card(text_title, text_body, footer, bg_image=None, chart_path=None, output_path="card.png"):
    W, H = CARD_SIZE
    if bg_image is None:
        bg_image = pick_background()
    bg = bg_image.resize((W, H))
    bg = bg.filter(ImageFilter.GaussianBlur(2))
    overlay = Image.new("RGBA", (W,H), (0,0,0,160))
    bg = Image.alpha_composite(bg.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(bg)
    font_title = get_font(68, bold=True)
    font_body = get_font(40, bold=False)
    font_footer = get_font(28, bold=False)
    y = 160
    # 타이틀 (줄바꿈 지원)
    for line in text_title.split("\n"):
        draw.text((70, y), line, font=font_title, fill=(255,255,255))
        y += 85
    y += 30
    for line in text_body.split("\n"):
        if not line.strip():
            continue
        draw.text((70, y), f"• {line}", font=font_body, fill=(230,230,230))
        y += 78
    draw.text((70, H-100), footer, font=font_footer, fill=(170,170,170))
    if chart_path and Path(chart_path).exists():
        try:
            chart = Image.open(chart_path).convert("RGBA")
            chart = chart.resize((920, 300))
            bg.paste(chart, (80, H-480), chart)
        except Exception as e:
            print(f"chart paste fail: {e}")
    bg.save(output_path)
    return output_path

def generate_all_cards(data, stock_info, output_dir, bg_path=None):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    bg = pick_background(bg_path)
    create_card(data['headline'], f"{data['company']} | {stock_info['ticker']}\n{stock_info['date']}", "HOLLYWOOD INDUSTRY DAILY", bg, None, f"{output_dir}/card_01_cover.png")
    create_card("01. INDUSTRY NEWS", data['industry'], f"Source: {data['source']}", bg, None, f"{output_dir}/card_02_industry.png")
    create_card("02. BEHIND THE SCENES", data['behind'], f"Source: {data['source']}", bg, None, f"{output_dir}/card_03_behind.png")
    create_card("03. PROMO TRACKING", data['promo'], f"Source: {data['source']}", bg, None, f"{output_dir}/card_04_promo.png")
    create_card(f"04. MARKET CLOSE\n{stock_info['ticker']} ${stock_info['close']:.2f} ({stock_info['change']:+.1f}%)", f"전일 종가 기준\n일주일간 흐름", "Data: NYSE / yfinance", bg, stock_info.get('chart_path'), f"{output_dir}/card_05_stock.png")
    try:
        from moviepy.editor import ImageClip, concatenate_videoclips
        order = ["cover","industry","behind","promo","stock"]
        clips = [ImageClip(f"{output_dir}/card_0{i+1}_{order[i]}.png").set_duration(4) for i in range(5)]
        video = concatenate_videoclips(clips, method="compose")
        video.write_videofile(f"{output_dir}/final_shorts.mp4", fps=24, codec="libx264", audio=False, logger=None)
    except Exception as e:
        print(f"mp4 skip: {e}")
