# CINEPARK0410 YouTube Factory - 구글 올인원
# 5분 가로 + 1분20초 세로 동시 생성 공장

이 리포지토리는 기존 Naver 블로그용 AutoPost에서 **CINEPARK0410 유튜브 전용**으로 완전히 교체된 버전입니다.

## 특징
- **주제 자동화**: 50개 주제어 중 AI가 스코어링해서 Top 1 선정 (사람은 주제 입력 안 함)
- **하네스 깎기**: `config.py`의 CREDIBILITY_HARNESS가 모든 프롬프트에 강제 주입
- **AI 서로 스코어링 QA**: Gemini 작가가 쓰면 Gemini 심사관이 100점 만점으로 채점, 85점 미만이면 자동 재생성
- **신뢰도**: 모든 대본은 우리말샘 Open API 데이터를 1차 출처로만 사용, 영상에 `출처: 국립국어원 우리말샘` 고정 자막
- **구글 올인원**: Gemini(대본) + Imagen(이미지) + Cloud TTS(음성) + Colab(조립) + Drive(저장) + YouTube 업로드

## 출력
- `output/YYYY-MM-DD_키워드_dual/`
  - `script_5min.txt` - 5분 가로 대본 (300초, 5챕터)
  - `script_80sec.txt` - 1분20초 세로 대본 (80초)
  - `meta.json` - QA 점수, 우리말샘 원문, 시각 프롬프트 포함
  - `final_horizontal.mp4` - Colab에서 생성된 1920x1080
  - `final_vertical.mp4` - Colab에서 생성된 1080x1920

## 필요 Secrets (기존 Secrets 그대로 사용)
- `GEMINI_API_KEY` 또는 `GOOGLE_API_KEY` - Google AI Studio에서 발급
- `OURIMALSAEM_API_KEY` - 03372... (이미 발급됨)
- `GDRIVE_FOLDER_ID_OUTPUT` - 5분 가로 저장 폴더
- `GDRIVE_FOLDER_ID_BACKGROUND` - 세로 배경 폴더
- `GOOGLE_OAUTH_CLIENT_ID / SECRET / REFRESH_TOKEN` - 유튜브 업로드용

## 실행
```bash
pip install -r requirements.txt
python main.py
```

## GitHub Actions
매일 오전 7시 KST 자동 실행 - `.github/workflows/youtube.yml`
