# Assets 폴더
   
   이 폴더에는 AutoPost에서 사용하는 정적 파일들이 저장됩니다.
   
   - book_cover.png: 감각구역 책 표지
```

6. **"Commit new file"** 클릭

#### Step 2: 책 표지 이미지 업로드

1. 이제 `assets` 폴더가 생겼습니다
2. **assets 폴더로 들어가기**
3. **"Add file"** → **"Upload files"** 클릭
4. 다운로드한 **`book_cover.png`** 파일을 드래그 또는 선택
5. **"Commit changes"** 클릭

---

### 방법 2: 빈 파일로 폴더 생성 (더 간단)

1. GitHub 저장소
2. "Add file" → "Create new file"
3. 파일명에 입력:
```
   assets/.gitkeep
```
   (`.gitkeep`은 빈 폴더를 Git에 유지하기 위한 더미 파일)

4. 내용은 비워두고 **Commit**
5. 이제 `assets` 폴더로 들어가서 `book_cover.png` 업로드

---

## 🎯 확인 방법:

업로드 완료 후 브라우저에서 다음 URL 열기:
```
https://raw.githubusercontent.com/cinepark-1974/AutoPost/main/assets/book_cover.png
```

→ 감각구역 표지가 보이면 성공! ✅

---

## 📸 스크린샷 가이드:

### 1. "Create new file" 화면:
```
Name your file...
assets/README.md    ← 이렇게 입력

[내용 입력 영역]

[Commit new file 버튼]
```

### 2. assets 폴더 확인:
```
AutoPost/
├── assets/          ← 폴더 생성됨
│   └── README.md    ← 파일 있음
├── streamlit_app.py
└── ...
```

### 3. 이미지 업로드:
```
assets 폴더 안에서
[Add file] → [Upload files]
→ book_cover.png 드래그
→ Commit
