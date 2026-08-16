# -*- coding: utf-8 -*-
import os

# ===== 비용 안전장치: 검색 횟수 상한 (돈이 새지 않도록 하드캡) =====
# Claude가 실행당 사용할 수 있는 web_search 최대 횟수.
# 1회 = $0.01. MAX_SEARCHES=10이면 실행당 검색비 최대 $0.10 로 확정 상한.
MAX_SEARCHES = int(os.getenv("MAX_SEARCHES", "10"))

# 모델
MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5")
MAX_TOKENS = 4000

# ===== 카드 스타일 토큰 =====
BG = "#070A1A"
TXT = "#E6EAF2"
SUB = "#9DB0C8"
BLUE = "#4CC9F0"
GOLD = "#F4C56A"
GREEN = "#34D399"
RED = "#EF4444"
FRAME = "rgba(76,201,240,0.25)"

CARD_W = 1080
CARD_H = 1920
SAFE_TOP = 220
SAFE_BOTTOM = 380

# ===== 경로 / 드라이브 =====
OUTPUT_BASE = "output"
GDRIVE_OUTPUT_ID = os.getenv("GDRIVE_FOLDER_ID_OUTPUT") or os.getenv("GDRIVE_FOLDER_ID_Output") or ""

# 비상장사 → 대표 상장사 매핑 (프롬프트 참고용, Claude가 최종 판단)
TICKER_MAP = {
    "Disney": "DIS", "Marvel": "DIS", "Pixar": "DIS", "Lucasfilm": "DIS",
    "Warner": "WBD", "Warner Bros": "WBD", "HBO": "WBD", "DC": "WBD", "Max": "WBD",
    "Universal": "CMCSA", "Comcast": "CMCSA", "DreamWorks": "CMCSA", "Focus": "CMCSA",
    "Paramount": "PARA", "Netflix": "NFLX",
    "Sony": "SONY", "Sony Pictures": "SONY", "Columbia": "SONY", "Crunchyroll": "SONY",
    "Lionsgate": "LGF.A", "IMAX": "IMAX", "AMC": "AMC", "Cinemark": "CNK",
    "Apple": "AAPL", "Amazon": "AMZN", "MGM": "AMZN",
    "A24": "N/A", "Runway": "N/A", "Neon": "N/A",
    "Adobe": "ADBE", "Nvidia": "NVDA",
}
