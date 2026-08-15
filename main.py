import os, json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

from config import TICKER_MAP, OUTPUT_BASE, GDRIVE_BACKGROUND_ID, GDRIVE_OUTPUT_ID
from utils.news_fetcher import fetch_rss
from utils.stock import get_stock_data
from utils.card_generator import generate_all_cards
from utils.drive_uploader import upload_to_drive, download_random_background
from prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

def summarize_with_claude(articles, api_key):
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    articles_text = "\n".join([f"- {a['title']}: {a['summary']}" for a in articles[:12]])
    prompt = USER_PROMPT_TEMPLATE.format(articles=articles_text)
    resp = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[{"role":"user", "content": prompt}]
    )
    # Claude가 JSON을 텍스트로 줄 수 있어서 JSON 추출
    text = resp.content[0].text
    # ```json ... ``` 제거
    if "```" in text:
        text = text.split("```")[1].replace("json","").strip() if "```" in text else text
    try:
        return json.loads(text)
    except:
        # 파싱 실패 시 첫 { } 찾기
        import re
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            return json.loads(m.group())
        raise

def summarize_with_openai(articles, api_key):
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    articles_text = "\n".join([f"- {a['title']}: {a['summary']}" for a in articles[:12]])
    prompt = USER_PROMPT_TEMPLATE.format(articles=articles_text)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"system", "content": SYSTEM_PROMPT},{"role":"user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(resp.choices[0].message.content)

def summarize_with_llm(articles):
    claude_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if claude_key:
        print("Claude API로 요약 중...")
        try:
            return summarize_with_claude(articles, claude_key)
        except Exception as e:
            print(f"Claude 실패, OpenAI로 fallback: {e}")
    
    if openai_key:
        print("OpenAI API로 요약 중...")
        return summarize_with_openai(articles, openai_key)
    
    print("API 키 없음 → 더미 데이터 사용 (테스트용)")
    return {
        "headline": "디즈니, 판타스틱4 촬영 본격 돌입",
        "industry": "마블 페이즈6 재편\n극장 윈도우 45일로 연장\n디즈니+ 동시공개 축소",
        "behind": "런던 Pinewood 스튜디오\nIMAX 카메라 40% 사용\n실물 세트 위주 제작",
        "promo": "티저 24시간 8000만뷰\nCinemaCon 호평\n한국 홍보 일정 미정",
        "company": "Disney",
        "ticker": "DIS",
        "source": "Variety"
    }

def main():
    print("=== Hollywood CardNews Generator (Claude+Drive BG) ===")
    articles = fetch_rss()
    print(f"기사 {len(articles)}개 수집")

    data = summarize_with_llm(articles)
    ticker = data.get("ticker") or TICKER_MAP.get(data.get("company","Disney"), "DIS")
    data["ticker"] = ticker

    print("배경 이미지 다운로드 시도...")
    bg_path = download_random_background(GDRIVE_BACKGROUND_ID)

    stock_info = get_stock_data(ticker)
    print(f"주식 {ticker}: close={stock_info.get('close')}")

    date_str = datetime.now().strftime("%Y-%m-%d")
    output_dir = f"{OUTPUT_BASE}/{date_str}_{ticker}"
    
    generate_all_cards(data, stock_info, output_dir, bg_path=bg_path)

    with open(f"{output_dir}/meta.json", "w", encoding="utf-8") as f:
        json.dump({"data": data, "stock": {k:v for k,v in stock_info.items() if k!='chart_path'}, "articles": articles[:5]}, f, ensure_ascii=False, indent=2)

    upload_to_drive(output_dir, GDRIVE_OUTPUT_ID)
    print(f"완료: {output_dir}")

if __name__ == "__main__":
    main()
