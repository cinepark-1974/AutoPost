# -*- coding: utf-8 -*-
import os

# ===== 구글 올인원 팩토리 설정 =====
# CINEPARK0410 전용: 5분 가로 + 1분20초 세로

# 하네스 버전 - 이 숫자만 올리면 AI가 알아서 더 깎음
HARNESS_VERSION = "v4.1_credibility"

# ===== 출력 규격 =====
HORIZONTAL = {"w": 1920, "h": 1080, "duration_sec": 300}  # 5분
VERTICAL = {"w": 1080, "h": 1920, "duration_sec": 80}   # 1분20초

# ===== 신뢰도 하네스 =====
# 이 토큰은 모든 프롬프트에 강제 주입됨
CREDIBILITY_HARNESS = """
[신뢰도 하네스 - 절대 규칙]
1. 모든 맞춤법 설명은 국립국어원 우리말샘 Open API 데이터를 1차 출처로 한다. 우리말샘에 없는 설명은 하지 않는다.
2. 화면에 반드시 '출처: 국립국어원 우리말샘' 자막을 3초 이상 노출한다.
3. 영화 프로듀서 관점에서 말한다. 예: '시나리오에 이렇게 쓰면 투자 심사에서 바로 탈락합니다'
4. 낚시 제목 금지. 정확한 정보만.
5. 건축 도해 비유를 반드시 1개 이상 사용한다. 예: '며칠은 건물의 뼈대처럼 붙어 쓰는 말입니다'
"""

# ===== AI 스코어링 QA 기준 =====
# 주제 검수
TOPIC_SCORE_WEIGHTS = {
    "search_volume": 0.30,  # 네이버 월 검색량
    "competition": 0.20,    # 유튜브 경쟁도 낮을수록 고득점
    "educational": 0.20,    # 교육적 가치
    "viral": 0.20,          # 쇼츠 바이럴 가능성
    "duplicate": 0.10       # 기존 CINEPARK 채널 중복 여부
}

# 내용 검수 - 100점 만점, 85점 미만이면 재생성
CONTENT_QA_RUBRIC = {
    "fact_accuracy": 30,      # 우리말샘과 일치하는가
    "producer_insight": 25,   # 프로듀서 관점 코멘트 있는가
    "blueprint_visual": 20,   # 건축 도해 설명 있는가
    "retention_hook": 15,     # 3초 훅 있는가
    "source_display": 10      # 출처 명시 있는가
}
QA_THRESHOLD = 85

# ===== 모델 =====
# 구글 올인원: Gemini 1개로 작가/채점자 역할 분리
GEMINI_MODEL_WRITER = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")
GEMINI_MODEL_QA = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")

# ===== 경로 =====
OUTPUT_BASE = "output"
GDRIVE_OUTPUT_ID = os.getenv("GDRIVE_FOLDER_ID_OUTPUT", "")
GDRIVE_BACKGROUND_ID = os.getenv("GDRIVE_FOLDER_ID_BACKGROUND", "")

# ===== 우리말샘 API =====
OURIMAL_API_KEY = os.getenv("OURIMALSAEM_API_KEY", "03372")
OURIMAL_API_URL = "https://opendict.korean.go.kr/api"

# ===== 스타일 토큰 (CINEPARK 브랜딩) =====
BG = "#070A1A"
BG_GRADIENT = ["#04050E", "#080B22"]
BLUE = "#4CC9F0"
GOLD = "#F4C56A"
TXT = "#E6EAF2"
SUB = "#9DB0C8"
