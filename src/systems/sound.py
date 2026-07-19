import os
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtCore import QUrl
import config
from src.utils.logger import get_logger

logger = get_logger(__name__)

class SoundSystem:
    def __init__(self):
        self.sounds = {}
        self.volume = 0.5  # 0.0 to 1.0
        
        # Preload standard sounds if they exist
        self._load_sound("meow", "meow.wav")
        self._load_sound("purr", "purr.wav")
        self._load_sound("eat", "eat.wav")
        self._load_sound("click", "click.wav")
        
    def _load_sound(self, name: str, filename: str):
        path = config.SOUNDS_DIR / filename
        if path.exists():
            effect = QSoundEffect()
            effect.setSource(QUrl.fromLocalFile(str(path)))
            effect.setVolume(self.volume)
            self.sounds[name] = effect
        else:
            logger.debug(f"Sound file not found, skipping: {path}")
            
    def set_volume(self, vol: float):
        self.volume = max(0.0, min(1.0, vol))
        for effect in self.sounds.values():
            effect.setVolume(self.volume)
            
    def play(self, name: str):
        if name in self.sounds:
            self.sounds[name].play()
        else:
            logger.debug(f"Attempted to play unknown or unloaded sound: {name}")
