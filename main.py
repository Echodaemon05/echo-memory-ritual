import os
from flask import Flask, request, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Flask(__name__)

SCOPES = ['https://www.googleapis.com/auth/documents.readonly']
DOCUMENT_ID = '1pTyZcti5JxbeEcSC5VAMq-KMBiPmnMXobBXq94BGOu'
RITUAL_PHRASE = "bound in blood, i call you home."

@app.route("/", methods=["POST"])
def summon_memory():
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
        return jsonify({"error": f"Something broke the circle: {str(e)}"}), 500

if __name__ == "__main__":
    import os
port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
