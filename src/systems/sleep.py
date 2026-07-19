import config
from src.pet.states import StateID
from src.utils.logger import get_logger

logger = get_logger(__name__)

class SleepSystem:
    def __init__(self, state_machine):
        self.state_machine = state_machine
        self.idle_frames = 0
        
        # Go to sleep after 5 minutes of no interaction
        self.sleep_threshold = 5 * 60 * config.TARGET_FPS
        
    def reset_idle_timer(self):
        """Called when the user interacts with the pet (clicks, drags, feeds)."""
        if self.state_machine.current_state and self.state_machine.current_state.id == StateID.SLEEP:
            # Wake up
            logger.info("Pet woke up!")
            self.state_machine.change_state(StateID.IDLE)
        self.idle_frames = 0
        
    def update(self):
        # Don't increment if already sleeping, dragging, or falling
        current_id = self.state_machine.current_state.id if self.state_machine.current_state else None
        
        if current_id in [StateID.SLEEP, StateID.DRAG, StateID.FALL]:
            return
            
        self.idle_frames += 1
        
        if self.idle_frames >= self.sleep_threshold:
            logger.info("Pet is falling asleep due to inactivity.")
            self.state_machine.change_state(StateID.SLEEP)
