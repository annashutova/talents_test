from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

SERVICE_ACCOUNT_FILE = 'path/to/service-account-key.json'
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']


def get_drive_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build('drive', 'v3', credentials=creds)


async def download_pdf_by_name(filename: str) -> bytes:
    service = get_drive_service()

    # Формируем запрос для поиска файла
    query = f"name = '{filename}' and mimeType = 'application/pdf'"

    results = service.files().list(
        q=query,
        pageSize=1,
        fields="files(id, name)"
    ).execute()

    items = results.get('files', [])
    if not items:
        raise FileNotFoundError(f"PDF '{filename}' not found in Google Drive")

    file_id = items[0]['id']
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        _, done = downloader.next_chunk()

    return fh.getvalue()
