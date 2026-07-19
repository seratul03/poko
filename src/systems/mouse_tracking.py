import math
from pynput import mouse
from PySide6.QtCore import QPoint
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Distance thresholds (pixels) for curiosity zones
CURIOSITY_NEAR = 200   # Close enough to notice
CURIOSITY_CLOSE = 100  # Close enough to get really interested
CURIOSITY_TOUCH = 40   # Practically touching — pounce range


class MouseTrackingSystem:
    def __init__(self):
        self.current_pos = QPoint(0, 0)
        self.prev_pos = QPoint(0, 0)
        self.is_moving = False

        # Cursor velocity (pixels per callback, roughly proportional to speed)
        self.cursor_speed = 0.0

        # Start pynput listener
        try:
            self.listener = mouse.Listener(on_move=self._on_move)
            self.listener.start()
            logger.info("Mouse tracking started successfully.")
        except Exception as e:
            logger.error(f"Failed to start mouse tracking: {e}")
            self.listener = None

    def _on_move(self, x, y):
        self.prev_pos = QPoint(self.current_pos.x(), self.current_pos.y())
        self.current_pos.setX(int(x))
        self.current_pos.setY(int(y))
        self.is_moving = True

        dx = self.current_pos.x() - self.prev_pos.x()
        dy = self.current_pos.y() - self.prev_pos.y()
        self.cursor_speed = math.sqrt(dx * dx + dy * dy)

    def get_mouse_pos(self) -> QPoint:
        return self.current_pos

    def check_and_reset_moving(self) -> bool:
        """Returns True if the mouse moved recently, then resets the flag."""
        was_moving = self.is_moving
        self.is_moving = False
        return was_moving

    # ------------------------------------------------------------------
    # Proximity helpers — called from the update loop with the pet rect
    # ------------------------------------------------------------------

    def distance_to(self, pet_center_x: float, pet_center_y: float) -> float:
        """Euclidean distance from the cursor to the pet's centre."""
        dx = self.current_pos.x() - pet_center_x
        dy = self.current_pos.y() - pet_center_y
        return math.sqrt(dx * dx + dy * dy)

    def direction_to_cursor(self, pet_center_x: float) -> float:
        """Returns a normalised value in [-1, 1] indicating whether the
        cursor is to the left (-1) or right (+1) of the pet centre.
        The magnitude indicates how far off-centre it is (clamped)."""
        dx = self.current_pos.x() - pet_center_x
        if abs(dx) < 1:
            return 0.0
        return max(-1.0, min(1.0, dx / 150.0))  # smooth ramp over 150px

    def vertical_to_cursor(self, pet_center_y: float) -> float:
        """Returns a normalised value in [-1, 1] indicating whether the
        cursor is above (-1) or below (+1) the pet centre."""
        dy = self.current_pos.y() - pet_center_y
        if abs(dy) < 1:
            return 0.0
        return max(-1.0, min(1.0, dy / 150.0))

    def is_cursor_fast(self) -> bool:
        """True when the cursor is zipping across the screen."""
        return self.cursor_speed > 40

    def stop(self):
        if self.listener:
            self.listener.stop()
