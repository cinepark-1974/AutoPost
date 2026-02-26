import streamlit as st
import anthropic
import requests
from datetime import datetime
import json
import re

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
    st.session_state['saved_api_key'] = key
    return True

def load_api_key():
    if 'saved_api_key' in st.session_state:
        return st.session_state['saved_api_key']
    return ""

# SEO 분석
def analyze_seo(title, content, keyword):
    score = 0
    feedback = []
    improvements = []
    
    if keyword.lower() in title.lower():
        score += 20
        feedback.append("✅ 제목에 키워드 포함")
    else:
        feedback.append("❌ 제목에 키워드 추가")
        improvements.append(f"제목에 '{keyword}' 추가")
    
    if 15 <= len(title) <= 40:
        score += 10
        feedback.append("✅ 제목 길이 적절")
    else:
        feedback.append(f"⚠️ 제목 길이 조정 ({len(title)}자)")
        improvements.append("제목 25-35자로 조정")
    
    content_length = len(content)
    if 1500 <= content_length <= 3000:
        score += 15
        feedback.append(f"✅ 본문 적절 ({content_length}자)")
    else:
        feedback.append(f"⚠️ 본문 조정 ({content_length}자)")
        if content_length < 1500:
            improvements.append(f"본문 {1500 - content_length}자 추가")
    
    keyword_count = content.lower().count(keyword.lower())
    if 3 <= keyword_count <= 7:
        score += 20
        feedback.append(f"✅ 키워드 밀도 적절 ({keyword_count}회)")
    else:
        feedback.append(f"⚠️ 키워드 조정 ({keyword_count}회)")
        if keyword_count < 3:
            improvements.append(f"'{keyword}' {3 - keyword_count}회 추가")
    
    subtitle_count = content.count("##")
    if subtitle_count >= 3:
        score += 10
        feedback.append(f"✅ 소제목 충분 ({subtitle_count}개)")
    else:
        feedback.append(f"⚠️ 소제목 추가")
        improvements.append("소제목 3개 이상 추가")
    
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
        improvements.append("이모지 3-5개 추가")
    
    if "#" in content:
        score += 15
        feedback.append("✅ 해시태그 포함")
    else:
        feedback.append("⚠️ 해시태그 추가")
        improvements.append("해시태그 10개 추가")
    
    return score, feedback, improvements

# 올인원 자동 생성
def generate_optimized_post(keyword, category, word_count, claude_api_key):
    try:
        client = anthropic.Anthropic(api_key=claude_api_key)
        
        prompt = f"""네이버 블로그 글을 SEO 100점 목표로 작성해주세요.

키워드: {keyword}
카테고리: {category}
목표 글자수: {word_count}자

📋 필수 요구사항:

1. 제목 (25-35자):
   - "{keyword}" 포함
   - 숫자 포함 (5가지, 10분)
   - 감탄사 (꿀팁, 대박)

2. 본문 ({word_count}자 이상):
   - 시작: "안녕하세요. 영화 프로듀서의 블로그, CINEPARK입니다."
   - "{keyword}" 5-7회 포함
   - 소제목 3-5개 (물음표/느낌표)
   - 이모지 3-5개
   - 블로그 말투

3. 해시태그 10개

출력:
## [제목]

안녕하세요. 영화 프로듀서의 블로그, CINEPARK입니다.

[본문...]

## 태그
#{keyword} #태그들"""
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )
        
        generated_content = message.content[0].text
        
        title_match = re.search(r'##\s*(.+?)(?:\n|$)', generated_content)
        title = title_match.group(1).strip() if title_match else keyword
        
        final_content = generated_content + f"""

---

## 📚 제 저서를 소개합니다

<img src="{BOOK_INFO['cover_url']}" alt="{BOOK_INFO['title']}" width="200">

**제목**: [{BOOK_INFO['title']}]({BOOK_INFO['link']})  
**저자**: {BOOK_INFO['authors']}  
**출판사**: {BOOK_INFO['publisher']}

많은 다운로드를 부탁합니다. 꾸벅 🙇
"""
        
        score, feedback, improvements = analyze_seo(title, final_content, keyword)
        
        if score < 80:
            retry_prompt = f"""SEO {score}점입니다. 개선해서 다시:

{chr(10).join(improvements)}

키워드: {keyword}
목표: 80점 이상"""
            
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
            title_match = re.search(r'##\s*(.+?)(?:\n|$)', generated_content)
            title = title_match.group(1).strip() if title_match else keyword
            
            final_content = generated_content + f"""

---

## 📚 제 저서를 소개합니다

<img src="{BOOK_INFO['cover_url']}" alt="{BOOK_INFO['title']}" width="200">

**제목**: [{BOOK_INFO['title']}]({BOOK_INFO['link']})  
**저자**: {BOOK_INFO['authors']}  
**출판사**: {BOOK_INFO['publisher']}

많은 다운로드를 부탁합니다. 꾸벅 🙇
"""
            
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

# 이미지 생성
def generate_sd_image(keyword, hf_token):
    """Stable Diffusion으로 이미지 생성"""
    try:
        API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
        headers = {"Authorization": f"Bearer {hf_token}"}
        
        prompt = f"{keyword}, high quality, detailed, professional photography, 8k"
        
        response = requests.post(
            API_URL,
            headers=headers,
            json={"inputs": prompt},
            timeout=60
        )
        
        if response.status_code == 200:
            from PIL import Image
            import io
            image = Image.open(io.BytesIO(response.content))
            return {"image": image, "source": "Stable Diffusion XL"}
        
        return None
    except:
        return None

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

# CSS (깔끔한 흰색 디자인)
st.markdown("""
<style>
    /* 기본 */
    [data-testid="stSidebar"] { display: none !important; }
    .main .block-container { 
        max-width: 900px !important; 
        padding: 2rem 1rem !important; 
        margin: 0 auto !important; 
    }
    .stApp { 
        background: #ffffff !important; 
    }
    
    /* 헤더 */
    h1 {
        color: #191970 !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 0.5rem !important;
    }
    
    h2 {
        color: #191970 !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
    }
    
    h3 {
        color: #4a4a4a !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }
    
    /* 버튼 */
    .stButton > button[kind="primary"] {
        background: #191970 !important;
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        border-radius: 8px !important;
        width: 100% !important;
        font-size: 1rem !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: #252d7a !important;
        box-shadow: 0 4px 12px rgba(25, 25, 112, 0.25) !important;
    }
    
    .stButton > button {
        background: white !important;
        color: #191970 !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
    }
    
    /* 입력 필드 */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div,
    .stTextArea > div > div > textarea {
        border: 1px solid #e0e0e0 !important;
        border-radius: 8px !important;
        padding: 0.75rem !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #191970 !important;
        box-shadow: 0 0 0 1px #191970 !important;
    }
    
    /* 라벨 */
    .stTextInput > label,
    .stSelectbox > label,
    .stTextArea > label,
    .stSlider > label {
        color: #4a4a4a !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
    }
    
    /* 카드 */
    .info-card {
        background: #f8f9fa;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    /* SEO 점수 */
    .seo-score {
        text-align: center;
        background: #f8f9fa;
        border: 2px solid #e0e0e0;
        border-radius: 12px;
        padding: 2rem;
        margin: 2rem 0;
    }
    
    .score-number {
        font-size: 4rem;
        font-weight: 800;
        color: #191970;
        margin: 0;
    }
    
    .score-label {
        font-size: 1.2rem;
        color: #666;
        margin-top: 0.5rem;
    }
    
    /* 성공/경고 메시지 */
    .stSuccess {
        background-color: #f0f9f4 !important;
        border-left: 4px solid #10b981 !important;
        color: #065f46 !important;
    }
    
    .stWarning {
        background-color: #fffbeb !important;
        border-left: 4px solid #f59e0b !important;
        color: #92400e !important;
    }
    
    .stError {
        background-color: #fef2f2 !important;
        border-left: 4px solid #ef4444 !important;
        color: #991b1b !important;
    }
    
    .stInfo {
        background-color: #eff6ff !important;
        border-left: 4px solid #3b82f6 !important;
        color: #1e40af !important;
    }
    
    /* 슬라이더 */
    .stSlider > div > div > div > div {
        background-color: #191970 !important;
    }
    
    /* 구분선 */
    hr {
        border: none;
        border-top: 1px solid #e0e0e0;
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# 헤더
st.markdown("""
<div style="text-align: center; padding: 2rem 0 3rem 0;">
    <h1 style="margin-bottom: 0.5rem;">✍️ AutoPost</h1>
    <p style="font-size: 1.2rem; color: #666; margin: 0;">
        AI 블로그 자동화 툴
    </p>
    <p style="font-size: 0.95rem; color: #999; margin-top: 0.5rem;">
        키워드만 입력하면 SEO 최적화된 완벽한 글 자동 생성
    </p>
</div>
""", unsafe_allow_html=True)

# 히어로 이미지
try:
    st.image(HERO_IMAGE, use_container_width=True)
except:
    pass

st.markdown("<br>", unsafe_allow_html=True)

# API 키 설정
with st.expander("⚙️ API 설정", expanded=False):
    col1, col2 = st.columns([4, 1])
    with col1:
        saved_key = load_api_key()
        api_key = st.text_input(
            "Claude API Key",
            value=saved_key,
            type="password",
            placeholder="sk-ant-api03-..."
        )
    with col2:
        st.markdown("<div style='padding-top: 1.8rem;'></div>", unsafe_allow_html=True)
        if st.button("저장"):
            if api_key:
                save_api_key(api_key)
                st.success("✅ 저장됨")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # HuggingFace Token (선택사항)
    hf_token = st.text_input(
        "HuggingFace Token (AI 이미지 생성용 - 선택)",
        type="password",
        placeholder="hf_xxxxx",
        help="huggingface.co에서 무료 발급. 입력하면 Stable Diffusion으로 이미지 생성"
    )

st.markdown("<br><br>", unsafe_allow_html=True)

# 메인
st.markdown("## 🚀 글 자동 생성")

col1, col2 = st.columns([2, 1])

with col1:
    keyword = st.text_input(
        "키워드",
        placeholder="예: 주식 초보 추천, 부산 맛집"
    )

with col2:
    category = st.selectbox(
        "카테고리",
        ["영화", "책", "주식", "맛집", "여행", "IT", "일상", "건강", "요리"]
    )

word_count = st.slider("목표 글자수", 1500, 3000, 2000, 100)

col_img1, col_img2 = st.columns([3, 1])
with col_img1:
    include_image = st.checkbox("AI 이미지 생성", value=True, help="Pexels에서 자동으로 이미지 검색")
with col_img2:
    pass

st.markdown("<br>", unsafe_allow_html=True)

if st.button("생성하기", type="primary"):
    claude_key = load_api_key()
    
    if not claude_key:
        st.error("⚠️ API 키를 먼저 저장해주세요")
    elif not keyword:
        st.error("⚠️ 키워드를 입력해주세요")
    else:
        progress = st.progress(0)
        status = st.empty()
        
        status.text("제목 최적화 중...")
        progress.progress(33)
        
        status.text("본문 생성 중...")
        progress.progress(66)
        
        result = generate_optimized_post(keyword, category, word_count, claude_key)
        
        status.text("SEO 분석 중...")
        progress.progress(100)
        
        if "error" in result:
            st.error(f"❌ {result['error']}")
        else:
            status.empty()
            progress.empty()
            
            # SEO 점수
            st.markdown(f"""
            <div class="seo-score">
                <div class="score-number">{result['seo_score']}</div>
                <div class="score-label">/ 100점</div>
                <div style="margin-top: 1rem; font-size: 1.1rem; color: #666;">
                    {"🏆 상위 노출 가능" if result['seo_score'] >= 80 else 
                     "👍 양호" if result['seo_score'] >= 60 else "⚠️ 개선 필요"}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 피드백
            st.markdown("### 📊 분석 결과")
            for fb in result['feedback']:
                st.markdown(f"- {fb}")
            
            if result['improvements']:
                st.markdown("### 💡 개선 사항")
                for imp in result['improvements']:
                    st.markdown(f"- {imp}")
            
            st.markdown("---")
            
            # 이미지 (체크박스로 선택한 경우만)
            if include_image:
                st.markdown("### 🖼️ AI 생성 이미지")
                
                # HuggingFace Token이 있으면 Stable Diffusion 시도
                if hf_token:
                    with st.spinner("AI가 이미지를 생성하는 중... (30-60초)"):
                        sd_result = generate_sd_image(keyword, hf_token)
                        if sd_result and 'image' in sd_result:
                            st.image(sd_result['image'], caption=f"출처: {sd_result['source']}", use_container_width=True)
                        else:
                            st.info("💡 AI 이미지 생성 실패. 무료 이미지로 대체합니다.")
                            image_info = get_free_image(keyword)
                            st.image(image_info['url'], caption=f"출처: {image_info['source']}", use_container_width=True)
                else:
                    # Token 없으면 무료 이미지
                    image_info = get_free_image(keyword)
                    st.image(image_info['url'], caption=f"출처: {image_info['source']}", use_container_width=True)
                    st.info("💡 HuggingFace Token을 입력하면 AI로 이미지를 생성할 수 있습니다.")
            
            # 글
            st.markdown("### 📄 생성된 글")
            st.markdown(result['content'])
            
            # 다운로드
            st.download_button(
                "💾 다운로드",
                result['content'],
                file_name=f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            )

# Footer
st.markdown("""
<div style="text-align: center; padding: 3rem 0 2rem 0; color: #999; border-top: 1px solid #e0e0e0; margin-top: 4rem;">
    <p style="margin: 0;">Made with ❤️ by CINEPARK</p>
    <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">AutoPost v4.0</p>
</div>
""", unsafe_allow_html=True)
