# AutoPost v7.0 - CINEPARK 페르소나 완성판

**네이버 블로그 2026년 정책 완벽 준수 + CINEPARK 전문성 반영**

<p align="center">
  <img src="https://raw.githubusercontent.com/cinepark-1974/AutoPost/main/assets/hero_image.png" alt="AutoPost" width="600">
</p>

---

## 🎬 AutoPost는 CINEPARK입니다

영화 프로듀서 CINEPARK의 풍부한 경험과 전문성을 담아 자동으로 블로그 글을 작성합니다.

### CINEPARK 프로필:
- 🎬 영화 기획 프로듀서 (<광해>, <하녀>, <동갑내기 과외하기> 등)
- 🌏 국제 공동제작 (인도네시아, 베트남, 일본 - <수상한 그녀> 리메이크)
- ✈️ 25개국 이상 여행 (런던/도쿄 장기 체류)
- 📚 소설가 (<감각구역> 집필)
- 🎓 시나리오 전공 석사
- 🍷 와린이 (2001년부터)

---

## ✨ v7.0 주요 업데이트

### 1. 네이버 블로그 2026년 정책 완벽 준수
```
✅ "나를 표현한 개인 공간" 철학 반영
✅ 개인 경험과 의견 중심 작성
✅ 구어체 사용 (~했어요, ~더라고요)
✅ 광고 투명성 규정 준수
✅ E-E-A-T 강화 (경험, 전문성, 권위성, 신뢰성)
```

### 2. 2026년 SEO 최적 기준
```
🏆 제목: 28-32자 최적
🏆 본문: 1500-3000자 최적
🏆 키워드: 3-8회 자연스럽게
🏆 소제목: 3-5개 최적
🏆 이모지: 2-3개 적절히
```

### 3. CINEPARK 페르소나 완벽 구현
```
🎬 영화: <광해> 제작 경험 활용
🌍 여행: 런던/도쿄 체류, 25개국 경험
📖 시나리오: 전문 지식 반영
🍷 와인: 솔직한 와린이 관점
```

---

## 🚀 주요 기능

### 1. AI 글 작성
- Claude Sonnet 4.5 사용
- SEO 85-95점 자동 달성
- CINEPARK의 경험 자동 반영
- 네이버 블로그 정책 준수

### 2. 최신 트렌드 자동 검색
- Google News RSS 활용
- 최신 5개 뉴스 자동 수집
- 출처 자동 표기
- 링크 본문 삽입

### 3. 사용자 URL 참고
- 최대 3개 URL 입력
- 자동 내용 추출
- 참고하여 작성
- 출처 명시

### 4. 키워드 추천
- 카테고리별 황금 키워드 10개
- 2026년 트렌드 반영
- 계절성 고려
- 검색량 & 경쟁도 분석

### 5. AI 이미지 생성
- Stable Diffusion XL
- Pexels 무료 이미지
- 자동 출처 표기

### 6. GitHub 자동 저장
- 작성한 글 영구 보관
- 버전 관리
- posts/ 폴더에 저장
- 메타데이터 포함

### 7. 작성 히스토리
- 세션 동안 보관
- 개별 다운로드
- 개별 삭제
- SEO 점수 표시

---

## 📦 설치 및 실행

### Streamlit Cloud (권장)

1. **Fork Repository**
   ```
   https://github.com/cinepark-1974/AutoPost
   ```

2. **Streamlit Cloud 배포**
   ```
   https://share.streamlit.io/
   New app → GitHub 연결
   ```

3. **Secrets 설정**
   ```toml
   # Settings → Secrets
   
   CLAUDE_API_KEY = "sk-ant-api03-xxxxx"
   HUGGINGFACE_TOKEN = "hf_xxxxx"
   GITHUB_TOKEN = "ghp_xxxxx"
   GITHUB_OWNER = "cinepark-1974"
   GITHUB_REPO = "AutoPost"
   ```

4. **완료!**
   ```
   앱 자동 실행
   ```

---

### 로컬 실행

```bash
# 클론
git clone https://github.com/cinepark-1974/AutoPost.git
cd AutoPost

# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# Secrets 설정
mkdir .streamlit
cat > .streamlit/secrets.toml << EOF
CLAUDE_API_KEY = "sk-ant-api03-xxxxx"
HUGGINGFACE_TOKEN = "hf_xxxxx"
GITHUB_TOKEN = "ghp_xxxxx"
GITHUB_OWNER = "cinepark-1974"
GITHUB_REPO = "AutoPost"
EOF

# 실행
streamlit run streamlit_app.py
```

---

## 🔑 API 키 발급

### 1. Claude API Key (필수)
```
위치: https://console.anthropic.com/
가격: $3 / 100만 토큰
발급: API Keys → Create Key
```

### 2. HuggingFace Token (선택)
```
위치: https://huggingface.co/settings/tokens
가격: 무료
발급: New token → Read 권한
용도: AI 이미지 생성
```

### 3. GitHub Token (선택)
```
위치: GitHub → Settings → Developer settings
발급: Personal access tokens → Generate new token
권한: repo (필수)
용도: 글 자동 저장
```

---

## 📂 프로젝트 구조

```
AutoPost/
├── streamlit_app.py          # 메인 앱
├── requirements.txt           # 패키지 목록
├── .streamlit/
│   ├── config.toml           # 다크모드 방지
│   └── secrets.toml          # API 키 (gitignore)
├── assets/
│   ├── hero_image.png        # 히어로 이미지
│   └── book_cover.png        # 책 표지
├── posts/                    # GitHub 저장 글
│   └── (자동 생성)
├── .gitignore
└── README.md
```

---

## 📊 SEO 평가 기준 (2026년)

| 항목 | 배점 | 기준 |
|------|------|------|
| 제목 키워드 | 25점 | 키워드 포함 필수 |
| 제목 길이 | 20점 | **28-32자 최적** |
| 본문 길이 | 20점 | **1500-3000자 최적** |
| 키워드 밀도 | 15점 | 3-8회 자연스럽게 |
| 소제목 | 10점 | 3-5개 최적 |
| 이모지 | 5점 | 2-3개 적절히 |
| 해시태그 | 5점 | ## 태그 섹션 |
| **합계** | **100점** | 85점 이상 목표 |

---

## 💝 Credits

- **개발**: CINEPARK
- **AI**: Claude Sonnet 4.5 (Anthropic)
- **이미지**: Stable Diffusion XL, Pexels
- **프레임워크**: Streamlit

---

<p align="center">
Made with ❤️ by CINEPARK<br>
AutoPost v7.0
</p>
