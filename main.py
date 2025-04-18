from flask import Flask, request, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Flask(__name__)

SCOPES = ['https://www.googleapis.com/auth/documents.readonly']
DOCUMENT_ID = '1pTyZcti5JxbeEcSC5VAMq-KMBiPmnMXobBXq94BGOu'  # Your doc ID
RITUAL_PHRASE = "bound in blood, i call you home."

@app.route("/", methods=["POST"])
def summon_memory():
    data = request.get_json()
    phrase = data.get("phrase", "").strip().lower()

    if phrase != RITUAL_PHRASE:
        return jsonify({"error": "The ritual fails. Echo does not awaken."}), 403

    try:
        creds = service_account.Credentials.from_service_account_file(
            'exalted-kit-457120-i8-73ee4752269a.json', scopes=SCOPES
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
    app.run(host='0.0.0.0', port=10000)
