import os, json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from config import TICKER_MAP, OUTPUT_BASE
from utils.news_fetcher import fetch_rss
from utils.stock import get_stock_data
from utils.card_generator import generate_all_cards
from utils.drive_uploader import upload_to_drive
from prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

# OpenAI 사용 (키 없으면 더미 데이터로 동작)
def summarize_with_llm(articles):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY 없음 → 더미 데이터 사용")
        return {
            "headline": "디즈니, 마블 판타스틱4 촬영 돌입",
            "industry": "마블 페이즈6 재편\n극장 윈도우 45일로 연장\n디즈니+ 동시공개 축소",
            "behind": "런던 Pinewood 스튜디오\nIMAX 카메라 40% 사용\n실물 세트 위주 제작",
            "promo": "티저 24시간 8000만뷰\nCinemaCon 호평\n한국 홍보 일정 미정",
            "company": "Disney",
            "ticker": "DIS",
            "source": "Variety"
        }
    
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    articles_text = "\n".join([f"- {a['title']}: {a['summary']}" for a in articles[:10]])
    prompt = USER_PROMPT_TEMPLATE.format(articles=articles_text)
    
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role":"system", "content": SYSTEM_PROMPT},
            {"role":"user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    return json.loads(resp.choices[0].message.content)

def main():
    print("=== Hollywood CardNews Generator ===")
    articles = fetch_rss()
    print(f"기사 {len(articles)}개 수집")

    data = summarize_with_llm(articles)
    ticker = data.get("ticker") or TICKER_MAP.get(data.get("company","Disney"), "DIS")
    data["ticker"] = ticker

    stock_info = get_stock_data(ticker)
    print(f"주식 {ticker}: {stock_info['close']}")

    date_str = datetime.now().strftime("%Y-%m-%d")
    output_dir = f"{OUTPUT_BASE}/{date_str}_{ticker}"
    
    generate_all_cards(data, stock_info, output_dir)

    # meta 저장
    with open(f"{output_dir}/meta.json", "w", encoding="utf-8") as f:
        json.dump({"data": data, "stock": stock_info, "articles": articles[:5]}, f, ensure_ascii=False, indent=2)

    # 드라이브 업로드 (선택)
    drive_output_id = os.getenv("GDRIVE_FOLDER_ID_Output")
    upload_to_drive(output_dir, drive_output_id)

    print(f"완료: {output_dir}")

if __name__ == "__main__":
    main()
