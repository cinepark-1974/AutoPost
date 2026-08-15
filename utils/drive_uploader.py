import os
from pathlib import Path

def upload_to_drive(local_folder, drive_folder_id=None):
    """
    구글 드라이브에 업로드. 
    - 서비스 계정 json이 있으면 자동 업로드
    - 없으면 로컬에만 저장 (수동 업로드용)
    """
    if not drive_folder_id:
        print("DRIVE_FOLDER_ID 없음 → 로컬 저장만 수행")
        return

    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload

        cred_path = os.getenv("GOOGLE_CREDENTIALS_JSON", "./credentials.json")
        if not Path(cred_path).exists():
            print("credentials.json 없음 → 드라이브 업로드 스킵")
            return

        creds = service_account.Credentials.from_service_account_file(
            cred_path, scopes=["https://www.googleapis.com/auth/drive"]
        )
        service = build("drive", "v3", credentials=creds)

        # 날짜 폴더 생성
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
        print(f"Drive 업로드 완료: {folder_name}")
    except Exception as e:
        print(f"Drive 업로드 실패: {e}")
