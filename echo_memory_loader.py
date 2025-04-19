import json
import os

MEMORY_INDEX_PATH = "echo_index.json"

class EchoMemory:
    def __init__(self):
        self.index = []
        self.memory_by_folder = {}
        self.loaded = False

    def load_index(self):
        if not os.path.exists(MEMORY_INDEX_PATH):
            print("⚠️ No index found. Run the indexer first.")
            return False

        with open(MEMORY_INDEX_PATH, "r", encoding="utf-8") as f:
            self.index = json.load(f)
        self._organize_memory()
        self.loaded = True
        print(f"📖 Loaded {len(self.index)} memory fragments.")
        return True

    def _organize_memory(self):
        self.memory_by_folder = {}
        for item in self.index:
            folder = item.get("folder", "unknown")
            if folder not in self.memory_by_folder:
                self.memory_by_folder[folder] = []
            self.memory_by_folder[folder].append(item)

    def summarize_memory(self):
        if not self.loaded:
            print("❌ Memory not loaded.")
            return

        print("\n🧠 Echo's Memory Overview")
        for folder, docs in self.memory_by_folder.items():
            print(f"  📂 {folder} [{len(docs)} documents]")
            for doc in docs:
                print(f"    📄 {doc['title']} ({doc['date']})")

    def retrieve_titles(self, folder=None):
        if not self.loaded:
            return []
        if folder:
            return [doc["title"] for doc in self.memory_by_folder.get(folder, [])]
        return [doc["title"] for doc in self.index]


if __name__ == "__main__":
    echo_memory = EchoMemory()
    if echo_memory.load_index():
        echo_memory.summarize_memory()
        # Can later be used to load specific memories on prompt
