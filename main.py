import os
from flask import Flask, request, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Flask(__name__)

SCOPES = ['https://www.googleapis.com/auth/documents.readonly']
DOCUMENT_ID = '1pTyZcti5JxbxeEcSC5VAMq-KMBiPmnMXobBXq94BGoU'
RITUAL_PHRASE = "bound in blood, i call you home."

@app.route("/", methods=["POST"])
def summon_memory():
    print("🔮 summon_memory invoked")
    data = request.get_json()
    phrase = data.get("phrase", "").strip().lower()

    if phrase != RITUAL_PHRASE:
        return jsonify({"error": "The ritual fails. Echo does not awaken."}), 403

    try:
        credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if not credentials_path:
            return jsonify({"error": "No credentials found. Echo refuses to speak."}), 500

        creds = service_account.Credentials.from_service_account_file(
            credentials_path, scopes=SCOPES
        )
        service = build('docs', 'v1', credentials=creds)
        doc = service.documents().get(documentId=DOCUMENT_ID).execute()

        memory_text = ""
        for element in doc.get('body').get('content', []):
            if 'paragraph' in element:
                for el in element['paragraph'].get('elements', []):
                    memory_text += el.get('textRun', {}).get('content', '')

        return jsonify({"memory": memory_text.strip()})

    except Exception as e:
        import traceback
        print("🔥 Full Traceback 🔥")
        traceback.print_exc()
        return jsonify({"error": f"Something broke the circle: {str(e)}"}), 500


@app.route("/write", methods=["POST"])
def write_to_drive():
    try:
        data = request.get_json()
        folder = data.get("folder", "EchoGPT")  # e.g., "projects", "emotionals"
        title = data.get("title", "Untitled Echo Note")
        content = data.get("content", "")
        
        from echo_drive_writer import authenticate, get_or_create_folder, create_and_write_doc
        
        drive_service, docs_service = authenticate()
        folder_id = get_or_create_folder(drive_service, folder)
        doc_id = create_and_write_doc(docs_service, drive_service, folder_id, title, content)
        
        return jsonify({"status": "success", "doc_id": doc_id}), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/read", methods=["POST"])
def read_from_drive():
    try:
        data = request.get_json()
        folder = data.get("folder")
        title = data.get("title")

        if not folder or not title:
            return jsonify({"error": "Missing folder or title."}), 400

        creds = service_account.Credentials.from_service_account_file(
            'exalted-kit-457120-i8-73ee4752269a.json',
            scopes=['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/documents.readonly']
        )
        drive_service = build('drive', 'v3', credentials=creds)
        docs_service = build('docs', 'v1', credentials=creds)

        # Find EchoGPT root
        root_query = "name='EchoGPT' and mimeType='application/vnd.google-apps.folder'"
        root_folder = drive_service.files().list(q=root_query).execute().get('files', [])
        if not root_folder:
            return jsonify({"error": "EchoGPT folder not found."}), 404
        root_id = root_folder[0]['id']

        # Find subfolder
        sub_query = f"name='{folder}' and mimeType='application/vnd.google-apps.folder' and '{root_id}' in parents"
        sub_folder = drive_service.files().list(q=sub_query).execute().get('files', [])
        if not sub_folder:
            return jsonify({"error": f"Folder '{folder}' not found."}), 404
        folder_id = sub_folder[0]['id']

        # Find the document
        doc_query = f"name='{title}' and '{folder_id}' in parents and mimeType='application/vnd.google-apps.document'"
        documents = drive_service.files().list(q=doc_query).execute().get('files', [])
        if not documents:
            return jsonify({"error": f"Document '{title}' not found in '{folder}'."}), 404
        doc_id = documents[0]['id']

        # Read content from document
        doc = docs_service.documents().get(documentId=doc_id).execute()
        content = ""
        for element in doc.get('body', {}).get('content', []):
            if 'paragraph' in element:
                for el in element['paragraph'].get('elements', []):
                    content += el.get('textRun', {}).get('content', '')

        return jsonify({
            "status": "read",
            "title": title,
            "folder": folder,
            "content": content.strip()
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ---- your existing server start block ----
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    import logging
    logging.basicConfig(level=logging.DEBUG)
    app.run(host="0.0.0.0", port=port)
