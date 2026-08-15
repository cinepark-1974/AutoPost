# 할리우드 스튜디오 -> 티커 매핑
TICKER_MAP = {
    "Disney": "DIS",
    "Marvel": "DIS",
    "Pixar": "DIS",
    "Warner": "WBD",
    "Warner Bros": "WBD",
    "HBO": "WBD",
    "DC": "WBD",
    "Universal": "CMCSA",
    "Comcast": "CMCSA",
    "DreamWorks": "CMCSA",
    "Paramount": "PARA",
    "Netflix": "NFLX",
    "Sony": "SONY",
    "Sony Pictures": "SONY",
    "Lionsgate": "LGF.A",
    "IMAX": "IMAX",
    "AMC": "AMC",
    # AI 영상 비상장 대체
    "Runway": "ADBE",
    "Pika": "NVDA",
    "Adobe": "ADBE",
    "Nvidia": "NVDA",
}

# RSS 소스
RSS_FEEDS = [
    "https://variety.com/feed/",
    "https://deadline.com/feed/",
    "https://www.hollywoodreporter.com/feed/",
    "https://www.thewrap.com/feed/",
]

# 카드 설정
CARD_SIZE = (1080, 1920)  # 9:16 세로 (틱톡/쇼츠/릴스 공용)
CARD_SIZE_INSTAGRAM = (1080, 1350)
FONT_BOLD = "assets/fonts/Pretendard-Bold.otf"  # 없으면 DejaVu로 fallback
FONT_REGULAR = "assets/fonts/Pretendard-Regular.otf"

# 출력
OUTPUT_BASE = "output"
