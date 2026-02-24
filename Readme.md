# ✍️ AutoPost - AI 블로그 자동화 시스템

Claude API 기반 범용 블로그 콘텐츠 자동 생성 + 네이버 블로그 자동 포스팅

## 🎯 주요 기능

### ✅ 현재 구현됨
- **범용 콘텐츠 생성**: 영화, 책, 맛집, 여행, IT, 일상 등 모든 주제 지원
- **Claude AI 기반**: 자연스러운 한국어, AI 티 안나는 글쓰기
- **SEO 최적화**: 키워드 자동 배치, 제목 최적화, 해시태그 생성
- **다양한 스타일**: 정보 전달형, 후기형, 스토리텔링형
- **실시간 미리보기**: 생성된 글 바로 확인
- **커스텀 테마**: 블루-옐로우 컬러 + 페이퍼로지 폰트
- **무료 이미지 자동 검색**: Pexels API 연동, 출처 자동 표기

### 🚧 개발 예정
- 네이버 블로그 자동 발행
- 예약 발행 시스템
- AI 이미지 생성 (DALL-E 연동) - 선택사항
- 통계 대시보드

## 🚀 빠른 시작

### 1. 필요한 것
- Claude API Key ([발급 받기](https://console.anthropic.com))
- Python 3.8 이상 (Streamlit Cloud 사용 시 불필요)

### 2. 로컬 실행

```bash
# 저장소 클론
git clone https://github.com/cinepark-1974/AutoPost.git
cd AutoPost

# 패키지 설치
pip install -r requirements.txt

# 실행
streamlit run streamlit_app.py
```

### 3. Streamlit Cloud 배포 (권장)

1. 이 저장소를 Fork
2. [Streamlit Cloud](https://streamlit.io/cloud) 접속
3. "New app" → GitHub 저장소 연결
4. 자동 배포 완료!

## 📖 사용 방법

### 기본 사용법

1. **API 설정**: 왼쪽 사이드바에 Claude API Key 입력
2. **주제 선택**: 작성하고 싶은 카테고리 선택
3. **키워드 입력**: 검색 노출을 원하는 키워드 입력
4. **생성**: "글 생성" 버튼 클릭
5. **활용**: 생성된 글을 블로그에 붙여넣기

### SEO 최적화 팁

- 키워드는 구체적일수록 좋음
- 키워드 밀도를 3-7회로 조절
- 해시태그 자동 생성 활용

## 💰 비용

### Claude API 가격
- Input: $3 per million tokens
- Output: $15 per million tokens
- 신규 가입 시 $5 무료 크레딧

### 예상 비용
- 2,000자 블로그 글 1개: 약 $0.01~0.03
- 월 100개 생성 시: 약 $1~3

## 🛠️ 기술 스택

- **Frontend**: Streamlit
- **AI**: Claude Sonnet 4.5 (Anthropic)
- **Deployment**: Streamlit Cloud
- **언어**: Python 3.8+
- **폰트**: Paybooc (페이퍼로지)
- **컬러**: 블루(#191970) + 옐로우(#ffcb05)

## 📂 프로젝트 구조

```
AutoPost/
├── .gitignore           # Git 제외 파일 설정
├── .streamlit/
│   └── config.toml     # Streamlit 테마 설정
├── README.md           # 프로젝트 문서
├── requirements.txt    # Python 패키지
└── streamlit_app.py    # 메인 애플리케이션
```

## 🔐 보안

**중요**: API 키는 절대 GitHub에 올리지 마세요!

### Streamlit Secrets 사용 (필수 설정!)

**한 번만 설정하면 PC/모바일 모두에서 자동으로 작동합니다.**

#### 설정 방법:

1. **Streamlit Cloud 접속**
   - https://share.streamlit.io
   - 로그인

2. **앱 선택**
   - AutoPost 앱 클릭

3. **Settings 열기**
   - 우측 상단 ⚙️ (Settings) 클릭
   - **Secrets** 탭 선택

4. **API 키 입력**
   ```toml
   CLAUDE_API_KEY = "sk-ant-api03-여기에실제키입력"
   NAVER_CLIENT_ID = "여기에실제ID입력"
   NAVER_CLIENT_SECRET = "여기에실제시크릿입력"
   NAVER_BLOG_ID = "cinepark"
   ```

5. **Save 클릭**

#### 설정 완료 후:

✅ **PC에서**: 사이드바에 "✅ API Key 자동 로드 완료" 표시
✅ **모바일에서**: 동일하게 자동 로드, 입력 불필요
✅ **안전**: GitHub에 노출 안 됨, 암호화 저장

### 로컬 개발용 (선택사항)

로컬에서 테스트할 때:

```bash
# .streamlit 폴더 생성
mkdir .streamlit

# .streamlit/secrets.toml 생성 후 API 키 입력
echo 'CLAUDE_API_KEY = "your-key"' > .streamlit/secrets.toml
```

**주의**: `.gitignore`에 의해 자동으로 Git에서 제외됩니다.

## 🎨 커스터마이징

### 색상 변경
`.streamlit/config.toml` 파일에서 색상 수정:
```toml
primaryColor = "#ffcb05"      # 메인 컬러
textColor = "#191970"         # 텍스트 컬러
backgroundColor = "#f8f9fd"   # 배경색
```

### 폰트 변경
`streamlit_app.py` CSS 섹션에서 폰트 수정

## 📝 라이선스

MIT License

## 🤝 기여

버그 제보 및 기능 제안은 [Issues](https://github.com/cinepark-1974/AutoPost/issues)에서!

## 📞 문의

- 블로그: [https://blog.naver.com/cinepark](https://blog.naver.com/cinepark)
- GitHub: [https://github.com/cinepark-1974/AutoPost](https://github.com/cinepark-1974/AutoPost)

---

Made with ❤️ using Claude API | AutoPost v1.0
