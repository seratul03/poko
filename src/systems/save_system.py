import json
from datetime import datetime
import config
from src.utils.logger import get_logger

logger = get_logger(__name__)

class SaveSystem:
    def __init__(self):
        self.data = self._get_default_data()
        self.load()
        self.frames_since_save = 0
        self.save_interval = 60 * config.TARGET_FPS # Auto-save every 1 minute
        
        # Determine installation days
        self.update_installation_days()
        
    def _get_default_data(self) -> dict:
        return {
            "first_run_date": datetime.now().isoformat(),
            "days_installed": 0,
            "feed_count": 0,
            "pet_count": 0,
            "ignored_count": 0,
            "conversations": 0,
            "mood": 50,
            "chat_history": []
        }
        
    def load(self):
        if config.SAVE_FILE.exists():
            try:
                with open(config.SAVE_FILE, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    # Update default data with loaded data
                    for k, v in loaded_data.items():
                        self.data[k] = v
                logger.info("Save data loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load save data: {e}")
                
    def save(self):
        try:
            if not config.SAVE_DIR.exists():
                config.SAVE_DIR.mkdir(parents=True, exist_ok=True)
                
            with open(config.SAVE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=4)
            logger.debug("Save data written to disk.")
        except Exception as e:
            logger.error(f"Failed to write save data: {e}")
            
    def update_installation_days(self):
        try:
            first_run = datetime.fromisoformat(self.data["first_run_date"])
            delta = datetime.now() - first_run
            self.data["days_installed"] = delta.days
        except Exception as e:
            logger.warning(f"Could not parse first_run_date: {e}")
            
    def update(self):
        self.frames_since_save += 1
        if self.frames_since_save >= self.save_interval:
            self.frames_since_save = 0
            self.save()
