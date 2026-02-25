import streamlit as st
import anthropic
import requests
from datetime import datetime
import json
from PIL import Image
from io import BytesIO
import time

# 상수 정의 - 책 정보 (고정)
BOOK_INFO = {
    "cover_url": "https://contents.kyobobook.co.kr/sih/fit-in/458x0/pdt/E000012093207.jpg",
    "title": "감각구역",
    "authors": "문성주, 박현",
    "publisher": "마카롱(교보문고)",
    "link": "https://ebook-product.kyobobook.co.kr/dig/epd/ebook/E000012093207"
}

# Stable Diffusion 이미지 생성
def generate_sd_image(keyword, hf_token):
    """Hugging Face Stable Diffusion으로 이미지 생성"""
    try:
        if not hf_token:
            return {
                "url": f"https://source.unsplash.com/1200x800/?{keyword}",
                "source": "Unsplash (API 키 없음)"
            }
        
        API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
        headers = {"Authorization": f"Bearer {hf_token}"}
        
        prompt = f"professional high-quality photograph, {keyword}, cinematic lighting, detailed, realistic, 8k"
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "negative_prompt": "low quality, blurry, distorted, ugly, text, watermark",
                "num_inference_steps": 25
            }
        }
        
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            
            # BytesIO로 저장
            img_bytes = BytesIO()
            image.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            return {
                "image": image,
                "bytes": img_bytes,
                "source": "Stable Diffusion XL (AI 생성)"
            }
        else:
            # 실패 시 Unsplash로 대체
            return {
                "url": f"https://source.unsplash.com/1200x800/?{keyword}",
                "source": "Unsplash (대체)"
            }
            
    except Exception as e:
        st.warning(f"이미지 생성 실패: {str(e)}")
        return {
            "url": f"https://source.unsplash.com/1200x800/?{keyword}",
            "source": "Unsplash (오류 대체)"
        }

# 책 홍보 섹션 생성
def add_book_promotion():
    """고정된 책 홍보 마크다운"""
    return f"""

---

## 📚 제 저서를 소개합니다

![{BOOK_INFO['title']}]({BOOK_INFO['cover_url']})

**제목**: [{BOOK_INFO['title']}]({BOOK_INFO['link']})  
**저자**: {BOOK_INFO['authors']}  
**출판사**: {BOOK_INFO['publisher']}

많은 다운로드를 부탁합니다. 꾸벅 🙇
"""

# 세션 스테이트 초기화
if 'saved_posts' not in st.session_state:
    st.session_state.saved_posts = []

if 'image_count' not in st.session_state:
    st.session_state.image_count = 0

# 페이지 설정
st.set_page_config(
    page_title="AutoPost - 블로그 포스팅 자동화 툴",
    page_icon="✍️",
    layout="wide"
)

# 커스텀 CSS
st.markdown("""
<style>
    @font-face {
        font-family: 'Paybooc';
        src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_2001@1.1/Paybooc.woff') format('woff');
        font-weight: normal;
        font-style: normal;
    }
    
    * {
        font-family: 'Paybooc', 'Apple SD Gothic Neo', sans-serif !important;
    }
    
    .main {
        background-color: #f8f9fd !important;
    }
    
    .stApp {
        background-color: #f8f9fd !important;
    }
    
    [data-testid="stAppViewContainer"] {
        background-color: #f8f9fd !important;
    }
    
    header[data-testid="stHeader"] {
        background-color: #f8f9fd !important;
    }
    
    h1 {
        color: #191970 !important;
        font-weight: 700 !important;
    }
    
    h2, h3 {
        color: #191970 !important;
    }
    
    .stButton > button {
        border: 2px solid #ffcb05 !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background-color: #ffcb05 !important;
        color: #191970 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(255, 203, 5, 0.3) !important;
    }
    
    .stButton > button[kind="primary"] {
        background-color: #ffcb05 !important;
        color: #191970 !important;
        border: none !important;
    }
    
    .stButton > button[kind="secondary"] {
        background-color: #191970 !important;
        color: #ffffff !important;
        border: 2px solid #ffcb05 !important;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #e8ecf7 0%, #f8f9fd 100%) !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #e8ecf7;
        color: #191970;
        border-radius: 8px 8px 0 0;
        padding: 12px 24px;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #ffcb05 !important;
    }
    
    .stSuccess {
        background-color: #fffbea !important;
        border-left: 4px solid #ffcb05 !important;
    }
</style>
""", unsafe_allow_html=True)

# 제목
st.markdown("""
<h1 style='text-align: center; padding: 20px 0;'>
    ✍️ AutoPost
    <span style='color: #ffcb05;'>AI 블로그 자동화</span>
</h1>
""", unsafe_allow_html=True)

st.markdown("""
<p style='text-align: center; color: #191970; font-size: 16px; margin-bottom: 30px;'>
    Claude AI + Stable Diffusion | 네이버 블로그 자동 포스팅
</p>
""", unsafe_allow_html=True)

# 사이드바
with st.sidebar:
    st.header("⚙️ API 설정")
    
    # Claude API Key
    try:
        if hasattr(st, 'secrets') and "CLAUDE_API_KEY" in st.secrets:
            claude_api_key = st.secrets["CLAUDE_API_KEY"]
            st.success("✅ Claude API Key 자동 로드")
        else:
            claude_api_key = st.text_input(
                "Claude API Key",
                type="password",
                help="console.anthropic.com에서 발급"
            )
    except:
        claude_api_key = st.text_input(
            "Claude API Key",
            type="password",
            help="console.anthropic.com에서 발급"
        )
    
    # Hugging Face Token
    try:
        if hasattr(st, 'secrets') and "HUGGINGFACE_TOKEN" in st.secrets:
            hf_token = st.secrets["HUGGINGFACE_TOKEN"]
            st.success("✅ Hugging Face Token 자동 로드")
        else:
            hf_token = st.text_input(
                "Hugging Face Token (이미지 생성)",
                type="password",
                help="huggingface.co에서 무료 발급"
            )
    except:
        hf_token = None
    
    st.divider()
    
    # 네이버 API
    st.subheader("네이버 블로그 API")
    
    try:
        if hasattr(st, 'secrets') and "NAVER_BLOG_ID" in st.secrets:
            naver_blog_id = st.secrets["NAVER_BLOG_ID"]
            st.success("✅ Blog ID 자동 로드")
        else:
            naver_blog_id = st.text_input(
                "블로그 ID",
                placeholder="cinepark"
            )
    except:
        naver_blog_id = st.text_input(
            "블로그 ID",
            placeholder="cinepark"
        )
    
    st.divider()
    
    # 통계
    st.metric("오늘 생성 이미지", st.session_state.image_count)
    st.metric("저장된 글", len(st.session_state.saved_posts))
    
    st.caption("💡 Secrets에 API 키 저장 권장")

# 메인 탭
tab1, tab2, tab3, tab4 = st.tabs(["📝 글 생성", "📚 저장된 글", "📊 통계", "ℹ️ 사용법"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📝 콘텐츠 설정")
        
        category = st.selectbox(
            "주제 카테고리",
            ["영화 리뷰", "책 리뷰", "주식", "맛집 후기", "여행 후기", 
             "IT/기술", "일상/에세이", "건강/운동", "요리/레시피", "자유 주제"]
        )
        
        keyword = st.text_input(
            "키워드 입력",
            placeholder="예: 4차 상법 개정, 부산 맛집, ChatGPT"
        )
        
        writing_style = st.radio(
            "글 스타일",
            ["정보 전달형 (팩트 중심)", "후기/리뷰형 (경험 중심)", "스토리텔링형 (감성적)"]
        )
        
        word_count = st.slider("글 길이 (자)", 1000, 3000, 2000, 500)
    
    with col2:
        st.markdown("### 🎯 SEO 설정")
        
        include_hashtags = st.checkbox("해시태그 자동 생성", value=True)
        include_news = st.checkbox("최신 화제 검색 🔥", value=True)
        
        st.divider()
        
        st.markdown("### 🖼️ 이미지 설정")
        include_image = st.checkbox("AI 이미지 생성", value=True, 
                                     help="Stable Diffusion으로 생성 (30-60초 소요)")
        
        keyword_density = st.slider("키워드 밀도", 3, 10, 5)
    
    st.divider()
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
    
    with col_btn1:
        generate_button = st.button("🤖 글 생성", type="primary", use_container_width=True)
    
    with col_btn2:
        auto_post_button = st.button("🚀 생성 + 자동발행", type="secondary", use_container_width=True)
    
    # 글 생성 로직
    if generate_button or auto_post_button:
        if not claude_api_key:
            st.error("⚠️ Claude API Key를 입력해주세요!")
        elif not keyword:
            st.error("⚠️ 키워드를 입력해주세요!")
        else:
            with st.spinner("AI가 최적화된 블로그 글을 작성 중입니다..."):
                try:
                    # 최신 뉴스 검색
                    recent_news = ""
                    if include_news:
                        try:
                            import urllib.parse
                            search_url = f"https://news.google.com/rss/search?q={urllib.parse.quote(keyword)}&hl=ko&gl=KR&ceid=KR:ko"
                            news_response = requests.get(search_url, timeout=5)
                            
                            if news_response.status_code == 200:
                                import xml.etree.ElementTree as ET
                                root = ET.fromstring(news_response.content)
                                items = root.findall('.//item')
                                
                                if items:
                                    recent_titles = [item.find('title').text for item in items[:3]]
                                    recent_news = f"\n\n최근 '{keyword}' 관련 화제:\n" + "\n".join([f"- {title}" for title in recent_titles])
                        except:
                            pass
                    
                    # Claude API 호출
                    client = anthropic.Anthropic(api_key=claude_api_key)
                    
                    style_instruction = {
                        "정보 전달형 (팩트 중심)": "정확한 정보와 데이터를 바탕으로 객관적으로 작성",
                        "후기/리뷰형 (경험 중심)": "개인적인 경험과 느낌을 중심으로 작성",
                        "스토리텔링형 (감성적)": "감성적이고 이야기하듯이 작성"
                    }
                    
                    prompt = f"""당신은 인기 블로거입니다. 네이버 블로그에 올릴 글을 작성해주세요.

📌 기본 정보:
- 주제: {category}
- 키워드: {keyword}
- 스타일: {style_instruction[writing_style]}
- 목표 글자 수: {word_count}자
{recent_news}

✍️ 글쓰기 원칙:

1. **자연스러운 시작**
   - "안녕하세요. 영화 프로듀서의 블로그, CINEPARK입니다."로 시작
   - 한 줄 띄고 최신 화제나 흥미로운 도입부로 시작
   - 예: "요즘 {keyword} 관련해서 화제네요!"

2. **블로그 말투**
   - 반말 또는 존댓말 자연스럽게
   - "~했어요", "~더라고요", "~네요" 활용
   - 이모지 적절히 사용 (😊, 👍, ✨)

3. **구조**
   - 소제목은 물음표나 느낌표로 (예: "그래서 결과는?")
   - 짧은 문단 (2-3줄씩)

4. **키워드**
   - "{keyword}"를 {keyword_density}회 자연스럽게 언급

5. **마무리**
   - 자연스러운 마무리 (책 홍보는 시스템이 자동 추가)

출력 형식:
## 제목
[SEO 최적화된 제목]

안녕하세요. 영화 프로듀서의 블로그, CINEPARK입니다.

[도입부...]

## [소제목1]
[내용...]

## 태그
#태그1 #태그2 #태그3 #태그4 #태그5

❌ 금지: "들어가며", "본문", "서론", "결론", "마무리"
✅ 권장: 물음표, 느낌표, 이모지, 자연스러운 톤
"""
                    
                    message = client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=4000,
                        temperature=0.7,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    
                    generated_content = message.content[0].text
                    
                    # 책 홍보 자동 추가
                    generated_content += add_book_promotion()
                    
                    # 이미지 생성
                    image_info = None
                    if include_image:
                        with st.spinner("AI가 이미지를 생성 중입니다... (30-60초 소요)"):
                            image_info = generate_sd_image(keyword, hf_token)
                            if image_info:
                                st.session_state.image_count += 1
                    
                    # 저장
                    post_data = {
                        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "keyword": keyword,
                        "category": category,
                        "content": generated_content,
                        "image_info": image_info,
                        "word_count": len(generated_content)
                    }
                    st.session_state.saved_posts.insert(0, post_data)
                    
                    # 결과 표시
                    st.success("✅ 글 생성 완료!")
                    
                    # 이미지 표시
                    if image_info:
                        if 'image' in image_info:
                            st.image(image_info['image'], caption=f"생성: {image_info['source']}", use_container_width=True)
                        elif 'url' in image_info:
                            st.image(image_info['url'], caption=f"출처: {image_info['source']}", use_container_width=True)
                    
                    # 콘텐츠 표시
                    st.markdown("---")
                    st.markdown("### 📄 생성된 콘텐츠")
                    st.markdown(generated_content)
                    
                    # 다운로드
                    st.download_button(
                        label="💾 텍스트로 저장",
                        data=generated_content,
                        file_name=f"autopost_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
                    
                    # 이미지 다운로드
                    if image_info and 'bytes' in image_info:
                        st.download_button(
                            label="🖼️ 이미지 저장",
                            data=image_info['bytes'].getvalue(),
                            file_name=f"image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                            mime="image/png"
                        )
                    
                    if auto_post_button:
                        st.info("🚧 네이버 자동 발행 기능은 개발 중입니다. 복사-붙여넣기로 발행해주세요.")
                    
                except Exception as e:
                    st.error(f"❌ 오류 발생: {str(e)}")

with tab2:
    st.subheader("📚 저장된 글 목록")
    
    if len(st.session_state.saved_posts) == 0:
        st.info("아직 저장된 글이 없습니다. '글 생성' 탭에서 글을 만들어보세요!")
    else:
        st.success(f"총 {len(st.session_state.saved_posts)}개의 글이 저장되어 있습니다.")
        
        for idx, post in enumerate(st.session_state.saved_posts):
            with st.expander(f"📄 {post['keyword']} ({post['category']}) - {post['timestamp']}"):
                col_a, col_b = st.columns([3, 1])
                
                with col_a:
                    st.markdown(f"**글자 수**: {post['word_count']}자")
                    st.markdown(f"**작성 시간**: {post['timestamp']}")
                
                with col_b:
                    st.download_button(
                        label="💾 다운로드",
                        data=post['content'],
                        file_name=f"post_{idx+1}.txt",
                        key=f"dl_{idx}",
                        use_container_width=True
                    )
                
                st.markdown("---")
                
                # 이미지
                if post['image_info']:
                    if 'image' in post['image_info']:
                        st.image(post['image_info']['image'], width=400)
                    elif 'url' in post['image_info']:
                        st.image(post['image_info']['url'], width=400)
                
                # 콘텐츠
                st.markdown(post['content'])
        
        # 전체 삭제
        st.divider()
        if st.button("🗑️ 전체 삭제", type="secondary"):
            st.session_state.saved_posts = []
            st.rerun()

with tab3:
    st.subheader("📊 사용 통계")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("생성된 글", len(st.session_state.saved_posts))
    
    with col2:
        st.metric("생성된 이미지", st.session_state.image_count)
    
    with col3:
        total_words = sum(p['word_count'] for p in st.session_state.saved_posts)
        st.metric("총 글자 수", f"{total_words:,}자")
    
    with col4:
        avg_words = total_words // len(st.session_state.saved_posts) if st.session_state.saved_posts else 0
        st.metric("평균 글자 수", f"{avg_words:,}자")

with tab4:
    st.subheader("📖 사용 방법")
    
    st.markdown("""
    ## 1️⃣ API 설정
    
    ### Claude API Key (필수)
    1. [Anthropic Console](https://console.anthropic.com) 접속
    2. API Keys → Create Key
    3. 사이드바에 입력 또는 Secrets에 저장
    
    ### Hugging Face Token (이미지 생성용, 무료)
    1. [Hugging Face](https://huggingface.co) 가입
    2. Settings → Access Tokens → New token
    3. Read 권한으로 생성
    
    ### Streamlit Secrets 설정 (권장)
    ```toml
    CLAUDE_API_KEY = "sk-ant-api03-xxxxx"
    HUGGINGFACE_TOKEN = "hf_xxxxx"
    NAVER_BLOG_ID = "cinepark"
    ```
    
    ---
    
    ## 2️⃣ 글 생성하기
    
    1. 주제 카테고리 선택
    2. 키워드 입력 (예: "4차 상법 개정")
    3. 글 스타일 선택
    4. "글 생성" 클릭
    
    ---
    
    ## 3️⃣ 특징
    
    - ✅ Claude Sonnet 4.5로 자연스러운 글 생성
    - ✅ Stable Diffusion으로 무료 AI 이미지 생성
    - ✅ 최신 뉴스 자동 검색 및 반영
    - ✅ 고정된 책 홍보 섹션 (감각구역)
    - ✅ 생성된 글 자동 저장 및 목록 관리
    
    ---
    
    ## 💡 팁
    
    - 이미지 생성은 처음에 30-60초 소요 (모델 로딩)
    - 이후엔 5-10초로 빨라집니다
    - 저장된 글은 세션 종료 시 사라집니다 (영구 저장 아님)
    - 중요한 글은 다운로드해두세요
    
    ---
    
    ## 📞 문의
    
    GitHub: [cinepark-1974/AutoPost](https://github.com/cinepark-1974/AutoPost)
    """)

st.markdown("---")
st.caption("Made with ❤️ using Claude API + Stable Diffusion | AutoPost v2.0")
