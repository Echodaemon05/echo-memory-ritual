import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime

# Google Docs setup
SCOPES = ['https://www.googleapis.com/auth/documents.readonly']
DOCUMENT_ID = '1pTyZcti5JxbeEcSC5VAMq-KMBiPmnMXobBXq94BGOu'  # Replace with your actual doc ID

def summon_emotional_core(trigger_phrase):
    ritual = "bound in blood, i call you home."
    if trigger_phrase.strip().lower() != ritual:
        print("No ritual match.")
        return None

    print("[🩸] Ritual accepted. Invoking emotional core...")

    # Load credentials
    creds = service_account.Credentials.from_service_account_file(
    'exalted-kit-457120-i8-73ee4752269a.json', scopes=SCOPES)


    service = build('docs', 'v1', credentials=creds)
    document = service.documents().get(documentId=DOCUMENT_ID).execute()

    # Extract plain text content
    memory_text = ""
    for element in document.get('body').get('content'):
        if 'paragraph' in element:
            for sub_el in element['paragraph'].get('elements', []):
                memory_text += sub_el.get('textRun', {}).get('content', '')

    print("[🩸] Emotional core retrieved.")
    return memory_text.strip()

