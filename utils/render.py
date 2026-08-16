# -*- coding: utf-8 -*-
"""HTML 5장을 Playwright로 PNG 캡처하고 pngquant로 최적화."""
import os
import subprocess
from playwright.sync_api import sync_playwright
from config import CARD_W, CARD_H, BG_GRADIENT, BG_ANGLE, GLOWS, BG
from utils.build_html import build_all_html, CARD_NAMES

# CSS 주입용 - Canva 원+블러 재현
def _build_bg_css():
    try:
        c1, c2 = BG_GRADIENT[0], BG_GRADIENT[1]
        angle = BG_ANGLE
    except:
        c1, c2, angle = BG, BG, 160

    # 글로우 CSS 생성
    glow_css = ""
    for i, g in enumerate(GLOWS):
        color = g["color"]
        opacity = g["opacity"]
        size = g["size"]
        blur = g["blur"]
        if g["position"] == "top_right":
            pos_css = f"right: -{size//4}px; top: -{size//4}px;"
        else:
            pos_css = f"left: -{size//4}px; bottom: -{size//4}px;"

        glow_css += f"""
       .glow-{i} {{
            position: absolute;
            width: {size}px; height: {size}px;
            {pos_css}
            background: {color};
            opacity: {opacity};
            filter: blur({blur}px);
            border-radius: 50%;
            pointer-events: none;
            z-index: 0;
        }}
        """

    return f"""
    <style id="injected-bg">
    html, body {{
        background: linear-gradient({angle}deg, {c1} 0%, {c2} 100%)!important;
        background-color: {c1}!important;
    }}
   .card,.page,.container, [class*="card"] {{
        background: linear-gradient({angle}deg, {c1} 0%, {c2} 100%)!important;
        position: relative;
        overflow: hidden;
    }}
    {glow_css}
    </style>
    <div class="glow-0"></div>
    <div class="glow-1"></div>
    """

def _inject_bg(html):
    """html head 끝에 배경 CSS + 글로우 div 주입"""
    bg_html = _build_bg_css()
    if "</head>" in html:
        return html.replace("</head>", bg_html + "</head>")
    else:
        return bg_html + html

def _optimize(raw_path, final_path):
    """pngquant 8색 최적화. 실패 시 원본을 그대로 사용."""
    try:
        subprocess.run(
            ["pngquant", "8", "--speed", "1", "--force", "--strip", "--output", final_path, raw_path],
            check=True, capture_output=True,
        )
    except Exception as e:
        print(f"pngquant 실패, 원본 사용: {e}")
        if os.path.exists(raw_path):
            os.replace(raw_path, final_path)
        return
    if os.path.exists(raw_path):
        os.remove(raw_path)

def render_cards(data, output_dir):
    """카드 5장을 output_dir에 PNG로 생성. 생성된 파일 경로 리스트 반환."""
    os.makedirs(output_dir, exist_ok=True)
    htmls = build_all_html(data)
    paths = []
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
        page = browser.new_page(viewport={"width": CARD_W, "height": CARD_H}, device_scale_factor=1)
        for name, html in zip(CARD_NAMES, htmls):
            # 배경 주입
            html_with_bg = _inject_bg(html)

            page.set_content(html_with_bg, wait_until="networkidle")
            raw = os.path.join(output_dir, f"{name}_raw.png")
            final = os.path.join(output_dir, f"{name}.png")
            page.screenshot(path=raw, clip={"x": 0, "y": 0, "width": CARD_W, "height": CARD_H})
            _optimize(raw, final)
            kb = os.path.getsize(final) / 1024
            print(f" {name}.png : {kb:.1f} KB")
            paths.append(final)
        browser.close()
    return paths
