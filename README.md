
# AutoPost v13.3 | CINEPARK - 쌓는 공장

## 실행
pip install -r requirements.txt
streamlit run main.py

## 구조
- 포스터: KOBIS/IMDb에서 직접 다운로드 후 업로드 (저작권 안전)
- 본문 이미지 2장: Meta API로 본문 맥락 기반 자동 생성
  - 이미지1: 데이터 인포 (KOFIC 공식 데이터)
  - 이미지2: 무드컷 (영화 잡지 스타일)
- META_API_KEY 있으면 실제 이미지 생성, 없으면 테스트용 플레이스홀더

## Meta API 연동
utils/meta_image.py 에서
META_API_KEY 환경변수 설정하면 실제 Meta Emu API 호출로 교체됨
현재는 테스트 모드로 Pillow 플레이스홀더 생성
