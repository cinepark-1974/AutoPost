# -*- coding: utf-8 -*-
"""
CINEPARK0410 Main - 다크 시네마틱 + 영화 시나리오 3요소(씬/대사/지문) 20장
"""
import os, json, time
from dotenv import load_dotenv
load_dotenv()

from config import OUTPUT_BASE, GDRIVE_OUTPUT_ID, QA_THRESHOLD
from prompts import SYSTEM_PROMPT_WRITER_5MIN, SYSTEM_PROMPT_WRITER_SHORTS, SYSTEM_PROMPT_QA, SYSTEM_PROMPT_TOPIC_SCORER, USER_PROMPT_TEMPLATE
from ourmalsam_client import fetch_ourmalsam_real
from datetime import datetime, timezone, timedelta

def _kst_today():
    kst = timezone(timedelta(hours=9))
    return datetime.now(kst).strftime("%Y-%m-%d")

def get_client_type():
    if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
        return "gemini"
    if os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY"):
        return "claude"
    return None

def get_gemini_client():
    from google import genai
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    return genai.Client(api_key=api_key)

def gen_json_gemini(client, system_prompt, user_prompt):
    from google.genai import types
    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=[f"{system_prompt}\n\n{user_prompt}"],
        config=types.GenerateContentConfig(temperature=0.7, response_mime_type="application/json")
    )
    text = response.text.strip()
    if "```" in text:
        for p in text.split("```"):
            p=p.strip()
            if p.startswith("json"): p=p[4:].strip()
            if p.startswith("{"): text=p; break
    return json.loads(text)

def get_claude_client():
    import anthropic
    api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")
    return anthropic.Anthropic(api_key=api_key)

def gen_json_claude(client, system_prompt, user_prompt):
    resp = client.messages.create(
        model=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5"),
        max_tokens=6000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )
    text = resp.content[0].text.strip()
    if "```" in text:
        for p in text.split("```"):
            p=p.strip()
            if p.startswith("json"): p=p[4:].strip()
            if p.startswith("{"): text=p; break
    return json.loads(text)

def main():
    client_type = get_client_type()
    if not client_type: raise SystemExit("API KEY 없음")
    print(f"=== CINEPARK0410 다크 시네마 + 시나리오 3요소 20장 ({client_type.upper()}) ===")

    if client_type == "gemini":
        client = get_gemini_client()
        gen_json = lambda s,u: gen_json_gemini(client,s,u)
    else:
        client = get_claude_client()
        gen_json = lambda s,u: gen_json_claude(client,s,u)

    candidate_keywords = ["되/돼", "며칠", "웬/왠", "어떻게/어떡해", "던/든", "로써/로서", "금세/금새"]
    try:
        scored = gen_json(SYSTEM_PROMPT_TOPIC_SCORER, f"주제어 목록: {candidate_keywords}")
        keyword = scored.get("top_pick") or candidate_keywords[0]
    except:
        scored = {"top_pick": candidate_keywords[0]}
        keyword = candidate_keywords[0]

    ourmalsam_data = fetch_ourmalsam_real(keyword)

    user_prompt = USER_PROMPT_TEMPLATE.format(keyword=keyword, ourmalsam_data=json.dumps(ourmalsam_data, ensure_ascii=False), today=_kst_today())
    user_prompt += "\n추가 지시: 영화 시나리오 맞춤법에서 출발. 시나리오는 씬, 대사, 지문 세 종류로 이루어진다. 건축 비유 금지, 씬/대사/지문으로 설명. 채널은 CINEPARK0410 영화 채널. 출처는 국립국어원 표준국어대사전·우리말샘."

    draft = None
    for attempt in range(1,4):
        print(f"[5분 대본 - 씬/대사/지문 톤] {attempt}/3")
        try:
            draft = gen_json(SYSTEM_PROMPT_WRITER_5MIN, user_prompt)
            qa_input = f"ourmalsam_data: {json.dumps(ourmalsam_data, ensure_ascii=False)}\n대본: {json.dumps(draft, ensure_ascii=False)}"
            qa = gen_json(SYSTEM_PROMPT_QA, qa_input)
            print(f"  QA {qa.get('total_score')}점")
            if qa.get("total_score",0) >= QA_THRESHOLD:
                draft["_qa"]=qa; break
            user_prompt+=f"\n[피드백] {qa.get('feedback')}"
            draft["_qa"]=qa
        except Exception as e:
            print(f"  실패: {e}"); time.sleep(2)

    if not draft: raise SystemExit("대본 실패")

    try:
        data_shorts = gen_json(SYSTEM_PROMPT_WRITER_SHORTS, f"5분 대본: {json.dumps(draft, ensure_ascii=False)}")
    except:
        data_shorts = {"keyword": keyword, "script_80sec": draft.get("full_script_5min","")[:400]}

    date_str = _kst_today()
    output_dir = f"{OUTPUT_BASE}/{date_str}_{keyword}_dark20"
    os.makedirs(output_dir, exist_ok=True)

    with open(f"{output_dir}/meta.json", "w", encoding="utf-8") as f:
        json.dump({"keyword": keyword, "ourmalsam": ourmalsam_data, "5min": draft, "shorts": data_shorts, "topic_score": scored}, f, ensure_ascii=False, indent=2)
    with open(f"{output_dir}/script_5min.txt", "w", encoding="utf-8") as f:
        f.write(draft.get("full_script_5min",""))
    with open(f"{output_dir}/script_80sec.txt", "w", encoding="utf-8") as f:
        f.write(data_shorts.get("script_80sec",""))

    print("\n[20장 도판 생성 - 다크 시네마 + 씬/대사/지문]")
    try:
        from encyclopedia_factory_dark_cinema import build_20_plates_dark
        h,v = build_20_plates_dark(keyword, ourmalsam_data, output_dir)
        print(f"  20장 완성 - 색감: {['#04050E','#080B22']} 그라데이션")
    except Exception as e:
        print(f"  도판 실패: {e}")
        import traceback; traceback.print_exc()

    try:
        from drive_uploader import upload_to_drive
        upload_to_drive(output_dir, GDRIVE_OUTPUT_ID)
    except Exception as e:
        print(f"드라이브 스킵: {e}")

if __name__ == "__main__":
    main()
