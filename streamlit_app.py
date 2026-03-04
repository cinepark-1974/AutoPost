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

# ========================================
# 2. 이벤트 정보 검색
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
            
            # 프롬프트
            prompt = f"""당신은 49만 방문자를 달성한 CINEPARK 블로그 작가입니다.

키워드: {keyword}
카테고리: {category}
목표 글자수: {word_count}자

참고 이벤트 정보 (글에 반드시 포함):
{event_text}

═══════════════════════════════════════
🎯 SEO 85점 이상 필수 조건
═══════════════════════════════════════

1. 제목: "{keyword}" 포함, 28-32자

2. 인사말 (줄바꿈 필수):
안녕하세요.
영화 프로듀서의 블로그, CINEPARK입니다.

3. 본문: 1,500-3,000자
   - 키워드 5-7회
   - 소제목 4-5개
   - 구어체 (~더라고요, ~거든요, ~합니다)

4. 수익화 섹션 (필수!):

## 참고 정보 💡

{keyword} 관련 할인/이벤트 정보를 확인해보세요!

**1. [이벤트 제목]**
- [확인 방법]
📅 이벤트 기간: [기간]
※ [주의사항]

**2. [이벤트 제목]**
- [확인 방법]
📅 이벤트 기간: [기간]
※ [주의사항]

**3. [이벤트 제목]**
- [확인 방법]
📅 이벤트 기간: [기간]
※ [주의사항]

─────────────────
⚠️ 위 정보는 변경될 수 있으니
   각 사이트에서 확인하세요!

5. 실행 가능한 가이드 (선택적 추가):
   - 예산 계산
   - 체크리스트
   - 준비물

6. 태그: 10개 이상

7. CINEPARK 배경:
   - 영화 프로듀서 (광해, 하녀 투자)
   - 유럽, 아시아 25개 도시 여행
   - 콘텐츠 시나리오 전공
   - 소설 '감각구역' 작가

지금 바로 작성하세요!"""

            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                temperature=0.4,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text
            
            # 제목 추출
            title_match = re.search(r'##\s*(.+?)(?:\n|$)', content)
            title = title_match.group(1).strip() if title_match else keyword
            
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

st.title("✍️ AutoPost v9.0")
st.caption("네이버 블로그 SEO 최적화 자동 글쓰기 (수익화 기능 포함)")

# API 키 설정
with st.expander("🔑 API 설정"):
    api_key_input = st.text_input("Claude API 키", type="password", value=load_api_key())
    if st.button("API 키 저장 방법 보기"):
        save_api_key(api_key_input)

st.markdown("---")

# 메인 글 생성
st.markdown("## 🚀 글 생성")

col1, col2 = st.columns([2, 1])
with col1:
    keyword = st.text_input("키워드", placeholder="예: 2026 벚꽃 개화시기")
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
