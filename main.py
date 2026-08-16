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
    text = resp.content[0].text
    if "```" in text:
        try:
            text = text.split("```")[1].replace("json","").strip()
        except:
            pass
    try:
        return json.loads(text)
    except:
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

    # --- 자동 패치: drive_uploader 구버전이면 최신으로 교체 ---
    try:
        from pathlib import Path
        du_path = Path("utils/drive_uploader.py")
        if du_path.exists():
            txt = du_path.read_text(encoding="utf-8")
            if "GOOGLE_CREDENTIALS_JSON_CONTENT" not in txt:
                print("구버전 drive_uploader 감지 → 자동 패치 중...")
                du_path.write_text("""import os
import json
from pathlib import Path

def get_drive_service():
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    scopes = ["https://www.googleapis.com/auth/drive"]
    json_content = os.getenv("GOOGLE_CREDENTIALS_JSON_CONTENT")
    if json_content:
        try:
            info = json.loads(json_content)
            creds = service_account.Credentials.from_service_account_info(info, scopes=scopes)
            print("Drive 인증: GOOGLE_CREDENTIALS_JSON_CONTENT 사용")
            return build("drive", "v3", credentials=creds)
        except Exception as e:
            print(f"JSON_CONTENT 파싱 실패: {e}")
    cred_path = os.getenv("GOOGLE_CREDENTIALS_JSON", "./credentials.json")
    if Path(cred_path).exists():
        creds = service_account.Credentials.from_service_account_file(cred_path, scopes=scopes)
        print(f"Drive 인증: 파일 사용 {cred_path}")
        return build("drive", "v3", credentials=creds)
    print("credentials.json 없음 → 드라이브 업로드 스킵")
    return None

def download_random_background(drive_folder_id):
    if not drive_folder_id:
        return None
    try:
        service = get_drive_service()
        if not service:
            return None
        query = f"'{drive_folder_id}' in parents and trashed=false and mimeType contains 'image/'"
        results = service.files().list(q=query, fields="files(id, name)", pageSize=100).execute()
        files = results.get('files', [])
        if not files:
            print("Background 폴더에 이미지 없음")
            return None
        import random
        chosen = random.choice(files)
        print(f"Background 선택: {chosen['name']}")
        from googleapiclient.http import MediaIoBaseDownload
        import io
        request = service.files().get_media(fileId=chosen['id'])
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        tmp_path = f"/tmp/bg_{chosen['name']}"
        with open(tmp_path, 'wb') as f:
            f.write(fh.getvalue())
        return tmp_path
    except Exception as e:
        print(f"Background 다운로드 실패: {e}")
        return None

def upload_to_drive(local_folder, drive_folder_id=None):
    if not drive_folder_id:
        print("DRIVE_FOLDER_ID 없음")
        return
    try:
        service = get_drive_service()
        if not service:
            return
        from googleapiclient.http import MediaFileUpload
        folder_name = Path(local_folder).name
        file_metadata = {"name": folder_name, "mimeType": "application/vnd.google-apps.folder", "parents": [drive_folder_id]}
        folder = service.files().create(body=file_metadata, fields="id").execute()
        new_folder_id = folder.get("id")
        print(f"Drive 폴더 생성: {folder_name} ({new_folder_id})")
        for file in Path(local_folder).glob("*"):
            if file.is_file():
                media = MediaFileUpload(str(file), resumable=True)
                service.files().create(body={"name": file.name, "parents": [new_folder_id]}, media_body=media, fields="id").execute()
                print(f"  업로드: {file.name}")
        print(f"Drive 업로드 완료: {folder_name}")
    except Exception as e:
        print(f"Drive 업로드 실패: {e}")
        raise
""", encoding="utf-8")
                print("drive_uploader.py 자동 패치 완료!")
    except Exception as e:
        print(f"자동 패치 실패 (무시): {e}")
    # --- 패치 끝 ---

    print("=== Hollywood CardNews Generator (Drive BG 버전) ===")
    articles = fetch_rss()
    print(f"기사 {len(articles)}개 수집")
    data = summarize_with_llm(articles)
    ticker = data.get("ticker") or TICKER_MAP.get(data.get("company","Disney"), "DIS")
    data["ticker"] = ticker

    print("배경 이미지 다운로드 시도...")
    try:
        bg_path = download_random_background(GDRIVE_BACKGROUND_ID)
        if not bg_path:
            print("Background 폴더에 이미지 없음 → 로컬 배경 또는 단색으로 대체")
    except Exception as e:
        print(f"Background 다운로드 실패 (무시하고 계속): {e}")
        bg_path = None

    # 주가 데이터 - None 방어
    try:
        stock_info = get_stock_data(ticker)
        if not stock_info:
            stock_info = {"ticker": ticker, "close": 0, "change": 0, "history": [], "chart_path": None, "date": datetime.now().strftime("%Y-%m-%d")}
    except Exception as e:
        print(f"주식 데이터 실패 {ticker}: {e}")
        stock_info = {"ticker": ticker, "close": 0, "change": 0, "history": [], "chart_path": None, "date": datetime.now().strftime("%Y-%m-%d")}

    # 안전하게 출력
    close_val = stock_info.get('close', 0) if stock_info else 0
    print(f"주식 {ticker}: close={close_val}")

    date_str = datetime.now().strftime("%Y-%m-%d")
    output_dir = f"{OUTPUT_BASE}/{date_str}_{ticker}"
    
    generate_all_cards(data, stock_info, output_dir, bg_path=bg_path)

    with open(f"{output_dir}/meta.json", "w", encoding="utf-8") as f:
        safe_stock = {k:v for k,v in (stock_info or {}).items() if k!='chart_path'}
        json.dump({"data": data, "stock": safe_stock, "articles": articles[:5]}, f, ensure_ascii=False, indent=2)

    upload_to_drive(output_dir, GDRIVE_OUTPUT_ID)
    print(f"완료: {output_dir}")

if __name__ == "__main__":
    main()
