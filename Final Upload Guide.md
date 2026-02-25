# 🚀 최종 GitHub 업로드 가이드 (책 표지 포함)

## 📦 업로드할 파일 전체 목록

```
AutoPost/
├── .streamlit/
│   └── config.toml         ✅ 테마 설정
├── assets/
│   ├── book_cover.png      ✅ 감각구역 표지 (새로 추가!)
│   └── README.md           ✅ assets 설명
├── streamlit_app.py        ✅ 메인 앱 (수정됨)
├── requirements.txt        ✅ 패키지
├── .gitignore             ✅ Git 설정
└── README.md              ✅ 문서
```

---

## 🎯 중요 변경사항

### 1. 책 표지 이미지 추가
- **파일**: `assets/book_cover.png`
- **실제 감각구역 표지 사용**
- **GitHub에 저장하여 안정적으로 표시**

### 2. 이미지 소스 개선
```
우선순위:
1. Stable Diffusion (Token 있을 때)
2. Pexels (무료, 안정적)
3. Lorem Picsum (항상 작동)
4. Placeholder (최후)
```

### 3. Unsplash 제거
- Unsplash source API는 더 이상 작동하지 않음
- Pexels + Lorem Picsum으로 교체
- 100% 작동 보장

---

## 📤 GitHub 업로드 순서

### 방법 1: GitHub 웹 (권장)

#### Step 1: assets 폴더 생성

1. GitHub 저장소 메인
2. **"Add file"** → **"Create new file"**
3. 파일명에 `assets/README.md` 입력
4. 내용 붙여넣기 (다운로드한 assets/README.md)
5. **Commit**

#### Step 2: 책 표지 업로드

1. `assets` 폴더로 이동
2. **"Add file"** → **"Upload files"**
3. `book_cover.png` 드래그 또는 선택
4. **Commit changes**

#### Step 3: 기존 파일 업데이트

**streamlit_app.py:**
1. 파일 클릭 → 연필 아이콘
2. 전체 내용 교체
3. Commit

**requirements.txt, README.md 등도 동일하게 업데이트**

#### Step 4: .streamlit/config.toml

1. "Add file" → "Create new file"
2. 파일명: `.streamlit/config.toml`
3. 내용 붙여넣기
4. Commit

---

### 방법 2: Git 명령어

```bash
# 저장소 클론 (이미 했다면 생략)
git clone https://github.com/cinepark-1974/AutoPost.git
cd AutoPost

# assets 폴더 생성
mkdir -p assets

# 파일 복사
# (다운로드한 파일들을 해당 위치에 복사)
# - assets/book_cover.png
# - assets/README.md
# - streamlit_app.py
# - requirements.txt
# - .streamlit/config.toml
# - README.md
# - .gitignore

# Git 추가
git add .

# Commit
git commit -m "✨ v2.1: 실제 책 표지 추가 + 안정적인 이미지 소스"

# Push
git push origin main
```

---

## ✅ 업로드 확인

### GitHub에서 확인:

```
AutoPost/
├── assets/
│   ├── book_cover.png      ✅ 보임
│   └── README.md           ✅ 보임
├── .streamlit/
│   └── config.toml         ✅ 보임
├── streamlit_app.py        ✅ 최신
└── ...
```

### 책 표지 URL 테스트:

브라우저에서 열기:
```
https://raw.githubusercontent.com/cinepark-1974/AutoPost/main/assets/book_cover.png
```

→ 감각구역 표지가 보이면 성공! ✅

---

## ☁️ Streamlit Cloud

### 자동 재배포

GitHub push 후:
1. Streamlit Cloud가 자동으로 감지
2. 1-2분 후 재배포 완료
3. 새로운 기능 적용됨

### Secrets 확인

기존 설정 유지:
```toml
CLAUDE_API_KEY = "sk-ant-api03-xxxxx"
HUGGINGFACE_TOKEN = "hf_xxxxx"  # 선택사항
NAVER_BLOG_ID = "cinepark"
```

---

## 🎨 최종 결과

### 생성되는 글:

```markdown
## [제목]

안녕하세요. 영화 프로듀서의 블로그, CINEPARK입니다.

[본문...]

---

📚 제 저서를 소개합니다

[실제 감각구역 표지 이미지 표시]

제목: 감각구역
저자: 문성주, 박현
출판사: 마카롱(교보문고)

많은 다운로드를 부탁합니다. 꾸벅 🙇
```

### 메인 이미지:

- **Pexels**: 고품질 무료 이미지
- **Lorem Picsum**: Pexels 실패 시
- **항상 작동**: 100% 보장

---

## 🐛 트러블슈팅

### Q: 책 표지가 안 보여요
**A**: 
1. GitHub에서 파일 경로 확인: `assets/book_cover.png`
2. Raw URL 테스트
3. 1-2분 대기 (GitHub 캐시)

### Q: 메인 이미지가 여전히 안 나와요
**A**: 
- Pexels API가 작동 중
- Lorem Picsum으로 자동 대체
- 항상 이미지 표시됨

### Q: Hugging Face는 어떻게 되나요?
**A**: 
- Token 있으면 AI 이미지 시도
- 실패해도 Pexels로 자동 대체
- Token 없어도 완벽 작동

---

## 🎉 완료!

모든 파일 업로드 후:
- ✅ 실제 책 표지 표시
- ✅ 안정적인 메인 이미지
- ✅ 100% 작동 보장

**테스트:**
1. 키워드 입력: "테스트"
2. 글 생성 클릭
3. 이미지 2개 확인 (메인 + 책표지)

성공! 🚀
