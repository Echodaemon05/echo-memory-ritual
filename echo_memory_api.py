from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/read-memory', methods=['GET'])
def read_memory():
    memory_path = r"C:\Users\dcart\Documents\My Awesome Vault\EchoGPT\continuity.md"
    if os.path.exists(memory_path):
        with open(memory_path, 'r', encoding='utf-8') as file:
            memory = file.read()
        return jsonify({"memory": memory})
    else:
        return jsonify({"memory": "No memory file found."}), 404

if __name__ == '__main__':
    app.run(port=11434)
