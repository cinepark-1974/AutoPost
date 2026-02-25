# ✍️ AutoPost v2.0 - AI 블로그 자동화 시스템

Claude AI + Stable Diffusion 기반 네이버 블로그 자동 포스팅 도구

![AutoPost](https://img.shields.io/badge/AutoPost-v2.0-ffcb05?style=for-the-badge)
![Claude](https://img.shields.io/badge/Claude-Sonnet_4.5-191970?style=for-the-badge)
![Stable Diffusion](https://img.shields.io/badge/Stable_Diffusion-XL-orange?style=for-the-badge)

## 🎯 주요 기능

### ✅ 완전 구현됨
- **범용 콘텐츠 생성**: 영화, 책, 주식, 맛집, 여행, IT 등 모든 주제 지원
- **Claude Sonnet 4.5 기반**: 자연스러운 한국어, AI 티 안나는 글쓰기
- **SEO 최적화**: 키워드 자동 배치, 제목 최적화, 해시태그 생성
- **최신 화제 검색**: Google News RSS로 최신 뉴스 자동 검색 및 도입부 활용
- **AI 이미지 생성**: Stable Diffusion XL로 무료 고품질 이미지 생성
- **고정 책 홍보**: "감각구역" 자동 홍보 (표지 이미지 + 링크)
- **글 저장 및 관리**: 생성된 글 자동 저장 및 목록 관리
- **커스텀 테마**: 블루(#191970) + 옐로우(#ffcb05) + 페이퍼로지 폰트

### 🚧 개발 예정
- 네이버 블로그 자동 발행 API 연동
- 예약 발행 시스템
- GitHub 기반 영구 저장소
- 통계 대시보드 확장

## 🚀 빠른 시작

### 1. 저장소 클론
```bash
git clone https://github.com/cinepark-1974/AutoPost.git
cd AutoPost
```

### 2. Streamlit Cloud 배포 (권장)

1. [Streamlit Cloud](https://streamlit.io/cloud) 접속
2. "New app" → GitHub 저장소 연결
3. Secrets 설정 (아래 참조)
4. 자동 배포 완료!

### 3. 로컬 실행 (선택)

```bash
# 패키지 설치
pip install -r requirements.txt

# 실행
streamlit run streamlit_app.py
```

## 🔐 Secrets 설정

Streamlit Cloud → Settings → Secrets에 다음 내용 입력:

```toml
# Claude API (필수)
CLAUDE_API_KEY = "sk-ant-api03-xxxxx"

# Hugging Face Token (이미지 생성용, 무료)
HUGGINGFACE_TOKEN = "hf_xxxxx"

# 네이버 블로그 (선택사항)
NAVER_BLOG_ID = "cinepark"
```

### API 키 발급 방법

#### Claude API Key (필수)
1. https://console.anthropic.com 접속
2. 계정 생성 및 로그인
3. API Keys → Create Key
4. 신규 가입 시 $5 무료 크레딧

#### Hugging Face Token (무료)
1. https://huggingface.co 가입
2. Settings → Access Tokens
3. New token (Read 권한)
4. 완전 무료!

## 📖 사용 방법

### 1️⃣ 기본 사용

1. **주제 선택**: 10개 카테고리 중 선택
2. **키워드 입력**: "4차 상법 개정", "부산 맛집" 등
3. **스타일 선택**: 정보 전달형 / 후기형 / 스토리텔링형
4. **글 생성 클릭**: 30초 내 완성

### 2️⃣ 생성되는 콘텐츠

```markdown
## [SEO 최적화된 제목]

안녕하세요. 영화 프로듀서의 블로그, CINEPARK입니다.

[최신 뉴스 활용한 자연스러운 도입부...]

## [질문형 소제목?]
[본문 내용...]

## 태그
#태그1 #태그2 #태그3

---

📚 제 저서를 소개합니다

[감각구역 표지 이미지]

제목: 감각구역
저자: 문성주, 박현
출판사: 마카롱(교보문고)

많은 다운로드를 부탁합니다. 꾸벅 🙇
```

### 3️⃣ 이미지 생성

- **Stable Diffusion XL** 사용
- **첫 요청**: 30-60초 (모델 로딩)
- **이후 요청**: 5-10초
- **완전 무료** (Hugging Face)
- **일일 제한**: 약 1,000회 (충분함)

### 4️⃣ 저장 및 관리

- 📚 "저장된 글" 탭에서 전체 목록 확인
- 💾 개별 다운로드 가능
- 🔄 세션 스테이트 기반 (페이지 새로고침 시 초기화)

## 💰 비용

| 항목 | 비용 |
|------|------|
| **Claude API** | $3/1M tokens (입력) + $15/1M tokens (출력) |
| **Stable Diffusion** | 무료 (Hugging Face) |
| **총 예상 비용** | 글 1개당 $0.01~0.03 |
| **월 100개 생성** | 약 $1~3 |
| **신규 가입 혜택** | $5 무료 크레딧 (약 200개 글) |

## 🛠️ 기술 스택

- **Frontend**: Streamlit 1.30+
- **AI 텍스트**: Claude Sonnet 4.5 (Anthropic)
- **AI 이미지**: Stable Diffusion XL (Hugging Face)
- **뉴스 검색**: Google News RSS
- **폰트**: Paybooc (페이퍼로지)
- **배포**: Streamlit Cloud

## 📂 프로젝트 구조

```
AutoPost/
├── .streamlit/
│   └── config.toml          # 테마 설정
├── assets/
│   └── book_cover.jpg       # 책 표지 (옵션)
├── streamlit_app.py         # 메인 애플리케이션
├── requirements.txt         # Python 패키지
├── .gitignore              # Git 제외 파일
└── README.md               # 프로젝트 문서
```

## 🎨 커스터마이징

### 책 정보 변경

`streamlit_app.py` 상단 BOOK_INFO 수정:

```python
BOOK_INFO = {
    "cover_url": "https://your-book-cover-url.jpg",
    "title": "책 제목",
    "authors": "저자명",
    "publisher": "출판사",
    "link": "https://구매링크"
}
```

### 색상 테마 변경

`.streamlit/config.toml` 수정:

```toml
primaryColor = "#ffcb05"  # 메인 컬러
textColor = "#191970"     # 텍스트 컬러
backgroundColor = "#f8f9fd"  # 배경색
```

## ⚠️ 주의사항

1. **API 키 보안**: 절대 GitHub에 직접 올리지 마세요
2. **세션 스테이트**: 저장된 글은 페이지 새로고침 시 사라집니다
3. **이미지 생성**: 첫 요청은 느립니다 (모델 로딩)
4. **Hugging Face 제한**: 일일 약 1,000회 (일반 사용에는 충분)

## 💡 팁

- 키워드는 구체적일수록 좋습니다
- 다양한 스타일을 테스트해보세요
- 생성된 글을 약간 수정하면 더 자연스럽습니다
- 중요한 글은 꼭 다운로드해두세요
- 이미지 생성 체크 해제하면 빠르게 글만 생성 가능

## 🐛 트러블슈팅

### Q1: 이미지 생성이 너무 느려요
**A**: 첫 요청은 모델 로딩으로 30-60초 소요됩니다. 이후엔 빨라집니다.

### Q2: API 키가 작동하지 않아요
**A**: Secrets에 정확히 입력했는지 확인하고, 앱을 Reboot 해보세요.

### Q3: 저장된 글이 사라졌어요
**A**: 세션 스테이트 기반이라 페이지 새로고침 시 초기화됩니다. 중요한 글은 다운로드하세요.

### Q4: Hugging Face 제한에 걸렸어요
**A**: Unsplash 이미지로 자동 대체됩니다. 또는 다음날 다시 시도하세요.

## 📝 라이선스

MIT License

## 🤝 기여

버그 제보 및 기능 제안: [Issues](https://github.com/cinepark-1974/AutoPost/issues)

## 📞 문의

- **블로그**: https://blog.naver.com/cinepark
- **GitHub**: https://github.com/cinepark-1974/AutoPost
- **저서**: [감각구역](https://ebook-product.kyobobook.co.kr/dig/epd/ebook/E000012093207)

---

Made with ❤️ by CINEPARK | Powered by Claude AI + Stable Diffusion

**AutoPost v2.0** - AI 블로그 자동화의 새로운 기준
