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
    """응답 텍스트에서 JSON 오브젝트만 추출."""
    text = text.strip()
    if "```" in text:
        # ```json ... ``` 블록 우선
        m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if m:
            text = m.group(1)
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            return json.loads(m.group())
        raise ValueError("응답에서 JSON을 찾지 못했습니다.")


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
            "max_uses": MAX_SEARCHES,  # ← 실행당 검색 횟수 하드캡. 초과하면 Claude가 더 못 검색함.
        }],
    )

    # web_search 응답은 여러 블록(text, server_tool_use, web_search_tool_result)으로 옴.
    # 최종 텍스트 블록만 이어붙여 JSON 추출.
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

    data = _extract_json(full_text)
    # 날짜 보정
    if not data.get("date"):
        data["date"] = today
    return data
