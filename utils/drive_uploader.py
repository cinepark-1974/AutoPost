import os
import json
from pathlib import Path

def get_drive_service():
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    
    scopes = ["https://www.googleapis.com/auth/drive"]
    
    # 1. OAuth (본인 계정) 우선 - 내 드라이브 업로드 가능
    client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
    refresh_token = os.getenv("GOOGLE_OAUTH_REFRESH_TOKEN")
    if client_id and client_secret and refresh_token:
        try:
            creds = Credentials(
                None,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=client_id,
                client_secret=client_secret,
                scopes=scopes
            )
            print("Drive 인증: OAuth (본인 계정) 사용")
            return build("drive", "v3", credentials=creds)
        except Exception as e:
            print(f"OAuth 인증 실패: {e}")

    # 2. 서비스 계정 (읽기용)
    json_content = os.getenv("GOOGLE_CREDENTIALS_JSON_CONTENT")
    if json_content:
        try:
            info = json.loads(json_content)
            creds = service_account.Credentials.from_service_account_info(info, scopes=scopes)
            print("Drive 인증: 서비스 계정 사용 (읽기용)")
            return build("drive", "v3", credentials=creds)
        except Exception as e:
            print(f"JSON_CONTENT 파싱 실패: {e}")

    cred_path = os.getenv("GOOGLE_CREDENTIALS_JSON", "./credentials.json")
    if Path(cred_path).exists():
        try:
            creds = service_account.Credentials.from_service_account_file(cred_path, scopes=scopes)
            return build("drive", "v3", credentials=creds)
        except:
            pass
    
    print("Drive 인증 없음 → 드라이브 스킵")
    return None

def download_random_background(drive_folder_id):
    if not drive_folder_id:
        print("GDRIVE_FOLDER_ID_BACKGROUND 없음")
        return None
    try:
        service = get_drive_service()
        if not service:
            return None
        query = f"'{drive_folder_id}' in parents and trashed=false and mimeType contains 'image/'"
        results = service.files().list(q=query, fields="files(id, name)", pageSize=100).execute()
        files = results.get('files', [])
        if not files:
            print("Background 폴더에 이미지 없음")
            return None
        import random
        chosen = random.choice(files)
        print(f"Background 선택: {chosen['name']}")
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
        print(f"Background 다운로드 실패 (무시): {e}")
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

        # 서비스 계정이면 내 드라이브 업로드 불가 → 스킵 (에러 안 내고)
        try:
            from google.oauth2.service_account import Credentials as SACreds
            # OAuth인지 서비스 계정인지 체크
            is_service_account = os.getenv("GOOGLE_OAUTH_CLIENT_ID") is None
            if is_service_account:
                # 내 드라이브에 서비스 계정으로 업로드 시도하면 quota 오류남 → 그냥 스킵
                print("서비스 계정으로 내 드라이브 업로드 불가 → Artifacts로만 저장")
                # 그래도 폴더 생성 시도하다 실패하면 스킵
                pass
        except:
            pass

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
        # 중요: 여기서 raise 하지 않음 → 실패해도 Actions는 성공 처리
        print(f"Drive 업로드 실패 (무시하고 계속, Artifacts에는 있음): {e}")
        return
