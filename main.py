# -*- coding: utf-8 -*-
"""
CINEPARK0410 YouTube Factory - 하이브리드 (Gemini 또는 Claude 자동 선택)
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

def _kst_today():
    kst = timezone(timedelta(hours=9))
    return datetime.now(kst).strftime("%Y-%m-%d")

def get_client_type():
    """어떤 키가 있는지 자동 감지"""
    if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_GEMINI_API_KEY"):
        return "gemini"
    if os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY"):
        return "claude"
    return None

# ===== Gemini 클라이언트 =====
def get_gemini_client():
    from google import genai
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_GEMINI_API_KEY")
    return genai.Client(api_key=api_key)

def gen_json_gemini(client, system_prompt, user_prompt):
    from google.genai import types
    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=[f"{system_prompt}\n\n{user_prompt}"],
        config=types.GenerateContentConfig(
            temperature=0.7,
            response_mime_type="application/json"
        )
    )
    text = response.text.strip()
    if "```" in text:
        # ```json ... ``` 제거
        parts = text.split("```")
        for p in parts:
            p = p.strip()
            if p.startswith("json"):
                p = p[4:].strip()
            if p.startswith("{"):
                text = p
                break
    return json.loads(text)

# ===== Claude 클라이언트 =====
def get_claude_client():
    import anthropic
    api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")
    return anthropic.Anthropic(api_key=api_key)

def gen_json_claude(client, system_prompt, user_prompt):
    resp = client.messages.create(
        model=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5"),
        max_tokens=4000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )
    text = resp.content[0].text.strip()
    if "```" in text:
        parts = text.split("```")
        for p in parts:
            p = p.strip()
            if p.startswith("json"):
                p = p[4:].strip()
            if p.startswith("{"):
                text = p
                break
    return json.loads(text)

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

def main():
    client_type = get_client_type()
    if not client_type:
        raise SystemExit("GEMINI_API_KEY 또는 ANTHROPIC_API_KEY 없음 → Secrets에 키 추가 필요")

    print(f"=== CINEPARK0410 YouTube Factory ({client_type.upper()}) ===")
    print(f"QA 기준: {QA_THRESHOLD}점")

    if client_type == "gemini":
        client = get_gemini_client()
        gen_json = lambda sys_p, usr_p: gen_json_gemini(client, sys_p, usr_p)
    else:
        client = get_claude_client()
        gen_json = lambda sys_p, usr_p: gen_json_claude(client, sys_p, usr_p)
        print(f"  → Claude 모델 사용: {os.getenv('CLAUDE_MODEL', 'claude-sonnet-4-5')}")

    # 주제 자동화
    candidate_keywords = ["며칠", "웬/왠", "되/돼", "던/든", "로써/로서", "며칠 몇일", "금세/금새", "어떻게/어떡해", "왠지/웬지", "뵈요/봬요"]
    
    print(f"[주제 검수] {candidate_keywords} 스코어링 중...")
    try:
        scored = gen_json(SYSTEM_PROMPT_TOPIC_SCORER, f"주제어 목록: {candidate_keywords}")
        keyword = scored.get("top_pick") or candidate_keywords[0]
        print(f"  → Top Pick: {keyword}")
    except Exception as e:
        print(f"  주제 스코어링 실패, 첫 주제로 진행: {e}")
        scored = {"top_pick": candidate_keywords[0], "ranked": []}
        keyword = candidate_keywords[0]

    ourmalsam_data = fetch_ourmalsam(keyword)

    # 5분 대본 + QA
    user_prompt = USER_PROMPT_TEMPLATE.format(keyword=keyword, ourmalsam_data=json.dumps(ourmalsam_data, ensure_ascii=False), today=_kst_today())
    
    draft = None
    for attempt in range(1, 4):
        print(f"[5분 대본 작성] 시도 {attempt}/3")
        try:
            draft = gen_json(SYSTEM_PROMPT_WRITER_5MIN, user_prompt)
            print(f"[내용 검수 QA] {keyword} 채점 중...")
            qa_input = f"ourmalsam_data: {json.dumps(ourmalsam_data, ensure_ascii=False)}\n대본: {json.dumps(draft, ensure_ascii=False)}"
            qa = gen_json(SYSTEM_PROMPT_QA, qa_input)
            score = qa.get("total_score", 0)
            print(f"  → QA 점수: {score}점 / {qa.get('feedback')}")
            if score >= QA_THRESHOLD:
                draft["_qa"] = qa
                break
            else:
                user_prompt += f"\n\n[이전 QA 피드백 - 반드시 수정] {qa.get('feedback')} (점수 {score}점)"
                draft["_qa"] = qa
        except Exception as e:
            print(f"  생성 실패: {e}")
            time.sleep(2)
            continue

    if not draft:
        raise SystemExit("대본 생성 실패 - 3회 재시도 후 중단")

    # 쇼츠
    print(f"[쇼츠 1분20초 압축] {keyword}")
    try:
        data_shorts = gen_json(SYSTEM_PROMPT_WRITER_SHORTS, f"5분 대본: {json.dumps(draft, ensure_ascii=False)}")
    except:
        data_shorts = {"keyword": keyword, "script_80sec": draft.get("full_script_5min","")[:400]}

    # 저장
    date_str = _kst_today()
    output_dir = f"{OUTPUT_BASE}/{date_str}_{keyword}_dual"
    os.makedirs(output_dir, exist_ok=True)

    with open(f"{output_dir}/meta.json", "w", encoding="utf-8") as f:
        json.dump({"keyword": keyword, "ourmalsam": ourmalsam_data, "5min": draft, "shorts": data_shorts, "topic_score": scored}, f, ensure_ascii=False, indent=2)
    with open(f"{output_dir}/script_5min.txt", "w", encoding="utf-8") as f:
        f.write(draft.get("full_script_5min",""))
    with open(f"{output_dir}/script_80sec.txt", "w", encoding="utf-8") as f:
        f.write(data_shorts.get("script_80sec",""))

    print(f"\n=== 생성 완료 ===")
    print(f"폴더: {output_dir}")

    try:
        from drive_uploader import upload_to_drive
        upload_to_drive(output_dir, GDRIVE_OUTPUT_ID)
    except Exception as e:
        print(f"드라이브 스킵: {e}")

if __name__ == "__main__":
    main()
