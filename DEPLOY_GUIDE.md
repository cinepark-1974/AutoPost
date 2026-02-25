# 🚀 GitHub 업로드 및 배포 가이드

## 📦 완성된 파일 목록

```
AutoPost/
├── .streamlit/
│   └── config.toml         ✅ 생성됨
├── streamlit_app.py        ✅ 생성됨
├── requirements.txt        ✅ 생성됨
├── .gitignore             ✅ 생성됨
└── README.md              ✅ 생성됨
```

---

## 🔄 GitHub 업로드 방법

### 옵션 1: GitHub 웹에서 업로드 (가장 쉬움)

#### 1단계: 기존 파일 업데이트

**streamlit_app.py 교체:**
1. GitHub 저장소 → `streamlit_app.py` 클릭
2. 연필(✏️) 아이콘 클릭
3. 다운로드한 새 파일 내용으로 전체 교체
4. Commit changes

**requirements.txt 교체:**
1. `requirements.txt` 클릭
2. 연필 아이콘
3. 내용 교체
4. Commit

**README.md 교체:**
1. `README.md` 클릭
2. 연필 아이콘
3. 내용 교체
4. Commit

#### 2단계: 새 파일 추가

**.streamlit/config.toml 생성:**
1. "Add file" → "Create new file"
2. 파일명: `.streamlit/config.toml`
3. 내용 붙여넣기
4. Commit

**.gitignore 업데이트:**
1. 기존 `.gitignore` 열기
2. 내용 교체
3. Commit

---

### 옵션 2: Git 명령어 사용

```bash
# 로컬 저장소로 이동
cd AutoPost

# 파일 복사 (다운로드한 파일들을 복사)
# streamlit_app.py
# requirements.txt
# README.md
# .gitignore
# .streamlit/config.toml

# Git 추가
git add .

# Commit
git commit -m "🎨 v2.0 업데이트: Stable Diffusion + 저장 기능 + 책 홍보"

# Push
git push origin main
```

---

## ☁️ Streamlit Cloud 설정

### 1단계: Secrets 설정

1. **Streamlit Cloud** 접속: https://share.streamlit.io
2. **AutoPost 앱** 선택
3. **Settings (⚙️)** 클릭
4. **Secrets** 탭 선택
5. 다음 내용 입력:

```toml
# Claude API (필수)
CLAUDE_API_KEY = "sk-ant-api03-여기에실제키입력"

# Hugging Face Token (이미지 생성용, 무료)
HUGGINGFACE_TOKEN = "hf_여기에실제토큰입력"

# 네이버 블로그 ID (선택)
NAVER_BLOG_ID = "cinepark"
```

6. **Save** 클릭

### 2단계: Reboot

1. 앱 우측 상단 **⋮** 메뉴
2. **Reboot app** 클릭
3. 1-2분 대기

---

## 🔑 API 키 발급 가이드

### Claude API Key

1. https://console.anthropic.com 접속
2. 계정 생성 (Gmail로 간단 가입)
3. 좌측 **API Keys** 클릭
4. **Create Key** 클릭
5. 키 이름 입력 (예: "AutoPost")
6. 키 복사 (sk-ant-api03-로 시작)
7. ⚠️ 한 번만 보여주니 바로 복사!

**무료 크레딧:**
- 신규 가입 시 $5 무료
- 약 200개 블로그 글 생성 가능

### Hugging Face Token

1. https://huggingface.co 접속
2. 우측 상단 가입/로그인
3. 프로필 아이콘 → **Settings**
4. 좌측 **Access Tokens** 클릭
5. **New token** 클릭
6. Token name: "AutoPost"
7. Role: **Read** 선택
8. **Generate a token** 클릭
9. 토큰 복사 (hf_로 시작)

**완전 무료!**

---

## ✅ 배포 완료 확인

### 체크리스트

- [ ] GitHub에 모든 파일 업로드됨
- [ ] Streamlit Secrets에 API 키 입력됨
- [ ] 앱 Reboot 완료
- [ ] 앱 URL 접속 확인
- [ ] 사이드바에 "✅ 자동 로드" 표시 확인

### 테스트

1. 키워드 입력: "테스트"
2. 글 생성 클릭
3. 30초 대기
4. 결과 확인

---

## 🎨 최종 결과

### PC/모바일에서:

1. **사이드바**
   ```
   ✅ Claude API Key 자동 로드
   ✅ Hugging Face Token 자동 로드
   ✅ Blog ID 자동 로드
   ```

2. **글 생성**
   - AI 이미지 자동 생성
   - 자연스러운 블로그 글
   - 고정된 책 홍보

3. **저장된 글 탭**
   - 생성 이력 확인
   - 다운로드 가능

---

## 🐛 문제 해결

### "Module not found" 오류
**해결**: requirements.txt가 제대로 업로드되었는지 확인

### API 키가 작동 안 함
**해결**: Secrets 오타 확인, 앱 Reboot

### 이미지 생성 실패
**해결**: Hugging Face Token 확인, 또는 체크박스 해제

---

## 📞 추가 도움

- **Streamlit 문서**: https://docs.streamlit.io
- **GitHub Issues**: https://github.com/cinepark-1974/AutoPost/issues

---

**완료하셨나요?** 🎉

이제 어디서든 AI 블로그 자동화를 사용하실 수 있습니다!
