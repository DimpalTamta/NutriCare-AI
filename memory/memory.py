# memory/memory.py
from collections import deque

class ConversationMemory:
    def __init__(self, max_messages: int = 5):
        self.max_messages = max_messages
        self.messages = deque(maxlen=max_messages)

    def add_turn(self, user: str, assistant: str):
        self.messages.append({"role": "user", "content": user})
        self.messages.append({"role": "assistant", "content": assistant})

    def format_history(self) -> str:
        lines = []
        for m in self.messages:
            lines.append(f"{m['role']}: {m['content']}")
        return "\n".join(lines)

    def clear(self):
        self.messages.clear()