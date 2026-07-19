import random
from PySide6.QtWidgets import QApplication
import config
from src.utils.logger import get_logger

logger = get_logger(__name__)

class MovementSystem:
    def __init__(self, pet_window):
        self.pet = pet_window
        
        # Get screen geometry to restrict movement
        self.screen_rect = QApplication.primaryScreen().geometry()
        
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        
        # Current exact position (float) for smoother movement
        self.pos_x = float(self.pet.x())
        self.pos_y = float(self.pet.y())
        
        self.is_falling = False
        
    def move_left(self):
        # Add slight randomness to speed
        speed = config.BASE_SPEED * random.uniform(0.8, 1.2)
        self.velocity_x = -speed
        self.velocity_y = 0.0
        
    def move_right(self):
        speed = config.BASE_SPEED * random.uniform(0.8, 1.2)
        self.velocity_x = speed
        self.velocity_y = 0.0
        
    def roll_left(self):
        speed = config.BASE_SPEED * random.uniform(1.2, 1.8)
        self.velocity_x = -speed
        self.velocity_y = 0.0

    def roll_right(self):
        speed = config.BASE_SPEED * random.uniform(1.2, 1.8)
        self.velocity_x = speed
        self.velocity_y = 0.0
        
    def stop(self):
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        
    def fall(self):
        self.is_falling = True
        self.velocity_x = 0.0
        self.velocity_y = config.RUN_SPEED * 2.0  # Fall fast
        
    def is_grounded(self):
        return self.pos_y >= self.screen_rect.height() - config.PET_HEIGHT
        
    def is_at_left_edge(self):
        return self.pos_x <= 0
        
    def is_at_right_edge(self):
        return self.pos_x >= self.screen_rect.width() - config.PET_WIDTH
        
    def update(self):
        # If currently being dragged, we don't update positions based on velocity
        if self.pet.dragging:
            # Sync internal float pos with window pos
            self.pos_x = float(self.pet.x())
            self.pos_y = float(self.pet.y())
            self.stop()
            return
            
        self.pos_x += self.velocity_x
        self.pos_y += self.velocity_y
        
        # Collision with screen edges
        # We stop the velocity if we hit the edge, preventing sliding backward while still in a walk state
        if self.pos_x <= 0:
            self.pos_x = 0
            if self.velocity_x < 0:
                self.velocity_x = 0.0
                
        elif self.pos_x >= self.screen_rect.width() - config.PET_WIDTH:
            self.pos_x = self.screen_rect.width() - config.PET_WIDTH
            if self.velocity_x > 0:
                self.velocity_x = 0.0

        # Ground collision
        if self.pos_y >= self.screen_rect.height() - config.PET_HEIGHT:
            self.pos_y = self.screen_rect.height() - config.PET_HEIGHT
            if self.is_falling:
                self.is_falling = False
                self.velocity_y = 0.0

        # Update actual window
        self.pet.move(int(self.pos_x), int(self.pos_y))
