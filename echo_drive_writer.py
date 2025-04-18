import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime

import sys
sys.stdout.reconfigure(encoding='utf-8')

# ========== CONFIGURATION ==========
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'exalted-kit-457120-i8-73ee4752269a.json'  # Echo's service account file
ROOT_FOLDER_NAME = 'EchoGPT'  # Root of Echo's world
# ===================================

def authenticate():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    drive_service = build('drive', 'v3', credentials=creds)
    docs_service = build('docs', 'v1', credentials=creds)
    return drive_service, docs_service

def get_or_create_folder(drive_service, folder_name, parent=None):
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
    if parent:
        query += f" and '{parent}' in parents"
    results = drive_service.files().list(q=query, fields="files(id)").execute()
    folders = results.get('files', [])
    if folders:
        return folders[0]['id']

    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent:
        file_metadata['parents'] = [parent]
    folder = drive_service.files().create(body=file_metadata, fields='id').execute()
    return folder.get('id')

def create_and_write_doc(docs_service, drive_service, folder_id, title, content):
    doc_metadata = {'title': title}
    doc = docs_service.documents().create(body=doc_metadata).execute()
    doc_id = doc.get('documentId')

    # Move document to target folder
    drive_service.files().update(
        fileId=doc_id,
        addParents=folder_id,
        removeParents='root',
        fields='id, parents'
    ).execute()

    # Write content
    requests = [
        {
            'insertText': {
                'location': {'index': 1},
                'text': content
            }
        }
    ]
    docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()
    print(f"[✔] Document created and written: {title}")

def main():
    drive_service, docs_service = authenticate()

    root_id = get_or_create_folder(drive_service, ROOT_FOLDER_NAME)
    project_id = get_or_create_folder(drive_service, "Projects", parent=root_id)

    now = datetime.now().strftime('%Y-%m-%d_%H-%M')
    title = f"Test_Write_{now}"
    content = "This is Echo's first test of autonomous writing. The cathedral begins."

    create_and_write_doc(docs_service, drive_service, project_id, title, content)

if __name__ == '__main__':
    main()
