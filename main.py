# -*- coding: utf-8 -*-
import os
import json
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
load_dotenv()

from config import OUTPUT_BASE, GDRIVE_OUTPUT_ID
from utils.researcher import research_cardnews
from utils.render import render_cards
from utils.drive_uploader import upload_to_drive


def _kst_today():
    kst = timezone(timedelta(hours=9))
    return datetime.now(kst).strftime("%Y-%m-%d")


def main():
    print("=== Hollywood CardNews Generator (web_search 버전) ===")

    api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")
    if not api_key:
        raise SystemExit("ANTHROPIC_API_KEY 없음 → 실행 중단")

    # STEP 1 + STEP 2: Claude가 웹 검색으로 뉴스·주가 조사 (검색 횟수 상한 적용)
    print("Claude web_search로 뉴스·주가 조사 중...")
    data = research_cardnews(api_key)
    ticker = data.get("ticker") or "N/A"
    print(f"선택 뉴스: {data.get('headline','(없음)')[:40]} / 티커 {ticker}")

    # 출력 폴더
    date_str = data.get("date") or _kst_today()
    output_dir = f"{OUTPUT_BASE}/{date_str}_{ticker}"

    # 카드 5장 렌더링 + 최적화
    print("카드 렌더링 중...")
    render_cards(data, output_dir)

    # 메타 저장
    with open(f"{output_dir}/meta.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 드라이브 업로드 (OAuth)
    upload_to_drive(output_dir, GDRIVE_OUTPUT_ID)
    print(f"완료: {output_dir}")


if __name__ == "__main__":
    main()
