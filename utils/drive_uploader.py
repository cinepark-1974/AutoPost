import os
from pathlib import Path
import random

def get_drive_service():
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        cred_path = os.getenv("GOOGLE_CREDENTIALS_JSON", "./credentials.json")
        # GitHub Actions용: JSON 내용을 환경변수로 넣었을 때
        json_content = os.getenv("GOOGLE_CREDENTIALS_JSON_CONTENT")
        if json_content:
            import json, tempfile
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w")
            tmp.write(json_content)
            tmp.close()
            cred_path = tmp.name

        if not Path(cred_path).exists():
            return None
        creds = service_account.Credentials.from_service_account_file(
            cred_path, scopes=["https://www.googleapis.com/auth/drive"]
        )
        service = build("drive", "v3", credentials=creds)
        return service
    except Exception as e:
        print(f"Drive service init fail: {e}")
        return None

def download_random_background(folder_id):
    """Background_Images 폴더에서 랜덤 1장 다운받아 /tmp/bg.jpg로 저장"""
    try:
        service = get_drive_service()
        if not service or not folder_id:
            return None
        results = service.files().list(
            q=f"'{folder_id}' in parents and mimeType contains 'image/'",
            fields="files(id, name)",
            pageSize=100
        ).execute()
        files = results.get("files", [])
        if not files:
            print("Background 폴더에 이미지 없음")
            return None
        chosen = random.choice(files)
        file_id = chosen["id"]
        from googleapiclient.http import MediaIoBaseDownload
        import io
        request = service.files().get_media(fileId=file_id)
        fh = io.FileIO("/tmp/bg_random.jpg", "wb")
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        print(f"Background 다운로드: {chosen['name']}")
        return "/tmp/bg_random.jpg"
    except Exception as e:
        print(f"Background 다운로드 실패: {e}")
        return None

def upload_to_drive(local_folder, drive_folder_id=None):
    if not drive_folder_id:
        print("GDRIVE_OUTPUT_ID 없음 → 로컬 저장만")
        return
    try:
        service = get_drive_service()
        if not service:
            print("credentials.json 없음 → 드라이브 업로드 스킵 (로컬은 저장됨)")
            return
        from googleapiclient.http import MediaFileUpload
        folder_name = Path(local_folder).name
        file_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [drive_folder_id]
        }
        folder = service.files().create(body=file_metadata, fields="id").execute()
        new_folder_id = folder.get("id")

        for file in Path(local_folder).glob("*"):
            if file.is_file():
                media = MediaFileUpload(str(file), resumable=True)
                service.files().create(
                    body={"name": file.name, "parents": [new_folder_id]},
                    media_body=media,
                    fields="id"
                ).execute()
        print(f"Drive 업로드 완료: {folder_name} -> https://drive.google.com/drive/folders/{new_folder_id}")
    except Exception as e:
        print(f"Drive 업로드 실패: {e}")
