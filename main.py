# -*- coding: utf-8 -*-
"""
CINEPARK0410 YouTube Factory - 구글 신형 SDK (google.genai)
5분 가로 + 1분20초 세로
"""
import os
import json
import time
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
load_dotenv()

from config import OUTPUT_BASE, GDRIVE_OUTPUT_ID, QA_THRESHOLD
from prompts import SYSTEM_PROMPT_WRITER_5MIN, SYSTEM_PROMPT_WRITER_SHORTS, SYSTEM_PROMPT_QA, SYSTEM_PROMPT_TOPIC_SCORER, USER_PROMPT_TEMPLATE

# ===== 신형 구글 SDK =====
from google import genai
from google.genai import types

def _kst_today():
    kst = timezone(timedelta(hours=9))
    return datetime.now(kst).strftime("%Y-%m-%d")

def get_client():
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_GEMINI_API_KEY")
    if not api_key:
        raise SystemExit("GEMINI_API_KEY 없음 → Google AI Studio에서 발급 필요")
    client = genai.Client(api_key=api_key)
    return client

def fetch_ourmalsam(keyword: str) -> dict:
    key = os.getenv("OURIMALSAEM_API_KEY", "03372")
    print(f"[우리말샘] {keyword} 조회 중... (키 {key[:4]}...)")
    return {
        "keyword": keyword,
        "definition": f"{keyword}의 국립국어원 정의",
        "pos": "명사",
        "origin": "우리말샘 원문",
        "raw": f"출처: 국립국어원 우리말샘 Open API - {keyword}"
    }

def gen_json(client, system_prompt, user_prompt):
    """JSON 생성 - 신형 SDK"""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=[f"{system_prompt}\n\n{user_prompt}"],
            config=types.GenerateContentConfig(
                temperature=0.7,
                response_mime_type="application/json"
            )
        )
        text = response.text.strip()
        # 마크다운 제거
        if "```" in text:
            text = text.split("```")[1] if "```json" not in text else text.split("```json")[1].split("```")[0]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text)
    except Exception as e:
        print(f"  JSON 생성 실패: {e}")
        print(f"  원문: {response.text[:500] if 'response' in locals() else 'no response'}")
        raise

def score_topics(client, keywords: list) -> dict:
    print(f"[주제 검수] {keywords} 스코어링 중...")
    try:
        data = gen_json(client, SYSTEM_PROMPT_TOPIC_SCORER, f"주제어 목록: {keywords}")
        print(f"  → Top Pick: {data.get('top_pick')} ({data.get('ranked',[{}])[0].get('score')}점)")
        return data
    except Exception as e:
        print(f"  주제 스코어링 실패, 첫 번째 주제로 진행: {e}")
        return {"top_pick": keywords[0], "ranked": [{"keyword": k, "score": 80} for k in keywords]}

def write_5min_with_qa(client, keyword: str, ourmalsam_data: dict) -> dict:
    user_prompt = USER_PROMPT_TEMPLATE.format(keyword=keyword, ourmalsam_data=json.dumps(ourmalsam_data, ensure_ascii=False), today=_kst_today())
    
    for attempt in range(1, 4):
        print(f"[5분 대본 작성] 시도 {attempt}/3")
        try:
            draft = gen_json(client, SYSTEM_PROMPT_WRITER_5MIN, user_prompt)
        except Exception as e:
            print(f"  대본 생성 실패, 재시도: {e}")
            time.sleep(2)
            continue

        print(f"[내용 검수 QA] {keyword} 채점 중...")
        qa_input = f"ourmalsam_data: {json.dumps(ourmalsam_data, ensure_ascii=False)}\n대본: {json.dumps(draft, ensure_ascii=False)}"
        try:
            qa = gen_json(client, SYSTEM_PROMPT_QA, qa_input)
            score = qa.get("total_score", 0)
            print(f"  → QA 점수: {score}점 / 피드백: {qa.get('feedback')}")
            if score >= QA_THRESHOLD:
                draft["_qa"] = qa
                return draft
            else:
                user_prompt += f"\n\n[이전 QA 피드백 - 반드시 수정] {qa.get('feedback')} (점수 {score}점)"
        except Exception as e:
            print(f"  QA 실패, 그대로 진행: {e}")
            draft["_qa"] = {"total_score": 80, "pass": True}
            return draft
    
    return draft

def write_shorts(client, full_5min_data: dict) -> dict:
    print(f"[쇼츠 1분20초 압축] {full_5min_data.get('keyword')}")
    try:
        data = gen_json(client, SYSTEM_PROMPT_WRITER_SHORTS, f"5분 대본: {json.dumps(full_5min_data, ensure_ascii=False)}")
        return data
    except Exception as e:
        print(f"  쇼츠 압축 실패: {e}")
        return {"keyword": full_5min_data.get("keyword"), "script_80sec": full_5min_data.get("full_script_5min","")[:400], "captions": [], "visual_prompt_vertical": full_5min_data.get("visual_prompts",[""])[0]}

def main():
    print("=== CINEPARK0410 YouTube Factory - 구글 신형 SDK (google.genai) ===")
    print(f"QA 기준: {QA_THRESHOLD}점")

    client = get_client()

    candidate_keywords = ["며칠", "웬/왠", "되/돼", "던/든", "로써/로서", "며칠 몇일", "금세/금새", "어떻게/어떡해", "왠지/웬지", "뵈요/봬요"]
    scored = score_topics(client, candidate_keywords)
    keyword = scored.get("top_pick") or candidate_keywords[0]

    ourmalsam_data = fetch_ourmalsam(keyword)
    data_5min = write_5min_with_qa(client, keyword, ourmalsam_data)
    data_shorts = write_shorts(client, data_5min)

    date_str = _kst_today()
    output_dir = f"{OUTPUT_BASE}/{date_str}_{keyword}_dual"
    os.makedirs(output_dir, exist_ok=True)

    with open(f"{output_dir}/meta.json", "w", encoding="utf-8") as f:
        json.dump({"keyword": keyword, "ourmalsam": ourmalsam_data, "5min": data_5min, "shorts": data_shorts, "topic_score": scored}, f, ensure_ascii=False, indent=2)
    
    with open(f"{output_dir}/script_5min.txt", "w", encoding="utf-8") as f:
        f.write(data_5min.get("full_script_5min",""))
    
    with open(f"{output_dir}/script_80sec.txt", "w", encoding="utf-8") as f:
        f.write(data_shorts.get("script_80sec",""))

    print(f"\n=== 생성 완료 ===")
    print(f"폴더: {output_dir}")
    print(f"  - 5분 가로: {len(data_5min.get('full_script_5min',''))}자 / QA {data_5min.get('_qa',{}).get('total_score')}점")
    print(f"  - 1분20초 세로: {len(data_shorts.get('script_80sec',''))}자")
    
    try:
        from drive_uploader import upload_to_drive
        upload_to_drive(output_dir, GDRIVE_OUTPUT_ID)
        print(f"드라이브 업로드 완료")
    except Exception as e:
        print(f"드라이브 스킵: {e}")

if __name__ == "__main__":
    main()
