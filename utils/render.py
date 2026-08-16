# -*- coding: utf-8 -*-
"""HTML 5장을 Playwright로 PNG 캡처하고 pngquant로 최적화."""
import os
import subprocess
from playwright.sync_api import sync_playwright
from config import CARD_W, CARD_H
from utils.build_html import build_all_html, CARD_NAMES


def _optimize(raw_path, final_path):
    """pngquant 8색 최적화. 실패 시 원본을 그대로 사용."""
    try:
        subprocess.run(
            ["pngquant", "8", "--speed", "1", "--force", "--strip", "--output", final_path, raw_path],
            check=True, capture_output=True,
        )
    except Exception as e:
        print(f"pngquant 실패, 원본 사용: {e}")
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
            page.set_content(html, wait_until="networkidle")
            raw = os.path.join(output_dir, f"{name}_raw.png")
            final = os.path.join(output_dir, f"{name}.png")
            page.screenshot(path=raw, clip={"x": 0, "y": 0, "width": CARD_W, "height": CARD_H})
            _optimize(raw, final)
            kb = os.path.getsize(final) / 1024
            print(f"  {name}.png : {kb:.1f} KB")
            paths.append(final)
        browser.close()
    return paths
