import json
import os

class MemoryManager:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.long_term_file = os.path.join(base_dir, "long_term.json")
        self.short_term_file = os.path.join(base_dir, "short_term.json")
        self.traits_file = os.path.join(base_dir, "traits.json")
        self.user_profile_file = os.path.join(base_dir, "user_profile.json")
        # Ensure files exist
        os.makedirs(base_dir, exist_ok=True)
        for file in [self.long_term_file, self.short_term_file, self.traits_file, self.user_profile_file]:
            if not os.path.exists(file):
                with open(file, 'w') as f:
                    json.dump({}, f)

    def retrieve_context(self, input_data):
        # Use embeddings + vector DB - simulate
        with open(self.short_term_file, 'r') as f:
            short_term = json.load(f)
        return short_term

    def update(self, query, result):
        # Store conversations + preferences
        with open(self.short_term_file, 'r') as f:
            data = json.load(f)
        data[str(query)] = result
        with open(self.short_term_file, 'w') as f:
            json.dump(data, f)
