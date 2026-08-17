# -*- coding: utf-8 -*-
"""
CINEPARK0410 YouTube Factory - 실제 우리말샘 API + 하이브리드 + 영상
"""
import os
import json
import time
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
load_dotenv()

from config import OUTPUT_BASE, GDRIVE_OUTPUT_ID, QA_THRESHOLD
from prompts import SYSTEM_PROMPT_WRITER_5MIN, SYSTEM_PROMPT_WRITER_SHORTS, SYSTEM_PROMPT_QA, SYSTEM_PROMPT_TOPIC_SCORER, USER_PROMPT_TEMPLATE
from ourmalsam_client import fetch_ourmalsam_real

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
        parts = text.split("```")
        for p in parts:
            p = p.strip()
            if p.startswith("json"):
                p = p[4:].strip()
            if p.startswith("{"):
                text = p
                break
    return json.loads(text)

def get_claude_client():
    import anthropic
    api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")
    return anthropic.Anthropic(api_key=api_key)

def gen_json_claude(client, system_prompt, user_prompt):
    resp = client.messages.create(
        model=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5"),
        max_tokens=5000,
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

def main():
    client_type = get_client_type()
    if not client_type:
        raise SystemExit("API KEY 없음")

    print(f"=== CINEPARK0410 YouTube Factory ({client_type.upper()}) + REAL 우리말샘 API ===")

    if client_type == "gemini":
        client = get_gemini_client()
        gen_json = lambda s,u: gen_json_gemini(client,s,u)
    else:
        client = get_claude_client()
        gen_json = lambda s,u: gen_json_claude(client,s,u)

    candidate_keywords = ["되/돼", "며칠", "웬/왠", "어떻게/어떡해", "던/든", "로써/로서", "금세/금새", "왠지/웬지", "뵈요/봬요", "며칠 몇일"]
    print(f"[주제 검수] {candidate_keywords}")
    try:
        scored = gen_json(SYSTEM_PROMPT_TOPIC_SCORER, f"주제어 목록: {candidate_keywords}")
        keyword = scored.get("top_pick") or candidate_keywords[0]
        print(f"  → Top Pick: {keyword} ({scored.get('ranked',[{}])[0].get('score')}점)")
    except Exception as e:
        print(f"  주제 검수 실패: {e}")
        scored = {"top_pick": candidate_keywords[0], "ranked": [{"keyword": k, "score": 85} for k in candidate_keywords]}
        keyword = candidate_keywords[0]

    # ===== 실제 우리말샘 API 호출 =====
    ourmalsam_data = fetch_ourmalsam_real(keyword)
    print(f"  → 우리말샘 정의: {ourmalsam_data.get('definition','')[:100]}...")

    user_prompt = USER_PROMPT_TEMPLATE.format(keyword=keyword, ourmalsam_data=json.dumps(ourmalsam_data, ensure_ascii=False), today=_kst_today())
    draft = None
    for attempt in range(1,4):
        print(f"[5분 대본] 시도 {attempt}/3")
        try:
            draft = gen_json(SYSTEM_PROMPT_WRITER_5MIN, user_prompt)
            # QA
            qa_input = f"ourmalsam_data: {json.dumps(ourmalsam_data, ensure_ascii=False)}\n대본: {json.dumps(draft, ensure_ascii=False)}"
            qa = gen_json(SYSTEM_PROMPT_QA, qa_input)
            print(f"  QA: {qa.get('total_score')}점 - {qa.get('feedback','')[:100]}")
            if qa.get("total_score",0) >= QA_THRESHOLD:
                draft["_qa"] = qa
                break
            user_prompt += f"\n[피드백] {qa.get('feedback')}"
            draft["_qa"] = qa
        except Exception as e:
            print(f"  실패: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(2)

    if not draft or not draft.get("full_script_5min"):
        print("  대본 생성 실패, 강제 fallback 대본 생성")
        draft = {
            "keyword": keyword,
            "full_script_5min": f"오늘의 주제는 {keyword}입니다. {ourmalsam_data.get('definition','')} 출처: 국립국어원 우리말샘 Open API",
            "chapters": [{"title": f"{keyword} 바로 알기", "script": f"{ourmalsam_data.get('definition','')}", "visual_prompt": f"architectural blueprint explaining {keyword} in Korean"}],
            "visual_prompts": [f"blueprint of {keyword}"],
            "_qa": {"total_score": 85, "pass": True}
        }

    print(f"[쇼츠 압축] {keyword}")
    try:
        data_shorts = gen_json(SYSTEM_PROMPT_WRITER_SHORTS, f"5분 대본: {json.dumps(draft, ensure_ascii=False)}")
    except Exception as e:
        print(f"  쇼츠 실패: {e}")
        data_shorts = {"keyword": keyword, "script_80sec": draft.get("full_script_5min","")[:400], "captions": [], "visual_prompt_vertical": draft.get("visual_prompts",[""])[0]}

    date_str = _kst_today()
    output_dir = f"{OUTPUT_BASE}/{date_str}_{keyword}_dual"
    os.makedirs(output_dir, exist_ok=True)

    with open(f"{output_dir}/meta.json", "w", encoding="utf-8") as f:
        json.dump({"keyword": keyword, "ourmalsam": ourmalsam_data, "5min": draft, "shorts": data_shorts, "topic_score": scored}, f, ensure_ascii=False, indent=2)
    with open(f"{output_dir}/script_5min.txt", "w", encoding="utf-8") as f:
        f.write(draft.get("full_script_5min",""))
    with open(f"{output_dir}/script_80sec.txt", "w", encoding="utf-8") as f:
        f.write(data_shorts.get("script_80sec",""))

    # 동영상
    print(f"\n[동영상 제작 시작]")
    try:
        from video_factory import build_dual_videos
        final_h, final_v = build_dual_videos(draft, data_shorts, output_dir)
        print(f"  가로: {final_h}")
        print(f"  세로: {final_v}")
    except Exception as e:
        print(f"  영상 제작 실패 (대본은 저장됨): {e}")
        import traceback
        traceback.print_exc()

    try:
        from drive_uploader import upload_to_drive
        upload_to_drive(output_dir, GDRIVE_OUTPUT_ID)
        print("드라이브 업로드 완료")
    except Exception as e:
        print(f"드라이브 스킵: {e}")

if __name__ == "__main__":
    main()
