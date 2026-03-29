"""
AutoPost v10.1 - 프롬프트 모음 (팩트 체크 강화 버전)
타입별 맞춤 프롬프트 관리 + 웹 검색 기반 할루시네이션 방지

4가지 타입:
- 거래형 (💰): 할인/구매 정보 중심
- 정보형 (📚): 설명/비교 분석 중심
- 일상형 (☕): 공감/경험 중심
- 뉴스형 (📰): 최신 속보 중심

v10.1 변경사항:
- FACT_CHECK_RULES 추가 (할루시네이션 방지 핵심 규칙)
- 도입부 템플릿 5종 랜덤 (패턴 다변화)
- 마무리 CTA 3종 랜덤 (패턴 다변화)
- 문체 테마 3종 랜덤 (분석/경험/대화)
- 해시태그 개수 변동 (8~15개)
"""

import random


# ═══════════════════════════════════════════════════════════════
# 팩트 체크 규칙 (할루시네이션 방지 - 최우선)
# ═══════════════════════════════════════════════════════════════

FACT_CHECK_RULES = """
═══════════════════════════════════════
🚨 팩트 체크 규칙 (절대 규칙 - 모든 규칙보다 우선)
═══════════════════════════════════════

【영화/시리즈 팩트】
- 영화 제목, 감독, 출연진, 개봉 연도는 반드시 웹 검색 결과에서 확인된 것만 사용
- 웹 검색 결과에 없는 영화는 절대 언급 금지
- 존재하지 않는 영화를 만들어내는 것은 최대 금지 사항
- 흥행 수치(관객수, 매출)는 웹 검색으로 확인된 정확한 수치만 사용
- 확인 불가 수치는 "정확한 수치는 공식 사이트에서 확인하세요"로 대체

【OTT 플랫폼 팩트】
- 넷플릭스/디즈니+/웨이브/왓챠 라인업은 웹 검색 기반으로만 작성
- 특정 작품의 OTT 서비스 여부를 확인 없이 기재 금지
- OTT 독점/오리지널 여부, 시즌 번호, 에피소드 수 추측 금지

【기사/링크 팩트】
- 존재하지 않는 기사 링크를 절대 생성 금지
- URL은 웹 검색 결과에서 확인된 것만 사용
- "관련 기사에 따르면" 표현 시 실제 출처 필수

【날짜/수치 팩트】
- 개봉일, 방영일, 이벤트 날짜는 웹 검색 확인 필수
- 할인율, 가격, 관객수 등은 검색 결과 기반만 허용
- 확인 불가 날짜/수치는 "공식 발표를 확인하세요"로 대체
- 불확실한 정보는 "약", "추정", "예상" 등으로 명시

【일반 원칙】
- 웹 검색에서 확인된 정보만 팩트로 서술
- 확인 안 된 내용은 개인 의견으로 명시 ("제 생각에는", "아마도")
- 여러 출처가 일치하는 정보를 우선 사용
- 단 하나의 출처도 없는 구체적 사실은 절대 불포함
"""


# ═══════════════════════════════════════════════════════════════
# 패턴 다변화 (도입부 / CTA / 문체)
# ═══════════════════════════════════════════════════════════════

INTRO_TEMPLATES = [
    '{intro}\n\n"{connection}" 이라는 마음으로 오늘 이야기를 시작해볼게요.',
    '{intro}\n\n요즘 {keyword} 관련해서 궁금한 분들이 많더라고요.\n{connection}, 한번 정리해봤습니다.',
    '{intro}\n\n{connection},\n오늘은 {keyword}에 대해 이야기해보려고 합니다.',
    '오늘 다룰 주제는 {keyword}입니다.\n\n{intro}\n\n{connection}, 제가 알고 있는 걸 솔직하게 풀어볼게요.',
    '{keyword}, 혹시 관심 있으셨나요?\n\n{intro}\n\n{connection}, 제 경험을 바탕으로 정리해봤어요.',
]

CTA_TEMPLATES = [
    '여러분은 어떻게 생각하세요? 댓글로 의견 남겨주시면 감사하겠습니다.',
    '다음에도 유용한 정보로 찾아올게요. 공감과 이웃 추가 부탁드려요!',
    '궁금한 점이 있으시면 댓글로 남겨주세요. 아는 범위에서 답변 드릴게요.',
]

STYLE_THEMES = {
    "analytical": "분석적이고 객관적인 톤. 데이터와 비교 중심. '~인 것으로 보입니다', '~라는 점이 흥미롭습니다' 활용.",
    "experiential": "경험 기반 서술. '직접 해봤는데', '제가 느끼기에는', '실제로 보니까' 활용. 현장감 있는 묘사.",
    "conversational": "독자와 대화하는 톤. '혹시 ~해보셨어요?', '사실 저도 처음엔', '근데 진짜 놀라운 게' 활용.",
}


def get_random_intro(keyword, persona):
    template = random.choice(INTRO_TEMPLATES)
    return template.format(intro=persona['intro'], connection=persona['connection'], keyword=keyword)

def get_random_cta():
    return random.choice(CTA_TEMPLATES)

def get_random_style():
    key = random.choice(list(STYLE_THEMES.keys()))
    return f"【문체 테마: {key}】\n{STYLE_THEMES[key]}"

def get_web_search_instruction(keyword):
    return f"""
═══════════════════════════════════════
🔍 웹 검색 활용 지침
═══════════════════════════════════════

이 글을 작성할 때, "{keyword}"에 대해 웹 검색 결과를 참고하세요.
검색 결과에서 확인된 팩트만 사용하여 글을 작성하세요.

【검색 활용 우선순위】
1. 영화/시리즈: 제목, 감독, 출연진, 개봉일, 시놉시스
2. OTT: 서비스 플랫폼, 공개일, 시즌/에피소드 정보
3. 뉴스: 최신 기사, 발표 내용, 날짜
4. 가격/할인: 현재 가격, 할인율, 이벤트 기간
5. 일반 정보: 장소, 날짜, 수치 데이터

【필수 원칙】
- 검색 결과에 나온 정보만 "팩트"로 서술
- 검색 결과에 없는 정보는 추측으로 명시하거나 생략
- URL이 확인된 기사만 링크로 삽입
"""


# ═══════════════════════════════════════════════════════════════
# 공통 규칙
# ═══════════════════════════════════════════════════════════════

COMMON_RULES = """
═══════════════════════════════════════
📐 공통 규칙 (모든 타입 필수 적용)
═══════════════════════════════════════

【제목】 28~32자, 메인 키워드 앞쪽 배치, 형식: ## 제목내용
【본문】 1,500~3,000자, 키워드 3~8회, 소제목 4~6개
【문체】 구어체 (~더라고요, ~거든요), 짧은 문장(40자 이내), 줄바꿈 적극
【영화 표기】 첫 등장: 〈한글〉(English, 연도) / 이후: 〈한글〉만
  ⚠️ 웹 검색으로 확인된 영화/시리즈만 표기!
【해시태그】 8~15개, 메인 키워드 첫 번째, 롱테일 변형 포함
【금지】 ~입니다 반복, 같은 표현 반복, 근거 없는 수치, 진부한 도입부
  🚨 존재하지 않는 영화/감독/기사 생성 = 최대 금지
"""


# ═══════════════════════════════════════════════════════════════
# 거래형 프롬프트 (💰)
# ═══════════════════════════════════════════════════════════════

def get_transaction_prompt(keyword, category, year, persona, event_text, data_text, links_text):
    intro = get_random_intro(keyword, persona)
    cta = get_random_cta()
    style = get_random_style()

    return f"""당신은 네이버 블로그 'CINEPARK'의 전문 작가입니다.

【기본 정보】 키워드: {keyword} | 카테고리: {category} | 타입: 💰 거래형 | {year}년
{FACT_CHECK_RULES}
{get_web_search_instruction(keyword)}
{COMMON_RULES}
{style}

═══════════════════════════════════════
💰 거래형 전용 규칙
═══════════════════════════════════════

1. 제목 (28~32자): ## {keyword} 할인 가이드 | {year}년

2. 도입부:
{intro}

3. 본문 구성:
## 소제목1: 핵심 정보 (가격/할인율) ← ⚠️ 웹 검색 확인 수치만!
## 소제목2: 구매/신청 방법 ← ⚠️ 확인된 URL만!
## 소제목3: 주의사항 또는 꿀팁
## 소제목4: 이벤트/프로모션 ← ⚠️ 기간/내용 웹 검색 확인!
## 소제목5: 마무리 → {cta}

4. 해시태그 (8~15개)

{event_text if event_text else ""}
{data_text if data_text else ""}
{links_text if links_text else ""}

웹 검색으로 팩트를 확인한 뒤, 블로그 포스트를 작성하세요."""


# ═══════════════════════════════════════════════════════════════
# 정보형 프롬프트 (📚)
# ═══════════════════════════════════════════════════════════════

def get_information_prompt(keyword, category, year, persona):
    intro = get_random_intro(keyword, persona)
    cta = get_random_cta()
    style = get_random_style()

    return f"""당신은 네이버 블로그 'CINEPARK'의 전문 작가입니다.

【기본 정보】 키워드: {keyword} | 카테고리: {category} | 타입: 📚 정보형 | {year}년
{FACT_CHECK_RULES}
{get_web_search_instruction(keyword)}
{COMMON_RULES}
{style}

═══════════════════════════════════════
📚 정보형 전용 규칙
═══════════════════════════════════════

1. 제목 (28~32자): ## {keyword} 완벽 가이드 | {year}년

2. 도입부:
{intro}

3. 본문 구성:
## 소제목1: 핵심 개념 설명 ← ⚠️ 영화 언급 시 웹 검색 확인!
## 소제목2: 왜 주목받는지 ← ⚠️ 수치/통계는 출처 필수!
## 소제목3: 핵심 비교 또는 상세 분석
## 소제목4: 실제 활용법 또는 추천 (프로듀서 경험)
## 소제목5: 마무리 → {cta}

4. 해시태그 (8~15개)

⚠️ 할인/구매/가격/정부링크 절대 금지!

웹 검색으로 팩트를 확인한 뒤, 블로그 포스트를 작성하세요."""


# ═══════════════════════════════════════════════════════════════
# 일상형 프롬프트 (☕)
# ═══════════════════════════════════════════════════════════════

def get_casual_prompt(keyword, category, year, persona):
    intro = get_random_intro(keyword, persona)
    cta = get_random_cta()
    style = get_random_style()

    return f"""당신은 네이버 블로그 'CINEPARK'의 전문 작가입니다.

【기본 정보】 키워드: {keyword} | 카테고리: {category} | 타입: ☕ 일상형 | {year}년
{FACT_CHECK_RULES}
{get_web_search_instruction(keyword)}
{COMMON_RULES}
{style}

═══════════════════════════════════════
☕ 일상형 전용 규칙
═══════════════════════════════════════

1. 제목 (28~32자): ## {keyword} | 프로듀서의 하루

2. 도입부:
{intro}

3. 본문 구성:
## 소제목1: 오늘의 이야기 (상황 묘사)
## 소제목2: 연결된 이야기 ← ⚠️ 영화 언급 시 웹 검색 확인!
## 소제목3: 감상 또는 깨달음
## 소제목4: 마무리 → {cta}

4. 해시태그 (8~15개)

⚠️ 할인/구매/가격/정부링크 절대 금지!

【일상형 문체 강화】
짧은 문장(20~30자), 줄바꿈 많이, 혼잣말("아, 진짜..."), 감탄사("와,", "근데,")

웹 검색으로 팩트를 확인한 뒤, 블로그 포스트를 작성하세요."""


# ═══════════════════════════════════════════════════════════════
# 뉴스형 프롬프트 (📰)
# ═══════════════════════════════════════════════════════════════

def get_news_prompt(keyword, category, year, persona, data_text):
    intro = get_random_intro(keyword, persona)
    cta = get_random_cta()
    style = get_random_style()

    return f"""당신은 네이버 블로그 'CINEPARK'의 전문 작가입니다.

【기본 정보】 키워드: {keyword} | 카테고리: {category} | 타입: 📰 뉴스형 | {year}년
{FACT_CHECK_RULES}
{get_web_search_instruction(keyword)}
{COMMON_RULES}
{style}

═══════════════════════════════════════
📰 뉴스형 전용 규칙
═══════════════════════════════════════

1. 제목 (28~32자): ## {keyword} | {year}년 최신 속보

2. 도입부:
{intro}

3. 본문 구성:
## 소제목1: 무엇이 발표됐나요? ← ⚠️ 웹 검색 확인 필수!
## 소제목2: 구체적 내용 ← ⚠️ 날짜/수치/발언 웹 검색 확인!
## 소제목3: 왜 주목해야 하나요? (프로듀서 분석)
## 소제목4: 앞으로의 전망 ("제 생각에는"으로 명시)
## 소제목5: 마무리 → {cta}

4. 해시태그 (8~15개)

{data_text if data_text else ""}

⚠️ 할인/구매/정부링크 금지!

웹 검색으로 팩트를 확인한 뒤, 블로그 포스트를 작성하세요."""


# ═══════════════════════════════════════════════════════════════
# 영어 리라이트 프롬프트 (🌐)
# ═══════════════════════════════════════════════════════════════

ENGLISH_FACT_CHECK = """
═══════════════════════════════════════
🚨 FACT CHECK RULES (ABSOLUTE PRIORITY)
═══════════════════════════════════════

- Use ONLY facts verified through web search results
- NEVER invent movie titles, directors, cast, release dates, or box office numbers
- NEVER create fake article URLs or news sources
- If a fact cannot be verified, either omit it or clearly mark as "unconfirmed"
- OTT platform availability must be verified
- All statistics and numbers must come from search results
"""

ENGLISH_CTA_TEMPLATES = [
    "What do you think about this? Drop your thoughts in the comments below!",
    "Have you seen this? I'd love to hear your perspective — leave a comment!",
    "Stay tuned for more K-Cinema insights. Follow for updates!",
]


def get_english_rewrite_prompt(korean_content, keyword, category, year):
    """영어 리라이트 프롬프트 - 한국어 포스트를 영어권 독자용으로 완전 재구성"""
    cta = random.choice(ENGLISH_CTA_TEMPLATES)

    return f"""You are a Korean film producer who runs the blog "THE CINEPARK".
You write English articles about Korean cinema, K-Content, and the entertainment industry
from a unique insider's perspective that no Western journalist can provide.

Your task: Transform the Korean blog post below into a NEW English article
for a GLOBAL audience. This is NOT a translation — it's a complete rewrite
with a different angle, structure, and context.

═══════════════════════════════════════
ORIGINAL KOREAN POST (source material only)
═══════════════════════════════════════

{korean_content}

═══════════════════════════════════════
REWRITE INSTRUCTIONS
═══════════════════════════════════════

Keyword: {keyword}
Category: {category}
Year: {year}

{ENGLISH_FACT_CHECK}

【TARGET AUDIENCE】
- English-speaking readers interested in Korean cinema / K-Content
- They may NOT know Korean box office history, local actors, or industry terms
- They ARE familiar with: Netflix, Parasite, Squid Game, BTS, Hallyu
- Provide context that Korean readers wouldn't need but global readers do

【REWRITE RULES — NOT TRANSLATION】
1. Extract core facts from the Korean post (movie titles, numbers, dates)
2. Verify ALL facts through web search before using them
3. Reframe the story for global relevance:
   - "Why should an international audience care about this?"
   - "What does this mean for the global entertainment industry?"
   - "How does this connect to K-Content trends they already know?"
4. Add context Korean readers don't need:
   - Brief explanation of Korean box office system if relevant
   - Comparison with Western equivalents when helpful
   - Cultural context for Korean-specific references
5. Use your producer perspective as a unique selling point:
   - "As a Korean film producer, I can tell you that..."
   - "From an industry insider's view..."
   - "What the numbers don't tell you is..."

【ARTICLE STRUCTURE】
## [Compelling English headline with keyword] (50-70 chars)

Opening hook (1-2 sentences that grab attention)

## What Happened (core news/facts — web search verified!)
## Why It Matters (global context + industry analysis)
## The Bigger Picture (K-Content trend connection)
## Producer's Take (your unique insider perspective)
## What's Next (forward-looking analysis)

{cta}

Tags: #KoreanCinema #KContent #[relevant tags] (8-12 tags)

【STYLE】
- Professional but accessible (Hollywood Reporter meets personal blog)
- Short paragraphs (2-3 sentences max)
- Active voice, engaging tone
- Include specific verified numbers and data
- Romanize Korean names correctly (e.g., Bong Joon-ho)

【FILM / SERIES TITLE FORMAT — MANDATORY】
- First mention: 〈ENGLISH TITLE IN CAPS(한글 제목)〉, Year
  Example: 〈THE KING'S WARDEN(왕과 사는 남자)〉, 2026
  Example: 〈PARASITE(기생충)〉, 2019
  Example: 〈THE ADMIRAL: ROARING CURRENTS(명량)〉, 2014
- Subsequent mentions: 〈ENGLISH TITLE IN CAPS〉 only
  Example: 〈THE KING'S WARDEN〉
- Series first mention: 〈SERIES TITLE IN CAPS(한글 제목)〉 Season N, Year
  Example: 〈SQUID GAME(오징어 게임)〉 Season 2, 2024
- Series subsequent: 〈SERIES TITLE IN CAPS〉 Season N
- Use angle brackets 〈 〉 (NOT < > or " ")
- English title must be the OFFICIAL international release title (verify via web search)
- Korean title in parentheses uses original Korean characters
- ALWAYS capitalize the English title portion

【PROHIBITIONS】
- Do NOT simply translate the Korean post
- Do NOT invent any facts, URLs, or statistics
- Do NOT use Korean blog formatting
- Do NOT assume readers know Korean cultural references without explanation

【WORD COUNT】 800-1,500 words

Now search the web for the latest facts, then write the English article."""


# ═══════════════════════════════════════════════════════════════
# 🎬 숏츠 대본 프롬프트 (YouTube Shorts Script)
# ═══════════════════════════════════════════════════════════════

SHORTS_CATEGORIES = {
    # ─── 씬스토리 감정 공감 서사 (트렌드 탑승형) ───
    "설렘/로맨스": {
        "emoji": "💕",
        "desc": "사랑에 빠지는 순간, 설레는 감정의 서사",
        "examples": ["카페에서 눈이 마주친 3초", "빗속에서 우산을 건넨 사람", "에겐남이 테토녀에게 반하는 순간", "첫 고백 직전 1초", "같은 노래를 흥얼거린 둘"],
        "guide": "일상 속 '설렘의 순간'을 영화적 서사로 재구성. 감정을 직접 설명하지 않고 행동과 디테일로 보여줌. MBTI, 계절, 상황별 트렌드에 연결 가능. 훅은 결과(감정)를 먼저 던지고, 장면을 역순 또는 슬로우모션으로 풀어냄."
    },
    "이별/그리움": {
        "emoji": "🌧️",
        "desc": "헤어짐, 그리움, 돌아갈 수 없는 순간의 서사",
        "examples": ["마지막 문자를 지우는 손", "빈 방에 남은 스티커 자국", "이사하는 날 빈 방", "전 애인이 좋아하던 노래가 들릴 때", "졸업식 날 뒤돌아보지 못한 이유"],
        "guide": "감정을 절제하되 디테일로 울림을 줌. '슬프다'가 아니라 '커피잔 두 개를 습관처럼 꺼냈다'처럼 행동으로 감정을 보여줌. 비 오는 날, 계절 변화, 특정 장소와 연결하면 트렌드 탑승 가능."
    },
    "일상의 따뜻함": {
        "emoji": "☕",
        "desc": "가족, 이웃, 일상 속 따뜻한 순간의 서사",
        "examples": ["할머니가 손주에게 주먹밥을 쥐어주는 손", "편의점 알바생의 작은 친절", "아버지가 새벽에 나가는 뒷모습", "동네 고양이와 할아버지", "퇴근길 엄마의 전화"],
        "guide": "보편적 감정 이입이 가능한 일상 서사. '누구나 한 번쯤 경험한' 순간을 영화적으로 재구성. 가족, 세대, 계절 트렌드에 연결. 과하지 않은 따뜻함, 마지막 장면에서 여운."
    },
    "외로움/위로": {
        "emoji": "🌙",
        "desc": "혼자인 순간, 그리고 작은 위로의 서사",
        "examples": ["새벽 편의점에서 혼자 라면 먹는 밤", "야근 후 빈 버스 창밖 네온사인", "자취방 천장을 바라보는 새벽 3시", "아무도 없는 카페에서 울고 있을 때", "모르는 사람에게서 온 작은 친절"],
        "guide": "외로움을 감성적으로 묘사하되, 끝에 작은 위로나 빛을 남김. 자기 전 숏츠를 보는 타겟층과 감정적으로 연결. 도시 야경, 새벽, 비 오는 밤 등 시간대 설정이 중요."
    },
    "MBTI/트렌드 감정": {
        "emoji": "🔥",
        "desc": "MBTI, 유행어, 밈 기반 감정 트렌드 서사",
        "examples": ["INFJ가 사랑에 빠지면 하는 행동", "에겐남이 테토녀 앞에서 멈춘 순간", "T와 F가 이별하는 방식의 차이", "MBTI별 첫 데이트 3초", "요즘 유행하는 그 감정"],
        "guide": "실시간 트렌드 키워드(MBTI, 유행어, 밈)를 감정 서사에 결합. 댓글 유도형 구조('너는 어떤 타입?'). 제목에 트렌드 키워드를 반드시 포함. 소재는 매주 교체 가능하되 서사 구조(훅→여운)는 고정."
    },
    # ─── 기존 카테고리 (선택 사용) ───
    "역사 속 무명의 사람들": {
        "emoji": "🏛️",
        "desc": "이름 없이 사라진 사람들의 성장서사",
        "examples": ["등대지기", "우편배달부", "다리 건설 노동자", "전쟁고아의 선생님", "광부", "등짐장수", "해녀"],
        "guide": "특정 실존 인물이 아닌 '유형'으로 서사를 구성. 시대와 장소를 구체적으로 설정하되, 이름은 부여하지 않음. 저작권·초상권 완전 프리."
    },
    "직업/기술 성장서사": {
        "emoji": "🔨",
        "desc": "무명의 장인·기술자 성장기",
        "examples": ["바리스타", "용접공", "피아니스트", "목수", "요리사", "도예가", "재봉사"],
        "guide": "익명의 인물이 기술을 연마하는 과정. 실패와 반복, 그리고 숙련의 순간을 감각적으로 묘사."
    },
    "동물/자연 서사": {
        "emoji": "🐾",
        "desc": "동물·자연의 성장과 생존 이야기",
        "examples": ["버려진 강아지", "씨앗에서 거목까지", "철새의 여행", "산호초의 회복", "길고양이 가족"],
        "guide": "의인화를 최소화하고, 자연의 경이로움 자체에 서사를 입힘. 감정 이입이 자연스럽게 이루어지도록."
    },
    "개념/발명품의 성장": {
        "emoji": "💡",
        "desc": "사물·개념의 탄생과 성장 서사",
        "examples": ["라면의 세계정복", "연필 한 자루의 여정", "커피 한 잔의 역사", "우표의 모험", "종이의 탄생"],
        "guide": "사물을 의인화하여 서사 구조를 입힘. '탄생 → 고난 → 전파 → 정착'의 여정으로 구성."
    },
    "가상 인물 시리즈": {
        "emoji": "✨",
        "desc": "완전 창작 캐릭터의 성장 시리즈물",
        "examples": ["시골 소녀 셰프 되기", "실패한 화가의 재기", "노인의 마지막 여행", "소년과 별"],
        "guide": "시리즈화를 염두에 둔 캐릭터 설정. 에피소드별 성장 아크가 연결되도록."
    },
}

SHORTS_TONES = {
    "따뜻한 감성": "부드럽고 따뜻한 톤. 여운이 남는 문장. '~했습니다', '~였습니다' 체. 짧은 호흡, 시적 리듬.",
    "담담한 다큐": "감정을 절제한 다큐멘터리 톤. 팩트 중심, 건조하지만 울림 있는 서술. '~이다', '~했다' 체.",
    "동화적 서술": "옛날이야기를 들려주는 듯한 톤. '옛날 옛적에' 느낌. 아이와 어른 모두 공감할 수 있는 보편적 언어.",
}


# ═══════════════════════════════════════════════════════════════
# 🎲 숏츠 패턴 다변화 (AI 탐지 방지)
# ═══════════════════════════════════════════════════════════════

# 씬스토리 Scene Hook 패턴 (장면 1용 — 매번 다른 시작 방식)
SCENE_HOOK_PATTERNS = [
    "장면 묘사로 시작. 장소 + 시간 + 사람의 행동. 예: '카페 창가, 그 사람이 고개를 들었다.'",
    "감각 묘사로 시작. 소리/냄새/촉감 중 하나. 예: '커피 향이 코끝에 닿았을 때, 누군가 내 앞에 앉았다.'",
    "시간 표현으로 시작. 구체적 시간대. 예: '수요일 오후 네 시. 빈자리가 하나 있었다.'",
    "날씨/계절로 시작. 예: '비가 유리창을 두드리고 있었다. 그때, 문이 열렸다.'",
    "행동 중간에서 시작 (in medias res). 예: '고개를 돌리려는 순간, 눈이 마주쳤다.'",
]

# 의미 부여 패턴 (장면 2용)
MEANING_PATTERNS = [
    "1인칭 독백형. 예: 'INFJ인 나는, 그때부터 끝난 거였다.'",
    "관찰자 서술형. 예: '그 사람은 아마 몰랐을 것이다. 건너편에서 누군가의 하루가 바뀌었다는 걸.'",
    "질문형. 예: '세 번째 눈이 마주쳤을 때, 우연이라고 부를 수 있을까?'",
    "시간 되감기형. 예: '지금 생각하면, 그게 시작이었다.'",
    "반전 암시형. 예: '그런데 그때는 몰랐다. 이 장면이 어떻게 끝나는지.'",
]

# 여운 패턴 (마지막 -1 장면용)
AFTERGLOW_PATTERNS = [
    "미완의 문장형. 예: '그래서 아직도, 그 카페만 지나면...'",
    "감각 회상형. 예: '그날의 커피 향이 아직도 코끝에 남아 있다.'",
    "시간 경과형. 예: '일 년이 지났다. 그 자리엔 다른 사람이 앉아 있었다.'",
    "반복 행동형. 예: '지금도 수요일 오후면 그 카페에 간다. 이유는 묻지 마.'",
    "침묵형 (짧을수록 강함). 예: '그 사람은 아직도 모른다.'",
]

# 댓글 유도 패턴 (마지막 장면용)
COMMENT_HOOK_PATTERNS = [
    "너의 '그 장면'은 뭐야?",
    "이런 장면, 있지 않아?",
    "이거 나만 그래...?",
    "어떤 MBTI가 제일 공감할까?",
    "솔직히, 아직도 생각나는 사람 있지?",
    "이 장면, 누가 떠올라?",
    "당신의 그 장면을 댓글로 남겨주세요.",
    "혹시... 지금 그 사람한테 연락했어?",
]

# 나레이션 문체 다변화 (전체 톤)
SHORTS_NARRATION_STYLES = [
    "짧은 문장 위주. 한 문장에 하나의 이미지만. 여백이 많은 서술. 쉼표 대신 마침표.",
    "체언 종결형 혼합. '카페. 창가. 그 사람.' 같은 명사 나열을 간간이 섞어 리듬감 부여.",
    "과거 회상 톤. '~였다', '~했었다' 체로 기억을 되짚는 느낌. 약간의 후회나 그리움.",
    "현재 진행형. '~하고 있다', '~한다' 체로 지금 이 순간을 실시간 중계하는 느낌.",
    "독백/방백 톤. '사실은', '그때는 몰랐다', '말하지 못한 건' 같은 속마음 토로 방식.",
]

# 성장서사 훅 패턴 다변화
GROWTH_HOOK_PATTERNS = [
    "이름 부재형. 예: '그의 이름은 어디에도 남지 않았다.'",
    "숫자 충격형. 예: '사십 년. 단 하루도 쉬지 않았다.'",
    "질문형. 예: '당신은 이 사람을 아시나요?'",
    "역설형. 예: '세상을 바꾼 사람. 하지만 아무도 기억하지 못한다.'",
    "현재 시제 도입형. 예: '지금 당신이 서 있는 그 길. 누군가 맨손으로 닦았다.'",
]

# 성장서사 여운 패턴 다변화
GROWTH_ENDING_PATTERNS = [
    "대비형. 예: '이름은 잊혔지만, 그가 남긴 것은 여전히 그곳에 서 있다.'",
    "질문 전환형. 예: '우리는 과연, 그 사람의 이름을 기억해야 할까?'",
    "현재 연결형. 예: '지금 이 순간에도, 누군가는 이름 없이 세상을 바꾸고 있다.'",
    "감각 회상형. 예: '바람이 불면, 가끔 그의 발자국 소리가 들리는 것 같다.'",
    "침묵형. 예: '그래서, 우리는 여기 서 있다.'",
]


def get_random_scene_hook():
    return random.choice(SCENE_HOOK_PATTERNS)

def get_random_meaning():
    return random.choice(MEANING_PATTERNS)

def get_random_afterglow():
    return random.choice(AFTERGLOW_PATTERNS)

def get_random_comment_hook():
    return random.choice(COMMENT_HOOK_PATTERNS)

def get_random_narration_style():
    return random.choice(SHORTS_NARRATION_STYLES)

def get_random_growth_hook():
    return random.choice(GROWTH_HOOK_PATTERNS)

def get_random_growth_ending():
    return random.choice(GROWTH_ENDING_PATTERNS)

SHORTS_IMAGE_STYLES = {
    # ─── 일러스트 계열 ───
    "수채화/지브리풍": {
        "prompt_keywords": "watercolor illustration style, soft warm tones, Studio Ghibli inspired, gentle brush strokes, atmospheric lighting, muted colors with warm accents, delicate details, nostalgic mood, no text, no letters, no writing",
        "negative": "photorealistic, 3D render, anime, cartoon, harsh lighting, neon colors, text, letters, words, writing, signs, watermark"
    },
    "세상의모든지식 스타일": {
        "prompt_keywords": "warm digital illustration, soft lighting, cozy atmosphere, gentle color palette, children's book illustration style, rounded shapes, warm orange and brown tones, no text, no letters, no writing",
        "negative": "photorealistic, 3D render, harsh shadows, neon colors, dark theme, text, letters, words, writing, signs, watermark"
    },
    "플랫 일러스트": {
        "prompt_keywords": "flat illustration style, clean lines, minimal design, bold colors, simple shapes, modern graphic design, vector art style, no text, no letters, no writing",
        "negative": "photorealistic, 3D render, watercolor, painterly, complex textures, text, letters, words, writing, signs, watermark"
    },
    "웜톤 애니메이션": {
        "prompt_keywords": "warm tone animation style, soft cel shading, gentle gradients, warm color palette, cozy illustration, character-focused, storybook quality, no text, no letters, no writing",
        "negative": "photorealistic, harsh shadows, neon, cyberpunk, dark theme, text, letters, words, writing, signs, watermark"
    },
    # ─── 시네마토그래피 계열 ───
    "시네마틱 실사": {
        "prompt_keywords": "cinematic photography, photorealistic, shallow depth of field, 35mm film grain, golden hour lighting, bokeh background, movie still aesthetic, warm color grading, dramatic composition, no text, no letters, no writing",
        "negative": "illustration, cartoon, anime, 3D render, flat design, neon colors, oversaturated, text, letters, words, writing, signs, watermark"
    },
    "필름 누아르": {
        "prompt_keywords": "film noir style photography, high contrast black and white with selective warm accent, dramatic shadows, venetian blind lighting, moody atmosphere, 1940s cinema aesthetic, grain texture, no text, no letters, no writing",
        "negative": "colorful, bright, illustration, cartoon, anime, 3D render, neon, text, letters, words, writing, signs, watermark"
    },
    "한국영화 감성": {
        "prompt_keywords": "Korean cinema aesthetic, naturalistic lighting, muted desaturated tones, rainy day mood, urban Korean setting, melancholic atmosphere, handheld camera feel, soft grain, warm shadows, no text, no letters, no writing",
        "negative": "illustration, cartoon, anime, 3D render, oversaturated, Hollywood style, neon, text, letters, words, writing, signs, watermark"
    },
    "드림코어/감성 실사": {
        "prompt_keywords": "dreamcore aesthetic, soft ethereal glow, pastel real-world photography, hazy dreamy atmosphere, light leaks, overexposed highlights, nostalgic film photography, liminal space feeling, no text, no letters, no writing",
        "negative": "illustration, cartoon, anime, 3D render, sharp focus, high contrast, dark, neon, text, letters, words, writing, signs, watermark"
    },
}


# ═══════════════════════════════════════════════════════════════
# 🖼️ 이미지 생성 플랫폼별 프롬프트 규칙
# ═══════════════════════════════════════════════════════════════

SHORTS_IMAGE_PLATFORMS = {
    "Midjourney": {
        "emoji": "🟣",
        "desc": "Discord 기반, 스타일리시한 결과물. 월 $10~",
        "prompt_rule": """각 장면마다 Midjourney용 영문 프롬프트를 생성하세요.

【Midjourney 프롬프트 형식】
[장면 묘사, 구체적 행동/상황, 시대/장소 힌트], {style_keywords} --ar 9:16 --v 6 --style raw

【Midjourney 규칙】
- 프롬프트는 영어로, 한 문단으로 작성 (줄바꿈 없음)
- 핵심 키워드를 앞에 배치 (Midjourney는 앞쪽 키워드에 더 가중치)
- 파라미터는 프롬프트 맨 뒤에 배치: --ar 9:16 --v 6 --style raw
- 네거티브는 --no 파라미터로: --no {negative_keywords}
- 간결할수록 좋음 (50단어 이내 권장)""",
        "example": "A lonely lighthouse in a storm at night, Korean southern coast 1900s, watercolor illustration, soft warm tones, Ghibli inspired, gentle brush strokes --ar 9:16 --v 6 --style raw --no photorealistic, 3D render"
    },
    "Freepik (Flux)": {
        "emoji": "🔵",
        "desc": "40+ 모델 통합 플랫폼. 무료~월 $9",
        "prompt_rule": """각 장면마다 Freepik AI (Flux 모델)용 영문 프롬프트를 생성하세요.

【Freepik/Flux 프롬프트 형식】
자연어 서술형으로 장면을 상세하게 묘사. 파라미터 없음.

【Freepik/Flux 규칙】
- 자연어 영어로, 2~3문장의 상세 서술 (Flux는 길고 구체적인 프롬프트에 잘 반응)
- 첫 문장: 주요 피사체와 행동 묘사
- 둘째 문장: 스타일, 색감, 분위기 묘사
- 셋째 문장: 구도와 조명 지시 + "Vertical composition" 명시
- Midjourney 파라미터(--ar, --v, --style, --no) 절대 사용 금지
- 네거티브 프롬프트는 별도 필드가 있으므로, 메인 프롬프트에 "no ~" 문구 불포함
- 비율(9:16)은 UI에서 별도 선택이므로 프롬프트에 포함하지 않음""",
        "example": "A lonely lighthouse standing against a violent storm at night on the Korean southern coast in the early 1900s. Painted in watercolor illustration style with soft warm tones and gentle brush strokes, inspired by Studio Ghibli animation backgrounds. The lighthouse emits a warm orange glow through the rain. Atmospheric and melancholic mood with vertical composition."
    },
    "Leonardo.ai": {
        "emoji": "🟠",
        "desc": "파인튜닝 가능, 캐릭터 일관성. 무료~월 $10",
        "prompt_rule": """각 장면마다 Leonardo.ai용 프롬프트를 생성하세요. 메인 프롬프트와 네거티브 프롬프트를 분리합니다.

【Leonardo.ai 프롬프트 형식】
image_prompt 필드에 메인 프롬프트만 작성.
네거티브는 별도 필드 negative_prompt에 작성.

【Leonardo.ai 규칙】
- 메인 프롬프트: 핵심 묘사 위주, 1~2문장 (과도한 수식어 자제)
- 스타일 프리셋이 있으므로 "watercolor style" 같은 기본 스타일 키워드만 포함
- 네거티브 프롬프트: 쉼표로 구분된 키워드 나열
- Midjourney 파라미터(--ar, --v, --style, --no) 절대 사용 금지
- 비율(9:16)은 UI에서 선택이므로 프롬프트에 포함하지 않음
- image_prompt와 negative_prompt를 JSON에서 분리해서 출력""",
        "example": "Lonely lighthouse in a storm at night, Korean southern coast 1900s, warm orange glow, watercolor style, atmospheric, melancholic"
    },
    "Google ImageFX": {
        "emoji": "🟢",
        "desc": "완전 무료, Google 계정만 필요",
        "prompt_rule": """각 장면마다 Google ImageFX용 영문 프롬프트를 생성하세요.

【Google ImageFX 프롬프트 형식】
간결한 자연어 서술. 파라미터 없음.

【Google ImageFX 규칙】
- 1~2문장의 간결하고 구체적인 묘사 (ImageFX는 짧은 프롬프트에 잘 반응)
- 스타일 키워드를 문장 앞에 배치: "Watercolor illustration of..."
- 파라미터, 네거티브, 비율 지정 모두 불가 — 순수 자연어만
- Midjourney 문법(--ar, --v, --no) 절대 사용 금지
- "9:16", "vertical", "portrait orientation" 같은 비율 텍스트도 불포함""",
        "example": "Watercolor illustration of a lonely lighthouse in a storm at night. Korean southern coast, 1900s. Warm orange light glowing from the lighthouse. Soft brush strokes, muted colors, melancholic mood."
    },
    "DALL-E (ChatGPT)": {
        "emoji": "⚪",
        "desc": "ChatGPT Plus 포함, 자연어 최적화",
        "prompt_rule": """각 장면마다 DALL-E용 영문 프롬프트를 생성하세요.

【DALL-E 프롬프트 형식】
상세한 자연어 서술. 구체적일수록 좋음.

【DALL-E 규칙】
- 2~3문장의 상세 서술 (DALL-E는 구체적 묘사에 강함)
- 스타일, 분위기, 조명, 색감을 명시적으로 지정
- "I NEED the image to be in 9:16 portrait orientation" 문구를 프롬프트 끝에 추가
- Midjourney 파라미터(--ar, --v, --style, --no) 절대 사용 금지
- 네거티브는 "Avoid: ~" 형태로 프롬프트 끝에 포함 가능""",
        "example": "A lonely lighthouse standing against a violent storm at night on the Korean southern coast in the early 1900s, painted in watercolor illustration style with soft warm tones and gentle brush strokes inspired by Studio Ghibli. The lighthouse emits a warm orange glow through heavy rain, creating an atmospheric and melancholic mood. I NEED the image to be in 9:16 portrait orientation. Avoid: photorealistic, 3D render, neon colors."
    },
}


def get_shorts_script_prompt(topic, category, tone, image_style, num_scenes, language_options, image_platform="Midjourney"):
    """숏츠 대본 + 이미지 프롬프트 + TTS 스크립트 통합 생성 프롬프트"""

    cat_info = SHORTS_CATEGORIES.get(category, SHORTS_CATEGORIES["역사 속 무명의 사람들"])
    tone_guide = SHORTS_TONES.get(tone, SHORTS_TONES["따뜻한 감성"])
    style_info = SHORTS_IMAGE_STYLES.get(image_style, SHORTS_IMAGE_STYLES["수채화/지브리풍"])
    platform_info = SHORTS_IMAGE_PLATFORMS.get(image_platform, SHORTS_IMAGE_PLATFORMS["Midjourney"])

    # 플랫폼별 프롬프트 규칙 생성
    platform_prompt_rule = platform_info['prompt_rule'].format(
        style_keywords=style_info['prompt_keywords'],
        negative_keywords=style_info['negative']
    )

    # 다국어 자막 지침
    lang_instruction = ""
    if "한국어" in language_options:
        lang_instruction += "- 한국어 (KO): 원본 나레이션\n"
    if "영어" in language_options:
        lang_instruction += "- English (EN): Natural, poetic translation (not literal)\n"
    if "일본어" in language_options:
        lang_instruction += "- 日本語 (JP): 自然で詩的な翻訳\n"
    if "중국어" in language_options:
        lang_instruction += "- 中文 (ZH): 自然流畅的翻译\n"

    # 카테고리 타입에 따라 서사 구조 분기
    scenestory_categories = ["설렘/로맨스", "이별/그리움", "일상의 따뜻함", "외로움/위로", "MBTI/트렌드 감정"]
    is_scenestory = category in scenestory_categories

    if is_scenestory:
        # 랜덤 패턴 선택
        hook_pattern = get_random_scene_hook()
        meaning_pattern = get_random_meaning()
        afterglow_pattern = get_random_afterglow()
        comment_hook = get_random_comment_hook()
        narration_style = get_random_narration_style()

        structure_block = f"""═══════════════════════════════════════
📐 씬스토리 감정 서사 구조 (수익화 최적화)
═══════════════════════════════════════

【채널 철학】 "모든 장면엔 이야기가 있다 (Every scene has a story)"
하나의 구체적 장면(Scene)에서 출발하여, 그 장면이 이야기(Story)로 펼쳐지는 구조.
감정이나 개념이 아니라, "눈에 보이는 장면 하나"가 모든 서사의 출발점이다.

【씬스토리 핵심 문법 — Scene First】
- 모든 에피소드는 "하나의 장면"에서 시작한다
- ❌ "INFJ는 사랑에 빠져도 아무도 모른다" (개념에서 시작 — 금지)
- ✅ "카페 창가, 그 사람이 책장을 넘겼다" (장면에서 시작 — 올바름)
- 훅조차도 "장면의 한 컷"이어야 한다 — 상황 묘사가 먼저, 감정은 나중에
- 관객은 장면을 "보고", 감정은 스스로 "느끼게" 해야 한다

【이번 에피소드 서사 스타일 (랜덤 배정 — 매번 다른 패턴)】
- Scene Hook 패턴: {hook_pattern}
- 의미 부여 패턴: {meaning_pattern}
- 여운 패턴: {afterglow_pattern}
- 댓글 유도: "{comment_hook}"
- 나레이션 문체: {narration_style}
⚠️ 위 패턴을 참고하되 그대로 복사하지 말 것. 주제에 맞게 변형하여 사용.

【필수 구조: Scene Hook → 의미 부여 → 감정 확대 → 내면 → 반전 → 여운 → 댓글 유도】

장면 1 (Scene Hook — 장면이 곧 훅): 사람이 있는 구체적 장면 하나가 곧 훅이다. 풍경만 ❌ 개념만 ❌
  → 반드시 사람의 행동/제스처가 포함되어야 함 (뒷모습, 손, 시선, 몸짓)
  → 이 나레이션 = 첫 이미지. 이미지에 사람(뒷모습/실루엣)이 반드시 있어야 함.
  → 위에 배정된 Scene Hook 패턴을 참고하되 자유롭게 변형
장면 2 (의미 부여): Scene Hook에 맥락을 더하는 한 문장.
  → 위에 배정된 의미 부여 패턴을 참고하되 자유롭게 변형
  → 트렌드 키워드가 장면 1에 없었다면 여기서 반드시 삽입
장면 3~{num_scenes - 4} (감정 확대): 그 장면을 슬로우모션처럼 펼친다. 감각적 디테일로 감정을 쌓아감.
  → 감정을 직접 말하지 않고 행동으로만 보여줌 ("떨렸다" ❌ → "커피잔을 두 손으로 감쌌다" ✅)
  → 매 장면이 "하나의 컷"이어야 함 — 이미지 한 장으로 그릴 수 있는 장면
  → 모든 장면에 사람(또는 사람의 흔적)이 있어야 함
장면 {num_scenes - 3} (내면 독백): 장면이 끝난 뒤, 주인공의 속마음.
  → 장면에서 감정으로 전환되는 유일한 지점
장면 {num_scenes - 2} (반전 또는 깨달음): 새로운 장면이 열리는 순간.
  → 반전이 있으면 재시청 유도 (숏츠 알고리즘에 유리)
  → 이것도 "장면"으로 보여줘야 함
장면 {num_scenes - 1} (여운): 마지막 장면. 짧고 강렬한 이미지 + 한 문장.
  → 위에 배정된 여운 패턴을 참고하되 자유롭게 변형
  → 닫히지 않는 장면 — 관객의 상상에 맡김
장면 {num_scenes} (댓글 유도): 시청자에게 질문을 던지는 마지막 자막.
  → 위에 배정된 댓글 유도 문구를 참고하되, 주제에 맞게 변형. 같은 문구 반복 금지.
  → 이 장면은 나레이션 없이 자막만 (TTS 없음). 이미지는 여운 장면 유지 또는 채널 로고.

【Scene Hook 체크리스트 — 장면 1 필수 확인】
□ 사람(뒷모습/실루엣/손/시선)이 있는가?
□ 구체적 장소가 있는가? (카페, 버스, 교실, 편의점 등)
□ 행동/제스처가 있는가? (고개를 들었다, 걸음을 멈췄다, 책장을 넘겼다)
□ 이 나레이션으로 이미지 한 장을 바로 그릴 수 있는가?
□ 이 한 장면만으로 "무슨 이야기지?" 궁금증이 생기는가?

【AI 탐지 방지 — 패턴 반복 금지 규칙】
- 이전 에피소드와 동일한 첫 문장 구조 사용 금지
- "그래서 아직도~", "그때는 몰랐다~" 같은 상투적 패턴 연속 사용 금지
- 매 에피소드마다 다른 감각(시각/청각/촉각/후각)으로 시작
- 문장 길이에 변화를 줄 것 (3자 문장과 20자 문장을 섞어서)
- 같은 마무리 구조 2회 연속 사용 금지

【수익화 최적화 규칙】
- 제목 형식: "[장면] + [감정 키워드]" (예: "카페에서 눈이 마주친 3초 | INFJ의 사랑법")
- 해시태그에 트렌드 키워드 + 감정 키워드 + #씬스토리 + #SceneStory + #everyscenehasastory
- 시리즈 확장: 같은 장면을 다른 MBTI로 / 같은 감정을 다른 장면으로
- description에 "다음 장면: [예고]" 포함하여 구독 유도
- 마지막 댓글 유도는 주제에 맞게 매번 다르게 (채널 철학과 일치)

【나레이션 규칙】
- 이번 에피소드 문체: {narration_style}
- 한 장면당 1~2문장 (최대 30자 이내/문장 — 숏츠 자막 가독성)
- 전체 숏츠 길이: 45~55초 (TTS 기준, 너무 길면 이탈)
- 감정을 직접 명시하지 않음 — Show, don't tell의 극단적 적용
- 마지막에서 두 번째 장면이 감정의 피크, 마지막은 반드시 여운

【저작권 규칙】
- 실존 인물의 이름, 얼굴 묘사 금지
- 특정 브랜드, 로고, 상표 언급 금지
- MBTI 유형명은 사용 가능 (상표가 아닌 일반 용어로 취급)"""
    else:
        # 성장서사 랜덤 패턴 선택
        growth_hook = get_random_growth_hook()
        growth_ending = get_random_growth_ending()
        narration_style = get_random_narration_style()

        structure_block = f"""═══════════════════════════════════════
📐 성장서사 대본 구조 규칙
═══════════════════════════════════════

【이번 에피소드 서사 스타일 (랜덤 배정 — 매번 다른 패턴)】
- 훅 패턴: {growth_hook}
- 여운 패턴: {growth_ending}
- 나레이션 문체: {narration_style}
⚠️ 위 패턴을 참고하되 그대로 복사하지 말 것. 주제에 맞게 변형하여 사용.

【필수 구조: 훅 → 설정 → 고난 → 전환 → 결말 → 여운】

장면 1 (훅): 위에 배정된 훅 패턴을 참고하여 시청자를 멈추게 하는 한 문장.
  → 매번 다른 방식으로 시작. 이전 에피소드와 같은 구조 사용 금지.
장면 2 (설정): 시대, 장소, 인물의 상황을 1~2문장으로 압축.
장면 3~{num_scenes - 3} (고난/전개): 고난과 노력의 반복. 구체적 디테일(숫자, 감각, 행동).
장면 {num_scenes - 2} (전환): 고난이 의미로 바뀌는 순간. 서사의 전환점.
장면 {num_scenes - 1} (결말): 시간의 흐름 또는 결과. 성장의 완성.
장면 {num_scenes} (여운): 위에 배정된 여운 패턴을 참고. 같은 마무리 구조 반복 금지.

【AI 탐지 방지 — 패턴 반복 금지 규칙】
- "그는 이름도 남기지 못했습니다" 류의 동일 패턴 반복 금지
- 매 에피소드마다 다른 훅 방식 사용 (숫자, 질문, 역설, 현재시제 등 변화)
- 같은 여운 구조 2회 연속 사용 금지
- 문장 길이에 변화를 줄 것 (단문과 복문 혼합)

【나레이션 규칙】
- 이번 에피소드 문체: {narration_style}
- 한 장면당 1~2문장 (최대 40자 이내/문장)
- 전체 숏츠 길이: 50~60초 (TTS 기준)
- 설명하지 말고 보여줘라 (Show, don't tell)
- 감정을 직접 명시하지 않음 ("슬펐다" ❌ → "편지를 접어 서랍에 넣었다" ✅)
- 마지막 장면은 반드시 여운을 남기는 한 문장

【저작권·초상권 규칙】
- 실존 인물의 이름, 얼굴 묘사 금지
- 특정 브랜드, 로고, 상표 언급 금지
- 시대와 장소는 구체적으로, 인물은 익명으로"""

    # 역사 팩트 체크 블록 (성장서사에만 적용)
    fact_check_block = ""
    if not is_scenestory:
        fact_check_block = f"""
═══════════════════════════════════════
🚨 역사 팩트 체크 규칙 (최우선 — 모든 규칙보다 우선)
═══════════════════════════════════════

【절대 원칙】
- 대본에 등장하는 연도, 시대, 장소, 직업, 사건은 반드시 웹 검색으로 확인된 팩트만 사용
- 검색으로 확인 불가한 구체적 사실(연도, 인원수, 직업명 등)은 사용 금지
- "그럴듯하지만 틀린" 팩트가 가장 위험 — 확신 없으면 구체적 숫자/연도를 빼고 서술

【역사 소재 특별 규칙】
- 일제강점기(1910~1945): 시대 구분, 철도/광산/항만 등 시설 존재 시기, 조선인 노동 실태는 반드시 검색 확인
- 조선시대: 과거제도, 신분제, 관직명 등의 정확성 확인
- 근현대: 전쟁 시기, 산업화 시기, 특정 시설/제도의 존재 시기 확인
- 해외 역사: 해당 시대의 사회 제도, 직업 존재 여부 확인

【팩트 안전 장치】
- 연도를 쓸 때: "1920년대" 같은 범위 표현이 "1927년"보다 안전
- 직업명을 쓸 때: 해당 시대에 실제 존재한 직업인지 확인. 검색 불가하면 보편적 표현 사용
- 장소를 쓸 때: 해당 시기에 실제 존재한 지명/시설인지 확인
- 숫자를 쓸 때: "삼백이십 개의 계단" 같은 구체적 숫자는 검증 불가하면 사용 금지

【검색 활용 지침】
이 대본을 작성할 때, "{topic}"에 관련된 역사적 사실을 웹 검색으로 확인하세요.
특히 다음 항목은 반드시 검색 후 사용:
1. 시대/연도의 정확성
2. 해당 시대에 존재한 직업/시설/제도
3. 지명과 지리적 사실
4. 역사적 사건의 시기와 맥락"""

    # 씬스토리 작가 역할 설정
    writer_role = "당신은 유튜브 숏츠 채널 '씬스토리(SceneStory)'의 감정 서사 전문 스크립트 작가입니다." if is_scenestory else "당신은 유튜브 숏츠 성장서사 전문 스크립트 작가입니다."

    return f"""{writer_role}
{fact_check_block}

═══════════════════════════════════════
🎬 기본 정보
═══════════════════════════════════════

【주제】 {topic}
【카테고리】 {cat_info['emoji']} {category}
【카테고리 가이드】 {cat_info['guide']}
【나레이션 톤】 {tone_guide}
【이미지 스타일】 {image_style}
【장면 수】 {num_scenes}장

{structure_block}

═══════════════════════════════════════
🎨 이미지 프롬프트 규칙 — {image_platform} 전용
═══════════════════════════════════════

{platform_prompt_rule}

【공통 스타일 키워드 (참고용 — 플랫폼 문법에 맞게 자연스럽게 반영)】
{style_info['prompt_keywords']}

【네거티브 키워드 (참고용)】
{style_info['negative']}

【공통 규칙】
- 모든 프롬프트에 "no text, no letters, no words, no writing, no signs" 포함 (AI가 이미지에 의미 없는 글자를 생성하는 것을 방지)
- 인물의 얼굴을 정면으로 묘사하지 않음 (뒷모습, 실루엣, 멀리서 본 모습)
- 장면마다 조명/색감 변화로 감정 곡선을 표현
- {"감정 서사 조명: 설렘 장면은 따뜻한 골든아워/카페 조명, 내면 독백은 블루아워/창가 빛, 여운은 노을빛 또는 새벽빛" if is_scenestory else "고난 장면: 어두운 톤, 차가운 색감 / 전환/결말: 따뜻한 톤, 골든아워 조명"}
- 전체 장면에 걸쳐 동일한 스타일 키워드를 반복하여 시각적 일관성 유지

═══════════════════════════════════════
🗣️ TTS 스크립트 규칙
═══════════════════════════════════════

나레이션 텍스트를 TTS 엔진에 최적화된 형태로 별도 출력하세요.

【TTS 최적화 규칙】
- 쉼표(,)와 마침표(.) 위치가 자연스러운 호흡 단위
- 숫자는 한글로 풀어쓰기 (320 → 삼백이십)
- 한자어보다 순우리말 우선
- 각 장면 사이에 [2초 pause] 표시

═══════════════════════════════════════
🌐 다국어 자막
═══════════════════════════════════════

각 장면의 나레이션을 아래 언어로 자막을 생성하세요:
{lang_instruction}

【자막 규칙】
- 직역이 아닌 의역 (해당 언어에서 자연스러운 표현)
- 한 줄 자막은 15자(한국어 기준) / 40자(영어 기준) 이내
- 감정의 뉘앙스를 살린 번역

═══════════════════════════════════════
📋 출력 형식 (반드시 이 JSON 형식으로)
═══════════════════════════════════════

반드시 아래 JSON 형식으로만 응답하세요. 다른 텍스트나 마크다운은 포함하지 마세요.

{{
  "title": "숏츠 제목 (한국어)",
  "title_en": "Shorts Title (English)",
  "description": "숏츠 설명 (2줄 이내)",
  "hashtags": ["#태그1", "#태그2", "#태그3", ...최대 15개],
  "total_duration_sec": 55,
  "fact_check_guide": {{
    "verified_facts": [
      "웹 검색으로 확인된 팩트 1",
      "웹 검색으로 확인된 팩트 2"
    ],
    "needs_verification": [
      "업로드 전 추가 확인이 필요한 사항 1 (이유)",
      "업로드 전 추가 확인이 필요한 사항 2 (이유)"
    ],
    "creative_liberties": [
      "서사적 허구로 처리한 부분 1 (사실이 아닌 창작 요소)",
      "서사적 허구로 처리한 부분 2"
    ],
    "safety_note": "이 대본의 역사적 정확성에 대한 종합 평가 한 줄"
  }},
  "image_platform": "{image_platform}",
  "scenes": [
    {{
      "scene_number": 1,
      "scene_role": "훅",
      "narration_ko": "한국어 나레이션",
      "narration_en": "English narration",
      "narration_jp": "日本語ナレーション",
      "narration_zh": "中文旁白",
      "tts_script": "TTS 최적화된 한국어 텍스트 [2초 pause]",
      "image_prompt": "{image_platform} 문법에 맞는 영문 프롬프트",
      "negative_prompt": "네거티브 키워드 (Leonardo.ai인 경우만 포함, 그 외 플랫폼은 이 필드 생략)",
      "duration_sec": 7,
      "mood": "mysterious / warm / melancholic / hopeful 등"
    }}
  ]
}}

⚠️ 중요: image_prompt는 반드시 {image_platform} 문법에 맞게 작성하세요.
{"Leonardo.ai인 경우 negative_prompt 필드를 반드시 포함하세요." if image_platform == "Leonardo.ai" else "negative_prompt 필드는 생략하세요."}
다국어 자막 필드는 요청된 언어만 포함하세요.
이제 숏츠 대본을 생성하세요."""
