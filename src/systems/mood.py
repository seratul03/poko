import config
from src.utils.logger import get_logger

logger = get_logger(__name__)

class MoodSystem:
    def __init__(self, save_system):
        self.save_system = save_system
        self.current_mood = self.save_system.data.get("mood", 75)
        
        # We decay mood slowly. config.MOOD_DECAY_RATE is per minute.
        # Since we update at 60 FPS, 1 minute is 3600 frames.
        self.frames_since_decay = 0
        self.decay_threshold = 60 * config.TARGET_FPS # 1 minute
        
    def _clamp_mood(self):
        self.current_mood = max(config.MIN_MOOD, min(config.MAX_MOOD, self.current_mood))
        
    def add_mood(self, amount: int):
        old_mood = self.current_mood
        self.current_mood += amount
        self._clamp_mood()
        logger.debug(f"Mood changed: {old_mood} -> {self.current_mood}")
        self.save_system.data["mood"] = self.current_mood
        
    def feed(self):
        self.add_mood(config.MOOD_FEED_BOOST)
        
    def pet(self):
        self.add_mood(config.MOOD_PET_BOOST)
        
    def ignore(self):
        self.add_mood(-config.MOOD_IGNORE_PENALTY)
        
    def get_mood_state(self) -> str:
        # Bands are intentionally skewed positive — panda should almost always
        # look happy. Sad / angry only show after serious neglect.
        if self.current_mood >= 70: return "very_happy"  # 70-100
        if self.current_mood >= 20: return "happy"        # 20-69  (the big happy zone)
        if self.current_mood >= 10: return "neutral"      # 10-19
        if self.current_mood >= 3:  return "sad"          # 3-9
        return "angry"                                    # 0-2  (almost never)
        
    def update(self):
        self.frames_since_decay += 1
        if self.frames_since_decay >= self.decay_threshold:
            self.frames_since_decay = 0
            self.add_mood(-config.MOOD_DECAY_RATE)
