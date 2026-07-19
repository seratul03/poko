from typing import Optional
from PySide6.QtGui import QPixmap
from src.utils.logger import get_logger

logger = get_logger(__name__)

class Animator:
    def __init__(self, animations: dict[str, list[QPixmap]]):
        self.animations = animations
        self.current_anim_name = None
        self.current_frames = []
        self.frame_index = 0
        
        # We can slow down animations by holding a frame for multiple ticks
        self.ticks_per_frame = 10 # Adjust this to change animation speed
        self.tick_counter = 0

    def set_animation(self, anim_name: str):
        """Switches to a new animation if it exists."""
        if anim_name == self.current_anim_name:
            return
            
        if anim_name in self.animations:
            self.current_anim_name = anim_name
            self.current_frames = self.animations[anim_name]
            self.frame_index = 0
            self.tick_counter = 0
        else:
            # We are using procedural animations, so no need to warn about missing files.
            self.current_anim_name = anim_name
            self.current_frames = []

    def update(self) -> Optional[QPixmap]:
        """Called every game tick. Returns the current QPixmap to display."""
        if not self.current_frames:
            return None
            
        self.tick_counter += 1
        if self.tick_counter >= self.ticks_per_frame:
            self.tick_counter = 0
            self.frame_index = (self.frame_index + 1) % len(self.current_frames)
            
        return self.current_frames[self.frame_index]
