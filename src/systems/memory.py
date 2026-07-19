from src.systems.save_system import SaveSystem
from src.utils.logger import get_logger

logger = get_logger(__name__)

class MemorySystem:
    def __init__(self, save_system: SaveSystem):
        self.save_system = save_system
        
    def increment_feed(self):
        self.save_system.data["feed_count"] += 1
        
    def increment_pet(self):
        self.save_system.data["pet_count"] += 1
        
    def increment_ignored(self):
        self.save_system.data["ignored_count"] += 1
        
    def increment_conversations(self):
        self.save_system.data["conversations"] += 1
        
    def add_chat_history(self, user_msg: str, ai_msg: str):
        history = self.save_system.data.setdefault("chat_history", [])
        history.append({"user": user_msg, "ai": ai_msg})
        # Keep only the last 50 messages to prevent infinite growth
        if len(history) > 50:
            history.pop(0)
            
    def get_chat_history(self):
        return self.save_system.data.get("chat_history", [])
        
    def get_stats(self):
        return {
            "days_installed": self.save_system.data.get("days_installed", 0),
            "feed_count": self.save_system.data.get("feed_count", 0),
            "pet_count": self.save_system.data.get("pet_count", 0),
            "conversations": self.save_system.data.get("conversations", 0)
        }
