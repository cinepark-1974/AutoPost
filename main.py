import streamlit as st
import anthropic
import requests
from datetime import datetime, timedelta
import json
import re
from prompts import get_transaction_prompt, get_information_prompt, get_casual_prompt, get_news_prompt, get_english_rewrite_prompt

# ═══════════════════════════════════════════════════════════════
# 페이지 설정
# ═══════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="AutoPost v10.1",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ═══════════════════════════════════════════════════════════════
# 세션 상태 초기화
# ═══════════════════════════════════════════════════════════════

if 'post_history' not in st.session_state:
    st.session_state['post_history'] = []
if 'selected_keyword' not in st.session_state:
    st.session_state['selected_keyword'] = ''
if 'generated_result' not in st.session_state:
    st.session_state['generated_result'] = None


# ═══════════════════════════════════════════════════════════════
# API 키 관리
# ═══════════════════════════════════════════════════════════════

def load_api_key():
    """Streamlit Secrets에서 API 키 로드"""
    try:
        return st.secrets.get("CLAUDE_API_KEY", "")
    except Exception:
        return ""


# ═══════════════════════════════════════════════════════════════
# 키워드 타입 판별 시스템
# ═══════════════════════════════════════════════════════════════

def classify_keyword_type(keyword):
    """키워드 타입 자동 판별 (우선순위 기반)"""
    keyword_lower = keyword.lower()

    # 우선순위 1: 정보형 강제 판별
    information_force = [
        "무료 ai", "무료 툴", "무료 프로그램", "무료 앱", "무료 사이트",
        "베스트", "top", "순위", "랭킹", "best",
        "추천", "리뷰", "가이드", "총정리", "모음",
        "뭔가요", "설명", "차이", "vs", "비교",
        "방법", "어떻게", "how to", "하는법", "하는 법",
        "장단점", "분석", "정리", "요약"
    ]

    if any(kw in keyword_lower for kw in information_force):
        return "information"

    # 우선순위 2: 거래형
    transaction_keywords = [
        "할인", "저렴", "가성비", "특가", "세일", "최저가",
        "구매", "신청", "받는법", "지원금", "혜택", "무이자",
        "쿠폰", "이벤트", "프로모션", "가격", "얼마",
        "환급", "페이백", "캐시백", "적립"
    ]

    if any(kw in keyword_lower for kw in transaction_keywords):
        return "transaction"

    # 우선순위 3: 일상형
    casual_keywords = [
        "날씨", "오늘", "이번주", "주말", "일요일", "토요일",
        "추운", "더운", "비온", "눈온", "봄", "여름", "가을", "겨울",
        "감상", "생각", "느낀", "일상", "하루", "아침", "저녁",
        "카페", "산책", "힐링", "위로", "공감"
    ]

    if any(kw in keyword_lower for kw in casual_keywords):
        return "casual"

    # 우선순위 4: 뉴스형
    news_keywords = [
        "속보", "긴급", "발표", "공개", "확정",
        "신작", "개봉", "출시", "런칭", "오픈",
        "업데이트", "변경", "인수", "합병"
    ]

    if any(kw in keyword_lower for kw in news_keywords):
        return "news"

    # 기본값: 정보형
    return "information"


def get_type_display(keyword_type):
    """타입 표시 정보 반환"""
    type_info = {
        "transaction": {"emoji": "💰", "name": "거래형", "desc": "할인/구매/가격 정보 중심"},
        "information": {"emoji": "📚", "name": "정보형", "desc": "설명/비교/가이드 중심"},
        "casual":      {"emoji": "☕", "name": "일상형", "desc": "공감/경험/감상 중심"},
        "news":        {"emoji": "📰", "name": "뉴스형", "desc": "최신 속보/발표 중심"}
    }
    return type_info.get(keyword_type, type_info["information"])


# ═══════════════════════════════════════════════════════════════
# 콘텐츠 전략 시스템
# ═══════════════════════════════════════════════════════════════

def get_content_strategy(keyword_type):
    """타입별 콘텐츠 전략 (포함/제외 요소 결정)"""
    strategies = {
        "transaction": {
            "include_discount": True,
            "include_realtime_data": True,
            "include_official_links": True,
            "include_event_info": True
        },
        "information": {
            "include_discount": False,
            "include_realtime_data": False,
            "include_official_links": False,
            "include_event_info": False
        },
        "casual": {
            "include_discount": False,
            "include_realtime_data": False,
            "include_official_links": False,
            "include_event_info": False
        },
        "news": {
            "include_discount": False,
            "include_realtime_data": True,
            "include_official_links": False,
            "include_event_info": False
        }
    }
    return strategies.get(keyword_type, strategies["information"])


# ═══════════════════════════════════════════════════════════════
# 데이터 검색 함수들
# ═══════════════════════════════════════════════════════════════

def search_realtime_data(keyword):
    """실시간 데이터 검색 (금액/비율/날짜)"""
    # TODO: Google Search API 연동 시 실데이터 반환
    return {'money': [], 'percent': [], 'date': []}


def search_official_links(keyword, category):
    """공식 링크 검색"""
    base_links = [
        {"name": "네이버 검색", "url": f"https://search.naver.com/search.naver?query={keyword}", "desc": "네이버에서 검색"}
    ]

    # 카테고리별 추가 링크
    category_links = {
        "영화": [
            {"name": "CGV", "url": "https://www.cgv.co.kr", "desc": "CGV 공식"},
            {"name": "롯데시네마", "url": "https://www.lottecinema.co.kr", "desc": "롯데시네마 공식"},
            {"name": "메가박스", "url": "https://www.megabox.co.kr", "desc": "메가박스 공식"}
        ],
        "IT": [
            {"name": "ProductHunt", "url": "https://www.producthunt.com", "desc": "최신 IT 서비스"}
        ],
        "여행": [
            {"name": "한국관광공사", "url": "https://korean.visitkorea.or.kr", "desc": "관광 정보"}
        ],
        "맛집": [
            {"name": "네이버 플레이스", "url": f"https://map.naver.com/v5/search/{keyword}", "desc": "맛집 검색"}
        ],
        "경제": [
            {"name": "한국은행", "url": "https://www.bok.or.kr", "desc": "경제 통계"}
        ]
    }

    extra = category_links.get(category, [])
    return base_links + extra


def search_event_info(keyword, category):
    """이벤트/할인 정보 검색"""
    today = datetime.now()
    return [{
        "title": f"{keyword} 관련 이벤트",
        "info": "각 공식 사이트에서 최신 이벤트를 확인하세요",
        "period": f"{today.strftime('%Y.%m.%d')} 기준",
        "note": "이벤트 내용은 수시로 변경될 수 있습니다"
    }]


def search_latest_news(keyword, count=5):
    """최신 뉴스 검색 (Google News RSS)"""
    try:
        import urllib.parse
        encoded = urllib.parse.quote(keyword)
        url = f"https://news.google.com/rss/search?q={encoded}&hl=ko&gl=KR&ceid=KR:ko"
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            # 간단한 XML 파싱 (xml.etree 사용)
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)

            news_list = []
            items = root.findall('.//item')
            for item in items[:count]:
                title_el = item.find('title')
                link_el = item.find('link')
                pubdate_el = item.find('pubDate')

                if title_el is not None:
                    title_text = title_el.text or ""
                    # Google News 제목에서 소스 제거
                    title_clean = re.sub(r'\s*-\s*[^-]+$', '', title_text).strip()
                    news_list.append({
                        "title": title_clean,
                        "link": link_el.text if link_el is not None else "",
                        "date": pubdate_el.text if pubdate_el is not None else ""
                    })

            return news_list
    except Exception:
        pass

    return []


# ═══════════════════════════════════════════════════════════════
# 페르소나 시스템
# ═══════════════════════════════════════════════════════════════

def get_persona(category):
    """카테고리별 페르소나 반환"""
    intro = "안녕하세요.\n영화 프로듀서의 블로그, CINEPARK입니다."

    connections = {
        "영화": {
            "connection": "영화 제작과 투자 경험을 바탕으로",
            "credibility": "광해, 하녀 투자 경험"
        },
        "IT": {
            "connection": "콘텐츠 제작하며 IT 툴에 관심이 많아서",
            "credibility": "블로그 자동화 직접 구축/운영"
        },
        "여행": {
            "connection": "영화 촬영차 전국과 해외를 다니면서",
            "credibility": "로케이션 헌팅 경험"
        },
        "맛집": {
            "connection": "촬영장 근처 맛집을 찾아다니면서",
            "credibility": "촬영팀과 함께한 식사 경험"
        },
        "경제": {
            "connection": "영화 투자와 제작비 관리를 하면서",
            "credibility": "엔터테인먼트 투자 경험"
        },
        "일상": {
            "connection": "바쁜 촬영 일정 속에서도",
            "credibility": "프로듀서의 일상"
        },
        "OTT": {
            "connection": "OTT 콘텐츠를 분석하고 리뷰하면서",
            "credibility": "넷플릭스/디즈니+ 콘텐츠 분석"
        },
        "음악": {
            "connection": "영화 OST 작업을 하면서 음악에 관심이 깊어져서",
            "credibility": "영화 음악 제작 경험"
        }
    }

    default = {
        "connection": "다양한 경험을 쌓으면서",
        "credibility": "직접 경험"
    }

    result = connections.get(category, default)
    result["intro"] = intro
    return result


# ═══════════════════════════════════════════════════════════════
# 트렌드 키워드
# ═══════════════════════════════════════════════════════════════

def get_trending_keywords(category):
    """카테고리별 검증된 트렌드 키워드"""
    trends = {
        "영화": [
            "2026년 개봉 영화 추천",
            "넷플릭스 신작 추천",
            "CGV 할인 방법 총정리",
            "디즈니플러스 신작 라인업",
            "봄 영화 추천 베스트 10"
        ],
        "IT": [
            "ChatGPT 활용법 총정리",
            "무료 AI 툴 베스트 20",
            "블로그 자동화 방법",
            "Claude AI 사용법 가이드",
            "노션 AI 활용법 추천"
        ],
        "여행": [
            "2026년 봄 여행지 추천",
            "제주도 숨은 명소 가이드",
            "일본 벚꽃 여행 총정리",
            "국내 가성비 호텔 추천",
            "유럽 여행 준비물 체크리스트"
        ],
        "맛집": [
            "서울 맛집 베스트 10",
            "강남 데이트 맛집 추천",
            "혼밥 맛집 추천 총정리",
            "제주도 맛집 가이드",
            "브런치 맛집 베스트"
        ],
        "경제": [
            "2026년 부동산 전망",
            "주식 초보 가이드 총정리",
            "ETF 투자 방법 추천",
            "연말정산 꿀팁 총정리",
            "적금 금리 비교 추천"
        ],
        "일상": [
            "봄맞이 정리 꿀팁",
            "재택근무 꿀팁 총정리",
            "일상 루틴 만들기",
            "스트레스 해소법 추천",
            "주말 힐링 방법"
        ],
        "OTT": [
            "넷플릭스 인기 순위 총정리",
            "디즈니플러스 추천 시리즈",
            "왓챠 숨겨진 명작 추천",
            "웨이브 오리지널 추천",
            "OTT 가격 비교 총정리"
        ],
        "음악": [
            "2026년 인기곡 추천",
            "플레이리스트 추천 총정리",
            "애플뮤직 vs 스포티파이 비교",
            "영화 OST 명곡 추천",
            "힐링 음악 추천 베스트"
        ]
    }
    return trends.get(category, trends["IT"])


# ═══════════════════════════════════════════════════════════════
# 롱테일 키워드 생성
# ═══════════════════════════════════════════════════════════════

def generate_longtail_keywords(base_keyword):
    """우선순위별 롱테일 키워드 12개 생성"""
    priority_suffixes = {
        1: ["할인", "저렴", "가성비", "특가", "무료"],       # 할인/가성비
        2: ["직접해봄", "솔직후기", "후기", "경험담"],       # 경험
        3: ["방법", "이유", "꿀팁", "총정리"],               # 실용
        4: ["비교", "장단점", "차이", "추천"]                 # 비교
    }

    keywords = []
    for priority in sorted(priority_suffixes.keys()):
        for suffix in priority_suffixes[priority]:
            keywords.append(f"{base_keyword} {suffix}")
            if len(keywords) >= 12:
                return keywords

    return keywords


# ═══════════════════════════════════════════════════════════════
# 이미지 검색 (Unsplash)
# ═══════════════════════════════════════════════════════════════

def search_unsplash_images(keyword, count=3):
    """Unsplash 이미지 검색"""
    return [
        {
            "url": f"https://source.unsplash.com/800x600/?{keyword},{i}",
            "credit": "Unsplash",
            "description": f"{keyword} 관련 이미지 {i+1}"
        }
        for i in range(count)
    ]


# ═══════════════════════════════════════════════════════════════
# SEO 분석 시스템
# ═══════════════════════════════════════════════════════════════

def analyze_seo(title, content, keyword):
    """SEO 점수 분석 (100점 만점)"""
    score = 0
    feedback = []
    improvements = []

    clean_title = title.replace("#", "").strip()

    # 1. 제목 키워드 포함 (25점)
    keyword_main = keyword.split()[0] if " " in keyword else keyword
    if keyword.lower() in clean_title.lower():
        score += 25
        feedback.append("✅ 제목에 전체 키워드 포함")
    elif keyword_main.lower() in clean_title.lower():
        score += 15
        feedback.append(f"⚠️ 제목에 핵심 키워드만 포함 ('{keyword_main}')")
        improvements.append(f"제목에 '{keyword}' 전체를 포함하면 +10점")
    else:
        feedback.append(f"❌ 제목에 키워드 누락 ('{keyword}')")
        improvements.append(f"제목에 '{keyword}' 포함 필요 (+25점)")

    # 2. 제목 길이 (20점)
    title_len = len(clean_title)
    if 28 <= title_len <= 32:
        score += 20
        feedback.append(f"✅ 제목 길이 최적 ({title_len}자)")
    elif 25 <= title_len <= 35:
        score += 12
        feedback.append(f"⚠️ 제목 길이 보통 ({title_len}자, 권장 28~32자)")
        improvements.append(f"제목을 {28 - title_len if title_len < 28 else title_len - 32}자 {'추가' if title_len < 28 else '삭제'}하면 +8점")
    else:
        score += 5
        feedback.append(f"❌ 제목 길이 부적합 ({title_len}자, 권장 28~32자)")
        improvements.append("제목을 28~32자로 조정 필요 (+15점)")

    # 3. 본문 길이 (20점)
    content_len = len(content)
    if 1500 <= content_len <= 3000:
        score += 20
        feedback.append(f"✅ 본문 길이 최적 ({content_len}자)")
    elif 1200 <= content_len <= 3500:
        score += 12
        feedback.append(f"⚠️ 본문 길이 보통 ({content_len}자, 권장 1,500~3,000자)")
    else:
        score += 5
        feedback.append(f"❌ 본문 길이 부적합 ({content_len}자, 권장 1,500~3,000자)")

    # 4. 키워드 밀도 (15점)
    kw_count = content.lower().count(keyword.lower())
    if 3 <= kw_count <= 8:
        score += 15
        feedback.append(f"✅ 키워드 밀도 최적 ({kw_count}회)")
    elif 1 <= kw_count <= 10:
        score += 8
        feedback.append(f"⚠️ 키워드 밀도 보통 ({kw_count}회, 권장 3~8회)")
    else:
        feedback.append(f"❌ 키워드 밀도 부적합 ({kw_count}회)")

    # 5. 소제목 개수 (10점)
    subtitle_count = len(re.findall(r'^##\s', content, re.MULTILINE)) - 1  # 제목 제외
    if subtitle_count < 0:
        subtitle_count = 0
    if 4 <= subtitle_count <= 6:
        score += 10
        feedback.append(f"✅ 소제목 개수 최적 ({subtitle_count}개)")
    elif 3 <= subtitle_count <= 8:
        score += 6
        feedback.append(f"⚠️ 소제목 개수 보통 ({subtitle_count}개, 권장 4~6개)")
    else:
        feedback.append(f"❌ 소제목 부족 ({subtitle_count}개)")

    # 6. 해시태그 (10점)
    hashtag_count = len(re.findall(r'#\S+', content))
    if hashtag_count >= 10:
        score += 10
        feedback.append(f"✅ 해시태그 충분 ({hashtag_count}개)")
    elif hashtag_count >= 5:
        score += 5
        feedback.append(f"⚠️ 해시태그 부족 ({hashtag_count}개, 권장 10개 이상)")
        improvements.append(f"해시태그 {10 - hashtag_count}개 추가 필요")
    else:
        feedback.append(f"❌ 해시태그 부족 ({hashtag_count}개)")
        improvements.append("해시태그 10개 이상 추가 필요 (+10점)")

    return score, feedback, improvements


# ═══════════════════════════════════════════════════════════════
# 제목 최적화
# ═══════════════════════════════════════════════════════════════

def optimize_title(content, keyword, year, keyword_type):
    """제목 추출 및 최적화 (28~32자)"""

    # 제목 추출
    title_match = re.search(r'##\s*(.+?)(?:\n|$)', content)
    if title_match:
        title = title_match.group(1).strip()
    else:
        type_suffix = {
            "transaction": "할인 가이드",
            "information": "완벽 가이드",
            "casual": "프로듀서의 하루",
            "news": "최신 속보"
        }
        title = f"{keyword} {type_suffix.get(keyword_type, '가이드')} | {year}년"

    # '#' 제거
    clean_title = title.replace("#", "").strip()

    # 키워드 포함 확인
    keyword_main = keyword.split()[0] if " " in keyword else keyword
    if keyword_main.lower() not in clean_title.lower():
        clean_title = f"{keyword} | {clean_title}"

    # 길이 조정 (28~32자)
    title_len = len(clean_title)

    if title_len < 28:
        # 짧으면 연도/부제 추가
        fillers = [
            f" | {year}년 총정리",
            f" | {year}년 가이드",
            f" | 핵심만 쏙쏙",
            f" | 완벽 정리",
        ]
        for filler in fillers:
            candidate = clean_title + filler
            if 28 <= len(candidate) <= 32:
                clean_title = candidate
                break
        else:
            # 그래도 안 맞으면 가장 가까운 것
            clean_title = clean_title + fillers[0]
            if len(clean_title) > 32:
                clean_title = clean_title[:32]

    elif title_len > 32:
        # 길면 자르기 (단어 단위)
        if "|" in clean_title:
            parts = clean_title.split("|")
            clean_title = parts[0].strip()
            if len(clean_title) > 32:
                clean_title = clean_title[:30] + ".."
        else:
            clean_title = clean_title[:30] + ".."

    return clean_title


# ═══════════════════════════════════════════════════════════════
# 블로그 포스트 생성 (핵심 함수)
# ═══════════════════════════════════════════════════════════════

def generate_blog_post(keyword, category, word_count, api_key, use_web_search=True):
    """블로그 포스트 생성 (웹 검색 팩트 체크 + 최대 3회 재시도, SEO 85점 목표)"""
    max_retries = 3

    for attempt in range(max_retries):
        try:
            client = anthropic.Anthropic(api_key=api_key)

            today = datetime.now()
            year = today.year

            # 타입 판별 & 전략 결정
            keyword_type = classify_keyword_type(keyword)
            strategy = get_content_strategy(keyword_type)

            # 거래형 전용 데이터 수집
            event_text = ""
            if strategy['include_event_info']:
                events = search_event_info(keyword, category)
                event_text = "\n【이벤트 참고 데이터】\n" + "\n".join(
                    [f"- {e['title']}: {e['info']} ({e['period']})" for e in events]
                )

            data_text = ""
            if strategy['include_realtime_data']:
                realtime_data = search_realtime_data(keyword)
                if realtime_data['money']:
                    data_text += "\n【실시간 금액 데이터】\n" + "\n".join(
                        [f"- {a}{u}" for a, u in realtime_data['money']]
                    )
                if realtime_data['percent']:
                    data_text += "\n【비율 데이터】\n" + "\n".join(
                        [f"- {a}{u}" for a, u in realtime_data['percent']]
                    )

            links_text = ""
            if strategy['include_official_links']:
                official_links = search_official_links(keyword, category)
                links_text = "\n【공식 링크】\n" + "\n".join(
                    [f"- [{l['name']}]({l['url']}) - {l['desc']}" for l in official_links]
                )

            # 페르소나
            persona = get_persona(category)

            # 타입별 프롬프트 선택
            if keyword_type == "transaction":
                prompt = get_transaction_prompt(keyword, category, year, persona, event_text, data_text, links_text)
            elif keyword_type == "information":
                prompt = get_information_prompt(keyword, category, year, persona)
            elif keyword_type == "casual":
                prompt = get_casual_prompt(keyword, category, year, persona)
            else:
                prompt = get_news_prompt(keyword, category, year, persona, data_text)

            # 글자수 지침 추가
            prompt += f"\n\n【글자수 지침】\n본문 전체를 공백 포함 {word_count}자 내외로 작성하세요."

            # ═══════════════════════════════════════
            # Claude API 호출 (웹 검색 도구 포함)
            # ═══════════════════════════════════════
            api_params = {
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 4000,
                "temperature": 0.3,
                "messages": [{"role": "user", "content": prompt}]
            }

            # 웹 검색 도구 추가
            if use_web_search:
                api_params["tools"] = [{
                    "type": "web_search_20250305",
                    "name": "web_search",
                    "max_uses": 5
                }]

            response = client.messages.create(**api_params)

            # ═══════════════════════════════════════
            # 응답 파싱 (웹 검색 결과 포함 처리)
            # ═══════════════════════════════════════
            content_parts = []
            search_count = 0

            for block in response.content:
                if block.type == "text":
                    content_parts.append(block.text)
                elif block.type == "server_tool_use" and block.name == "web_search":
                    search_count += 1
                # web_search_tool_result는 Claude가 내부적으로 처리하므로 스킵

            content = "".join(content_parts)

            # 웹 검색 사용 횟수 기록
            web_search_used = 0
            if hasattr(response, 'usage') and hasattr(response.usage, 'server_tool_use'):
                if hasattr(response.usage.server_tool_use, 'web_search_requests'):
                    web_search_used = response.usage.server_tool_use.web_search_requests

            # 제목 최적화
            title = optimize_title(content, keyword, year, keyword_type)

            # 제목을 본문에 반영
            title_match = re.search(r'##\s*.+?(?:\n)', content)
            if title_match:
                content = content[:title_match.start()] + f"## {title}\n" + content[title_match.end():]
            else:
                content = f"## {title}\n\n{content}"

            # SEO 분석
            score, feedback, improvements = analyze_seo(title, content, keyword)

            # 결과 구성
            result = {
                "title": title,
                "content": content,
                "seo_score": score,
                "feedback": feedback,
                "improvements": improvements,
                "keyword_type": keyword_type,
                "attempts": attempt + 1,
                "success": score >= 85,
                "web_search_used": web_search_used,
            }

            if score >= 85:
                return result

            # 마지막 시도면 현재 점수로 반환
            if attempt == max_retries - 1:
                result["warning"] = f"⚠️ {max_retries}회 시도 후 {score}점 (목표: 85점)"
                return result

        except anthropic.AuthenticationError:
            return {"error": "❌ API 키가 올바르지 않습니다. 키를 확인해주세요."}
        except anthropic.RateLimitError:
            return {"error": "❌ API 호출 한도 초과. 잠시 후 다시 시도해주세요."}
        except Exception as e:
            if attempt == max_retries - 1:
                return {"error": f"❌ 생성 실패: {str(e)}"}

    return {"error": "❌ 알 수 없는 오류로 생성에 실패했습니다."}


# ═══════════════════════════════════════════════════════════════
# 영어 리라이트 생성
# ═══════════════════════════════════════════════════════════════

def generate_english_rewrite(korean_content, keyword, category, api_key):
    """한국어 포스트를 영어권 독자용으로 완전 재구성"""
    try:
        client = anthropic.Anthropic(api_key=api_key)
        year = datetime.now().year

        prompt = get_english_rewrite_prompt(korean_content, keyword, category, year)

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            temperature=0.4,
            tools=[{
                "type": "web_search_20250305",
                "name": "web_search",
                "max_uses": 5
            }],
            messages=[{"role": "user", "content": prompt}]
        )

        # 응답 파싱
        content_parts = []
        web_search_used = 0

        for block in response.content:
            if block.type == "text":
                content_parts.append(block.text)

        if hasattr(response, 'usage') and hasattr(response.usage, 'server_tool_use'):
            if hasattr(response.usage.server_tool_use, 'web_search_requests'):
                web_search_used = response.usage.server_tool_use.web_search_requests

        english_content = "".join(content_parts)

        return {
            "content": english_content,
            "web_search_used": web_search_used,
            "success": True
        }

    except anthropic.AuthenticationError:
        return {"error": "❌ API 키가 올바르지 않습니다.", "success": False}
    except anthropic.RateLimitError:
        return {"error": "❌ API 호출 한도 초과. 잠시 후 다시 시도해주세요.", "success": False}
    except Exception as e:
        return {"error": f"❌ 영어 리라이트 실패: {str(e)}", "success": False}


# ═══════════════════════════════════════════════════════════════
# UI 시작
# ═══════════════════════════════════════════════════════════════

st.title("✍️ AutoPost v10.1")
st.caption("네이버 블로그 SEO 최적화 · 타입별 맞춤 · 웹 검색 팩트 체크 · CINEPARK")

# ───────────────────────────────────────
# API 키 설정
# ───────────────────────────────────────
with st.expander("🔑 API 설정"):
    api_key_input = st.text_input(
        "Claude API Key",
        type="password",
        value=load_api_key(),
        help="Streamlit Cloud에서는 Settings > Secrets에 CLAUDE_API_KEY를 설정하세요."
    )
    if st.button("💡 설정 방법 보기"):
        st.code('CLAUDE_API_KEY = "sk-ant-api03-..."', language="toml")
        st.info("Streamlit Cloud > Manage app > Settings > Secrets에 위 형식으로 입력하세요.")

st.markdown("---")

# ───────────────────────────────────────
# 키워드 소스 (트렌드 + 뉴스)
# ───────────────────────────────────────
with st.expander("🔥 키워드 소스", expanded=False):
    tab_trend, tab_news = st.tabs(["💎 추천 키워드", "📰 최신 뉴스"])

    # 탭 1: 추천 키워드
    with tab_trend:
        trend_cat = st.selectbox(
            "카테고리 선택",
            ["영화", "IT", "여행", "맛집", "경제", "일상", "OTT", "음악"],
            key="trend_cat"
        )
        keywords_list = get_trending_keywords(trend_cat)

        cols = st.columns(2)
        for idx, kw in enumerate(keywords_list):
            with cols[idx % 2]:
                if st.button(f"⭐ {kw}", key=f"trend_{idx}", use_container_width=True):
                    st.session_state['selected_keyword'] = kw
                    st.rerun()

    # 탭 2: 최신 뉴스 (복원!)
    with tab_news:
        news_col1, news_col2 = st.columns([3, 1])
        with news_col1:
            news_query = st.text_input(
                "뉴스 검색어",
                placeholder="예: 넷플릭스 신작, 영화 할인, AI 뉴스",
                key="news_query"
            )
        with news_col2:
            st.markdown("<br>", unsafe_allow_html=True)
            search_news_btn = st.button("🔍 검색", key="search_news", use_container_width=True)

        if search_news_btn and news_query:
            with st.spinner("뉴스 검색 중..."):
                news_results = search_latest_news(news_query, count=5)

            if news_results:
                for idx, news in enumerate(news_results):
                    col_title, col_btn = st.columns([4, 1])
                    with col_title:
                        st.markdown(f"📌 **{news['title']}**")
                    with col_btn:
                        if st.button("선택", key=f"news_{idx}"):
                            st.session_state['selected_keyword'] = news['title']
                            st.rerun()
            else:
                st.warning("검색 결과가 없습니다. 다른 검색어를 시도해보세요.")

st.markdown("---")

# ───────────────────────────────────────
# 글 생성 메인 영역
# ───────────────────────────────────────
st.markdown("## 🚀 글 생성")

default_keyword = st.session_state.get('selected_keyword', '')

col_main, col_side = st.columns([2, 1])

with col_main:
    keyword = st.text_input(
        "키워드",
        value=default_keyword,
        placeholder="예: 무료 AI 툴 베스트 20, CGV 할인, 오늘 날씨",
        help="키워드를 입력하면 자동으로 타입(거래/정보/일상/뉴스)이 판별됩니다."
    )

    # 타입 자동 판별 표시
    if keyword and len(keyword) > 1:
        keyword_type = classify_keyword_type(keyword)
        type_info = get_type_display(keyword_type)
        st.info(f"{type_info['emoji']} **{type_info['name']}** 판별 — {type_info['desc']}")

    # 롱테일 키워드 제안
    if keyword and len(keyword) > 1:
        with st.expander("💡 롱테일 키워드 제안"):
            longtail = generate_longtail_keywords(keyword)
            lt_cols = st.columns(3)
            for idx, ltk in enumerate(longtail[:12]):
                with lt_cols[idx % 3]:
                    if st.button(f"📌 {ltk}", key=f"lt_{idx}", use_container_width=True):
                        st.session_state['selected_keyword'] = ltk
                        st.rerun()

with col_side:
    category = st.selectbox(
        "카테고리",
        ["영화", "IT", "여행", "맛집", "경제", "일상", "OTT", "음악"],
        help="카테고리에 따라 페르소나와 연결 문구가 달라집니다."
    )
    word_count = st.slider("목표 글자수", 1500, 3000, 2000, step=100)
    use_web_search = st.toggle("🔍 웹 검색 팩트 체크", value=True, help="AI가 글 생성 시 웹 검색으로 팩트를 확인합니다. 영화/OTT 정보의 정확성이 크게 향상됩니다. (검색당 $0.01 추가)")

    # 현재 페르소나 미리보기
    if category:
        persona_preview = get_persona(category)
        st.caption(f"🎭 \"{persona_preview['connection']}\"")

# 생성 버튼
st.markdown("")
generate_btn = st.button("✨ 블로그 포스트 생성", type="primary", use_container_width=True)

# ───────────────────────────────────────
# 생성 실행 & 결과 표시
# ───────────────────────────────────────
if generate_btn:
    api = load_api_key() or api_key_input

    if not api:
        st.error("⚠️ API 키를 입력해주세요.")
    elif not keyword or len(keyword) < 2:
        st.error("⚠️ 키워드를 2자 이상 입력해주세요.")
    else:
        keyword_type = classify_keyword_type(keyword)
        type_info = get_type_display(keyword_type)

        with st.spinner(f"{type_info['emoji']} {type_info['name']} 포스트 생성 중... {'(웹 검색 팩트 체크 ON)' if use_web_search else ''}"):
            result = generate_blog_post(keyword, category, word_count, api, use_web_search=use_web_search)

        st.session_state['generated_result'] = result

# 결과 표시 (세션에 저장된 결과)
result = st.session_state.get('generated_result')

if result:
    if "error" in result:
        st.error(result['error'])
    else:
        st.markdown("---")

        # SEO 점수 헤더
        score = result['seo_score']
        kw_type = result.get('keyword_type', 'information')
        type_info = get_type_display(kw_type)

        score_col, info_col = st.columns([1, 2])
        with score_col:
            if score >= 85:
                st.success(f"🏆 SEO {score}/100점")
            elif score >= 70:
                st.warning(f"⚠️ SEO {score}/100점")
            else:
                st.error(f"❌ SEO {score}/100점")

        with info_col:
            st.markdown(f"**{type_info['emoji']} {type_info['name']}** | 시도 {result['attempts']}회")
            if result.get('web_search_used', 0) > 0:
                st.caption(f"🔍 웹 검색 {result['web_search_used']}회 수행 (팩트 체크 완료)")
            if result.get('warning'):
                st.caption(result['warning'])

        # SEO 피드백 상세
        with st.expander("📊 SEO 분석 상세", expanded=False):
            for fb in result['feedback']:
                st.text(fb)

            if result['improvements']:
                st.markdown("**💡 개선 제안:**")
                for imp in result['improvements']:
                    st.text(f"  → {imp}")

        # 본문 미리보기
        st.markdown("### 📝 생성 결과")
        st.markdown(result['content'])

        # 다운로드 & 복사
        st.markdown("---")
        dl_col1, dl_col2 = st.columns(2)
        with dl_col1:
            filename = keyword.replace(" ", "_")
            st.download_button(
                "💾 TXT 다운로드",
                result['content'],
                f"{filename}.txt",
                mime="text/plain",
                use_container_width=True
            )
        with dl_col2:
            # 히스토리에 추가
            if st.button("📋 히스토리에 저장", use_container_width=True):
                st.session_state['post_history'].append({
                    "keyword": keyword,
                    "type": kw_type,
                    "score": score,
                    "title": result['title'],
                    "time": datetime.now().strftime("%H:%M")
                })
                st.success("히스토리에 저장했습니다!")

        # ───────────────────────────────────────
        # 🌐 영어 리라이트 섹션
        # ───────────────────────────────────────
        st.markdown("---")
        st.markdown("### 🌐 English Rewrite for Google Blog")
        st.caption("한국어 포스트를 영어권 독자용으로 완전 재구성합니다. (번역이 아닌 리라이트)")

        eng_col1, eng_col2 = st.columns([3, 1])
        with eng_col1:
            eng_keyword = st.text_input(
                "영어 키워드 (구글 SEO용)",
                value="",
                placeholder="예: Korean box office record, Netflix K-drama, K-Content analysis",
                key="eng_keyword"
            )
        with eng_col2:
            eng_category = st.selectbox(
                "영어 카테고리",
                ["K-Cinema", "K-Drama", "OTT", "Entertainment", "Industry"],
                key="eng_category"
            )

        if st.button("🌐 영어 리라이트 생성", use_container_width=True):
            api = load_api_key() or api_key_input
            if not api:
                st.error("⚠️ API 키를 입력해주세요.")
            elif not eng_keyword:
                st.error("⚠️ 영어 키워드를 입력해주세요.")
            else:
                with st.spinner("🌐 영어 리라이트 생성 중... (웹 검색 팩트 체크 포함)"):
                    eng_result = generate_english_rewrite(
                        result['content'], eng_keyword, eng_category, api
                    )

                if eng_result.get("success"):
                    st.markdown("---")
                    if eng_result.get('web_search_used', 0) > 0:
                        st.caption(f"🔍 웹 검색 {eng_result['web_search_used']}회 수행")

                    st.markdown("### 🌐 English Version")
                    st.markdown(eng_result['content'])

                    eng_filename = eng_keyword.replace(" ", "_")
                    st.download_button(
                        "💾 English TXT 다운로드",
                        eng_result['content'],
                        f"{eng_filename}_EN.txt",
                        mime="text/plain",
                        use_container_width=True,
                        key="eng_download"
                    )
                else:
                    st.error(eng_result.get('error', '영어 리라이트 생성 실패'))

# ───────────────────────────────────────
# 히스토리
# ───────────────────────────────────────
if st.session_state['post_history']:
    st.markdown("---")
    with st.expander(f"📚 생성 히스토리 ({len(st.session_state['post_history'])}건)"):
        for idx, item in enumerate(reversed(st.session_state['post_history'])):
            type_info = get_type_display(item['type'])
            st.text(
                f"{item['time']} | {type_info['emoji']} {item['score']}점 | {item['keyword']}"
            )

# ───────────────────────────────────────
# 푸터
# ───────────────────────────────────────
st.markdown("---")
st.caption("✍️ AutoPost v10.1 | BLUE JEANS PICTURES · CINEPARK | Powered by Claude AI + Web Search")
