import streamlit as st
import anthropic
import requests
from datetime import datetime
import json

# 페이지 설정
st.set_page_config(
    page_title="AutoPost - AI 블로그 자동화",
    page_icon="✍️",
    layout="wide"
)

# 제목
st.title("✍️ AutoPost - AI 블로그 자동화 시스템")
st.caption("Claude API 기반 범용 콘텐츠 생성 + 네이버 자동 포스팅")

# 사이드바 - API 설정
with st.sidebar:
    st.header("⚙️ API 설정")
    
    # Claude API Key
    claude_api_key = st.text_input(
        "Claude API Key",
        type="password",
        help="console.anthropic.com에서 발급"
    )
    
    st.divider()
    
    # 네이버 API 설정
    st.subheader("네이버 블로그 API")
    naver_client_id = st.text_input(
        "Client ID",
        type="password",
        help="developers.naver.com에서 발급"
    )
    naver_client_secret = st.text_input(
        "Client Secret",
        type="password"
    )
    naver_blog_id = st.text_input(
        "블로그 ID",
        help="예: cinepark"
    )
    
    st.divider()
    st.caption("💡 API 키는 Streamlit Secrets에 저장하는 것을 권장합니다")

# 메인 컨텐츠
tab1, tab2, tab3 = st.tabs(["📝 글 생성", "📊 대시보드", "ℹ️ 사용법"])

with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("콘텐츠 설정")
        
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
            ["정보 전달형 (팩트 중심)", "후기/리뷰형 (경험 중심)", "스토리텔링형 (감성적)"],
            horizontal=True
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
        st.subheader("SEO 설정")
        
        # SEO 옵션
        include_hashtags = st.checkbox("해시태그 자동 생성", value=True)
        include_meta = st.checkbox("메타 태그 생성", value=True)
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
                    
                    prompt = f"""당신은 전문 블로거입니다. 다음 조건에 맞는 블로그 글을 작성해주세요:

주제 카테고리: {category}
핵심 키워드: {keyword}
글 스타일: {style_instruction[writing_style]}
목표 글자 수: {word_count}자
키워드 사용 횟수: {keyword_density}회 (자연스럽게)

작성 규칙:
1. SEO 최적화: 제목에 키워드 포함, 본문에 키워드 자연스럽게 {keyword_density}회 정도 배치
2. 구조화: 서론-본론-결론 구조, 소제목 3-4개 포함
3. 가독성: 짧은 문단, 명확한 문장, 읽기 쉬운 표현
4. 자연스러움: AI가 쓴 티가 나지 않도록 자연스러운 한국어
5. 네이버 블로그 특성: 친근하고 공감 가는 톤

출력 형식:
## 제목
[SEO 최적화된 제목]

## 본문
[여기에 본문 작성]

## 태그
[5-7개의 해시태그]
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
                    
                    # 결과 표시
                    st.success("✅ 글 생성 완료!")
                    
                    # 생성된 글 표시
                    st.markdown("---")
                    st.markdown("### 📄 생성된 콘텐츠")
                    st.markdown(generated_content)
                    
                    # 저장 기능
                    st.download_button(
                        label="💾 텍스트로 저장",
                        data=generated_content,
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
    
    ---
    
    ## 4️⃣ 발행 방법
    
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
