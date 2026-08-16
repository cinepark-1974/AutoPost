# -*- coding: utf-8 -*-
"""
이미 생성된 카드의 텍스트 오타·표현을 고칠 때 쓴다.
사용법:
  1) output/2026-08-16_SONY/meta.json 을 열어 원하는 값을 직접 수정
  2) python rebuild.py output/2026-08-16_SONY
  → 같은 폴더에 카드 5장이 다시 생성된다. (웹 검색 없음 = 비용 0)

드라이브 재업로드까지 하려면:
  python rebuild.py output/2026-08-16_SONY --upload
"""
import sys
import json
import os
from dotenv import load_dotenv
load_dotenv()

from utils.render import render_cards


def main():
    if len(sys.argv) < 2:
        print("사용법: python rebuild.py <폴더경로> [--upload]")
        print("예:     python rebuild.py output/2026-08-16_SONY")
        raise SystemExit(1)

    folder = sys.argv[1].rstrip("/")
    do_upload = "--upload" in sys.argv

    meta_path = os.path.join(folder, "meta.json")
    if not os.path.exists(meta_path):
        raise SystemExit(f"meta.json 없음: {meta_path}")

    with open(meta_path, encoding="utf-8") as f:
        data = json.load(f)

    print(f"meta.json 로드: {meta_path}")
    print("카드 재생성 중 (웹 검색 없음, 비용 0)...")
    render_cards(data, folder)
    print(f"완료: {folder}")

    if do_upload:
        from config import GDRIVE_OUTPUT_ID
        from utils.drive_uploader import upload_to_drive
        print("드라이브 재업로드 중...")
        upload_to_drive(folder, GDRIVE_OUTPUT_ID)


if __name__ == "__main__":
    main()
