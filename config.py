# -*- coding: utf-8 -*-
import os

# ===== 비용 안전장치: 검색 횟수 상한 =====
MAX_SEARCHES = int(os.getenv("MAX_SEARCHES", "10"))

# 모델
MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5")
MAX_TOKENS = 4000

# ===== 카드 스타일 토큰 =====
# BG는 이제 단색이 아니라 그라데이션 + 글로우 조합으로 정의
# 기존 BG = "#070A1A"는 두 색의 평균이라 하위호환용으로 남겨둠

BG = "#070A1A" # fallback 단색
BG_GRADIENT = ["#04050E", "#080B22"] # 색1, 색2
BG_ANGLE = 160 # 대각선 방향

# 글로우 효과 - Canva에서 원+블러로 하던거
GLOWS = [
    {
        "color": "#4CC9F0", # 하늘색 글로우
        "opacity": 0.12, # 10~15% -> 0.12
        "blur": 120, # 블러 최대
        "position": "top_right", # 우상단
        "size": 700,
    },
    {
        "color": "#03045E", # 딥블루 글로우
        "opacity": 0.55,
        "blur": 100,
        "position": "bottom_left", # 좌하단
        "size": 600,
    }
]

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
