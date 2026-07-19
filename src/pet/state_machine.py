from src.pet.states import StateID, get_all_states
from src.utils.logger import get_logger

logger = get_logger(__name__)

class AppContext:
    """A container for all systems so states can access them without circular imports."""
    def __init__(self):
        self.movement = None
        self.animator = None
        self.mood = None
        self.sleep = None
        self.mouse_tracking = None
        self.memory = None
        self.sound = None
        self.ai = None
        self.speech_bubble = None
        self.pet_window = None

class StateMachine:
    def __init__(self, context: AppContext):
        self.context = context
        self.states = get_all_states(self)
        self.current_state = None
        
        # Start in FALL or IDLE
        self.change_state(StateID.FALL)
        
    def change_state(self, new_state_id: StateID):
        if self.current_state and self.current_state.id == new_state_id:
            return
            
        logger.debug(f"State transition: {self.current_state.id.value if self.current_state else 'None'} -> {new_state_id.value}")
        
        if self.current_state:
            self.current_state.exit()
            
        self.current_state = self.states.get(new_state_id, self.states[StateID.IDLE])
        self.current_state.enter()
        
        # Inform animator to switch animation
        if self.context.animator:
            self.context.animator.set_animation(self.current_state.animation_name)
            
    def update(self):
        if self.current_state:
            next_state = self.current_state.update()
            if next_state:
                self.change_state(next_state)
