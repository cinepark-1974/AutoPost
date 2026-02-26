# 📚 AutoPost 완전 가이드

> AI 블로그 자동화 툴 - 설치부터 활용까지 모든 것

---

## 🚀 빠른 시작 (5분)

### GitHub에 업로드할 필수 파일

```
AutoPost/
├── streamlit_app.py          ⭐ 메인 (필수)
├── requirements.txt           ⭐ 필수
├── assets/                    ⭐ 필수
│   ├── book_cover.png
│   └── hero_image.png
└── README.md                 (이 파일)
```

---

## ⚙️ Streamlit Cloud 설정

### Secrets 설정 (API 키 자동 로드)

**Settings → Secrets 탭:**

```toml
CLAUDE_API_KEY = "sk-ant-api03-xxxxx"
HUGGINGFACE_TOKEN = "hf_xxxxx"
```

저장 후 자동 재시작 → 완료!

---

## 📱 사용법

1. 키워드 입력: "주식 초보 추천"
2. 옵션 선택
3. 생성하기 클릭
4. 30초 대기
5. 복사 → 블로그 붙여넣기

---

## 🔑 API 키 발급

### Claude (필수)
- https://console.anthropic.com
- Get API Keys → Create
- 비용: 글 1개당 $0.01-0.03

### HuggingFace (선택)
- https://huggingface.co
- Settings → Access Tokens
- Read 권한 선택
- 무료!

---

## 🎨 이미지 문제 해결

### 이미지 안 보일 때

```bash
# 확인
https://raw.githubusercontent.com/본인계정/AutoPost/main/assets/hero_image.png

# 해결
1. assets 폴더 생성
2. hero_image.png 업로드
3. 파일명 정확히 (소문자)
```

---

## 📊 SEO 점수

- 80점 이상: 상위 노출 🏆
- 60-79점: 양호
- 60점 미만: 개선

---

## 💰 비용

월 100개 글: **$1-3** (약 3,000원)

---

## 🗂️ 파일 정리

### GitHub에 필요한 것만

```
✅ streamlit_app.py
✅ requirements.txt
✅ assets/ (폴더)
✅ README.md

❌ 다른 가이드 파일들 (로컬 보관)
```

---

## 🔧 문제 해결

**API 오류:** Secrets 설정 확인  
**이미지 실패:** 대체 UI 자동 표시  
**점수 낮음:** 2000자 이상, 트렌드 체크

---

**Made with ❤️ | AutoPost v5.0**
