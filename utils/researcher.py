# -*- coding: utf-8 -*-
"""Claude API + web_search로 STEP 1(뉴스), STEP 2(주가)를 조사하고 카드 JSON 반환."""
import os
import json
import re
from datetime import datetime, timezone, timedelta

import anthropic

from config import MODEL, MAX_TOKENS, MAX_SEARCHES
from prompts import SYSTEM_PROMPT, USER_PROMPT

def _kst_today():
    kst = timezone(timedelta(hours=9))
    return datetime.now(kst).strftime("%Y-%m-%d")

def _extract_json(text):
    """응답 텍스트에서 JSON 오브젝트만 추출 - 실패해도 최대한 복구"""
    original = text.strip()
    text = original

    # 1. ```json... ``` 블록 우선 추출
    if "```" in text:
        m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.DOTALL | re.IGNORECASE)
        if m:
            text = m.group(1).strip()

    # 2. 첫 { 와 마지막 } 로 범위 좁히기
    start = text.find('{')
    end = text.rfind('}')
    if start!= -1 and end!= -1 and end > start:
        candidate = text[start:end+1]
    else:
        candidate = text

    # 3. 기본 정리
    # trailing comma 제거:,},]
    candidate = re.sub(r',\s*([}\]])', r'\1', candidate)
    # 제어문자 제거 (JSON에 못들어가는 문자)
    candidate = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', candidate)

    # 4. 1차 시도: 표준 json.loads
    try:
        return json.loads(candidate)
    except json.JSONDecodeError as e1:
        print(f"[WARN] 1차 파싱 실패: {e1} (line {e1.lineno} col {e1.colno})")

    # 5. 2차 시도: json-repair (따옴표 미이스케이프, 줄바꿈, 콤마 누락 등 자동복구)
    try:
        from json_repair import repair_json
        print("[INFO] json-repair로 2차 복구 시도...")
        repaired = repair_json(candidate, return_objects=True)
        # repair_json이 list를 반환할 수도 있음
        if isinstance(repaired, dict):
            print("[INFO] json-repair 복구 성공")
            return repaired
        if isinstance(repaired, list) and repaired and isinstance(repaired[0], dict):
            print("[INFO] json-repair 복구 성공 (list[0] 사용)")
            return repaired[0]
    except ImportError:
        print("[WARN] json-repair 미설치. pip install json-repair 권장")
    except Exception as e2:
        print(f"[WARN] json-repair 실패: {e2}")

    # 6. 3차 시도: 가장 관대한 방법 - json.decoder로 raw_decode 스캔
    # candidate 안에 텍스트가 섞여있을 경우를 대비해 앞에서부터 디코딩 시도
    try:
        decoder = json.JSONDecoder()
        obj, idx = decoder.raw_decode(candidate)
        if isinstance(obj, dict):
            print(f"[INFO] raw_decode 복구 성공 (idx={idx})")
            return obj
    except Exception:
        pass

    # 7. 실패시 디버깅용 파일 저장하고 에러
    debug_path = "failed_json.txt"
    with open(debug_path, "w", encoding="utf-8") as f:
        f.write(f"--- ORIGINAL FULL TEXT ---\n{original}\n\n")
        f.write(f"--- CANDIDATE ---\n{candidate}\n")
    print(f"[ERROR] 모든 복구 실패. 원문 저장됨 -> {debug_path}")
    print(f"[ERROR] 원문 앞 1000자:\n{candidate[:1000]}")
    raise ValueError(f"응답에서 유효한 JSON을 찾지 못했습니다. {debug_path} 확인")

def research_cardnews(api_key):
    """web_search를 켠 Claude 호출. 검색 횟수는 MAX_SEARCHES로 상한(비용 하드캡)."""
    client = anthropic.Anthropic(api_key=api_key)
    today = _kst_today()

    resp = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": USER_PROMPT.format(today_kst=today)}],
        tools=[{
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": MAX_SEARCHES,
        }],
    )

    text_parts = []
    search_count = 0
    for block in resp.content:
        btype = getattr(block, "type", None)
        if btype == "text":
            text_parts.append(block.text)
        elif btype == "server_tool_use":
            search_count += 1

    print(f"web_search 사용 횟수: {search_count} (상한 {MAX_SEARCHES})")
    full_text = "\n".join(text_parts)

    # 디버깅용: Claude가 뭐라고 했는지 바로 보기
    if len(full_text) < 50:
        print(f"[WARN] Claude 응답이 너무 짧음: {full_text}")

    data = _extract_json(full_text)

    if not data.get("date"):
        data["date"] = today

    tk = data.get("ticker", "N/A")
    checks = {
        "종가": data.get("close"),
        "전일대비": data.get("change"),
        "52주최고": data.get("week52_high"),
        "52주최저": data.get("week52_low"),
    }
    got = [k for k, v in checks.items() if v is not None]
    missing = [k for k, v in checks.items() if v is None]
    print(f"주가 {tk}: 확보 {got if got else '없음'}" + (f" / 누락 {missing}" if missing else ""))

    return data
