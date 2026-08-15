# Hollywood CardNews Auto Generator

할리우드 산업 뉴스 → 카드뉴스 5장 + 쇼츠 영상 자동 생산 시스템
업로드는 수동 / 콘텐츠 생산만 자동화

## 구조
- `main.py`: 전체 파이프라인 실행
- `config.py`: 티커 맵, RSS, 설정
- `prompts.py`: LLM 프롬프트 (가십 제외)
- `utils/news_fetcher.py`: RSS 수집
- `utils/stock.py`: yfinance로 전일 종가 + 7일 그래프
- `utils/card_generator.py`: Pillow로 1080x1920 카드 생성 (Background_Images 활용)
- `utils/drive_uploader.py`: 구글 드라이브 Generated_Cards 업로드

## 구글 드라이브 구조 (권장)
```
Cluade Co-Work/
├── Background_Images/   # 범용 배경 (드라이브)
├── Movie_Posters/       # 포스터 (선택)
└── Generated_Cards/     # 자동 생성 결과물 저장 위치
```

## 사용법
1. `.env` 파일 생성 (`.env.example` 참고)
2. `pip install -r requirements.txt`
3. `python main.py`

GitHub Actions는 매일 08:00 KST 자동 실행, 결과는 드라이브에 저장.

## 출력물
output/2026-08-15_DIS/
- card_01_cover.png
- card_02_industry.png
- card_03_behind.png
- card_04_promo.png
- card_05_stock.png
- final_shorts.mp4 (옵션)
- meta.json
