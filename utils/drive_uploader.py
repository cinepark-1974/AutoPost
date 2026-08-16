import os
import json
from pathlib import Path


def get_drive_service():
    """
    인증 우선순위:
    1) OAuth (본인 계정 위임) - 개인 드라이브 업로드 가능
    2) 서비스 계정 (읽기 보조용, 개인 드라이브 쓰기 불가)
    """
    from googleapiclient.discovery import build

    scopes = ["https://www.googleapis.com/auth/drive"]

    # 1. OAuth (본인 계정) 우선 - 내 드라이브 업로드 가능
    client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
    refresh_token = os.getenv("GOOGLE_OAUTH_REFRESH_TOKEN")
    if client_id and client_secret and refresh_token:
        try:
            from google.oauth2.credentials import Credentials
            creds = Credentials(
                None,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=client_id,
                client_secret=client_secret,
                scopes=scopes,
            )
            print("Drive 인증: OAuth (본인 계정) 사용")
            return build("drive", "v3", credentials=creds)
        except Exception as e:
            print(f"OAuth 인증 실패: {e}")

    # 2. 서비스 계정 (읽기 보조용)
    json_content = os.getenv("GOOGLE_CREDENTIALS_JSON_CONTENT")
    if json_content:
        try:
            from google.oauth2 import service_account
            info = json.loads(json_content)
            creds = service_account.Credentials.from_service_account_info(info, scopes=scopes)
            print("Drive 인증: 서비스 계정 사용 (읽기 보조)")
            return build("drive", "v3", credentials=creds)
        except Exception as e:
            print(f"JSON_CONTENT 파싱 실패: {e}")

    cred_path = os.getenv("GOOGLE_CREDENTIALS_JSON", "./credentials.json")
    if Path(cred_path).exists():
        try:
            from google.oauth2 import service_account
            creds = service_account.Credentials.from_service_account_file(cred_path, scopes=scopes)
            return build("drive", "v3", credentials=creds)
        except Exception:
            pass

    print("Drive 인증 없음 → 드라이브 스킵")
    return None



def upload_to_drive(local_folder, drive_folder_id=None):
    if not drive_folder_id:
        print("GDRIVE_FOLDER_ID_OUTPUT 없음 → 로컬 저장만")
        return
    try:
        service = get_drive_service()
        if not service:
            print("Drive 서비스 없음 → 업로드 스킵 (Actions Artifacts에는 저장됨)")
            return

        from googleapiclient.http import MediaFileUpload

        folder_name = Path(local_folder).name
        file_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [drive_folder_id],
        }
        folder = service.files().create(
            body=file_metadata,
            fields="id",
            supportsAllDrives=True,
        ).execute()
        new_folder_id = folder.get("id")
        print(f"Drive 폴더 생성: {folder_name} ({new_folder_id})")

        uploaded = 0
        for file in Path(local_folder).glob("*"):
            if file.is_file():
                media = MediaFileUpload(str(file), resumable=True)
                service.files().create(
                    body={"name": file.name, "parents": [new_folder_id]},
                    media_body=media,
                    fields="id",
                    supportsAllDrives=True,
                ).execute()
                uploaded += 1
                print(f"  업로드: {file.name}")
        print(f"Drive 업로드 완료: {folder_name} (파일 {uploaded}개)")
    except Exception as e:
        print(f"Drive 업로드 실패 (무시하고 계속, Artifacts에는 있음): {e}")
        return
