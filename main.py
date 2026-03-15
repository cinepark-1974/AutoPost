import streamlit as st
import anthropic
import requests
from datetime import datetime, timedelta
import json
import re
from prompts import get_transaction_prompt, get_information_prompt, get_casual_prompt, get_news_prompt

# 페이지 설정
st.set_page_config(page_title="AutoPost v10.0", page_icon="✍️", layout="wide")

if 'post_history' not in st.session_state:
    st.session_state['post_history'] = []

def load_api_key():
    try:
        return st.secrets.get("CLAUDE_API_KEY", "")
    except:
        return ""

def save_api_key(api_key):
    st.info("💡 API 키는 Streamlit Cloud Settings > Secrets에서 설정하세요!")
    st.code(f'CLAUDE_API_KEY = "{api_key}"', language="toml")

def classify_keyword_type(keyword):
    """키워드 타입 자동 판별"""
    keyword_lower = keyword.lower()
    
    # 우선순위 1: 정보형 강제 판별
    information_force = [
        "무료 ai", "무료 툴", "무료 프로그램", "무료 앱",
        "베스트", "top", "순위", "랭킹",
        "추천", "리뷰", "가이드", "총정리",
        "뭔가요", "설명", "차이", "vs",
        "방법", "어떻게", "how to"
    ]
    
    if any(kw in keyword_lower for kw in information_force):
        return "information"
    
    # 우선순위 2: 거래형
    transaction_keywords = [
        "할인", "저렴", "가성비", "특가", "세일",
        "구매", "신청", "받는법", "지원금", "혜택",
        "쿠폰", "이벤트", "프로모션", "가격", "얼마"
    ]
    
    if any(kw in keyword_lower for kw in transaction_keywords):
        return "transaction"
    
    # 우선순위 3: 일상형
    casual_keywords = [
        "날씨", "오늘", "이번주", "주말",
        "추운", "더운", "비온",
        "감상", "생각", "느낀", "일상"
    ]
    
    if any(kw in keyword_lower for kw in casual_keywords):
        return "casual"
    
    # 우선순위 4: 뉴스형
    news_keywords = [
        "속보", "긴급", "발표", "공개",
        "신작", "개봉", "출시"
    ]
    
    if any(kw in keyword_lower for kw in news_keywords):
        return "news"
    
    return "information"

def get_content_strategy(keyword_type):
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

def search_realtime_data(keyword):
    return {'money': [], 'percent': [], 'date': []}

def search_official_links(keyword, category):
    return [{"name": "네이버", "url": f"https://search.naver.com/search.naver?query={keyword}", "desc": "검색"}]

def search_event_info(keyword, category):
    today = datetime.now()
    return [{
        "title": f"{keyword} 할인",
        "info": "각 사이트 확인",
        "period": today.strftime("%Y.%m.%d"),
        "note": "변경 가능"
    }]

def get_persona(category):
    intro = "안녕하세요.\n영화 프로듀서의 블로그, CINEPARK입니다."
    
    connections = {
        "영화": {
            "connection": "영화 제작과 투자 경험을 바탕으로",
            "credibility": "광해, 하녀 투자 경험"
        },
        "IT": {
            "connection": "콘텐츠 제작하며 IT 툴에 관심이 많아서",
            "credibility": "블로그 자동화 직접 사용"
        }
    }
    
    default = {"connection": "다양한 경험을 하면서", "credibility": "직접 경험"}
    result = connections.get(category, default)
    result["intro"] = intro
    return result

def get_trending_keywords(category):
    return ["ChatGPT 활용법", "무료 AI 툴 베스트 20", "블로그 자동화"]

def generate_longtail_keywords(base_keyword):
    suffixes = ["할인", "저렴", "가성비", "후기", "방법", "총정리"]
    return [f"{base_keyword} {suffix}" for suffix in suffixes[:12]]

def search_latest_news(keyword):
    return []

def search_unsplash_images(keyword, count=3):
    return [{"url": f"https://source.unsplash.com/800x600/?{keyword},{i}", "credit": "Unsplash", "description": f"{keyword} {i+1}"} for i in range(count)]

def analyze_seo(title, content, keyword):
    score = 0
    feedback = []
    improvements = []
    
    clean_title = title.replace("#", "").strip()
    
    if keyword.lower() in clean_title.lower():
        score += 25
        feedback.append("[OK] 제목 키워드")
    else:
        feedback.append("[X] 제목 키워드 누락")
    
    title_len = len(clean_title)
    if 28 <= title_len <= 32:
        score += 20
        feedback.append(f"[OK] 제목 ({title_len}자)")
    else:
        feedback.append(f"[!] 제목 ({title_len}자)")
    
    content_len = len(content)
    if 1500 <= content_len <= 3000:
        score += 20
        feedback.append(f"[OK] 본문 ({content_len}자)")
    else:
        feedback.append(f"[!] 본문 ({content_len}자)")
    
    kw_count = content.lower().count(keyword.lower())
    if 3 <= kw_count <= 8:
        score += 15
        feedback.append(f"[OK] 키워드 ({kw_count}회)")
    else:
        feedback.append(f"[!] 키워드 ({kw_count}회)")
    
    subtitle_count = content.count("##") - 1
    if 3 <= subtitle_count <= 6:
        score += 10
        feedback.append(f"[OK] 소제목 ({subtitle_count}개)")
    
    if "#" in content:
        score += 10
        feedback.append("[OK] 태그")
    
    return score, feedback, improvements

def generate_blog_post(keyword, category, word_count, api_key):
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            client = anthropic.Anthropic(api_key=api_key)
            
            today = datetime.now()
            year = today.year
            
            keyword_type = classify_keyword_type(keyword)
            strategy = get_content_strategy(keyword_type)
            
            event_text = ""
            if strategy['include_event_info']:
                events = search_event_info(keyword, category)
                event_text = "\n참고:\n" + "\n".join([f"- {e['title']}: {e['info']}" for e in events])
            
            data_text = ""
            if strategy['include_realtime_data']:
                realtime_data = search_realtime_data(keyword)
                if realtime_data['money']:
                    data_text += "\n금액:\n" + "\n".join([f"- {a}{u}" for a, u in realtime_data['money']])
            
            links_text = ""
            if strategy['include_official_links']:
                official_links = search_official_links(keyword, category)
                links_text = "\n링크:\n" + "\n".join([f"- [{l['name']}]({l['url']})" for l in official_links])
            
            persona = get_persona(category)
            
            if keyword_type == "transaction":
                prompt = get_transaction_prompt(keyword, category, year, persona, event_text, data_text, links_text)
            elif keyword_type == "information":
                prompt = get_information_prompt(keyword, category, year, persona)
            elif keyword_type == "casual":
                prompt = get_casual_prompt(keyword, category, year, persona)
            else:
                prompt = get_news_prompt(keyword, category, year, persona, data_text)
            
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text
            
            title_match = re.search(r'##\s*(.+?)(?:\n|$)', content)
            if title_match:
                title = title_match.group(1).strip()
            else:
                title = f"{keyword} 가이드 | {year}년"
            
            clean_title = title.replace("#", "").strip()
            
            keyword_main = keyword.split()[0] if " " in keyword else keyword
            if keyword_main.lower() not in clean_title.lower():
                clean_title = f"{keyword} | {clean_title}"
            
            title_len = len(clean_title)
            if title_len < 28:
                clean_title = f"{clean_title} | {year}년 총정리"
            elif title_len > 32:
                clean_title = clean_title[:30]
            
            title = clean_title
            
            if title_match:
                content = re.sub(r'##\s*.+?(?:\n)', f"## {title}\n", content, count=1)
            else:
                content = f"## {title}\n\n{content}"
            
            score, feedback, improvements = analyze_seo(title, content, keyword)
            
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
            
            if attempt == max_retries - 1:
                return {
                    "title": title,
                    "content": content,
                    "seo_score": score,
                    "feedback": feedback,
                    "improvements": improvements,
                    "attempts": attempt + 1,
                    "success": False,
                    "warning": f"⚠️ {score}점"
                }
                
        except Exception as e:
            if attempt == max_retries - 1:
                return {"error": str(e)}
    
    return {"error": "생성 실패"}

# UI
st.title("✍️ AutoPost v10.0")
st.caption("네이버 블로그 SEO 최적화 (타입별 맞춤)")

with st.expander("🔑 API 설정"):
    api_key_input = st.text_input("Claude API 키", type="password", value=load_api_key())
    if st.button("저장 방법"):
        save_api_key(api_key_input)

st.markdown("---")

with st.expander("🔥 트렌드", expanded=False):
    trend_cat = st.selectbox("카테고리", ["IT"], key="trend_cat")
    keywords = get_trending_keywords(trend_cat)
    
    for idx, kw in enumerate(keywords):
        if st.button(f"⭐ {kw}", key=f"trend_{idx}"):
            st.session_state['selected_keyword'] = kw
            st.rerun()

st.markdown("---")
st.markdown("## 🚀 글 생성")

default_keyword = st.session_state.get('selected_keyword', '')

col1, col2 = st.columns([2, 1])
with col1:
    keyword = st.text_input("키워드", value=default_keyword, placeholder="예: 무료 AI 툴 베스트 20")
    
    if keyword and len(keyword) > 2:
        keyword_type = classify_keyword_type(keyword)
        type_emoji = {"transaction": "💰", "information": "📚", "casual": "☕", "news": "📰"}
        type_name = {"transaction": "거래형", "information": "정보형", "casual": "일상형", "news": "뉴스형"}
        st.info(f"{type_emoji[keyword_type]} **판별:** {type_name[keyword_type]}")
    
    if keyword and len(keyword) > 2:
        with st.expander("💡 롱테일"):
            longtail = generate_longtail_keywords(keyword)
            for idx, ltk in enumerate(longtail[:6]):
                if st.button(f"📌 {ltk}", key=f"lt_{idx}"):
                    st.session_state['selected_keyword'] = ltk
                    st.rerun()

with col2:
    category = st.selectbox("카테고리", ["영화", "IT", "여행"])

word_count = st.slider("글자수", 1500, 3000, 2000)

if st.button("✨ 생성", type="primary"):
    api = load_api_key() or api_key_input
    
    if not api:
        st.error("⚠️ API 키 입력")
    elif not keyword:
        st.error("⚠️ 키워드 입력")
    else:
        with st.spinner("생성 중..."):
            result = generate_blog_post(keyword, category, word_count, api)
        
        if "error" in result:
            st.error(f"❌ {result['error']}")
        else:
            st.markdown(f"### SEO: {result['seo_score']}/100")
            
            if result['seo_score'] >= 85:
                st.success("🏆 85점 이상!")
            
            for fb in result['feedback']:
                st.text(fb)
            
            st.markdown("---")
            st.markdown(result['content'])
            
            st.download_button(
                "💾 다운로드",
                result['content'],
                f"{keyword.replace(' ', '_')}.txt",
                mime="text/plain"
            )
