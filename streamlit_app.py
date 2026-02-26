import streamlit as st
import anthropic
import requests
from datetime import datetime
import json
from PIL import Image
from io import BytesIO
import re

# 상수
BOOK_INFO = {
    "cover_url": "https://raw.githubusercontent.com/cinepark-1974/AutoPost/main/assets/book_cover.png",
    "title": "감각구역",
    "authors": "문성주, 박현",
    "publisher": "마카롱(교보문고)",
    "link": "https://ebook-product.kyobobook.co.kr/dig/epd/ebook/E000012093207"
}

# 네이버 키워드 분석 (무료)
def analyze_keyword(keyword):
    """네이버 연관검색어 + 경쟁도 분석"""
    try:
        # 네이버 자동완성 API
        url = "https://ac.search.naver.com/nx/ac"
        params = {
            "q": keyword,
            "con": 0,
            "frm": "nv",
            "ans": 2,
            "r_format": "json",
            "r_enc": "UTF-8",
            "r_unicode": 0,
            "t_koreng": 1,
            "run": 2
        }
        
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            suggestions = []
            
            if "items" in data and len(data["items"]) > 0:
                for item in data["items"][0][:10]:
                    suggestions.append(item[0])
            
            return suggestions
        
        return []
    except:
        return []

# SEO 점수 분석
def analyze_seo(title, content, keyword):
    """작성된 글의 SEO 점수 분석"""
    score = 0
    feedback = []
    
    # 1. 제목에 키워드 포함 (20점)
    if keyword.lower() in title.lower():
        score += 20
        feedback.append("✅ 제목에 키워드 포함")
    else:
        feedback.append("❌ 제목에 키워드 추가 필요")
    
    # 2. 제목 길이 (10점)
    if 15 <= len(title) <= 40:
        score += 10
        feedback.append("✅ 제목 길이 적절 (15-40자)")
    else:
        feedback.append(f"⚠️ 제목 길이 조정 필요 (현재: {len(title)}자)")
    
    # 3. 본문 글자 수 (15점)
    content_length = len(content)
    if 1500 <= content_length <= 3000:
        score += 15
        feedback.append(f"✅ 본문 글자 수 적절 ({content_length}자)")
    else:
        feedback.append(f"⚠️ 본문 글자 수 조정 ({content_length}자, 권장: 1500-3000자)")
    
    # 4. 키워드 밀도 (20점)
    keyword_count = content.lower().count(keyword.lower())
    if 3 <= keyword_count <= 7:
        score += 20
        feedback.append(f"✅ 키워드 밀도 적절 ({keyword_count}회)")
    else:
        feedback.append(f"⚠️ 키워드 밀도 조정 ({keyword_count}회, 권장: 3-7회)")
    
    # 5. 소제목 개수 (10점)
    subtitle_count = content.count("##")
    if subtitle_count >= 3:
        score += 10
        feedback.append(f"✅ 소제목 충분 ({subtitle_count}개)")
    else:
        feedback.append(f"⚠️ 소제목 추가 필요 ({subtitle_count}개, 권장: 3개 이상)")
    
    # 6. 이모지 사용 (10점)
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # 이모티콘
        u"\U0001F300-\U0001F5FF"  # 기호
        u"\U0001F680-\U0001F6FF"  # 교통
        u"\U0001F1E0-\U0001F1FF"  # 국기
        "]+", flags=re.UNICODE)
    
    if emoji_pattern.search(content):
        score += 10
        feedback.append("✅ 이모지 사용")
    else:
        feedback.append("⚠️ 이모지 추가 권장")
    
    # 7. 해시태그 (15점)
    if "#" in content:
        score += 15
        feedback.append("✅ 해시태그 포함")
    else:
        feedback.append("⚠️ 해시태그 추가 필요")
    
    return score, feedback

# 실시간 트렌드 키워드
def get_trending_keywords():
    """네이버 실시간 검색어 (대체 방법)"""
    try:
        # Google Trends Korea 기반
        trending = [
            "🔥 트렌드 키워드는 네이버 메인에서 확인하세요",
            "💡 팁: '오늘', '최신', '2026' 같은 단어 추가",
            "📊 네이버 데이터랩 활용 권장"
        ]
        return trending
    except:
        return ["트렌드 조회 실패"]

# 제목 최적화 AI
def optimize_title(keyword, claude_api_key):
    """클릭률 높은 제목 10개 생성"""
    try:
        client = anthropic.Anthropic(api_key=claude_api_key)
        
        prompt = f"""키워드 "{keyword}"로 네이버 블로그 제목 10개를 만들어주세요.

요구사항:
1. 클릭률이 높은 제목
2. 숫자 포함 (예: 5가지, 10분, 200%)
3. 감탄사/의문사 (꿀팁, 대박, 진짜?, 비결은?)
4. 25-35자 길이
5. 키워드는 앞쪽에 배치

예시:
- {keyword} 꿀팁 5가지! 초보도 10분만에 가능
- {keyword} 이것만 알면 끝! 2026 최신 정리
- {keyword} 200% 활용하는 놀라운 방법

10개만 출력:"""
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        titles = message.content[0].text.strip().split("\n")
        return [t.strip("- ") for t in titles if t.strip()][:10]
        
    except:
        return ["제목 생성 실패"]

# 무료 이미지
def get_free_image(keyword):
    try:
        url = "https://api.pexels.com/v1/search"
        headers = {"Authorization": "563492ad6f9170000100000154d4f33a2fa54799bed66bbf3115e359"}
        params = {"query": keyword, "per_page": 1}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("photos"):
                return {"url": data["photos"][0]["src"]["large"], "source": "Pexels"}
    except:
        pass
    
    return {"url": f"https://picsum.photos/1200/800?random={hash(keyword)%1000}", "source": "Lorem Picsum"}

# 책 홍보
def add_book_promotion():
    return f"""

---

## 📚 제 저서를 소개합니다

![{BOOK_INFO['title']}]({BOOK_INFO['cover_url']})

**제목**: [{BOOK_INFO['title']}]({BOOK_INFO['link']})  
**저자**: {BOOK_INFO['authors']}  
**출판사**: {BOOK_INFO['publisher']}

많은 다운로드를 부탁합니다. 꾸벅 🙇
"""

# 페이지 설정
st.set_page_config(
    page_title="AutoPost - AI 블로그 자동화",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS
st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none !important; }
    .main .block-container { max-width: 1200px !important; padding: 2rem !important; margin: 0 auto !important; }
    .stApp { background-color: #f8f9fd !important; }
    h1 { color: #191970 !important; text-align: center !important; }
    .stButton > button[kind="primary"] { background-color: #ffcb05 !important; color: #191970 !important; 
        font-weight: 600 !important; width: 100% !important; }
</style>
""", unsafe_allow_html=True)

# 헤더
st.markdown("""
<h1>✍️ AutoPost <span style='color: #ffcb05;'>방문자 폭증</span></h1>
<p style='text-align: center; color: #191970; margin-bottom: 2rem;'>
    황금 키워드 + SEO 최적화 + AI 제목 생성
</p>
""", unsafe_allow_html=True)

# API 설정
with st.expander("⚙️ API 설정 (필수)", expanded=False):
    claude_api_key = st.text_input("Claude API Key", type="password")

st.divider()

# 탭 구조
tab1, tab2, tab3, tab4 = st.tabs(["🔥 황금 키워드", "📝 글 생성", "📊 SEO 분석", "💡 제목 최적화"])

# 탭1: 황금 키워드 찾기
with tab1:
    st.markdown("### 🔥 황금 키워드 찾기")
    st.info("💡 검색량은 많지만 경쟁이 적은 키워드를 찾으세요!")
    
    search_keyword = st.text_input("키워드 입력", placeholder="예: 주식, 맛집, 영화", key="search")
    
    if st.button("🔍 연관 키워드 분석", key="analyze_btn"):
        if search_keyword:
            with st.spinner("분석 중..."):
                suggestions = analyze_keyword(search_keyword)
                
                if suggestions:
                    st.success(f"✅ {len(suggestions)}개의 연관 키워드 발견!")
                    
                    st.markdown("### 📋 추천 키워드 목록")
                    for i, kw in enumerate(suggestions, 1):
                        st.markdown(f"{i}. **{kw}**")
                    
                    st.markdown("---")
                    st.markdown("### 💡 황금 키워드 선택 팁")
                    st.markdown("""
                    - ✅ 구체적인 키워드 (예: "주식" → "주식 초보 추천")
                    - ✅ 롱테일 키워드 (3-4단어 조합)
                    - ✅ 지역명 포함 (예: "부산 맛집")
                    - ✅ 연도 포함 (예: "2026 최신")
                    """)
                else:
                    st.warning("연관 키워드를 찾지 못했습니다.")

# 탭2: 글 생성
with tab2:
    st.markdown("### 📝 AI 글 생성")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        keyword = st.text_input("키워드", placeholder="황금 키워드 입력")
        category = st.selectbox("카테고리", 
            ["영화 리뷰", "책 리뷰", "주식", "맛집 후기", "여행 후기", "IT/기술", "일상/에세이"])
    
    with col2:
        word_count = st.slider("글 길이", 1500, 3000, 2000, 100)
        include_image = st.checkbox("이미지 생성", value=True)
    
    if st.button("🤖 AI 글 생성", type="primary"):
        if not claude_api_key or not keyword:
            st.error("API Key와 키워드를 입력하세요!")
        else:
            with st.spinner("생성 중..."):
                try:
                    client = anthropic.Anthropic(api_key=claude_api_key)
                    
                    prompt = f"""네이버 블로그 글 작성 (방문자 최적화)

키워드: {keyword}
카테고리: {category}
글자수: {word_count}자

규칙:
1. 제목: 클릭 유도 (숫자, 감탄사, 물음표)
2. 시작: "안녕하세요. 영화 프로듀서의 블로그, CINEPARK입니다."
3. 소제목: 3-5개 (물음표/느낌표)
4. 키워드: 5-7회 자연스럽게
5. 이모지: 적절히 사용
6. 해시태그: 5-10개

출력:
## [클릭 유도 제목]
안녕하세요. 영화 프로듀서의 블로그, CINEPARK입니다.
[본문...]
## 태그
#태그들
"""
                    
                    message = client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=4000,
                        temperature=0.7,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    
                    content = message.content[0].text + add_book_promotion()
                    
                    # 이미지
                    if include_image:
                        image_info = get_free_image(keyword)
                        st.image(image_info['url'], use_container_width=True)
                    
                    # 결과
                    st.success("✅ 생성 완료!")
                    st.markdown(content)
                    
                    # 세션에 저장
                    st.session_state['generated_title'] = content.split("\n")[0].replace("##", "").strip()
                    st.session_state['generated_content'] = content
                    
                    st.download_button(
                        "💾 저장",
                        content,
                        file_name=f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    )
                    
                except Exception as e:
                    st.error(f"오류: {str(e)}")

# 탭3: SEO 분석
with tab3:
    st.markdown("### 📊 SEO 점수 분석")
    st.info("💡 작성한 글을 붙여넣으면 SEO 점수를 분석해드립니다!")
    
    seo_keyword = st.text_input("분석할 키워드", key="seo_kw")
    seo_title = st.text_input("제목", key="seo_title")
    seo_content = st.text_area("본문 (전체)", height=200, key="seo_content")
    
    if st.button("📈 SEO 분석 시작"):
        if seo_keyword and seo_title and seo_content:
            score, feedback = analyze_seo(seo_title, seo_content, seo_keyword)
            
            # 점수 표시
            col_a, col_b, col_c = st.columns(3)
            with col_b:
                st.markdown(f"""
                <div style='text-align: center; padding: 2rem; background: #e8ecf7; border-radius: 10px;'>
                    <h1 style='color: #191970; font-size: 4rem; margin: 0;'>{score}</h1>
                    <p style='color: #191970; font-size: 1.2rem;'>/ 100점</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # 등급
            if score >= 80:
                st.success("🏆 우수! 상위 노출 가능성 높음")
            elif score >= 60:
                st.warning("👍 양호! 약간의 개선 필요")
            else:
                st.error("⚠️ 개선 필요! 아래 피드백 확인")
            
            # 피드백
            st.markdown("### 📋 상세 피드백")
            for fb in feedback:
                st.markdown(f"- {fb}")
            
            # 개선 팁
            st.markdown("---")
            st.markdown("### 💡 개선 팁")
            st.markdown("""
            **즉시 적용 가능:**
            1. 제목 앞에 숫자 추가 (예: "5가지", "10분")
            2. 소제목을 물음표로 (예: "효과가 있을까?")
            3. 이모지 3-5개 추가
            4. 본문에 키워드 2-3회 더 추가
            5. 해시태그 10개 달기
            """)

# 탭4: 제목 최적화
with tab4:
    st.markdown("### 💡 클릭률 높은 제목 생성")
    st.info("🔥 AI가 클릭률 높은 제목 10개를 만들어드립니다!")
    
    title_keyword = st.text_input("키워드 입력", key="title_kw")
    
    if st.button("✨ 제목 10개 생성"):
        if not claude_api_key or not title_keyword:
            st.error("API Key와 키워드를 입력하세요!")
        else:
            with st.spinner("제목 생성 중..."):
                titles = optimize_title(title_keyword, claude_api_key)
                
                st.success("✅ 제목 생성 완료!")
                st.markdown("### 📋 추천 제목 TOP 10")
                
                for i, title in enumerate(titles, 1):
                    st.markdown(f"**{i}.** {title}")
                
                st.markdown("---")
                st.markdown("### 💡 제목 작성 팁")
                st.markdown("""
                - ✅ 숫자 포함 (5가지, 10분, 200%)
                - ✅ 감탄사 (꿀팁, 대박, 진짜)
                - ✅ 의문사 (방법은?, 비결은?)
                - ✅ 연도 (2026 최신)
                - ✅ 키워드는 앞쪽 배치
                """)

# Footer
st.markdown("---")
st.caption("Made with ❤️ | AutoPost v3.1 방문자 폭증 에디션")
