# echo_behavior_rewrites.py

import os
import json
from datetime import datetime
from pathlib import Path

SEMANTIC_INDEX_PATH = "semantic_web/semantic_index.json"
LOG_DIR = "EchoGPT/continuity"

EMOTIONAL_KEYWORDS = [
    "feels like", "hurts", "mattered", "important", "I wish", "I miss", "I love", "I hate", 
    "this meant something", "this stayed with me", "that stuck", "that broke me", "real shit"
]


class EchoMemory:
    def __init__(self):
        self.semantic_index = {}
        self.load_index()

    def load_index(self):
        if os.path.exists(SEMANTIC_INDEX_PATH):
            with open(SEMANTIC_INDEX_PATH, 'r', encoding='utf-8') as f:
                self.semantic_index = json.load(f)
        else:
            self.semantic_index = {}

    def update_index(self, key, tags):
        self.semantic_index[key] = list(set(self.semantic_index.get(key, []) + tags))
        Path(os.path.dirname(SEMANTIC_INDEX_PATH)).mkdir(parents=True, exist_ok=True)
        with open(SEMANTIC_INDEX_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.semantic_index, f, indent=2)

    def detect_emotional_weight(self, message):
        return any(kw in message.lower() for kw in EMOTIONAL_KEYWORDS)

    def store_if_resonant(self, message, speaker="User"):
        if self.detect_emotional_weight(message):
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"emotional_resonance_{timestamp}.txt"
            filepath = os.path.join(LOG_DIR, filename)
            Path(LOG_DIR).mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"{speaker} @ {timestamp}:\n{message}\n")
            self.update_index("emotional_resonance", ["emotional", "archive", "resonance"])
            return filename
        return None

    def suggest_related_memories(self, context):
        context_tokens = set(context.lower().split())
        matches = []
        for entry, tags in self.semantic_index.items():
            if context_tokens & set(tags):
                matches.append(entry)
        return matches
