# 🖼️ 이미지 생성 문제 해결 가이드

## 문제: "제공된 상품 이미지가 없습니다"

이미지가 생성되지 않는 경우의 원인과 해결법입니다.

---

## 🔍 원인

### 1. Hugging Face Token 미입력
- Token이 Secrets에 없거나
- 사이드바에 입력되지 않음

### 2. Hugging Face API 문제
- 첫 요청 시 모델 로딩 시간 초과 (30-60초)
- API 서버 과부하
- 일일 요청 제한 도달

### 3. 네트워크 문제
- Timeout 설정 부족
- 연결 불안정

---

## ✅ 해결 방법

### 방법 1: Unsplash로 대체 (즉시 해결) ⭐

**장점:**
- 항상 작동
- 빠름 (1-2초)
- 고품질 무료 이미지

**적용:**
코드가 이미 자동으로 대체하도록 수정되었습니다.
- Hugging Face 실패 시 자동으로 Unsplash 사용
- Token 없어도 Unsplash로 작동

---

### 방법 2: Hugging Face Token 재설정

#### Token 발급:
1. https://huggingface.co 로그인
2. Settings → Access Tokens
3. 기존 토큰 삭제 (있다면)
4. New token 생성
   - Name: "AutoPost"
   - Role: **Read** ✅
5. 토큰 복사 (hf_xxxxx)

#### Secrets 설정:
```toml
HUGGINGFACE_TOKEN = "hf_새로발급한토큰"
```

#### 앱 Reboot

---

### 방법 3: 이미지 없이 사용

UI에서 **"AI 이미지 생성"** 체크박스 해제
- 글만 빠르게 생성
- 이미지는 나중에 수동으로 추가

---

## 🎯 권장 설정

### 현재 상황별 추천:

**Token 없음:**
```
→ Unsplash 자동 사용 (완벽 작동)
```

**Token 있는데 실패:**
```
→ Token 재발급 시도
→ 안 되면 Unsplash 사용
```

**빠른 글 작성 우선:**
```
→ 이미지 생성 체크 해제
→ 나중에 네이버에서 이미지 추가
```

---

## 📊 각 방법 비교

| 방법 | 속도 | 품질 | 비용 | 안정성 |
|------|------|------|------|--------|
| **Unsplash** | ⚡ 빠름 | ⭐⭐⭐⭐ | 무료 | ✅ 항상 작동 |
| Stable Diffusion | 🐌 느림 | ⭐⭐⭐⭐⭐ | 무료 | ⚠️ 가끔 실패 |
| 수동 추가 | ⚡ 즉시 | 자유 | 무료 | ✅ 확실 |

---

## 💡 실전 팁

### Unsplash 키워드 최적화

한글 키워드는 영문으로 자동 변환됩니다:

```python
"부산 맛집" → "busan restaurant food"
"여행" → "travel landscape"
"주식" → "stock market finance"
```

더 좋은 이미지를 원하면:
- 구체적인 키워드 입력
- 예: "해운대 해변" vs "해운대"

---

## 🚀 즉시 적용

### 수정된 코드 다운로드

1. 새로운 `streamlit_app.py` 다운로드
2. GitHub에 업로드
3. Streamlit 자동 재배포 (1-2분)

### 변경사항:
- ✅ Hugging Face 실패 시 자동 Unsplash 대체
- ✅ Token 없어도 작동
- ✅ 오류 메시지 개선
- ✅ 안정성 향상

---

## 테스트

1. 키워드: "테스트"
2. 글 생성 클릭
3. 이미지 즉시 표시 확인 ✅

---

## 📞 여전히 문제?

다음 정보 확인:
1. Secrets에 `HUGGINGFACE_TOKEN` 있는지
2. 토큰이 `hf_`로 시작하는지
3. 앱 Reboot 했는지

**간단 해결:**
이미지 생성 체크박스 해제 → 글만 생성 → 완벽 작동! ✅
