import streamlit as st
import anthropic
import requests
from datetime import datetime
import json
from PIL import Image
from io import BytesIO

# Pexels API를 사용한 무료 이미지 검색
def search_free_image(keyword):
    """
    Pexels API로 무료 이미지 검색
    """
    try:
        # Pexels API (무료, 공식 API 키)
        url = "https://api.pexels.com/v1/search"
        headers = {
            "Authorization": "563492ad6f9170000100000154d4f33a2fa54799bed66bbf3115e359"
        }
        
        # 한글 키워드는 영문으로 간단히 변환 (필요시)
        search_query = keyword
        
        params = {
            "query": search_query,
            "per_page": 5,
            "orientation": "landscape",
            "size": "medium"
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if "photos" in data and len(data["photos"]) > 0:
                photo = data["photos"][0]
                return {
                    "url": photo["src"]["large"],
                    "photographer": photo["photographer"],
                    "photographer_url": photo["photographer_url"],
                    "source": "Pexels",
                    "source_url": photo["url"]
                }
        
        # API 실패 시 대체 방법 - Unsplash Source (API 키 불필요)
        return {
            "url": f"https://source.unsplash.com/1200x800/?{keyword}",
            "photographer": "Unsplash 커뮤니티",
            "photographer_url": "https://unsplash.com",
            "source": "Unsplash",
            "source_url": f"https://unsplash.com/s/photos/{keyword}"
        }
        
    except Exception as e:
        # 최종 대체: Unsplash Source (항상 작동)
        return {
            "url": f"https://source.unsplash.com/1200x800/?{keyword}",
            "photographer": "Unsplash 커뮤니티",
            "photographer_url": "https://unsplash.com",
            "source": "Unsplash",
            "source_url": f"https://unsplash.com/s/photos/{keyword}"
        }

def format_image_credit(image_info):
    """이미지 출처 포맷팅"""
    if not image_info:
        return ""
    
    credit = f"\n\n---\n\n📷 **이미지 출처**\n"
    credit += f"사진: [{image_info['photographer']}]({image_info['photographer_url']}) / "
    credit += f"[{image_info['source']}]({image_info['source_url']})\n"
    return credit

# 페이지 설정
st.set_page_config(
    page_title="AutoPost - AI 블로그 자동화",
    page_icon="✍️",
    layout="wide"
)

# 커스텀 CSS
st.markdown("""
<style>
    /* 페이퍼로지 폰트 불러오기 */
    @font-face {
        font-family: 'Paybooc';
        src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_2001@1.1/Paybooc.woff') format('woff');
        font-weight: normal;
        font-style: normal;
    }
    
    /* 전체 폰트 적용 */
    * {
        font-family: 'Paybooc', 'Apple SD Gothic Neo', sans-serif !important;
    }
    
    /* 메인 배경 강제 설정 */
    .main {
        background-color: #f8f9fd !important;
    }
    
    .stApp {
        background-color: #f8f9fd !important;
    }
    
    /* 전체 컨테이너 배경 */
    [data-testid="stAppViewContainer"] {
        background-color: #f8f9fd !important;
    }
    
    /* 헤더 배경 */
    header[data-testid="stHeader"] {
        background-color: #f8f9fd !important;
    }
    
    /* 메인 타이틀 스타일 */
    h1 {
        color: #191970 !important;
        font-weight: 700 !important;
        font-family: 'Paybooc' !important;
    }
    
    /* 서브 타이틀 */
    h2, h3 {
        color: #191970 !important;
    }
    
    /* 버튼 호버 효과 */
    .stButton > button {
        border: 2px solid #ffcb05 !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background-color: #ffcb05 !important;
        color: #191970 !important;
        border-color: #191970 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(255, 203, 5, 0.3) !important;
    }
    
    /* Primary 버튼 */
    .stButton > button[kind="primary"] {
        background-color: #ffcb05 !important;
        color: #191970 !important;
        border: none !important;
    }
    
    /* Secondary 버튼 */
    .stButton > button[kind="secondary"] {
        background-color: #191970 !important;
        color: #ffffff !important;
        border: 2px solid #ffcb05 !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background-color: #ffcb05 !important;
        color: #191970 !important;
    }
    
    /* 입력 필드 포커스 */
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #ffcb05 !important;
        box-shadow: 0 0 0 1px #ffcb05 !important;
    }
    
    /* 사이드바 스타일 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #e8ecf7 0%, #f8f9fd 100%) !important;
    }
    
    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #e8ecf7;
        color: #191970;
        border-radius: 8px 8px 0 0;
        padding: 12px 24px;
        font-weight: 600;
        border: 2px solid transparent;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #ffcb05 !important;
        border-color: #191970 !important;
    }
    
    /* 성공 메시지 */
    .stSuccess {
        background-color: #fffbea !important;
        border-left: 4px solid #ffcb05 !important;
        color: #191970 !important;
    }
    
    /* 정보 메시지 */
    .stInfo {
        background-color: #f0f2ff !important;
        border-left: 4px solid #191970 !important;
    }
    
    /* 메트릭 카드 */
    [data-testid="stMetricValue"] {
        color: #191970 !important;
        font-weight: 700 !important;
    }
    
    /* 다운로드 버튼 */
    .stDownloadButton > button {
        background-color: #191970 !important;
        color: #ffcb05 !important;
        border: 2px solid #ffcb05 !important;
    }
    
    .stDownloadButton > button:hover {
        background-color: #ffcb05 !important;
        color: #191970 !important;
    }
    
    /* 슬라이더 */
    .stSlider > div > div > div > div {
        background-color: #ffcb05 !important;
    }
    
    /* 체크박스 */
    .stCheckbox > label > div[data-testid="stMarkdownContainer"] > p {
        color: #191970 !important;
        font-weight: 500 !important;
    }
    
    /* 라디오 버튼 */
    .stRadio > label > div[data-testid="stMarkdownContainer"] > p {
        color: #191970 !important;
        font-weight: 500 !important;
    }
    
    /* 셀렉트박스 */
    .stSelectbox > label > div[data-testid="stMarkdownContainer"] > p {
        color: #191970 !important;
        font-weight: 600 !important;
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
    Claude API 기반 범용 콘텐츠 생성 + 네이버 자동 포스팅
</p>
""", unsafe_allow_html=True)

# 사이드바 - API 설정
with st.sidebar:
    st.header("⚙️ API 설정")
    
    # Claude API Key - Secrets에서 자동 로드 (더 안전한 방식)
    try:
        if hasattr(st, 'secrets') and "CLAUDE_API_KEY" in st.secrets:
            claude_api_key = st.secrets["CLAUDE_API_KEY"]
            st.success("✅ Claude API Key 자동 로드 완료")
            with st.expander("🔑 API Key 확인"):
                st.code(f"{claude_api_key[:20]}...{claude_api_key[-4:]}")
        else:
            claude_api_key = st.text_input(
                "Claude API Key",
                type="password",
                help="console.anthropic.com에서 발급",
                key="claude_key_input"
            )
            if not claude_api_key:
                st.warning("⚠️ API Key를 입력하거나 Secrets에 저장해주세요")
    except Exception as e:
        claude_api_key = st.text_input(
            "Claude API Key",
            type="password",
            help="console.anthropic.com에서 발급",
            key="claude_key_input_fallback"
        )
        st.error(f"Secrets 로드 오류: {str(e)}")
    
    st.divider()
    
    # 네이버 API 설정 - Secrets에서 자동 로드
    st.subheader("네이버 블로그 API")
    
    try:
        if hasattr(st, 'secrets') and "NAVER_CLIENT_ID" in st.secrets:
            naver_client_id = st.secrets["NAVER_CLIENT_ID"]
            st.success("✅ Naver Client ID 자동 로드")
        else:
            naver_client_id = st.text_input(
                "Client ID",
                type="password",
                help="developers.naver.com에서 발급"
            )
    except:
        naver_client_id = st.text_input(
            "Client ID",
            type="password",
            help="developers.naver.com에서 발급"
        )
    
    try:
        if hasattr(st, 'secrets') and "NAVER_CLIENT_SECRET" in st.secrets:
            naver_client_secret = st.secrets["NAVER_CLIENT_SECRET"]
            st.success("✅ Naver Client Secret 자동 로드")
        else:
            naver_client_secret = st.text_input(
                "Client Secret",
                type="password"
            )
    except:
        naver_client_secret = st.text_input(
            "Client Secret",
            type="password"
        )
    
    try:
        if hasattr(st, 'secrets') and "NAVER_BLOG_ID" in st.secrets:
            naver_blog_id = st.secrets["NAVER_BLOG_ID"]
            st.success("✅ Blog ID 자동 로드")
        else:
            naver_blog_id = st.text_input(
                "블로그 ID",
                help="예: cinepark"
            )
    except:
        naver_blog_id = st.text_input(
            "블로그 ID",
            help="예: cinepark"
        )
    
    st.divider()
    
    # Secrets 디버깅 정보 (개발용)
    with st.expander("🔧 Secrets 상태 확인"):
        if hasattr(st, 'secrets'):
            st.write("Secrets 사용 가능 ✅")
            secret_keys = list(st.secrets.keys()) if st.secrets else []
            st.write(f"저장된 키 개수: {len(secret_keys)}")
            if secret_keys:
                st.write("키 목록:", secret_keys)
        else:
            st.write("Secrets 사용 불가 ❌")
    
    st.caption("💡 Streamlit Cloud Settings → Secrets에서 API 키를 저장하세요")

# 메인 컨텐츠
tab1, tab2, tab3 = st.tabs(["📝 글 생성", "📊 대시보드", "ℹ️ 사용법"])

with tab1:
    col1, col2 = st.columns(2)  # 좌우 균등 분할
    
    with col1:
        st.markdown("### 📝 콘텐츠 설정")
        
        # 주제 선택
        category = st.selectbox(
            "주제 카테고리",
            [
                "영화 리뷰",
                "책 리뷰",
                "맛집 후기",
                "여행 후기",
                "IT/기술",
                "일상/에세이",
                "건강/운동",
                "요리/레시피",
                "자유 주제"
            ]
        )
        
        # 키워드 입력
        keyword = st.text_input(
            "키워드 입력",
            placeholder="예: 부산 해운대 맛집, ChatGPT 활용법, 겨울 제주도",
            help="검색에 노출되고 싶은 핵심 키워드를 입력하세요"
        )
        
        # 글 스타일
        writing_style = st.radio(
            "글 스타일",
            ["정보 전달형 (팩트 중심)", "후기/리뷰형 (경험 중심)", "스토리텔링형 (감성적)"]
        )
        
        # 글 길이
        word_count = st.slider(
            "글 길이 (자)",
            min_value=1000,
            max_value=3000,
            value=2000,
            step=500
        )
    
    with col2:
        st.markdown("### 🎯 SEO 설정")
        
        # SEO 옵션
        include_hashtags = st.checkbox("해시태그 자동 생성", value=True)
        include_meta = st.checkbox("메타 태그 생성", value=True)
        
        st.divider()
        
        # 이미지 옵션
        st.markdown("### 🖼️ 이미지 설정")
        include_image = st.checkbox("썸네일 이미지 추가", value=True, help="키워드 관련 무료 이미지 자동 검색")
        
        keyword_density = st.slider(
            "키워드 밀도",
            min_value=3,
            max_value=10,
            value=5,
            help="본문에 키워드가 나타나는 횟수"
        )
    
    st.divider()
    
    # 생성 버튼
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
                    # Claude API 호출
                    client = anthropic.Anthropic(api_key=claude_api_key)
                    
                    # 스타일에 따른 프롬프트 조정
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

✍️ 글쓰기 원칙 (매우 중요):

1. **자연스러운 시작**
   - "들어가며", "서론" 같은 제목 절대 금지
   - 바로 이야기로 시작하기
   - 예: "오늘 드디어 20만 전자가 되었어요!", "요즘 {keyword}에 푹 빠져있어요", "여러분, 이거 진짜 대박이에요!"
   
2. **블로그 말투**
   - 반말 또는 존댓말 (자연스럽게)
   - "~했어요", "~더라고요", "~네요" 활용
   - 이모지 적절히 사용 (😊, 👍, ✨ 등)
   - 독자에게 말 거는 느낌
   
3. **구조**
   - 소제목은 물음표나 느낌표로 (예: "그래서 결과는?", "진짜 효과 있을까?")
   - "본문", "결론" 같은 딱딱한 제목 금지
   - 자연스러운 이야기 흐름
   
4. **내용**
   - 개인적 경험 느낌 (실제 경험 아니어도 그렇게 작성)
   - "{keyword}" 키워드를 {keyword_density}회 정도 자연스럽게 언급
   - 짧은 문단 (2-3줄씩)
   - 공감 유도하는 질문 포함
   
5. **마무리**
   - "마무리", "결론" 같은 제목 금지
   - 자연스러운 마무리 멘트
   - 예: "여러분도 한번 시도해보세요!", "다음엔 더 좋은 정보로 찾아올게요 😊"

출력 형식:
## 제목
[SEO 최적화 + 클릭 유도하는 제목]

[바로 본문 시작 - 자연스러운 도입]

## [자연스러운 소제목1]
[내용]

## [자연스러운 소제목2]  
[내용]

## [자연스러운 소제목3]
[내용]

[자연스러운 마무리]

## 태그
#태그1 #태그2 #태그3 #태그4 #태그5

❌ 절대 사용 금지: "들어가며", "본문", "서론", "결론", "마무리" 같은 딱딱한 제목
✅ 사용 권장: 물음표, 느낌표, 이모지, 반말/존댓말 섞기, 독자에게 말 걸기
"""
                    
                    message = client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=4000,
                        temperature=0.7,
                        messages=[{
                            "role": "user",
                            "content": prompt
                        }]
                    )
                    
                    generated_content = message.content[0].text
                    
                    # 이미지 검색 및 추가
                    image_info = None
                    if include_image:
                        with st.spinner("관련 이미지를 검색 중입니다..."):
                            image_info = search_free_image(keyword)
                    
                    # 결과 표시
                    st.success("✅ 글 생성 완료!")
                    
                    # 이미지가 있으면 표시
                    if image_info:
                        try:
                            img_response = requests.get(image_info["url"], timeout=10)
                            img = Image.open(BytesIO(img_response.content))
                            st.image(img, caption=f"사진: {image_info['photographer']} / {image_info['source']}", use_container_width=True)
                        except:
                            st.warning("이미지 로딩 실패")
                    
                    # 생성된 글 표시
                    st.markdown("---")
                    st.markdown("### 📄 생성된 콘텐츠")
                    st.markdown(generated_content)
                    
                    # 이미지 출처 추가
                    if image_info:
                        st.markdown(format_image_credit(image_info))
                    
                    # 다운로드용 전체 콘텐츠 (이미지 URL + 출처 포함)
                    download_content = generated_content
                    if image_info:
                        download_content += f"\n\n## 썸네일 이미지\n"
                        download_content += f"![썸네일]({image_info['url']})\n"
                        download_content += format_image_credit(image_info)
                    
                    # 저장 기능
                    st.download_button(
                        label="💾 텍스트로 저장",
                        data=download_content,
                        file_name=f"autopost_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
                    
                    # 자동 발행 선택 시
                    if auto_post_button:
                        st.markdown("---")
                        if not naver_client_id or not naver_client_secret or not naver_blog_id:
                            st.warning("⚠️ 네이버 API 정보를 입력하면 자동 발행이 가능합니다!")
                        else:
                            with st.spinner("네이버 블로그에 발행 중..."):
                                # TODO: 네이버 API 연동 (추후 구현)
                                st.info("🚧 네이버 자동 발행 기능은 개발 중입니다!")
                                st.info("현재는 생성된 글을 복사해서 수동으로 발행해주세요.")
                    
                except Exception as e:
                    st.error(f"❌ 오류 발생: {str(e)}")
                    st.info("API Key가 올바른지, 크레딧이 있는지 확인해주세요.")

with tab2:
    st.subheader("📊 통계 대시보드")
    st.info("🚧 개발 예정: 생성한 글 수, 발행한 글 수, API 사용량 등의 통계를 보여줍니다.")
    
    # 임시 통계
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("생성된 글", "0", "0")
    with col2:
        st.metric("발행된 글", "0", "0")
    with col3:
        st.metric("이번 달 사용량", "$0.00", "0%")
    with col4:
        st.metric("평균 글자 수", "0", "0")

with tab3:
    st.subheader("📖 사용 방법")
    
    st.markdown("""
    ## 1️⃣ API 설정
    
    ### Claude API Key 발급
    1. [Anthropic Console](https://console.anthropic.com) 접속
    2. 계정 생성 및 로그인
    3. API Keys 메뉴에서 새 키 생성
    4. 왼쪽 사이드바에 입력
    
    ### 네이버 개발자 센터 (선택사항)
    1. [네이버 개발자 센터](https://developers.naver.com) 접속
    2. 애플리케이션 등록
    3. Client ID/Secret 발급
    
    ---
    
    ## 2️⃣ 글 생성하기
    
    1. **주제 선택**: 작성하고 싶은 카테고리 선택
    2. **키워드 입력**: 검색 노출을 원하는 핵심 키워드 입력
    3. **스타일 선택**: 글의 톤앤매너 선택
    4. **생성 버튼**: 클릭하면 AI가 자동으로 글 작성
    
    ---
    
    ## 3️⃣ SEO 최적화
    
    - ✅ 제목에 키워드 자동 포함
    - ✅ 본문에 키워드 자연스럽게 배치
    - ✅ 해시태그 자동 생성
    - ✅ 검색 엔진 친화적 구조
    - ✅ 무료 이미지 자동 검색 및 출처 표기
    
    ---
    
    ## 4️⃣ 이미지 기능
    
    ### 무료 이미지 자동 검색
    - **Pexels API** 사용
    - 키워드 관련 고품질 이미지 자동 검색
    - 완전 무료, 저작권 걱정 없음
    - 출처 자동 표기 (사진작가 + Pexels 링크)
    
    ### 사용 방법
    1. "썸네일 이미지 추가" 체크
    2. 글 생성 시 자동으로 관련 이미지 검색
    3. 이미지 미리보기 + 출처 자동 포함
    4. 다운로드 시 이미지 URL + 출처 포함
    
    ---
    
    ## 5️⃣ 발행 방법
    
    ### 수동 발행 (현재)
    1. 생성된 글 복사
    2. 네이버 블로그에 직접 붙여넣기
    3. 발행
    
    ### 자동 발행 (개발 예정)
    - 네이버 API 연동 완료 후 버튼 클릭만으로 자동 발행
    
    ---
    
    ## 💡 팁
    
    - 키워드는 구체적일수록 좋습니다
    - 다양한 스타일을 테스트해보세요
    - 생성된 글을 약간 수정하면 더 자연스럽습니다
    
    ---
    
    ## 📞 문의
    
    버그 제보 및 기능 제안: [GitHub Issues](https://github.com/cinepark-1974/AutoPost/issues)
    """)

# Footer
st.markdown("---")
st.caption("Made with ❤️ using Claude API | AutoPost v1.0")
