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

def pick_background():
    bg_dir = Path("assets/backgrounds")
    if bg_dir.exists():
        files = list(bg_dir.glob("*.jpg")) + list(bg_dir.glob("*.png"))
        if files:
            return Image.open(random.choice(files)).convert("RGB")
    # fallback 그라데이션
    img = Image.new("RGB", CARD_SIZE, (15,15,15))
    return img

def create_card(text_title, text_body, footer, bg_image=None, chart_path=None, output_path="card.png"):
    W, H = CARD_SIZE
    if bg_image is None:
        bg_image = pick_background()
    
    # 배경 리사이즈 + 블러 + 어둡게
    bg = bg_image.resize((W, H))
    bg = bg.filter(ImageFilter.GaussianBlur(3))
    overlay = Image.new("RGBA", (W,H), (0,0,0,160))
    bg = Image.alpha_composite(bg.convert("RGBA"), overlay).convert("RGB")

    draw = ImageDraw.Draw(bg)
    
    # 타이틀
    font_title = get_font(72, bold=True)
    font_body = get_font(42, bold=False)
    font_footer = get_font(30, bold=False)

    # 텍스트 박스
    y = 180
    # 타이틀 박스
    draw.text((80, y), text_title, font=font_title, fill=(255,255,255))
    y += 160
    
    # 본문 (줄바꿈)
    lines = text_body.split("\n")
    for line in lines:
        draw.text((80, y), f"• {line}", font=font_body, fill=(230,230,230))
        y += 90

    # 하단 출처
    draw.text((80, H-120), footer, font=font_footer, fill=(180,180,180))

    # 주식 차트가 있으면 붙이기
    if chart_path and Path(chart_path).exists():
        try:
            chart = Image.open(chart_path).convert("RGBA")
            chart = chart.resize((900, 280))
            bg.paste(chart, (90, H-500), chart)
        except Exception as e:
            print(f"chart paste fail: {e}")

    bg.save(output_path)
    return output_path

def generate_all_cards(data, stock_info, output_dir):
    """
    data: {headline, industry, behind, promo, company, ticker, source}
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    bg = pick_background()

    # 1. 커버
    create_card(
        text_title=data['headline'],
        text_body=f"{data['company']} | {stock_info['ticker']}\n{stock_info['date']}",
        footer="HOLLYWOOD INDUSTRY DAILY",
        bg_image=bg,
        output_path=f"{output_dir}/card_01_cover.png"
    )
    # 2. 산업
    create_card(
        text_title="01. INDUSTRY NEWS",
        text_body=data['industry'],
        footer=f"Source: {data['source']}",
        bg_image=bg,
        output_path=f"{output_dir}/card_02_industry.png"
    )
    # 3. 비하인드
    create_card(
        text_title="02. BEHIND THE SCENES",
        text_body=data['behind'],
        footer=f"Source: {data['source']}",
        bg_image=bg,
        output_path=f"{output_dir}/card_03_behind.png"
    )
    # 4. 홍보
    create_card(
        text_title="03. PROMO TRACKING",
        text_body=data['promo'],
        footer=f"Source: {data['source']}",
        bg_image=bg,
        output_path=f"{output_dir}/card_04_promo.png"
    )
    # 5. 주식
    create_card(
        text_title=f"04. MARKET CLOSE\n{stock_info['ticker']} ${stock_info['close']:.2f} ({stock_info['change']:+.1f}%)",
        text_body=f"전일 종가 기준\n일주일간 흐름",
        footer=f"Data: NYSE / yfinance",
        bg_image=bg,
        chart_path=stock_info.get('chart_path'),
        output_path=f"{output_dir}/card_05_stock.png"
    )

    # 쇼츠용 mp4 생성 (moviepy가 있으면)
    try:
        from moviepy.editor import ImageClip, concatenate_videoclips
        clips = []
        for i in range(1,6):
            path = f"{output_dir}/card_0{i}_{['cover','industry','behind','promo','stock'][i-1]}.png"
            clips.append(ImageClip(path).set_duration(4))
        video = concatenate_videoclips(clips, method="compose")
        video.write_videofile(f"{output_dir}/final_shorts.mp4", fps=24, codec="libx264", audio=False, logger=None)
    except Exception as e:
        print(f"mp4 skip: {e}")
