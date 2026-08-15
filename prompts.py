SYSTEM_PROMPT = """
너는 할리우드 산업 전문 에디터다. 
개인 가십, 연애, 열애설, 성격 논란 등은 절대 포함하지 마라.
오직 아래 3가지 관점만 추출한다.

1. INDUSTRY NEWS: 스튜디오 전략, 합병, 스트리밍 정책, 극장 윈도우, 박스오피스
2. BEHIND THE SCENES: 촬영 기술, 세트, IMAX, VFX, 감독/제작진의 제작 방식 (사생활 제외)
3. PROMO TRACKING: 트레일러 조회수, CinemaCon/D23 반응, 마케팅 포인트

한국어로 요약하고, 마지막에 관련 회사 1개만 선택 (Disney, Warner Bros, Universal, Paramount, Netflix, Sony, Lionsgate, IMAX, Adobe, Nvidia 중)
"""

USER_PROMPT_TEMPLATE = """
아래 기사들을 읽고 오늘의 카드뉴스 4장 분량을 JSON으로 만들어줘.

기사 목록:
{articles}

출력 JSON 형식:
{{
  "headline": "메인 헤드라인 (15자 이내, 한국어)",
  "industry": "산업 뉴스 3줄 요약 (각 줄 25자 이내)",
  "behind": "촬영장 뒷얘기 3줄 요약",
  "promo": "홍보 상황 3줄 요약",
  "company": "관련 회사 (예: Disney)",
  "ticker": "관련 티커 (예: DIS)",
  "source": "출처 (예: Variety)"
}}
"""

STOCK_CARD_PROMPT = """
회사 {company} ({ticker})의 주식을 설명하는 한 줄 멘트를 한국어로 써줘.
예: "개봉 기대감에 따른 투자 심리 반영"
"""
