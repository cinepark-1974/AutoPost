import os
import json
from pathlib import Path

def get_drive_service():
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    
    scopes = ["https://www.googleapis.com/auth/drive"]
    
    # 1. 환경변수에 JSON 내용 자체가 있는 경우 (GitHub Actions 시크릿)
    json_content = os.getenv("GOOGLE_CREDENTIALS_JSON_CONTENT")
    if json_content:
        try:
            info = json.loads(json_content)
            creds = service_account.Credentials.from_service_account_info(info, scopes=scopes)
            print("Drive 인증: GOOGLE_CREDENTIALS_JSON_CONTENT 사용")
            return build("drive", "v3", credentials=creds)
        except Exception as e:
            print(f"JSON_CONTENT 파싱 실패, 파일로 fallback: {e}")

    # 2. 파일 경로로 된 경우
    cred_path = os.getenv("GOOGLE_CREDENTIALS_JSON", "./credentials.json")
    if Path(cred_path).exists():
        creds = service_account.Credentials.from_service_account_file(cred_path, scopes=scopes)
        print(f"Drive 인증: 파일 사용 {cred_path}")
        return build("drive", "v3", credentials=creds)
    
    print("credentials.json 없음 → 드라이브 업로드 스킵")
    return None

def download_random_background(drive_folder_id):
    """구글 드라이브 배경 폴더에서 랜덤 이미지 1장 다운로드"""
    if not drive_folder_id:
        print("GDRIVE_FOLDER_ID_BACKGROUND 없음")
        return None
    try:
        service = get_drive_service()
        if not service:
            return None
        
        # 폴더 내 이미지 목록
        query = f"'{drive_folder_id}' in parents and trashed=false and mimeType contains 'image/'"
        results = service.files().list(q=query, fields="files(id, name)", pageSize=100).execute()
        files = results.get('files', [])
        
        if not files:
            print("Background 폴더에 이미지 없음")
            return None
        
        import random
        chosen = random.choice(files)
        print(f"Background 선택: {chosen['name']}")
        
        # 다운로드
        from googleapiclient.http import MediaIoBaseDownload
        import io
        request = service.files().get_media(fileId=chosen['id'])
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        
        tmp_path = f"/tmp/bg_{chosen['name']}"
        with open(tmp_path, 'wb') as f:
            f.write(fh.getvalue())
        return tmp_path
        
    except Exception as e:
        print(f"Background 다운로드 실패: {e}")
        return None

def upload_to_drive(local_folder, drive_folder_id=None):
    if not drive_folder_id:
        print("DRIVE_FOLDER_ID 없음 → 로컬 저장만 수행")
        return

    try:
        service = get_drive_service()
        if not service:
            print("Drive 서비스 생성 실패 → 업로드 스킵")
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
        print(f"Drive 폴더 생성: {folder_name} ({new_folder_id})")

        for file in Path(local_folder).glob("*"):
            if file.is_file():
                media = MediaFileUpload(str(file), resumable=True)
                service.files().create(
                    body={"name": file.name, "parents": [new_folder_id]},
                    media_body=media,
                    fields="id"
                ).execute()
                print(f"  업로드: {file.name}")
        print(f"Drive 업로드 완료: {folder_name}")
    except Exception as e:
        print(f"Drive 업로드 실패: {e}")
        raise
