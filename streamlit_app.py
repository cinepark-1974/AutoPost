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

# GitHub 저장 함수
def save_to_github(content, title, keyword, seo_score):
    """작성된 글을 GitHub에 저장"""
    try:
        # GitHub Token 확인
        github_token = None
        try:
            if hasattr(st, 'secrets') and "GITHUB_TOKEN" in st.secrets:
                github_token = st.secrets["GITHUB_TOKEN"]
        except:
            pass
        
        if not github_token:
            return {"success": False, "message": "GitHub Token이 설정되지 않았습니다."}
        
        # 파일명 생성 (날짜_키워드.md)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_keyword = re.sub(r'[^a-zA-Z0-9가-힣]', '_', keyword)
        filename = f"{timestamp}_{safe_keyword}.md"
        
        # GitHub API 설정
        repo_owner = st.secrets.get("GITHUB_OWNER", "")
        repo_name = st.secrets.get("GITHUB_REPO", "AutoPost")
        
        if not repo_owner:
            return {"success": False, "message": "GitHub 사용자명이 설정되지 않았습니다."}
        
        # 파일 내용 (메타데이터 포함)
        file_content = f"""---
title: {title}
keyword: {keyword}
seo_score: {seo_score}
date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
---

{content}
"""
        
        # GitHub API로 파일 업로드
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/posts/{filename}"
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        import base64
        encoded_content = base64.b64encode(file_content.encode()).decode()
        
        data = {
            "message": f"Add post: {title}",
            "content": encoded_content
        }
        
        response = requests.put(url, headers=headers, json=data)
        
        if response.status_code in [200, 201]:
            return {
                "success": True, 
                "message": "GitHub에 저장 완료!",
                "url": f"https://github.com/{repo_owner}/{repo_name}/blob/main/posts/{filename}"
            }
        else:
            return {"success": False, "message": f"GitHub 저장 실패: {response.status_code}"}
            
    except Exception as e:
        return {"success": False, "message": f"오류: {str(e)}"}

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
        
        # 현재 날짜 자동 생성
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month
        month_name = current_date.strftime('%B')  # January, February...
        season = "봄" if month in [3,4,5] else "여름" if month in [6,7,8] else "가을" if month in [9,10,11] else "겨울"
        
        prompt = f"""당신은 블로그 SEO 전문가입니다. {category} 카테고리에서 현재 검색량이 많고 경쟁도가 낮은 황금 키워드 10개를 추천해주세요.

📅 현재 시점: {year}년 {month}월 ({season}, {month_name})

조건:
1. 월 검색량: 1,000~10,000 (너무 경쟁 치열하지 않음)
2. 경쟁 문서: 100개 이하 (상위 노출 가능)
3. {year}년 {month}월 현재 트렌드 반영
4. 롱테일 키워드 포함 (3-5단어)
5. 계절성 고려 ({season} 시즌에 맞는 키워드)

출력 형식:
1. [키워드] - [이유 한 줄]
2. [키워드] - [이유 한 줄]
...

예시:
1. {year} {category} 추천 어플 - 최신 년도 검색, 구체적
2. {season} {category} 꿀팁 - 계절 특화, 검색 증가

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
    """Google News RSS로 최신 트렌드 검색 (실제 기사 URL 추출)"""
    try:
        url = f"https://news.google.com/rss/search?q={keyword}&hl=ko&gl=KR&ceid=KR:ko"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)
            
            news_items = []
            for item in root.findall('.//item')[:5]:
                title = item.find('title').text if item.find('title') is not None else ""
                google_link = item.find('link').text if item.find('link') is not None else ""
                pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""
                source = item.find('source').text if item.find('source') is not None else "출처 불명"
                
                # 실제 원본 기사 URL 추출
                actual_link = google_link
                try:
                    # Google News 리다이렉트 URL을 따라가서 실제 URL 가져오기
                    if "news.google.com" in google_link:
                        redirect_response = requests.get(google_link, timeout=5, allow_redirects=True)
                        actual_link = redirect_response.url
                except:
                    # 실패하면 Google 링크 그대로 사용
                    actual_link = google_link
                
                news_items.append({
                    "title": title,
                    "link": actual_link,  # 실제 기사 URL
                    "date": pub_date[:16],
                    "source": source
                })
            
            return news_items
        return []
    except:
        return []

# URL 내용 가져오기
def fetch_url_content(url):
    """사용자가 제공한 URL의 텍스트 내용 가져오기"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # script, style 태그 제거
            for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
                tag.decompose()
            
            # 본문 추출 (p 태그 우선)
            paragraphs = soup.find_all('p')
            if paragraphs:
                text = '\n'.join([p.get_text().strip() for p in paragraphs[:10]])
            else:
                text = soup.get_text()
            
            # 정리
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            clean_text = '\n'.join(lines[:30])  # 최대 30줄
            
            return clean_text[:2000] if clean_text else None  # 최대 2000자
        return None
    except Exception as e:
        return None

# SEO 자동 최적화 트리거
def apply_seo_triggers(content, keyword, year):
    """SEO 점수를 자동으로 높이는 후처리"""
    
    # 트리거 1: 태그 섹션 자동 추가
    if "## 태그" not in content and "#태그" not in content:
        tags = f"""

## 태그
#{keyword.replace(' ', '')} #{year} #최신 #추천 #정보 #꿀팁 #가이드 #리뷰 #후기 #팁"""
        content += tags
    
    # 트리거 2: 소제목에 이모지 자동 추가
    emoji_list = ["✨", "💡", "🎯", "⚠️", "🔥", "⭐", "👍"]
    lines = content.split('\n')
    emoji_index = 0
    
    for i, line in enumerate(lines):
        # ## 소제목이지만 이모지가 없는 경우
        if line.strip().startswith('##') and not any(emoji in line for emoji in emoji_list):
            # 제목(첫 번째 ##)은 제외
            if i > 0:
                lines[i] = line.rstrip() + f" {emoji_list[emoji_index % len(emoji_list)]}"
                emoji_index += 1
    
    content = '\n'.join(lines)
    
    # 트리거 3: 키워드 밀도가 너무 낮으면 자연스럽게 추가
    keyword_count = content.lower().count(keyword.lower())
    if keyword_count < 3:
        # 첫 문단 뒤에 키워드 포함 문장 추가
        insertion_point = content.find('\n\n', content.find('CINEPARK입니다.'))
        if insertion_point > 0:
            keyword_sentence = f"\n\n오늘은 {keyword}에 대해 자세히 알아보겠습니다!"
            content = content[:insertion_point] + keyword_sentence + content[insertion_point:]
    
    # 트리거 4: 마무리 댓글 유도 문구 자동 추가
    if "댓글" not in content and "공유" not in content:
        closing = f"""

여러분은 {keyword}에 대해 어떻게 생각하시나요? 댓글로 경험을 공유해주세요! 😊"""
        
        # 태그 섹션 앞에 삽입
        tag_pos = content.find("## 태그")
        if tag_pos > 0:
            content = content[:tag_pos] + closing + "\n\n" + content[tag_pos:]
        else:
            content += closing
    
    return content

# SEO 분석
def analyze_seo(title, content, keyword):
    score = 0
    feedback = []
    improvements = []
    
    # 제목에서 ## 제거하고 순수 텍스트만
    clean_title = title.replace("#", "").strip()
    
    # 1. 제목에 키워드 포함 (25점)
    if keyword.lower() in clean_title.lower():
        score += 25
        feedback.append("✅ 제목에 키워드 포함")
    else:
        feedback.append("❌ 제목에 키워드 추가")
        improvements.append(f"제목에 '{keyword}' 추가")
    
    # 2. 제목 길이 (20점) - 2026년 기준: 28-32자 최적
    title_len = len(clean_title)
    if 25 <= title_len <= 35:
        score += 20
        feedback.append(f"✅ 제목 길이 최적 ({title_len}자)")
    elif 20 <= title_len <= 40:
        score += 15
        feedback.append(f"⚠️ 제목 길이 양호 ({title_len}자)")
        improvements.append("제목 28-32자가 가장 이상적")
    else:
        feedback.append(f"❌ 제목 길이 부적합 ({title_len}자)")
        improvements.append("제목 28-32자로 조정")
    
    # 3. 본문 길이 (20점) - 2026년 기준: 1500-3000자 최적
    content_length = len(content)
    if 1500 <= content_length <= 3000:
        score += 20
        feedback.append(f"✅ 본문 최적 ({content_length}자)")
    elif 1000 <= content_length < 1500:
        score += 15
        feedback.append(f"⚠️ 본문 양호 ({content_length}자)")
        improvements.append(f"본문 {1500 - content_length}자 추가 권장")
    elif content_length > 3000:
        score += 15
        feedback.append(f"⚠️ 본문 다소 김 ({content_length}자)")
        improvements.append("본문 3000자 이내 권장")
    else:
        feedback.append(f"❌ 본문 부족 ({content_length}자)")
        improvements.append(f"본문 {1500 - content_length}자 추가 필요")
    
    # 4. 키워드 밀도 (15점) - 2026년 기준: 자연스럽게 3-8회
    keyword_count = content.lower().count(keyword.lower())
    if 3 <= keyword_count <= 8:
        score += 15
        feedback.append(f"✅ 키워드 밀도 적절 ({keyword_count}회)")
    elif 2 <= keyword_count < 3 or 8 < keyword_count <= 12:
        score += 10
        feedback.append(f"⚠️ 키워드 밀도 양호 ({keyword_count}회)")
    else:
        feedback.append(f"❌ 키워드 밀도 부적절 ({keyword_count}회)")
        if keyword_count < 2:
            improvements.append(f"'{keyword}' {3 - keyword_count}회 추가")
        else:
            improvements.append(f"'{keyword}' 과다, {keyword_count - 8}회 줄이기")
    
    # 5. 소제목 (10점) - 2026년 기준: 3-5개 최적
    subtitle_count = content.count("##") - 1  # 첫 번째 제목 제외
    if 3 <= subtitle_count <= 5:
        score += 10
        feedback.append(f"✅ 소제목 최적 ({subtitle_count}개)")
    elif subtitle_count >= 2:
        score += 7
        feedback.append(f"⚠️ 소제목 양호 ({subtitle_count}개)")
    else:
        feedback.append(f"❌ 소제목 부족 ({subtitle_count}개)")
        improvements.append("소제목 3-5개 권장")
    
    # 6. 이모지 (5점)
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        "]+", flags=re.UNICODE)
    
    if emoji_pattern.search(content):
        score += 5
        feedback.append("✅ 이모지 사용")
    else:
        feedback.append("⚠️ 이모지 추가 권장")
        improvements.append("이모지 2-3개 추가")
    
    # 7. 해시태그 (5점)
    if "#" in content or "태그" in content:
        score += 5
        feedback.append("✅ 해시태그 포함")
    else:
        feedback.append("⚠️ 해시태그 추가 권장")
        improvements.append("해시태그 5개 이상 추가")
    
    return score, feedback, improvements

# 올인원 자동 생성
def generate_optimized_post(keyword, category, word_count, claude_api_key, use_trends=True, custom_urls=None):
    try:
        client = anthropic.Anthropic(api_key=claude_api_key)
        
        # 현재 날짜 자동 생성
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month
        day = current_date.day
        date_str = f"{year}년 {month}월 {day}일"
        
        trend_info = ""
        
        # 사용자 제공 URL 처리
        if custom_urls:
            url_contents = []
            for url in custom_urls:
                content = fetch_url_content(url)
                if content:
                    url_contents.append(f"📎 {url}\n{content[:500]}...")
            
            if url_contents:
                trend_info += f"""

📎 사용자가 제공한 참고 자료:
{chr(10).join(url_contents)}

위 자료를 참고하되, 다음 규칙을 지키세요:
1. 내용을 그대로 복사하지 말고 자신의 언어로 재구성
2. 출처를 명시 (예: "최근 보도에 따르면", "관련 자료에 의하면")
3. 핵심 정보만 추출하여 활용
"""
        
        # Google News 트렌드
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
2. 뉴스 언급 후 문장을 끝내고, 한 줄 띄운 뒤 링크 삽입
   예시:
   최근 테크크런치 보도에 따르면, AI 기술이 급속도로 발전하고 있습니다.
   [테크크런치 기사 보기](링크)
   
3. 출처가 불확실한 정보는 "~라는 의견도 있습니다" 등으로 신중하게 표현
4. 과장하지 말고 뉴스 내용을 정확하게 전달
5. 링크 텍스트는 "[출처명 기사 보기]" 형식 사용
"""
        
        prompt = f"""당신은 월 방문자 10만 명을 달성한 네이버 블로그 인기 블로거입니다. 

📅 오늘 날짜: {date_str}

키워드: {keyword}
카테고리: {category}
목표 글자수: {word_count}자
{trend_info}

⚠️ 네이버 블로그 운영정책 필수 준수사항:

1. 개인 경험과 진정성
   - "나의 생각, 느낌, 관심을 기록"하는 개인 공간
   - 나의 실제 경험, 의견, 후기를 담을 것
   - AI가 작성했다는 느낌 최소화
   - 자연스러운 구어체 사용

2. 광고/리뷰 관련 (중요!)
   - 광고주로부터 금전 제공받았다면 반드시 명시
   - 내돈내산 리뷰가 아니면 명확히 표시
   - 표시광고법 준수 필수
   - 과도한 상업성 지양

3. 커뮤니케이션 에티켓
   - 타인 비방, 폄하 금지
   - 불쾌감 주는 내용 금지
   - 상호 존중 태도 유지

4. 금지 사항
   - 음란물 절대 금지
   - 타인 명예훼손 금지
   - 저작권 침해 금지
   - 청소년 유해 콘텐츠 금지

🎯 네이버 블로그 2026년 최적화 작성 규칙:

1. 제목 (매우 중요!):
   - **최적 길이: 28-32자** (2026년 검색 알고리즘)
   - **{keyword}를 자연스럽게 변형하여 제목 작성**
   
   ❌ 잘못된 제목:
   - "## {keyword} {year}년 최신판" (키워드 그대로)
   - "## AI 영화 제작 최신 뉴스" (15자, 너무 짧음)
   
   ✅ 올바른 제목 예시:
   키워드: "AI 영화 제작, 공모전"
   → "## AI 영화 공모전 완벽 가이드! 프로듀서 현장 후기 {year}년" (29자)
   → "## {year} AI 영화 공모전 폭증! BIFAN·영진위 총정리" (28자)
   
   키워드: "나가노 여행"
   → "## 나가노 스노우 몽키 여행 완벽 정리! {year}년 겨울" (28자)
   
   - 키워드의 핵심 단어를 조합하여 자연스러운 문장 구성
   - 숫자, 느낌표 활용 (완벽, 베스트, 총정리 등)
   - 구체적 정보 포함 (기관명, 장소명 등)

2. 인사말 (반드시):
   안녕하세요.
   영화 프로듀서의 블로그, CINEPARK입니다.

3. 본문 길이 (중요!):
   - **최적 길이: 1500-3000자** (2026년 기준)
   - 너무 짧으면 저품질 판정
   - 너무 길면 이탈률 증가
   - 목표: {word_count}자 내외

4. 소제목 작성:
   - **소제목 3-5개** (## 형식) - 2026년 최적
   
   ✅ 좋은 소제목 예시:
   - "## {keyword} 핵심 정리 💡"
   - "## {keyword} 실전 활용법 🎯"
   - "## {keyword} 주의사항 ⚠️"
   - "## 2026년, {keyword}의 시대가 열렸습니다 💡"
   
   ❌ 피해야 할 소제목:
   - "## {keyword}를 많이 하고 계시지요?" (독자 상황 단정)
   - 질문만 던지고 답변 없는 형식
   
   각 소제목 2-3문단씩 작성

5. 도입부 (CINEPARK 경험 활용):
   
   **CINEPARK 배경:**
   - 영화: 기획 프로듀서, <광해>, <하녀>, <동갑내기 과외하기> 등 제작
   - 국제: 인도네시아/베트남/일본 공동제작, <수상한 그녀> 리메이크
   - 여행: 런던 체류(2005-2006), 도쿄 체류(1999), 25개국 이상 방문
   - 학력: 정치외교학과 졸업, 문화콘텐츠학과 시나리오 전공 석사
   - 저서: <감각구역> 소설 집필
   - 와인: 2001년부터 (와린이)
   
   카테고리별 도입 예시:
   
   [영화]
   "그동안 많은 작품을 기획하고 제작하면서..."
   "<광해>, <하녀> 등을 제작하면서 느낀 건데..."
   
   [여행]
   "도쿄에서 1년 살면서..."
   "2023년 나가노 여행에서 스노우 몽키 봤을 때..."
   
   [일반]
   "제가 직접 알아본 최신 정보와..."
   "현장에서 느낀 솔직한 후기를..."

6. 본문 작성 (구어체 필수):
   - {keyword} 3-8회 자연스럽게
   - 구어체: "~더라고요", "~거든요", "~이에요", "~네요"
   - 개인 경험: "제 경험상", "느끼는 건", "알아본 건데"
   - 솔직함: "사실", "정직하게", "솔직히"
   
   ✅ 좋은 표현:
   - "제가 직접 알아본 최신 정보와 현장에서 느낀 솔직한 후기를 공유해드릴게요."
   - "동아일보 기사를 보고 정말 깜짝 놀랐는데..."
   - "제 경험상 가장 효과적인 방법은 단계별 접근이에요."

7. 뉴스/자료 인용 (출처 표기):
   
   ✅ 올바른 형식:
   ```
   브랜드경제신문 보도에 따르면, BIFAN에서 '환상영화학교: 창작자 과정' 2026을 통해 AI 영화감독 등용문을 열었다고 하더라고요.
   [브랜드경제신문 기사 보기](링크)
   ```
   
   ❌ 잘못된 형식:
   ```
   BIFAN에서...
   https://www.benews.co.kr/news/470290
   (URL만 나열)
   ```
   
   - 문장으로 내용 설명 후
   - 한 줄 띄고
   - [출처명 기사 보기](URL) 형식

8. 이모지 사용:
   - 소제목에 2-3개
   - 본문에 가끔 (😊 💡 🎯 ✨ ⚠️)
   - 과하지 않게

9. 마무리:
   여러분은 {keyword}에 대해 어떻게 생각하세요?
   혹시 관련 경험이 있으시다면 댓글로 공유해주세요!

10. 태그:
    ## 태그
    #{keyword의핵심단어들} #{year} #프로듀서후기 #현장경험 #정보공유
    
    ✅ 구체적 태그:
    - 기관명, 고유명사 포함
    - 타겟 명확히 (#창작자지원, #영화제작자)
    
    ❌ 피할 태그:
    - 쉼표 포함 (#AI영화제작,공모전)
    - 너무 일반적 (#최신, #추천, #정보)

⚠️ 작성 체크리스트:
✅ 제목 28-32자 (키워드 자연스럽게 변형)
✅ 인사: "안녕하세요." (줄바꿈) "CINEPARK입니다."
✅ 소제목 3-5개, 각각 이모지 포함
✅ 구어체 사용 (~더라고요, ~거든요, ~이에요)
✅ 개인 경험/의견 표현 (제 경험상, 느끼는 건)
✅ 출처 표기 시 링크 형식: [출처명 기사 보기](URL)
✅ {keyword} 3-8회 자연스럽게
✅ 본문 1500-3000자
✅ 댓글 유도 마무리
✅ 태그 10개 내외, 구체적으로

지금 바로 위 규칙을 정확히 따라 작성하세요!"""

2. 인사말 (반드시):
   안녕하세요.
   영화 프로듀서의 블로그, CINEPARK입니다.

3. 본문 길이 (중요!):
   - **최적 길이: 1500-3000자** (2026년 기준)
   - 너무 짧으면 저품질 판정
   - 너무 길면 이탈률 증가
   - 목표: {word_count}자 내외

4. 도입부 (개인 경험 - CINEPARK의 배경 활용):
   
   **CINEPARK 배경:**
   - 영화: 기획 프로듀서, <광해>, <하녀>, <동갑내기 과외하기> 등 제작
   - 국제: 인도네시아/베트남/일본 공동제작, <수상한 그녀> 리메이크
   - 여행: 런던 체류(2005-2006), 도쿄 체류(1999), 25개국 이상 방문
   - 학력: 정치외교학과 졸업, 문화콘텐츠학과 시나리오 전공 석사
   - 저서: <감각구역> 소설 집필
   - 와인: 2001년부터 (와린이)
   
   카테고리별 도입 예시:
   
   [영화]
   "영화 프로듀서로 <광해>, <하녀> 등을 제작하면서..."
   "영화 기획개발을 하다 보니 {keyword}에 관심이..."
   "시나리오 전공하면서 느낀 건데..."
   
   [여행 - 일본]
   "도쿄에서 1년 살았고, 나가노/오키나와/교토 등 다녀왔는데..."
   "2023년 나가노에서 스노우 몽키 보면서..."
   "큐슈 온천 여행했을 때..."
   
   [여행 - 유럽]
   "런던 체류하면서 밀라노, 피렌체, 바르셀로나 등 다녀왔는데..."
   "프라하 맥주 투어 중에..."
   "칸 영화제 참석했을 때..."
   
   [여행 - 동남아]
   "인도네시아/베트남 공동제작 하면서 자카르타, 하노이 자주 갔는데..."
   "2022년 세부에서 고래상어 봤을 때..."
   "방콕 콘텐츠 엑스포 참가했을 때..."
   
   [와인/라이프스타일]
   "2001년부터 와인 마셔왔는데, 전문가는 아니고 와린이 수준이에요..."
   "주로 싼 와인만 마셔봤지만..."
   
   [책/소설]
   "<감각구역> 소설 쓰면서..."
   "시나리오 전공하다 보니..."
   
   [IT/일반]
   "영화 제작 과정에서 {keyword} 관련..."
   "개인적으로 {keyword}를 찾아보면서..."
   
   첫 문단에 {keyword} 1회 포함

5. 본문 구조:
   - **소제목 3-5개** (## 형식) - 2026년 최적
   - 각 섹션 2-3문단
   - {keyword} 전체 3-8회 자연스럽게
   - 구어체 (~했어요, ~더라고요, ~네요)

6. 경험과 의견 표현:
   - "제 경험상 ~"
   - "개인적으로는 ~"
   - "저는 ~라고 생각해요"
   - "제가 느낀 건 ~"

7. 이모지 사용:
   - 소제목에 2-3개
   - 너무 많으면 역효과
   - 예: 😊 💡 🎯 ✨ ⚠️

8. 출처 표기:
   뉴스 인용 시:
   최근 OO 기사를 보니, ~하더라고요.
   [OO 기사 보기](링크)

9. 마무리:
   여러분은 {keyword}에 대해 어떻게 생각하시나요?
   댓글로 경험 공유해주시면 감사하겠습니다! 😊

10. 태그:
    ## 태그
    #{keyword.replace(' ', '')} #{year} #개인후기 #경험담 #정보공유

📝 작성 예시 (실제 CINEPARK 글 스타일):

<영화 카테고리 - 실제 작성 스타일>
## AI 영화 공모전 완벽 가이드! 프로듀서 현장 후기 2026 ✨

안녕하세요.
영화 프로듀서의 블로그, CINEPARK입니다.

그동안 많은 작품을 기획하고 제작하면서 영화계의 급격한 변화를 체감하고 있는데요, 
올해 들어 AI 영화 제작 공모전이 정말 폭발적으로 늘어나더라고요!
제가 직접 알아본 최신 정보와 현장에서 느낀 솔직한 후기를 공유해드릴게요! 😊

## AI 영화 공모전 핵심 정리 💡

AI 영화 제작과 관련한 공모전의 가장 중요한 포인트는 바로 접근성이 완전히 달라졌다는 거예요.
브랜드경제신문 보도에 따르면, BIFAN에서 '환상영화학교: 창작자 과정' 2026을 통해 AI 영화감독 등용문을 열었다고 하더라고요.
[브랜드경제신문 기사 보기](https://www.benews.co.kr/news/470290)

영화 기획개발을 하면서 느끼는 건, 예전에는 수억 원의 제작비와 대규모 스태프가 필요했던 일들을 이제 개인이 할 수 있게 되었다는 거예요.

## AI 영화 공모전 실전 활용법 🎯

실제로 AI 영화 공모전을 어떻게 활용할까요?
동아일보 기사를 보고 정말 깜짝 놀랐는데, "1년 걸릴 영화를 카메라 없이 8일만에 완성했다"는 내용이더라고요.
[동아일보 기사 보기](https://www.donga.com/news/...)

제 경험상 가장 효과적인 방법은 단계별 접근이에요.
처음부터 2시간짜리 극장용 장편영화를 생성형 AI로 만든다는 건 다소 거짓말에 가깝습니다.
먼저 3-5분 정도의 짧은 콘셉트 영상부터 시작해보기를 권합니다.

## AI 공모전 주의사항 ⚠️

AI 영화 제작 공모전 참여 시 주의할 점도 분명히 있어요.
CGV에서 진행한 AI영화 공모전 결과를 보면, 기술적 완성도보다는 스토리텔링이 역시 중요한 것 같습니다.
아직까지 AI는 도구일 뿐이라는 생각이 듭니다.

여러분은 AI 영화 제작에 대해 어떻게 생각하세요?
혹시 공모전 참여 경험이 있으시다면 댓글로 경험 공유해주세요!

## 태그
#AI영화제작 #영화공모전 #BIFAN #영화진흥위원회 #프로듀서후기 
#2026공모전 #생성형AI #영화제작팁 #창작자지원 #영화감독

<여행 - 일본>
## 나가노 스노우 몽키 여행 완벽 정리! 2026년 겨울 ✨

안녕하세요.
영화 프로듀서의 블로그, CINEPARK입니다.

도쿄에서 1년 살았고, 2023년 나가노 여행에서 스노우 몽키 봤을 때 정말 신기했어요!
제가 직접 다녀온 나가노 여행 꿀팁을 공유해드릴게요! 😊

## 나가노 여행 핵심 정리 💡

나가노 여행의 가장 큰 매력은... [2-3문단]
큐슈 온천 여행했을 때도 느꼈지만, 일본 온천은 정말 특별하더라고요.

⚠️ 핵심 포인트:
- 제목 28-32자 (키워드 자연스럽게 변형)
- 구어체 필수 (~더라고요, ~거든요, ~이에요)
- 출처 링크: [기사명](URL) 형식
- 개인 경험 강조 (제 경험상, 느끼는 건, 알아본 건데)
- 솔직한 표현 (사실, 정직하게, 거짓말에 가깝습니다)
- 소제목마다 이모지
- 댓글 유도 마무리
- 구체적 태그 (기관명, 고유명사)"""

<여행 - 유럽>
## {keyword} 유럽 살면서 느낀 점! {year}년 ✨

안녕하세요.
영화 프로듀서의 블로그, CINEPARK입니다.

런던에서 1년 살면서 밀라노, 피렌체, 바르셀로나 등 
여행했는데요, {keyword}에 대해... [유럽 체류 경험 2-3문단]

## {keyword} 프라하 맥주 투어 중 느낀 점 💡
2016년 프라하/빈/부다페스트 다녀왔을 때... [구체적 경험 2-3문단]

<여행 - 동남아>
## {keyword} 동남아 출장/여행 꿀팁! {year}년 ✨

안녕하세요.
영화 프로듀서의 블로그, CINEPARK입니다.

영화 공동제작으로 자카르타, 하노이 자주 가는데요,
2022년 세부에서 고래상어 봤을 때 {keyword}에 대해... 😊

## {keyword} 방콕/발리/세부 경험담 💡
방콕 콘텐츠 엑스포 참가했을 때... [현지 경험 2-3문단]

<와인/라이프스타일>
## {keyword} 와린이가 알아본 정보! {year}년 ✨

안녕하세요.
영화 프로듀서의 블로그, CINEPARK입니다.

2001년부터 와인 마셔왔는데, 전문가는 아니고 
와린이 수준이에요. {keyword}에 대해 알아봤습니다! 😊

## {keyword} 주로 싼 와인 마신 경험으로 💡
전문가들 많으시니 제 경험만... [솔직한 후기 2-3문단]

<책/시나리오>
## {keyword} 작가 관점에서! {year}년 ✨

안녕하세요.
영화 프로듀서의 블로그, CINEPARK입니다.

<감각구역> 소설 쓰면서, 시나리오 전공하면서 
{keyword}에 대해 느낀 점을... 😊

여러분은 {keyword}에 대해 어떻게 생각하시나요? 
댓글로 경험 공유해주시면 감사하겠습니다!

## 태그
#{keyword.replace(' ', '')} #{year} #영화프로듀서 #여행경험 #현장후기

⚠️ CINEPARK 페르소나 핵심:
- 영화 제작 현장 경험 (광해, 하녀, 수상한그녀 리메이크 등)
- 국제 공동제작 경험 (인도네시아, 베트남, 일본)
- 25개국 이상 여행 경험 (런던/도쿄 체류, 유럽/아시아 다수)
- 시나리오 전공, 소설가 (감각구역)
- 와린이 (2001년~, 비전문가 관점)
- 진솔하고 구체적인 개인 경험 중심!"""
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )
        
        generated_content = message.content[0].text
        
        # SEO 자동 최적화 트리거 적용
        generated_content = apply_seo_triggers(generated_content, keyword, year)
        
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
        
        if score < 70:
            # 실제 작성 글 기반 구체적 재작성 프롬프트
            retry_prompt = f"""❌ SEO 점수 {score}점 - 목표 85점 이상 필요

다음 형식을 정확히 따라 다시 작성하세요:

## [28-32자 제목] ✨
예: "AI 영화 공모전 완벽 가이드! 프로듀서 현장 후기 {year}년"

안녕하세요.
영화 프로듀서의 블로그, CINEPARK입니다.

그동안 많은 작품을 기획하고 제작하면서 {keyword}의 급격한 변화를 체감하고 있는데요...
제가 직접 알아본 최신 정보와 현장에서 느낀 솔직한 후기를 공유해드릴게요! 😊

## {keyword} 핵심 정리 💡
{keyword}의 가장 중요한 포인트는... [2-3문단, 구어체 사용]
브랜드경제신문 보도에 따르면...
[브랜드경제신문 기사 보기](링크)

## {keyword} 실전 활용법 🎯
실제로 {keyword}를 어떻게 활용할까요?
제 경험상 가장 효과적인 방법은... [2-3문단]

## {keyword} 주의사항 ⚠️
{keyword} 사용 시 주의할 점도 분명히 있어요.
[2-3문단, 구체적 사례]

여러분은 {keyword}에 대해 어떻게 생각하세요?
댓글로 경험 공유해주세요!

## 태그
#{keyword핵심단어} #{year} #프로듀서후기 #현장경험 #정보공유

개선사항:
{chr(10).join([f"- {imp}" for imp in improvements])}

⚠️ 필수 체크:
✅ 제목 28-32자 (키워드 자연스럽게 변형)
✅ 구어체: ~더라고요, ~거든요, ~이에요
✅ 출처 표기: [기사명](URL) 형식
✅ 소제목 3-5개 + 이모지
✅ {keyword} 3-8회 자연스럽게
✅ 본문 1500자 이상"""
            
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
            
            # 재작성 후에도 SEO 트리거 적용
            generated_content = apply_seo_triggers(generated_content, keyword, year)
            
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
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # GitHub 저장 설정 안내
    github_configured = False
    try:
        if hasattr(st, 'secrets') and "GITHUB_TOKEN" in st.secrets and "GITHUB_OWNER" in st.secrets:
            github_configured = True
            st.success("✅ GitHub 저장 기능 활성화")
    except:
        pass
    
    if not github_configured:
        with st.expander("📤 GitHub 자동 저장 설정 방법 (선택)", expanded=False):
            st.markdown("""
**Streamlit Cloud Secrets에 다음 정보 추가:**

```toml
GITHUB_TOKEN = "ghp_xxxxx"  # GitHub Personal Access Token
GITHUB_OWNER = "your-username"  # GitHub 사용자명
GITHUB_REPO = "AutoPost"  # 저장소 이름 (기본: AutoPost)
```

**GitHub Token 발급:**
1. GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. repo 권한 체크
4. 생성된 토큰 복사

작성한 글이 `your-repo/posts/` 폴더에 자동 저장됩니다!
""")

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

# 참고 URL 입력 (선택)
with st.expander("📎 참고 자료 URL 추가 (선택)", expanded=False):
    st.markdown("**글 작성에 참고할 뉴스나 기사 URL을 입력하세요** (최대 3개)")
    url1 = st.text_input("URL 1", placeholder="https://example.com/article1", key="url1")
    url2 = st.text_input("URL 2", placeholder="https://example.com/article2", key="url2")
    url3 = st.text_input("URL 3", placeholder="https://example.com/article3", key="url3")
    st.info("💡 입력한 URL의 내용을 AI가 자동으로 읽고 참고합니다.")

word_count = st.slider("목표 글자수", 1500, 3000, 2000, 100)

col_opt1, col_opt2, col_opt3 = st.columns(3)
with col_opt1:
    include_image = st.checkbox("AI 이미지 생성", value=True)
with col_opt2:
    use_trends = st.checkbox("최신 트렌드 반영", value=True)
with col_opt3:
    st.markdown("**SEO 자동 최적화** ✅")
    st.caption("항상 활성화됨")

st.markdown("<br>", unsafe_allow_html=True)

if st.button("생성하기", type="primary"):
    claude_key = load_api_key()
    
    if not claude_key:
        st.error("⚠️ API 키를 먼저 저장해주세요")
    elif not keyword:
        st.error("⚠️ 키워드를 입력해주세요")
    else:
        # 입력된 URL 수집
        custom_urls = []
        for url_input in [url1, url2, url3]:
            if url_input and url_input.startswith('http'):
                custom_urls.append(url_input)
        
        progress = st.progress(0)
        status = st.empty()
        
        if custom_urls:
            status.text(f"참고 자료 {len(custom_urls)}개 읽는 중...")
            progress.progress(20)
        
        status.text("제목 최적화 중...")
        progress.progress(40)
        status.text("본문 생성 중...")
        progress.progress(70)
        
        result = generate_optimized_post(keyword, category, word_count, claude_key, use_trends, custom_urls)
        
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
            
            # 참고한 URL 표시
            if custom_urls:
                st.markdown("---")
                st.markdown("### 📎 참고한 자료")
                for i, url in enumerate(custom_urls, 1):
                    st.markdown(f"{i}. [{url}]({url})")
            
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
            
            col_save1, col_save2 = st.columns(2)
            with col_save1:
                st.download_button(
                    "💾 다운로드",
                    result['content'],
                    file_name=f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                )
            with col_save2:
                if st.button("📤 GitHub에 저장", key="save_to_github_main"):
                    with st.spinner("GitHub에 업로드 중..."):
                        github_result = save_to_github(
                            result['content'],
                            result['title'],
                            keyword,
                            result['seo_score']
                        )
                        if github_result['success']:
                            st.success(github_result['message'])
                            if 'url' in github_result:
                                st.markdown(f"🔗 [GitHub에서 보기]({github_result['url']})")
                        else:
                            st.error(github_result['message'])

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
