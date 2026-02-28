import streamlit as st
import anthropic
import requests
from datetime import datetime
import json
import re
import os
from pathlib import Path

# 히스토리 파일 경로
HISTORY_FILE = Path("/home/claude/post_history.json")

# 히스토리 불러오기
def load_history():
    """히스토리 파일에서 불러오기"""
    try:
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # timestamp를 datetime으로 변환
                for item in data:
                    if isinstance(item['timestamp'], str):
                        item['timestamp'] = datetime.fromisoformat(item['timestamp'])
                return data
    except:
        pass
    return []

# 히스토리 저장하기
def save_history(history):
    """히스토리를 파일로 저장"""
    try:
        # datetime을 string으로 변환
        data = []
        for item in history:
            item_copy = item.copy()
            if isinstance(item_copy['timestamp'], datetime):
                item_copy['timestamp'] = item_copy['timestamp'].isoformat()
            data.append(item_copy)
        
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"히스토리 저장 실패: {str(e)}")

# 상수
BOOK_INFO = {
    "cover_url": "https://raw.githubusercontent.com/cinepark-1974/AutoPost/main/assets/book_cover.png",
    "title": "감각구역",
    "authors": "문성주, 박현",
    "publisher": "마카롱(교보문고)",
    "link": "https://ebook-product.kyobobook.co.kr/dig/epd/ebook/E000012093207"
}

# API 키 저장/불러오기
def save_api_key(key):
    st.session_state['saved_api_key'] = key
    return True

def load_api_key():
    """API 키 불러오기 (Secrets 우선)"""
    try:
        if hasattr(st, 'secrets') and "CLAUDE_API_KEY" in st.secrets:
            return st.secrets["CLAUDE_API_KEY"]
    except:
        pass
    if 'saved_api_key' in st.session_state:
        return st.session_state['saved_api_key']
    return ""

# 키워드 추천
def recommend_keywords(category, claude_api_key):
    """카테고리별 인기 키워드 추천"""
    try:
        client = anthropic.Anthropic(api_key=claude_api_key)
        
        prompt = f"""당신은 블로그 SEO 전문가입니다. {category} 카테고리에서 현재 검색량이 많고 경쟁도가 낮은 황금 키워드 10개를 추천해주세요.

조건:
1. 월 검색량: 1,000~10,000 (너무 경쟁 치열하지 않음)
2. 경쟁 문서: 100개 이하 (상위 노출 가능)
3. 2026년 2월 28일 현재 트렌드 반영
4. 롱테일 키워드 포함 (3-5단어)

출력 형식:
1. [키워드] - [이유 한 줄]
2. [키워드] - [이유 한 줄]
...

예시:
1. 주식 초보 추천 어플 - 초보자 타겟, 구체적
2. 부산 해운대 숨은 맛집 - 지역 특화, 롱테일

지금 바로 {category} 카테고리 황금 키워드 10개를 추천하세요!"""
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text
    except Exception as e:
        return f"추천 실패: {str(e)}"

# 최신 트렌드 검색
def search_latest_trends(keyword):
    """Google News RSS로 최신 트렌드 검색 (출처 포함)"""
    try:
        url = f"https://news.google.com/rss/search?q={keyword}&hl=ko&gl=KR&ceid=KR:ko"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)
            
            news_items = []
            for item in root.findall('.//item')[:5]:
                title = item.find('title').text if item.find('title') is not None else ""
                link = item.find('link').text if item.find('link') is not None else ""
                pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""
                source = item.find('source').text if item.find('source') is not None else "출처 불명"
                
                news_items.append({
                    "title": title,
                    "link": link,
                    "date": pub_date[:16],
                    "source": source
                })
            
            return news_items
        return []
    except:
        return []

# SEO 분석
def analyze_seo(title, content, keyword):
    score = 0
    feedback = []
    improvements = []
    
    # 제목에서 ## 제거하고 순수 텍스트만
    clean_title = title.replace("#", "").strip()
    
    if keyword.lower() in clean_title.lower():
        score += 20
        feedback.append("✅ 제목에 키워드 포함")
    else:
        feedback.append("❌ 제목에 키워드 추가")
        improvements.append(f"제목에 '{keyword}' 추가")
    
    if 15 <= len(clean_title) <= 40:
        score += 10
        feedback.append("✅ 제목 길이 적절")
    else:
        feedback.append(f"⚠️ 제목 길이 조정 ({len(clean_title)}자)")
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
    if 5 <= keyword_count <= 10:
        score += 20
        feedback.append(f"✅ 키워드 밀도 적절 ({keyword_count}회)")
    else:
        feedback.append(f"⚠️ 키워드 조정 ({keyword_count}회)")
        if keyword_count < 5:
            improvements.append(f"'{keyword}' {5 - keyword_count}회 추가")
    
    subtitle_count = content.count("##") - 1  # 첫 번째 제목 제외
    if subtitle_count >= 3:
        score += 10
        feedback.append(f"✅ 소제목 충분 ({subtitle_count}개)")
    else:
        feedback.append(f"⚠️ 소제목 추가 필요")
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
    
    if "#" in content and "태그" in content:
        score += 15
        feedback.append("✅ 해시태그 포함")
    else:
        feedback.append("⚠️ 해시태그 추가")
        improvements.append("해시태그 10개 추가")
    
    return score, feedback, improvements

# 올인원 자동 생성
def generate_optimized_post(keyword, category, word_count, claude_api_key, use_trends=True):
    try:
        client = anthropic.Anthropic(api_key=claude_api_key)
        
        trend_info = ""
        if use_trends:
            trends = search_latest_trends(keyword)
            if trends:
                trend_text = "\n".join([
                    f"- {item['title']}\n  출처: {item['source']}\n  링크: {item['link']}\n  날짜: {item['date']}"
                    for item in trends
                ])
                trend_info = f"""

📰 최신 트렌드 정보 (반드시 출처 표기):
{trend_text}

위 최신 뉴스를 참고하되, 다음 규칙을 반드시 지키세요:
1. 뉴스 내용을 언급할 때는 반드시 출처 표기 (예: "OO신문에 따르면", "OO 보도에 의하면")
2. 링크는 본문에 포함하지 말고, 사실만 언급
3. 출처가 불확실한 정보는 "~라는 의견도 있습니다" 등으로 신중하게 표현
4. 과장하지 말고 뉴스 내용을 정확하게 전달
"""
        
        prompt = f"""당신은 월 방문자 10만 명을 달성한 인기 블로거입니다. 정확한 정보만 제공하는 것으로 유명하며, 독자들의 신뢰가 두텁습니다.

키워드: {keyword}
카테고리: {category}
목표 글자수: {word_count}자
{trend_info}

🎯 SEO 점수 90점 이상 필수 조건:

1. 제목 (30점):
   - 반드시 "{keyword}" 포함 (정확히)
   - 25-35자 길이 엄수
   - 숫자 활용 (5가지, 10분, 2026년)
   - 예: "{keyword} 완벽 가이드! 2026년 최신 5가지"

2. 키워드 밀도 (30점):
   - "{keyword}" 정확히 7-9회 반복
   - 첫 문단에 1회 필수
   - 각 소제목에 관련 단어 포함
   - 본문 전체에 고르게 분산

3. 소제목 (20점):
   - ## 형식으로 4-5개 필수
   - 각 소제목은 물음표(?) 또는 느낌표(!)로 끝
   - 예: "## {keyword} 선택 방법은?"

4. 이모지 (10점):
   - 본문에 정확히 5-7개 삽입
   - 추천: 😊 👍 ✨ 💡 🔥 ⭐ 📌
   - 각 소제목 또는 주요 포인트에 배치

5. 해시태그 (10점):
   - 반드시 "## 태그" 섹션 추가
   - #{keyword} 포함하여 10개 작성
   - 예: #{keyword} #2026 #최신 #추천 #후기 #팁 #정보 #꿀팁 #리뷰 #가이드

📋 필수 구조:

## [{keyword} 관련 제목 25-35자]

안녕하세요. 영화 프로듀서의 블로그, CINEPARK입니다.

[첫 문단에 "{keyword}" 1회 포함]
[독자 공감 유도 - 질문 또는 경험]

## {keyword} 핵심 정리! ✨
["{keyword}" 포함 + 이모지]
[구체적 정보 2-3문단]

## {keyword} 선택 방법은? 🤔
["{keyword}" 포함 + 이모지]
[실용적 팁 2-3문단]

## {keyword} 활용 꿀팁! 💡
["{keyword}" 포함 + 이모지]
[실전 예시 2-3문단]

## {keyword} 주의사항 ⚠️
["{keyword}" 포함 + 이모지]
[주의점 2-3문단]

[마무리 + 댓글 유도]
"여러분은 어떻게 생각하세요? 댓글로 경험 공유해주세요!"

## 태그
#{keyword} #2026 #최신 #추천 #후기 #팁 #정보 #꿀팁 #리뷰 #가이드

⚠️ 체크리스트 (반드시 확인):
✅ 제목에 "{keyword}" 포함
✅ 제목 25-35자
✅ 본문 {word_count}자 이상
✅ "{keyword}" 7-9회 사용
✅ 소제목 4-5개 (##)
✅ 이모지 5-7개
✅ "## 태그" 섹션 + #{keyword} 포함 10개

지금 바로 SEO 90점 이상 글을 작성하세요!"""
        
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
        
        if score < 85:
            # 상세한 개선 지침 생성
            retry_prompt = f"""❌ 현재 SEO 점수: {score}점 (목표: 90점 이상)

🔧 필수 개선사항:
{chr(10).join([f"- {imp}" for imp in improvements])}

📋 SEO 90점 체크리스트 (반드시 확인):

1. 제목 체크:
   ✅ "{keyword}" 키워드 포함 (정확히)
   ✅ 25-35자 길이
   ✅ 숫자 포함 (5가지, 10분 등)

2. 키워드 밀도:
   ✅ "{keyword}" 정확히 7-9회 반복
   ✅ 첫 문단에 1회
   ✅ 각 소제목 근처에 1회씩

3. 구조:
   ✅ 소제목(##) 4-5개
   ✅ 이모지 5-7개 (😊 👍 ✨ 💡 🔥)
   ✅ 반드시 "## 태그" 섹션 추가

4. 태그:
   ✅ #{keyword} 포함한 해시태그 10개
   ✅ 예: #{keyword} #2026 #최신 #추천 #후기 #팁 #정보 #꿀팁 #리뷰 #가이드

⚠️ 위 체크리스트를 100% 충족하여 다시 작성하세요!"""
            
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
    try:
        API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
        headers = {"Authorization": f"Bearer {hf_token}"}
        prompt = f"{keyword}, high quality, detailed, professional photography, 8k"
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt}, timeout=60)
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

# 세션 상태 초기화
if 'post_history' not in st.session_state:
    # 파일에서 불러오기 시도
    loaded_history = load_history()
    if loaded_history:
        st.session_state['post_history'] = loaded_history
    else:
        # 빈 리스트로 시작
        st.session_state['post_history'] = []

# 디버그: 히스토리 개수 표시 (개발용)
if st.session_state['post_history']:
    st.sidebar.success(f"✅ 저장된 글: {len(st.session_state['post_history'])}개")

# CSS
st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none !important; }
    .main .block-container { max-width: 900px !important; padding: 2rem 1rem !important; margin: 0 auto !important; }
    
    /* 다크모드 방지 */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], .main {
        background-color: #ffffff !important;
    }
    
    /* 텍스트 */
    h1 { color: #191970 !important; font-size: 2.5rem !important; font-weight: 700 !important; }
    h2 { color: #191970 !important; font-size: 1.5rem !important; font-weight: 600 !important; }
    h3 { color: #4a4a4a !important; font-size: 1.1rem !important; font-weight: 600 !important; }
    p, span, div { color: #262730 !important; }
    
    /* 버튼 */
    .stButton > button[kind="primary"] {
        background: #191970 !important; 
        color: #ffffff !important; 
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
    
    /* 일반 버튼 */
    .stButton > button {
        color: #262730 !important;
        background: #ffffff !important;
        border: 1px solid #e0e0e0 !important;
    }
    .stButton > button:hover {
        background: #f8f9fa !important;
    }
    
    /* 입력 필드 */
    .stTextInput > div > div > input, .stSelectbox > div > div > div, .stTextArea > div > div > textarea {
        background-color: #ffffff !important; color: #262730 !important;
        border: 1px solid #e0e0e0 !important; border-radius: 8px !important; padding: 0.75rem !important;
    }
    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
        border-color: #191970 !important; box-shadow: 0 0 0 1px #191970 !important;
    }
    
    /* SEO 점수 */
    .seo-score {
        text-align: center; background: #f8f9fa !important;
        border: 2px solid #e0e0e0; border-radius: 12px; padding: 2rem; margin: 2rem 0;
    }
    .score-number { font-size: 4rem; font-weight: 800; color: #191970 !important; margin: 0; }
    
    /* Expander */
    .streamlit-expanderHeader { background-color: #f8f9fa !important; color: #191970 !important; }
    [data-testid="stExpander"] { background-color: #ffffff !important; border: 1px solid #e0e0e0 !important; }
</style>
""", unsafe_allow_html=True)

# 헤더 (Autosend 스타일 - 왼쪽 텍스트 + 오른쪽 이미지)
st.markdown("""
<div style="padding: 3rem 0 2rem 0;">
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 4rem; align-items: center;">
        <!-- 왼쪽: 텍스트 -->
        <div>
            <h1 style="color: #191970; font-size: 2.5rem; font-weight: 700; margin: 0 0 1rem 0; line-height: 1.2;">
                ✍️ AutoPost
            </h1>
            <p style="color: #191970; font-size: 1.3rem; font-weight: 500; margin: 0 0 1rem 0; line-height: 1.4;">
                키워드만 입력하면<br>
                SEO 최적화된 완벽한 글 자동 생성
            </p>
            <p style="color: #666; font-size: 1rem; margin: 0; line-height: 1.6;">
                최신 트렌드 반영 • AI 이미지 생성 • 자동 팩트체크
            </p>
        </div>
        <!-- 오른쪽: 이미지 -->
        <div style="text-align: center;">
            <img src="https://raw.githubusercontent.com/cinepark-1974/AutoPost/main/assets/hero_image.png" 
                 alt="AI 블로그 자동화" 
                 style="max-width: 100%; height: auto; border-radius: 12px;">
        </div>
    </div>
</div>

<!-- 모바일 대응 -->
<style>
    @media (max-width: 768px) {
        div[style*="grid-template-columns"] {
            display: block !important;
        }
        div[style*="grid-template-columns"] > div:last-child {
            margin-top: 2rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# API 설정
with st.expander("⚙️ API 설정", expanded=False):
    saved_key = load_api_key()
    from_secrets = False
    try:
        if hasattr(st, 'secrets') and "CLAUDE_API_KEY" in st.secrets:
            from_secrets = True
            st.success("✅ Claude API Key 자동 로드 완료 (Secrets)")
    except:
        pass
    
    col1, col2 = st.columns([4, 1])
    with col1:
        api_key = st.text_input(
            "Claude API Key" if not from_secrets else "Claude API Key (자동 로드됨)",
            value=saved_key if not from_secrets else "••••••••",
            type="password",
            placeholder="sk-ant-api03-..." if not from_secrets else "자동 로드됨",
            disabled=from_secrets
        )
    with col2:
        st.markdown("<div style='padding-top: 1.8rem;'></div>", unsafe_allow_html=True)
        if not from_secrets and st.button("저장"):
            if api_key:
                save_api_key(api_key)
                st.success("✅ 저장됨")
    
    if not from_secrets and not saved_key:
        st.info("💡 Streamlit Cloud Secrets에 CLAUDE_API_KEY를 설정하면 자동 로드됩니다.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    hf_from_secrets = False
    hf_token = ""
    try:
        if hasattr(st, 'secrets') and "HUGGINGFACE_TOKEN" in st.secrets:
            hf_from_secrets = True
            hf_token = st.secrets["HUGGINGFACE_TOKEN"]
            st.success("✅ HuggingFace Token 자동 로드 완료 (Secrets)")
    except:
        pass
    
    if not hf_from_secrets:
        hf_token = st.text_input(
            "HuggingFace Token (AI 이미지 생성용 - 선택)",
            type="password",
            placeholder="hf_xxxxx",
            help="huggingface.co에서 무료 발급"
        )

st.markdown("<br><br>", unsafe_allow_html=True)

# 메인
st.markdown("## 🚀 글 자동 생성")

col1, col2 = st.columns([2, 1])
with col1:
    keyword = st.text_input("키워드", placeholder="예: 주식 초보 추천, 부산 맛집")
with col2:
    category = st.selectbox("카테고리", ["영화", "책", "주식", "맛집", "여행", "IT", "일상", "건강", "요리"])

# 키워드 추천 버튼
col_rec1, col_rec2 = st.columns([1, 3])
with col_rec1:
    if st.button("💡 키워드 추천", help="카테고리별 인기 키워드 추천"):
        claude_key = load_api_key()
        if not claude_key:
            st.error("⚠️ API 키를 먼저 저장해주세요")
        else:
            with st.spinner(f"{category} 카테고리 황금 키워드 찾는 중..."):
                recommendations = recommend_keywords(category, claude_key)
                st.markdown("### 📝 추천 키워드")
                st.markdown(recommendations)
                st.info("💡 위 키워드 중 하나를 선택해서 입력란에 붙여넣으세요!")

st.markdown("<br>", unsafe_allow_html=True)

word_count = st.slider("목표 글자수", 1500, 3000, 2000, 100)

col_opt1, col_opt2 = st.columns(2)
with col_opt1:
    include_image = st.checkbox("AI 이미지 생성", value=True)
with col_opt2:
    use_trends = st.checkbox("최신 트렌드 반영", value=True)

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
        
        result = generate_optimized_post(keyword, category, word_count, claude_key, use_trends)
        
        status.text("SEO 분석 중...")
        progress.progress(100)
        
        if "error" in result:
            st.error(f"❌ {result['error']}")
        else:
            status.empty()
            progress.empty()
            
            # 히스토리에 저장
            st.session_state['post_history'].insert(0, {
                'timestamp': datetime.now(),
                'keyword': keyword,
                'category': category,
                'title': result['title'],
                'content': result['content'],
                'seo_score': result['seo_score']
            })
            
            # 최대 20개까지만 저장
            if len(st.session_state['post_history']) > 20:
                st.session_state['post_history'] = st.session_state['post_history'][:20]
            
            # 파일로 저장
            save_history(st.session_state['post_history'])
            
            st.markdown(f"""
            <div class="seo-score">
                <div class="score-number">{result['seo_score']}</div>
                <div style="font-size: 1.2rem; color: #666; margin-top: 0.5rem;">/ 100점</div>
                <div style="margin-top: 1rem; font-size: 1.1rem; color: #666;">
                    {"🏆 상위 노출 가능" if result['seo_score'] >= 80 else "👍 양호" if result['seo_score'] >= 60 else "⚠️ 개선 필요"}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### 📊 분석 결과")
            for fb in result['feedback']:
                st.markdown(f"- {fb}")
            
            if result['improvements']:
                st.markdown("### 💡 개선 사항")
                for imp in result['improvements']:
                    st.markdown(f"- {imp}")
            
            st.markdown("---")
            
            if include_image:
                st.markdown("### 🖼️ AI 생성 이미지")
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
                    image_info = get_free_image(keyword)
                    st.image(image_info['url'], caption=f"출처: {image_info['source']}", use_container_width=True)
                    st.info("💡 HuggingFace Token을 입력하면 AI로 이미지를 생성할 수 있습니다.")
            
            st.markdown("### 📄 생성된 글")
            st.markdown(result['content'])
            
            # 뉴스 출처는 글 아래에 표시
            if use_trends:
                st.markdown("---")
                st.markdown("### 📰 참고한 최신 트렌드")
                trend_data = search_latest_trends(keyword)
                if trend_data:
                    with st.expander("뉴스 정보 보기 (출처 포함)", expanded=False):
                        for i, news in enumerate(trend_data, 1):
                            st.markdown(f"""
**{i}. {news['title']}**
- 출처: {news['source']}
- 날짜: {news['date']}
- [기사 링크]({news['link']})
""")
                            if i < len(trend_data):
                                st.markdown("---")
                else:
                    st.info("최신 뉴스를 찾을 수 없습니다.")
            
            st.download_button(
                "💾 다운로드",
                result['content'],
                file_name=f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            )

# 작성 히스토리
st.markdown("---")
st.markdown("## 📝 작성 히스토리")

if st.session_state['post_history']:
    for idx, post in enumerate(st.session_state['post_history']):
        with st.expander(
            f"**{post['title'][:50]}{'...' if len(post['title']) > 50 else ''}** "
            f"(SEO: {post['seo_score']}점) - {post['timestamp'].strftime('%m/%d %H:%M')}"
        ):
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.markdown(f"**키워드:** {post['keyword']}")
            with col2:
                st.markdown(f"**카테고리:** {post['category']}")
            with col3:
                st.markdown(f"**점수:** {post['seo_score']}/100")
            
            st.markdown("---")
            st.markdown(post['content'])
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                st.download_button(
                    "💾 다운로드",
                    post['content'],
                    file_name=f"post_{post['timestamp'].strftime('%Y%m%d_%H%M%S')}.txt",
                    key=f"download_{idx}"
                )
            with col_btn2:
                if st.button("🗑️ 삭제", key=f"delete_{idx}"):
                    st.session_state['post_history'].pop(idx)
                    save_history(st.session_state['post_history'])
                    st.rerun()
else:
    st.info("📭 아직 작성한 글이 없습니다. 위에서 키워드를 입력하고 글을 생성해보세요!")

# Footer
st.markdown("""
<div style="text-align: center; padding: 3rem 0 2rem 0; color: #999; border-top: 1px solid #e0e0e0; margin-top: 4rem;">
    <p style="margin: 0;">Made with ❤️ by CINEPARK</p>
    <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">AutoPost v5.0</p>
</div>
""", unsafe_allow_html=True)
