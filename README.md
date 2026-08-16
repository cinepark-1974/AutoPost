# Hollywood CardNews (web_search 버전)

할리우드 산업 뉴스 1건 → 5장 카드뉴스(1080x1920) 자동 생성 → 구글 드라이브 저장.
사람은 드라이브에서 받아 업로드만 하면 됩니다.

## 흐름
1. Claude가 web_search로 최근 3일 내 산업 뉴스 조사 + 미국 증시 종가 조회 (STEP 1/2)
2. HTML 카드 5장 생성 (블루블랙 #070A1A, Noto Sans CJK KR)
3. Playwright로 PNG 캡처 + pngquant 최적화
4. OAuth로 구글 드라이브 업로드

## 비용 안전장치
- 검색 횟수 상한: `MAX_SEARCHES`(기본 10). 1회=$0.01 → 실행당 검색비 최대 $0.10 확정.
- 하루 1회 실행 기준 월 예상 약 $6 (원화 8천원대).

## 로컬 실행
1. `.env.example` → `.env` 복사 후 값 입력
2. `pip install -r requirements.txt`
3. `python -m playwright install chromium`
4. `sudo apt-get install -y fonts-noto-cjk pngquant`
5. `python main.py`

## GitHub Actions
- 매일 08:00 KST 자동 실행 (`.github/workflows/daily.yml`)
- Secrets: ANTHROPIC_API_KEY, GDRIVE_FOLDER_ID_OUTPUT, GOOGLE_OAUTH_CLIENT_ID/SECRET/REFRESH_TOKEN

## 카드 구조
1. 표지: 라벨 + 헤드라인(핵심숫자 골드) + 서브 + 푸터
2. 01 INDUSTRY NEWS: 핵심 뉴스 + (기사에 수치 있으면) 막대 비교
3. 02 BY THE NUMBERS: 스탯 3개 (기사 명시 수치만)
4. 03 WHY IT MATTERS: 소제목 + 본문
5. 04 MARKET CLOSE: 현재가 + 등락 + 7거래일 차트 + 매핑규칙 + 출처

## 수치 원칙
기사 원문에 명시된 숫자만 사용. 없으면 해당 블록 미표시. 주가 확인 불가 시 "라이브 차트 확인 필요".
