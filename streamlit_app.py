import streamlit as st
import anthropic
import requests
from datetime import datetime
import json
from PIL import Image
from io import BytesIO
import re
import os

# 상수
BOOK_INFO = {
    "cover_url": "https://raw.githubusercontent.com/cinepark-1974/AutoPost/main/assets/book_cover.png",
    "title": "감각구역",
    "authors": "문성주, 박현",
    "publisher": "마카롱(교보문고)",
    "link": "https://ebook-product.kyobobook.co.kr/dig/epd/ebook/E000012093207"
}

HERO_IMAGE = "https://raw.githubusercontent.com/cinepark-1974/AutoPost/main/assets/hero_image.png"

# API 키 저장/불러오기
def save_api_key(key):
    """API 키를 세션에 저장"""
    st.session_state['saved_api_key'] = key
    return True

def load_api_key():
    """저장된 API 키 불러오기"""
    if 'saved_api_key' in st.session_state:
        return st.session_state['saved_api_key']
    return ""

# 키워드 분석
def analyze_keyword(keyword):
    try:
        url = "https://ac.search.naver.com/nx/ac"
        params = {"q": keyword, "con": 0, "frm": "nv", "ans": 2, "r_format": "json"}
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if "items" in data and len(data["items"]) > 0:
                return [item[0] for item in data["items"][0][:10]]
        return []
    except:
        return []

# SEO 분석
def analyze_seo(title, content, keyword):
    score = 0
    feedback = []
    improvements = []
    
    # 1. 제목 키워드
    if keyword.lower() in title.lower():
        score += 20
        feedback.append("✅ 제목에 키워드 포함")
    else:
        feedback.append("❌ 제목에 키워드 추가 필요")
        improvements.append(f"제목 앞부분에 '{keyword}' 추가")
    
    # 2. 제목 길이
    if 15 <= len(title) <= 40:
        score += 10
        feedback.append("✅ 제목 길이 적절")
    else:
        feedback.append(f"⚠️ 제목 길이 조정 ({len(title)}자)")
        improvements.append("제목을 25-35자로 조정")
    
    # 3. 본문 글자수
    content_length = len(content)
    if 1500 <= content_length <= 3000:
        score += 15
        feedback.append(f"✅ 본문 적절 ({content_length}자)")
    else:
        feedback.append(f"⚠️ 본문 조정 ({content_length}자)")
        if content_length < 1500:
            improvements.append(f"본문을 {1500 - content_length}자 더 작성")
    
    # 4. 키워드 밀도
    keyword_count = content.lower().count(keyword.lower())
    if 3 <= keyword_count <= 7:
        score += 20
        feedback.append(f"✅ 키워드 밀도 적절 ({keyword_count}회)")
    else:
        feedback.append(f"⚠️ 키워드 조정 ({keyword_count}회)")
        if keyword_count < 3:
            improvements.append(f"본문에 '{keyword}' 키워드 {3 - keyword_count}회 더 추가")
    
    # 5. 소제목
    subtitle_count = content.count("##")
    if subtitle_count >= 3:
        score += 10
        feedback.append(f"✅ 소제목 충분 ({subtitle_count}개)")
    else:
        feedback.append(f"⚠️ 소제목 추가 ({subtitle_count}개)")
        improvements.append("물음표나 느낌표로 된 소제목 3개 이상 추가")
    
    # 6. 이모지
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        "]+", flags=re.UNICODE)
    
    if emoji_pattern.search(content):
        score += 10
        feedback.append("✅ 이모지 사용")
    else:
        feedback.append("⚠️ 이모지 추가")
        improvements.append("적절한 위치에 이모지 3-5개 추가 (😊, 👍, ✨)")
    
    # 7. 해시태그
    if "#" in content:
        score += 15
        feedback.append("✅ 해시태그 포함")
    else:
        feedback.append("⚠️ 해시태그 추가")
        improvements.append("본문 끝에 관련 해시태그 10개 추가")
    
    return score, feedback, improvements

# 올인원 최적화 생성 (진짜 자동)
def generate_optimized_post(keyword, category, word_count, claude_api_key):
    """키워드만 입력 → 자동으로 제목 최적화 + SEO 100점 목표 글 생성"""
    
    try:
        client = anthropic.Anthropic(api_key=claude_api_key)
        
        # 한 번에 모든 최적화를 AI에게 지시
        prompt = f"""네이버 블로그 글을 SEO 100점 목표로 작성해주세요.

키워드: {keyword}
카테고리: {category}
목표 글자수: {word_count}자

📋 필수 요구사항 (반드시 모두 충족):

1. 제목 (25-35자):
   - 반드시 키워드 "{keyword}" 포함
   - 숫자 포함 (5가지, 10분, 200% 등)
   - 감탄사/의문사 (꿀팁, 대박, 진짜?, 비결은?)
   - 예: "{keyword} 꿀팁 5가지! 초보도 10분이면 끝"

2. 본문 ({word_count}자 이상):
   - 첫 문장: "안녕하세요. 영화 프로듀서의 블로그, CINEPARK입니다."
   - 키워드 "{keyword}" 정확히 5-7회 자연스럽게 포함
   - 소제목 3-5개 (모두 물음표? 또는 느낌표! 필수)
   - 각 소제목 아래 2-3 문단
   - 이모지 3-5개 사용 (😊, 👍, ✨, 💡, 🔥)
   - 자연스러운 블로그 말투 (~했어요, ~더라고요, ~네요)

3. 해시태그:
   - 본문 끝에 #{keyword} 포함 총 10개

출력 형식 (정확히 따를 것):

## [클릭 유도 제목]

안녕하세요. 영화 프로듀서의 블로그, CINEPARK입니다.

[도입부 - {keyword} 언급]

## [물음표/느낌표 소제목1]
[본문 - {keyword} 포함]

## [물음표/느낌표 소제목2]
[본문 - {keyword} 포함]

## [물음표/느낌표 소제목3]
[본문 - {keyword} 포함]

## [물음표/느낌표 소제목4] (선택)
[본문]

## 태그
#{keyword} #관련태그1 #관련태그2 #관련태그3 #관련태그4 #관련태그5 #관련태그6 #관련태그7 #관련태그8 #관련태그9

지금 바로 작성 시작!"""
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )
        
        generated_content = message.content[0].text
        
        # 제목 추출
        title_match = re.search(r'##\s*(.+?)(?:\n|$)', generated_content)
        title = title_match.group(1).strip() if title_match else keyword
        
        # 책 홍보 추가
        final_content = generated_content + f"""

---

## 📚 제 저서를 소개합니다

<img src="{BOOK_INFO['cover_url']}" alt="{BOOK_INFO['title']}" width="200">

**제목**: [{BOOK_INFO['title']}]({BOOK_INFO['link']})  
**저자**: {BOOK_INFO['authors']}  
**출판사**: {BOOK_INFO['publisher']}

많은 다운로드를 부탁합니다. 꾸벅 🙇
"""
        
        # SEO 자동 분석
        score, feedback, improvements = analyze_seo(title, final_content, keyword)
        
        # 점수가 80점 미만이면 자동 재생성 (1회)
        if score < 80:
            retry_prompt = f"""이전 글의 SEO 점수가 {score}점입니다. 다음 사항을 개선해서 다시 작성해주세요:

{chr(10).join(improvements)}

키워드: {keyword}
카테고리: {category}
목표: SEO 80점 이상

이전과 동일한 형식으로 작성하되, 위 개선사항을 반드시 반영하세요."""
            
            retry_message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": generated_content},
                    {"role": "user", "content": retry_prompt}
                ]
            )
            
            generated_content = retry_message.content[0].text
            
            # 다시 제목 추출
            title_match = re.search(r'##\s*(.+?)(?:\n|$)', generated_content)
            title = title_match.group(1).strip() if title_match else keyword
            
            # 책 홍보 다시 추가
            final_content = generated_content + f"""

---

## 📚 제 저서를 소개합니다

<img src="{BOOK_INFO['cover_url']}" alt="{BOOK_INFO['title']}" width="200">

**제목**: [{BOOK_INFO['title']}]({BOOK_INFO['link']})  
**저자**: {BOOK_INFO['authors']}  
**출판사**: {BOOK_INFO['publisher']}

많은 다운로드를 부탁합니다. 꾸벅 🙇
"""
            
            # 재분석
            score, feedback, improvements = analyze_seo(title, final_content, keyword)
        
        return {
            "title": title,
            "content": final_content,
            "seo_score": score,
            "feedback": feedback,
            "improvements": improvements
        }
        
    except Exception as e:
        return {"error": str(e)}

# 이미지
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
    return {"url": f"https://picsum.photos/1200/800?random={hash(keyword)%1000}", "source": "Picsum"}

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
    .main .block-container { max-width: 1400px !important; padding: 1rem 2rem !important; margin: 0 auto !important; }
    .stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important; }
    
    .hero-section {
        background: white;
        border-radius: 20px;
        padding: 3rem;
        margin-bottom: 2rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }
    
    .hero-title {
        color: #191970;
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .feature-card {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        font-size: 1.1rem !important;
        border-radius: 10px !important;
        width: 100% !important;
    }
    
    .score-display {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
    }
    
    .score-number {
        font-size: 4rem;
        font-weight: 800;
        margin: 0;
    }
</style>
""", unsafe_allow_html=True)

# 히어로 섹션
st.markdown("""
<div class="hero-section">
    <div style="display: flex; align-items: center; gap: 3rem;">
        <div style="flex: 1;">
            <h1 class="hero-title">✍️ AutoPost 올인원</h1>
            <p style="text-align: center; color: #666; font-size: 1.3rem;">
                키워드 하나만 입력하세요<br>
                <span style="color: #667eea; font-weight: 600;">제목 최적화 + SEO 분석 + 완벽한 글 자동 생성</span>
            </p>
        </div>
        <div style="flex: 1; text-align: center;">
            <img src="https://raw.githubusercontent.com/cinepark-1974/AutoPost/main/assets/hero_image.png" 
                 style="max-width: 100%; border-radius: 15px;">
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# API 키 설정 (상단에 고정)
st.markdown('<div class="feature-card">', unsafe_allow_html=True)
st.markdown("### ⚙️ API 키 설정")

col_api1, col_api2 = st.columns([3, 1])

with col_api1:
    saved_key = load_api_key()
    api_key_input = st.text_input(
        "Claude API Key", 
        value=saved_key,
        type="password",
        help="console.anthropic.com에서 발급",
        key="api_key_input"
    )

with col_api2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💾 저장", key="save_key"):
        if api_key_input:
            save_api_key(api_key_input)
            st.success("✅ 저장 완료!")
        else:
            st.error("키를 입력하세요")

if saved_key:
    st.info(f"✅ API 키 저장됨: {saved_key[:10]}...")

st.markdown('</div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# 메인: 올인원 글 생성
st.markdown('<div class="feature-card">', unsafe_allow_html=True)
st.markdown("### 🚀 올인원 자동 생성")
st.info("💡 키워드만 입력하면 제목 최적화 → SEO 분석 → 완벽한 글 자동 생성!")

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    keyword = st.text_input(
        "키워드 입력",
        placeholder="예: 주식 초보 추천, 부산 맛집, ChatGPT 활용",
        key="main_keyword"
    )

with col2:
    category = st.selectbox(
        "카테고리",
        ["영화", "책", "주식", "맛집", "여행", "IT", "일상", "건강", "요리"],
        key="main_category"
    )

with col3:
    word_count = st.slider(
        "목표 글자수",
        1500, 3000, 2000, 100,
        key="main_wordcount"
    )

st.markdown("<br>", unsafe_allow_html=True)

if st.button("🎯 완벽한 글 자동 생성", type="primary", key="generate_all"):
    
    claude_key = load_api_key()
    
    if not claude_key:
        st.error("⚠️ API 키를 먼저 저장해주세요!")
    elif not keyword:
        st.error("⚠️ 키워드를 입력해주세요!")
    else:
        # 프로그레스 바
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1: 제목 생성
        status_text.text("1/4 최적화된 제목 생성 중...")
        progress_bar.progress(25)
        
        # Step 2: 본문 생성
        status_text.text("2/4 SEO 최적화된 본문 생성 중...")
        progress_bar.progress(50)
        
        # Step 3: SEO 분석
        status_text.text("3/4 SEO 점수 분석 중...")
        progress_bar.progress(75)
        
        # 실제 생성
        result = generate_optimized_post(keyword, category, word_count, claude_key)
        
        # Step 4: 이미지 생성
        status_text.text("4/4 이미지 생성 중...")
        progress_bar.progress(100)
        
        if "error" in result:
            st.error(f"❌ 오류: {result['error']}")
        else:
            status_text.text("✅ 완성!")
            progress_bar.empty()
            
            # SEO 점수 표시
            st.markdown(f"""
            <div class="score-display">
                <div class="score-number">{result['seo_score']}</div>
                <div style="font-size: 1.5rem;">/ 100점</div>
                <div style="margin-top: 1rem; font-size: 1.1rem;">
                    {"🏆 우수! 상위 노출 가능" if result['seo_score'] >= 80 else 
                     "👍 양호! 약간 개선 필요" if result['seo_score'] >= 60 else 
                     "⚠️ 개선 필요"}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # SEO 피드백
            st.markdown("### 📊 SEO 분석 결과")
            for fb in result['feedback']:
                st.markdown(f"- {fb}")
            
            # 개선 사항 (점수가 낮을 때만)
            if result['seo_score'] < 80 and result['improvements']:
                st.markdown("### 💡 개선 사항")
                for imp in result['improvements']:
                    st.markdown(f"- {imp}")
            
            st.markdown("---")
            
            # 이미지
            image_info = get_free_image(keyword)
            st.image(image_info['url'], caption=f"출처: {image_info['source']}", use_container_width=True)
            
            # 생성된 글
            st.markdown("### 📄 생성된 글")
            st.markdown(result['content'])
            
            # 다운로드
            col_d1, col_d2 = st.columns(2)
            
            with col_d1:
                st.download_button(
                    "💾 텍스트로 저장",
                    result['content'],
                    file_name=f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
            
            with col_d2:
                # 분석 리포트 생성
                report = f"""AutoPost 생성 리포트
===================

키워드: {keyword}
카테고리: {category}
생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SEO 점수: {result['seo_score']}/100

제목: {result['title']}

SEO 분석:
{chr(10).join(result['feedback'])}

{chr(10).join(['개선 사항:', *result['improvements']]) if result['improvements'] else ''}

==================
{result['content']}
"""
                st.download_button(
                    "📊 리포트 다운로드",
                    report,
                    file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; padding: 2rem; color: white; margin-top: 3rem;">
    <p style="font-size: 1.1rem; margin-bottom: 0.5rem;">Made with ❤️ by CINEPARK</p>
    <p style="opacity: 0.8;">AutoPost v4.0 - 올인원 완전 자동화</p>
</div>
""", unsafe_allow_html=True)
