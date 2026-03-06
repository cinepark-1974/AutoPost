import streamlit as st
import anthropic
import requests
from datetime import datetime, timedelta
import json
import re
from pathlib import Path

# 페이지 설정
st.set_page_config(page_title="AutoPost v9.0", page_icon="✍️", layout="wide")

# 세션 초기화
if 'post_history' not in st.session_state:
    st.session_state['post_history'] = []

# ========================================
# 1. API 키 관리
# ========================================

def load_api_key():
    """Streamlit Secrets에서 API 키 로드"""
    try:
        return st.secrets.get("CLAUDE_API_KEY", "")
    except:
        return ""

def save_api_key(api_key):
    """API 키는 Streamlit Secrets에 저장 (코드에서는 저장 불가)"""
    st.info("💡 API 키는 Streamlit Cloud Settings > Secrets에서 설정하세요!")
    st.code(f'CLAUDE_API_KEY = "{api_key}"', language="toml")

def search_realtime_data(keyword):
    """실시간 숫자, 금액, 데이터 검색"""
    
    try:
        # Google 검색으로 최신 정보 찾기
        search_query = f"{keyword} 금액 2026"
        url = f"https://www.google.com/search?q={search_query}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 숫자 패턴 찾기 (금액, 퍼센트, 날짜 등)
            import re
            text = soup.get_text()
            
            # 금액 패턴 (만원, 원, 억)
            money_patterns = re.findall(r'(\d+[,\d]*)\s*(만원|원|억원)', text)
            
            # 퍼센트 패턴
            percent_patterns = re.findall(r'(\d+\.?\d*)\s*%', text)
            
            # 날짜 패턴
            date_patterns = re.findall(r'(\d{4})년\s*(\d{1,2})월', text)
            
            data = {
                'money': money_patterns[:3] if money_patterns else [],
                'percent': percent_patterns[:3] if percent_patterns else [],
                'date': date_patterns[:3] if date_patterns else [],
                'source': 'Google 검색 결과'
            }
            
            return data
    except:
        pass
    
    # 기본값 반환 (검색 실패 시)
    return {
        'money': [],
        'percent': [],
        'date': [],
        'source': '정부 공식 홈페이지'
    }

def search_official_links(keyword, category):
    """키워드 관련 공식 링크 검색"""
    
    # 카테고리별 공식 사이트
    official_sites = {
        "재테크": [
            {"name": "국민연금공단", "url": "https://www.nps.or.kr", "desc": "연금 계산"},
            {"name": "국세청 홈택스", "url": "https://www.hometax.go.kr", "desc": "세금 계산"},
            {"name": "금융감독원", "url": "https://www.fss.or.kr", "desc": "금융상품 비교"}
        ],
        "정부지원": [
            {"name": "복지로", "url": "https://www.bokjiro.go.kr", "desc": "정부 지원금 통합"},
            {"name": "정부24", "url": "https://www.gov.kr", "desc": "민원 서비스"},
            {"name": "4대보험 공단", "url": "https://www.nhis.or.kr", "desc": "건강보험 계산"}
        ],
        "부동산": [
            {"name": "국토교통부", "url": "https://www.molit.go.kr", "desc": "부동산 정책"},
            {"name": "한국부동산원", "url": "https://www.reb.or.kr", "desc": "실거래가 조회"},
            {"name": "청약홈", "url": "https://www.applyhome.co.kr", "desc": "청약 신청"}
        ]
    }
    
    # 키워드로 카테고리 자동 판단
    for cat, sites in official_sites.items():
        if cat in keyword or any(site['desc'] in keyword for site in sites):
            return sites[:3]
    
    # 기본 링크
    return [
        {"name": "정부24", "url": "https://www.gov.kr", "desc": "정부 통합 서비스"},
        {"name": "네이버 검색", "url": f"https://search.naver.com/search.naver?query={keyword}", "desc": "최신 정보"},
        {"name": "정부 공식 홈페이지", "url": "https://www.korea.kr", "desc": "대한민국 정부"}
    ]

def generate_longtail_keywords(base_keyword):
    """롱테일 키워드 자동 생성 (할인 우선, 경쟁 낮음)"""
    
    # 우선순위별 접미사
    suffixes = [
        # 우선순위 1: 할인/가성비 (조회수 폭발!)
        "할인", "저렴", "가성비", "특가", "무료",
        
        # 우선순위 2: 직접 경험
        "직접해봄", "솔직후기", "후기", "경험담",
        
        # 우선순위 3: 실용 정보
        "방법", "이유", "꿀팁", "총정리",
        
        # 우선순위 4: 비교/분석
        "비교", "장단점", "차이", "추천"
    ]
    
    longtail_keywords = []
    for suffix in suffixes[:12]:  # 상위 12개
        longtail_keywords.append(f"{base_keyword} {suffix}")
    
    return longtail_keywords

def get_naver_realtime_keywords():
    """네이버 실시간 검색어 가져오기"""
    
    try:
        # 네이버 데이터랩 트렌드 키워드 (간단 버전)
        url = "https://datalab.naver.com/keyword/realtimeList.naver"
        response = requests.get(url, timeout=10)
        
        # 실제 파싱은 복잡하므로 시뮬레이션
        realtime_keywords = [
            "최신 뉴스 이슈",
            "정부 지원금",
            "세금 환급",
            "부동산 대책",
            "주식 급등",
        ]
        
        return realtime_keywords
    except:
        return []

# ========================================
# 2. 트렌드 키워드 & 최신 뉴스
# ========================================

def get_persona(category):
    """카테고리별 적합한 도입부 (브랜드는 항상 동일)"""
    
    # 브랜드는 항상 동일
    intro = "안녕하세요.\n영화 프로듀서의 블로그, CINEPARK입니다."
    
    # 카테고리별 자연스러운 연결
    connections = {
        "영화": {
            "connection": "영화 제작과 투자 경험을 바탕으로",
            "credibility": "광해, 하녀 같은 작품에 투자했던 경험"
        },
        "여행": {
            "connection": "영화 촬영차 전국과 해외를 다니면서",
            "credibility": "유럽, 아시아 25개 도시를 직접 다녀본 경험"
        },
        "와인": {
            "connection": "유럽 영화제 참석하며 와인을 접하게 됐고",
            "credibility": "프랑스, 이탈리아 와이너리를 직접 방문한 경험"
        },
        "재테크": {
            "connection": "영화 투자를 하다 보니 재테크에도 관심이 생겨서",
            "credibility": "광해, 하녀 투자로 실제 수익을 낸 경험"
        },
        "책": {
            "connection": "시나리오 작가이자 소설 작가로서",
            "credibility": "소설 '감각구역'을 집필한 경험"
        },
        "IT": {
            "connection": "콘텐츠 제작을 하다 보니 IT 툴에 관심이 많아서",
            "credibility": "블로그 자동화 등 직접 사용해본 경험"
        },
        "건강": {
            "connection": "바쁜 영화 제작 현장에서 건강 관리의 중요성을 느껴",
            "credibility": "현장에서 직접 실천해본 건강 관리법"
        },
        "요리": {
            "connection": "촬영 현장과 해외 출장 중 다양한 음식을 접하며",
            "credibility": "25개 도시의 미식을 경험"
        },
        "일상": {
            "connection": "영화 제작자로 살면서",
            "credibility": "현장에서의 생생한 일상"
        },
        "패션": {
            "connection": "영화제와 시사회 참석하며 패션에 관심을 갖게 됐고",
            "credibility": "레드카펫 경험"
        }
    }
    
    default = {
        "connection": "다양한 경험을 하면서",
        "credibility": "직접 경험한 내용"
    }
    
    result = connections.get(category, default)
    result["intro"] = intro
    
    return result

def get_trending_keywords(category):
    """카테고리별 트렌드 키워드 TOP 10"""
    
    today = datetime.now()
    year = today.year
    month = today.month
    season = "봄" if month in [3,4,5] else "여름" if month in [6,7,8] else "가을" if month in [9,10,11] else "겨울"
    
    keywords = {
        "영화": [
            f"{year}년 {month}월 개봉 영화 기대작",
            f"{season} 시즌 영화 추천 베스트 10",
            f"{year}년 넷플릭스 인기 영화 순위",
            "영화 투자 수익률 계산 가이드",
            f"{year}년 아카데미 후보작 정리",
            "CGV 메가박스 롯데시네마 할인 비교",
            "영화 시나리오 공모전 상금 순위",
            f"{season} 데이트 영화 추천",
            "OTT 무료 체험 완벽 가이드",
            "영화 제작 비용 분석"
        ],
        "여행": [
            f"{year}년 {season} 국내 여행지 추천",
            "나가노 온천 여행 완벽 가이드",
            "도쿄 3박4일 여행 코스",
            f"{month}월 제주도 여행 꿀팁",
            "유럽 여행 경비 절약 방법",
            "항공권 50% 할인 받는 법",
            "호텔 예약 최저가 찾기",
            f"{season} 벚꽃 명소 베스트 10",
            "혼자 여행 추천 도시",
            "여행 준비 체크리스트"
        ],
        "와인": [
            "3만원대 와인 추천 베스트",
            "와인 초보 입문 가이드",
            "마트 와인 가성비 순위",
            "와인 페어링 완벽 정리",
            f"{year}년 와인 페어 일정",
            "프랑스 와인 vs 칠레 와인",
            "와인 보관 방법 꿀팁",
            "레드 와인 추천 TOP 10",
            "와인 할인 이벤트 정보",
            "와인바 추천 서울"
        ],
        "책": [
            f"{year}년 베스트셀러 순위",
            "자기계발서 추천 필독서",
            "작가 되는 법 완벽 가이드",
            "출판사 계약 노하우",
            "전자책 vs 종이책 비교",
            "독서 습관 만들기",
            "시나리오 작법 입문",
            "북클럽 운영 가이드",
            "책 할인 이벤트",
            "추리소설 추천 명작"
        ],
        "IT": [
            "ChatGPT 활용법 완벽 가이드",
            "AI 이미지 생성 툴 비교",
            "블로그 자동화 방법",
            f"{year}년 스마트폰 추천",
            "노션 활용 꿀팁 50가지",
            "무료 AI 툴 베스트 20",
            "생산성 앱 추천",
            "웹사이트 만들기 가이드",
            "업무 자동화 도구",
            "클라우드 스토리지 비교"
        ]
    }
    
    default = [
        f"{year}년 {category} 트렌드",
        f"{category} 추천 베스트 10",
        f"{category} 초보 가이드",
        f"{category} 완벽 정리",
        f"{category} 할인 정보"
    ]
    
    return keywords.get(category, default)

def search_latest_news(keyword):
    """Google News에서 최신 뉴스 검색"""
    
    try:
        url = f"https://news.google.com/rss/search?q={keyword}&hl=ko&gl=KR&ceid=KR:ko"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)
            
            news_list = []
            for item in root.findall('.//item')[:5]:
                title = item.find('title').text if item.find('title') is not None else ""
                source = item.find('source').text if item.find('source') is not None else ""
                
                if title:
                    clean_title = title.split(' - ')[0].strip()
                    news_list.append({
                        'title': clean_title,
                        'source': source
                    })
            
            return news_list
        return []
    except:
        return []

# ========================================
# 3. 이미지 검색 (Unsplash)
# ========================================

def search_unsplash_images(keyword, count=3):
    """Unsplash에서 무료 이미지 검색"""
    
    try:
        # Unsplash API (무료, 인증 불필요)
        url = f"https://source.unsplash.com/800x600/?{keyword}"
        
        # 간단한 이미지 정보 반환
        images = []
        for i in range(count):
            images.append({
                "url": f"https://source.unsplash.com/800x600/?{keyword},{i}",
                "credit": "Photo by Unsplash",
                "description": f"{keyword} 관련 이미지 {i+1}"
            })
        
        return images
    except:
        return []

# ========================================
# 4. 이벤트 정보 검색
# ========================================

def search_event_info(keyword, category):
    """키워드에 맞는 할인/이벤트 정보 자동 생성"""
    
    today = datetime.now()
    event_start = today.strftime("%Y.%m.%d")
    event_end = (today + timedelta(days=30)).strftime("%Y.%m.%d")
    
    # 카테고리별 이벤트 정보
    event_templates = {
        "여행": [
            {
                "title": f"{keyword} 숙박 특가",
                "info": "각 호텔 예약 사이트에서 비교",
                "period": f"{event_start} ~ {event_end}",
                "note": "주말은 빨리 마감되니 서두르세요"
            },
            {
                "title": "교통 할인 (KTX/항공)",
                "info": "코레일/항공사 홈페이지",
                "period": "조기예매 시 최대 30% 할인",
                "note": "좌석 마감 시 종료"
            },
            {
                "title": "지역 맛집 쿠폰",
                "info": "관광 홈페이지 참고",
                "period": f"{event_start} ~ {event_end}",
                "note": "쿠폰 소진 시 조기 종료"
            }
        ],
        "영화": [
            {
                "title": "CGV/롯데/메가박스 할인",
                "info": "각 영화관 홈페이지",
                "period": "매월 변경",
                "note": "카드사별 할인 혜택 다름"
            },
            {
                "title": "OTT 무료 체험",
                "info": "넷플릭스/왓챠/티빙",
                "period": "신규 가입자 대상",
                "note": "플랫폼별 약관 확인"
            },
            {
                "title": "영화 관람권 할인",
                "info": "각 카드사 이벤트",
                "period": f"{event_start} ~ {event_end}",
                "note": "카드사별 상이"
            }
        ],
        "와인": [
            {
                "title": f"{keyword} 와인 세일",
                "info": "와인샵/백화점",
                "period": f"{event_start} ~ {event_end}",
                "note": "재고 소진 시 조기 종료"
            },
            {
                "title": "와인 페어/시음회",
                "info": "와인 커뮤니티",
                "period": "월별 개최",
                "note": "사전 예약 필요"
            },
            {
                "title": "마트 와인 프로모션",
                "info": "대형마트 홈페이지",
                "period": f"{event_start} ~ {event_end}",
                "note": "매장별 상이"
            }
        ]
    }
    
    # 기본 템플릿
    default_events = [
        {
            "title": f"{keyword} 관련 할인 정보",
            "info": "각 사이트에서 확인",
            "period": f"{event_start} ~ {event_end}",
            "note": "기간 변경 가능"
        }
    ]
    
    return event_templates.get(category, default_events)

# ========================================
# 3. SEO 분석
# ========================================

def analyze_seo(title, content, keyword):
    """SEO 점수 분석"""
    score = 0
    feedback = []
    improvements = []
    
    # 제목 분석
    clean_title = title.replace("#", "").strip()
    if keyword.lower() in clean_title.lower():
        score += 25
        feedback.append("[OK] 제목에 키워드 포함")
    else:
        feedback.append("[X] 제목에 키워드 누락")
        improvements.append(f"제목에 '{keyword}' 추가")
    
    title_len = len(clean_title)
    if 28 <= title_len <= 32:
        score += 20
        feedback.append(f"[OK] 제목 최적 ({title_len}자)")
    else:
        feedback.append(f"[!] 제목 길이 ({title_len}자)")
        improvements.append("제목 28-32자로 조정")
    
    # 본문 분석
    content_len = len(content)
    if 1500 <= content_len <= 3000:
        score += 20
        feedback.append(f"[OK] 본문 최적 ({content_len}자)")
    else:
        feedback.append(f"[!] 본문 길이 ({content_len}자)")
        if content_len < 1500:
            improvements.append(f"본문 {1500 - content_len}자 추가")
    
    # 키워드 밀도
    kw_count = content.lower().count(keyword.lower())
    if 3 <= kw_count <= 8:
        score += 15
        feedback.append(f"[OK] 키워드 밀도 ({kw_count}회)")
    else:
        feedback.append(f"[!] 키워드 밀도 ({kw_count}회)")
        if kw_count < 3:
            improvements.append(f"'{keyword}' {3 - kw_count}회 추가")
    
    # 소제목
    subtitle_count = content.count("##") - 1
    if 3 <= subtitle_count <= 6:
        score += 10
        feedback.append(f"[OK] 소제목 ({subtitle_count}개)")
    else:
        feedback.append(f"[!] 소제목 ({subtitle_count}개)")
        if subtitle_count < 3:
            improvements.append("소제목 3-6개 권장")
    
    # 태그
    if "#" in content:
        score += 10
        feedback.append("[OK] 태그 포함")
    else:
        improvements.append("태그 섹션 추가")
    
    return score, feedback, improvements

# ========================================
# 4. 블로그 글 생성 (핵심!)
# ========================================

def generate_blog_post(keyword, category, word_count, api_key):
    """수익화 기능이 포함된 블로그 글 생성"""
    
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            client = anthropic.Anthropic(api_key=api_key)
            
            today = datetime.now()
            year = today.year
            month = today.month
            
            # 이벤트 정보 가져오기
            events = search_event_info(keyword, category)
            event_text = "\n".join([
                f"- {e['title']}: {e['info']} (📅 {e['period']}, ※ {e['note']})"
                for e in events
            ])
            
            # 실시간 데이터 검색
            realtime_data = search_realtime_data(keyword)
            data_text = ""
            if realtime_data['money']:
                data_text += "\n실제 금액:\n"
                for amount, unit in realtime_data['money']:
                    data_text += f"- {amount}{unit}\n"
            if realtime_data['percent']:
                data_text += "\n실제 비율:\n"
                for pct in realtime_data['percent']:
                    data_text += f"- {pct}%\n"
            
            # 공식 링크 검색
            official_links = search_official_links(keyword, category)
            links_text = "\n공식 링크:\n"
            for link in official_links:
                links_text += f"- [{link['name']}]({link['url']}): {link['desc']}\n"
            
            # 이미지 검색
            images = search_unsplash_images(keyword, count=3)
            
            # 메인 이미지 (맨 위에 표시)
            main_image = images[0] if images else {
                "url": f"https://source.unsplash.com/1200x600/?{keyword}",
                "credit": "Photo by Unsplash",
                "description": f"{keyword} 대표 이미지"
            }
            
            # 본문 삽입용 이미지 (나머지)
            image_text = "\n".join([
                f"![{img['description']}]({img['url']})\n*{img['credit']}*"
                for img in images[1:]
            ]) if len(images) > 1 else ""
            
            # 페르소나 가져오기
            persona = get_persona(category)
            
            # 프롬프트
            prompt = f"""당신은 49만 방문자를 달성한 CINEPARK 블로그 작가입니다.

키워드: {keyword}
카테고리: {category}
목표 글자수: {word_count}자

페르소나 (항상 동일한 브랜드!):
인사말: {persona['intro']}

자연스러운 연결:
"{persona['connection']}"를 활용해서 주제와 자연스럽게 연결

신뢰도 강화:
"{persona['credibility']}"를 언급하여 신뢰도 확보

참고 이벤트 정보 (글에 반드시 포함):
{event_text}

실시간 데이터 (구체적 숫자 사용!):
{data_text}

공식 링크 (신뢰도 UP):
{links_text}

═══════════════════════════════════════
⚠️ 절대 규칙 - 반드시 지켜야 함!
═══════════════════════════════════════

💰 핵심 전략 3가지 (조회수 폭발!)

1️⃣ 할인/저렴 키워드 우선 (54건 vs 7건!)
2️⃣ 실시간 데이터 사용 (구체적 숫자!)
3️⃣ 정부/공식 링크 신뢰도 (신뢰성!)

═══════════════════════════════════════

🚨 제목이 가장 중요합니다! (45점)

반드시 글의 첫 줄에:
## {keyword} 할인 관련 제목 28-32자

예시 (정확히 따라하세요):
## CGV 메가박스 롯데시네마 할인 2026년 3월 완벽 정리
## 재택치료 지원금 10만원 받는 법 | 2026년 최신

⚠️ 중요: "할인", "저렴", "가성비" 키워드 우선!

규칙:
1. ## 기호로 시작
2. "{keyword}" 반드시 포함
3. "할인/저렴/무료" 키워드 포함 (조회수 8배!)
4. 정확히 28-32자
5. 숫자나 년도 포함 권장

❌ 절대 금지:
- 제목 없이 본문부터 시작
- 키워드 누락
- 20자 이하 짧은 제목
- 40자 이상 긴 제목

✅ 올바른 예:
## {keyword} 할인 완벽 가이드 | {year}년 최신 정보 총정리

지금 반드시 ## 제목부터 시작하세요!

2. 인사말 (제목 다음 줄):
{persona['intro']}

"{persona['connection']}"를 활용해서 자연스럽게 연결
"{persona['credibility']}"를 언급하여 신뢰도 확보

3. 본문 스타일 (매우 중요!):
   
   ⚠️ 직접 경험한 것처럼 작성!
   
   ✅ 좋은 예:
   "제가 직접 {keyword}을 해봤는데요, 처음엔 어려웠지만..."
   "저도 {keyword} 때문에 고민이 많았거든요. 그래서 직접..."
   "실제로 경험해보니 이런 점이 좋더라고요."
   
   ❌ 나쁜 예:
   "{keyword}은 이렇습니다."
   "{keyword}에 대해 알아보겠습니다."
   
   필수 표현:
   - "제가 직접 해봤는데"
   - "~더라고요", "~거든요", "~했어요"
   - "솔직히", "개인적으로"
   - "처음엔 ~했지만, 나중엔..."
   
4. 본문 구성: 1,500-3,000자
   - "{keyword}" 본문에 5-7회 반복
   - 소제목 4-5개 (## 형식)
   - 경험담 중심
   - **구체적 숫자 필수!**
   
   ⚠️ 구체적 숫자 사용 (매우 중요!):
   
   ✅ 좋은 예:
   "재택치료 지원금은 **10만원**입니다"
   "신청 후 **3일 만에** 입금됐어요"
   "이 글은 **63만 뷰**를 기록했습니다"
   "댓글이 **200개**나 달렸어요"
   
   ❌ 나쁜 예:
   "지원금을 받을 수 있습니다"
   "빠르게 입금됩니다"
   "많은 조회수를 기록했습니다"
   
   위에 제공된 실시간 데이터의 숫자를 반드시 사용!

5. 공식 링크 삽입 (신뢰도 UP!):

## 공식 사이트 안내

더 자세한 정보는 아래 공식 사이트를 참고하세요!

- [정부24](링크): 정부 통합 서비스
- [국세청 홈택스](링크): 세금 계산
- [복지로](링크): 지원금 신청

6. 후기 섹션 추가 (필수!):

## 직접 해본 {keyword} 후기

제가 실제로 {keyword}을 경험해보니,
처음엔 어려웠지만 막상 해보니 생각보다 쉽더라고요.

특히 [구체적 경험]이 가장 도움이 됐어요.
여러분도 한번 해보시길 추천드립니다!

6. 이미지 삽입 (선택):
   
   본문 중간중간에 아래 이미지 삽입:
   {image_text}
   
   예시 위치:
   - 첫 소제목 아래
   - 중간 소제목 아래
   - 마지막 부분

6. 태그: 10개 이상

6. CINEPARK 배경:
   - 영화 프로듀서 (광해, 하녀 투자)

═══════════════════════════════════════
⚠️ 다시 확인: 첫 줄은 ## {keyword} 포함 제목!
═══════════════════════════════════════

지금 바로 ## 제목부터 작성하세요!"""

            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                temperature=0.3,  # 0.4 → 0.3 (더 정확하게)
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text
            
            # 제목 추출 및 자동 생성 (강화됨!)
            title_match = re.search(r'##\s*(.+?)(?:\n|$)', content)
            
            if title_match:
                title = title_match.group(1).strip()
            else:
                # 제목이 아예 없으면 키워드로 생성
                title = f"{keyword} 완벽 가이드 | {year}년 최신 정보"
            
            # 제목 정제
            clean_title = title.replace("#", "").strip()
            
            # === 제목 자동 수정 시스템 ===
            
            # 1. 키워드 포함 확인 (가장 중요!)
            keyword_main = keyword.split()[0] if " " in keyword else keyword  # 핵심 키워드만
            
            if keyword_main.lower() not in clean_title.lower():
                # 키워드가 없으면 강제로 추가
                if len(clean_title) < 20:
                    # 너무 짧으면 키워드를 앞에
                    clean_title = f"{keyword} {clean_title}"
                else:
                    # 적당하면 키워드만 앞에 추가
                    clean_title = f"{keyword} | {clean_title}"
            
            # 2. 길이 강제 조정 (28-32자)
            title_len = len(clean_title)
            
            if title_len < 28:
                # 28자 미만이면 무조건 추가
                shortage = 28 - title_len
                if shortage > 15:
                    clean_title = f"{clean_title} | {year}년 최신 정보 완벽 가이드"
                elif shortage > 8:
                    clean_title = f"{clean_title} | {year}년 완벽 정리"
                elif shortage > 4:
                    clean_title = f"{clean_title} | {year}년"
                else:
                    clean_title = f"{clean_title} 정리"
                    
            elif title_len > 32:
                # 32자 초과면 자르기
                clean_title = clean_title[:30]
                # 단어 중간에서 끊기지 않도록
                if " " in clean_title:
                    clean_title = clean_title.rsplit(" ", 1)[0]
            
            # 3. 최종 검증
            final_len = len(clean_title)
            if final_len < 28:
                # 그래도 짧으면 강제로 28자 맞추기
                clean_title = f"{clean_title} 총정리"
            
            # 최종 제목 확정
            title = clean_title
            
            # 본문에서 첫 제목 교체
            if title_match:
                content = re.sub(r'##\s*.+?(?:\n)', f"## {title}\n", content, count=1)
            else:
                content = f"## {title}\n\n{content}"
            
            # SEO 분석
            score, feedback, improvements = analyze_seo(title, content, keyword)
            
            # 85점 이상이면 성공
            if score >= 85:
                return {
                    "title": title,
                    "content": content,
                    "seo_score": score,
                    "feedback": feedback,
                    "improvements": improvements,
                    "attempts": attempt + 1,
                    "success": True
                }
            
            # 마지막 시도면 그냥 반환
            if attempt == max_retries - 1:
                return {
                    "title": title,
                    "content": content,
                    "seo_score": score,
                    "feedback": feedback,
                    "improvements": improvements,
                    "attempts": attempt + 1,
                    "success": False,
                    "warning": f"⚠️ {max_retries}번 시도 후 {score}점"
                }
                
        except Exception as e:
            if attempt == max_retries - 1:
                return {"error": str(e)}
    
    return {"error": "생성 실패"}

# ========================================
# 5. UI
# ========================================

# 메인 헤더 이미지
st.image("https://raw.githubusercontent.com/cinepark-1974/AutoPost/main/hero_image.png", use_container_width=True)

st.title("✍️ AutoPost v9.0")
st.caption("네이버 블로그 SEO 최적화 자동 글쓰기 (수익화 기능 포함)")

# API 키 설정
with st.expander("🔑 API 설정"):
    api_key_input = st.text_input("Claude API 키", type="password", value=load_api_key())
    if st.button("API 키 저장 방법 보기"):
        save_api_key(api_key_input)

st.markdown("---")

# 트렌드 키워드 & 최신 뉴스
with st.expander("🔥 트렌드 키워드 & 최신 뉴스", expanded=False):
    tab1, tab2 = st.tabs(["💎 추천 키워드", "📰 최신 뉴스"])
    
    with tab1:
        st.info("💡 카테고리별 검증된 트렌드 키워드 TOP 10")
        
        trend_cat = st.selectbox("카테고리 선택", [
            "영화", "여행", "와인", "책", "IT"
        ], key="trend_cat")
        
        keywords = get_trending_keywords(trend_cat)
        
        st.markdown("### 💎 오늘의 TOP 10")
        cols = st.columns(2)
        for idx, kw in enumerate(keywords):
            with cols[idx % 2]:
                if st.button(f"⭐ {kw}", key=f"trend_{idx}", use_container_width=True):
                    st.session_state['selected_keyword'] = kw
                    st.rerun()
    
    with tab2:
        st.info("📰 Google News 실시간 검색")
        
        news_query = st.text_input("검색어", placeholder="예: 영화 할인", key="news_query")
        
        if st.button("🔍 뉴스 검색", key="search_news"):
            if news_query:
                with st.spinner("뉴스 검색 중..."):
                    news_list = search_latest_news(news_query)
                
                if news_list:
                    st.success(f"✅ 최신 뉴스 {len(news_list)}개")
                    
                    for idx, news in enumerate(news_list):
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.markdown(f"**{news['title']}**")
                            st.caption(f"출처: {news['source']}")
                        with col2:
                            if st.button("선택", key=f"news_{idx}"):
                                st.session_state['selected_keyword'] = news['title']
                                st.rerun()
                else:
                    st.warning("뉴스를 찾을 수 없습니다")
            else:
                st.warning("검색어를 입력하세요")

st.markdown("---")

# 메인 글 생성
st.markdown("## 🚀 글 생성")

# 선택된 키워드 자동 입력
default_keyword = st.session_state.get('selected_keyword', '')

col1, col2 = st.columns([2, 1])
with col1:
    keyword = st.text_input("키워드", value=default_keyword, placeholder="예: 2026 벚꽃 개화시기")
    
    # 롱테일 키워드 제안
    if keyword and len(keyword) > 2:
        with st.expander("💡 롱테일 키워드 제안 (경쟁률 낮음)"):
            longtail = generate_longtail_keywords(keyword)
            st.info("⚠️ 경쟁이 낮은 키워드로 노출 확률 UP!")
            
            cols = st.columns(2)
            for idx, ltk in enumerate(longtail[:6]):
                with cols[idx % 2]:
                    if st.button(f"📌 {ltk}", key=f"lt_{idx}", use_container_width=True):
                        st.session_state['selected_keyword'] = ltk
                        st.rerun()
with col2:
    category = st.selectbox("카테고리", [
        "영화", "여행", "와인", "책", "IT", 
        "일상", "건강", "요리", "재테크", "패션"
    ])

word_count = st.slider("목표 글자수", 1500, 3000, 2000)

if st.button("✨ 생성 (SEO 85점 자동 달성)", type="primary"):
    api = load_api_key() or api_key_input
    
    if not api:
        st.error("⚠️ API 키를 입력하세요")
    elif not keyword:
        st.error("⚠️ 키워드를 입력하세요")
    else:
        with st.spinner("생성 중... (최대 3번 시도)"):
            result = generate_blog_post(keyword, category, word_count, api)
        
        if "error" in result:
            st.error(f"❌ 오류: {result['error']}")
        else:
            # 결과 표시
            attempts_text = f" ({result.get('attempts', 1)}번 시도)" if 'attempts' in result else ""
            st.markdown(f"### SEO: {result['seo_score']}/100{attempts_text}")
            
            if result['seo_score'] >= 85:
                st.success("🏆 SEO 85점 이상! 네이버 검색 최적화 완료!")
            elif result['seo_score'] >= 70:
                st.warning("⚠️ 70점대 - 재생성 권장")
            else:
                st.error("❌ 70점 미만 - 키워드 변경 권장")
            
            # 피드백
            for fb in result['feedback']:
                st.text(fb)
            
            if result.get('improvements'):
                with st.expander("💡 개선 사항"):
                    for imp in result['improvements']:
                        st.text(f"- {imp}")
            
            # 경고
            if 'warning' in result:
                st.warning(result['warning'])
            
            # 이미지 미리보기
            if keyword:
                with st.expander("🖼️ 사용된 이미지 (Unsplash)"):
                    images = search_unsplash_images(keyword, count=3)
                    cols = st.columns(3)
                    for idx, img in enumerate(images):
                        with cols[idx]:
                            st.image(img['url'], caption=img['description'], use_container_width=True)
                            st.caption(img['credit'])
            
            st.markdown("---")
            st.markdown(result['content'])
            
            # 다운로드
            st.download_button(
                "💾 다운로드 (.txt)",
                result['content'],
                f"{keyword.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )
            
            # 히스토리 저장
            st.session_state['post_history'].insert(0, {
                'timestamp': datetime.now(),
                'keyword': keyword,
                'seo_score': result['seo_score']
            })

# 히스토리
if st.session_state['post_history']:
    st.markdown("---")
    st.markdown("## 📝 생성 히스토리")
    
    for idx, item in enumerate(st.session_state['post_history'][:5]):
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.text(f"{item['keyword']}")
        with col2:
            st.text(f"SEO: {item['seo_score']}")
        with col3:
            st.caption(item['timestamp'].strftime("%m/%d %H:%M"))
