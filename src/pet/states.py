from enum import Enum
import random
from typing import Optional, TYPE_CHECKING
import config

if TYPE_CHECKING:
    from src.pet.state_machine import StateMachine

class StateID(Enum):
    IDLE = "idle"
    WALK_LEFT = "walk_left"
    WALK_RIGHT = "walk_right"
    SLEEP = "sleep"
    TALK = "talk"
    EAT = "eat"
    HAPPY = "happy"
    DRAG = "drag"
    FALL = "fall"
    ROLL_LEFT = "roll_left"
    ROLL_RIGHT = "roll_right"
    STAY_CALM = "stay_calm"

class PetState:
    def __init__(self, state_machine: 'StateMachine'):
        self.state_machine = state_machine
        self.id = StateID.IDLE
        self.duration_frames = 0
        self.frames_in_state = 0
        self.animation_name = "idle"
        
    def enter(self):
        """Called when state is entered."""
        self.frames_in_state = 0
        
    def exit(self):
        """Called when state is exited."""
        pass
        
    def update(self) -> Optional['StateID']:
        """Called every frame. Return a new StateID to transition, or None to stay."""
        self.frames_in_state += 1
        if self.duration_frames > 0 and self.frames_in_state >= self.duration_frames:
            return self.on_complete()
        return None
        
    def on_complete(self) -> Optional['StateID']:
        """Called when duration is up."""
        return StateID.IDLE
        
class IdleState(PetState):
    def __init__(self, sm):
        super().__init__(sm)
        self.id = StateID.IDLE
        self.animation_name = "idle"
        
    def enter(self):
        super().enter()
        # Random duration between 2 and 5 seconds
        self.duration_frames = random.randint(2 * config.TARGET_FPS, 5 * config.TARGET_FPS)
        # Ensure movement stops when entering idle
        self.state_machine.context.movement.stop()
        
    def on_complete(self):
        # Choose a random next state to show off animations
        choices = [
            StateID.WALK_LEFT, StateID.WALK_RIGHT, 
            StateID.IDLE, StateID.HAPPY,
            StateID.ROLL_LEFT, StateID.ROLL_RIGHT
        ]
        return random.choice(choices)

class StayCalmState(PetState):
    def __init__(self, sm):
        super().__init__(sm)
        self.id = StateID.STAY_CALM
        self.animation_name = "stay_calm"
        self.duration_frames = 0 # Stays calm until another action is chosen
        
    def enter(self):
        super().enter()
        self.state_machine.context.movement.stop()

class WalkLeftState(PetState):
    def __init__(self, sm):
        super().__init__(sm)
        self.id = StateID.WALK_LEFT
        self.animation_name = "walk_left"
        
    def enter(self):
        super().enter()
        self.duration_frames = random.randint(3 * config.TARGET_FPS, 6 * config.TARGET_FPS)
        
    def update(self):
        # Trigger movement system left
        self.state_machine.context.movement.move_left()
        if self.state_machine.context.movement.is_at_left_edge():
            return StateID.IDLE
        return super().update()

class WalkRightState(PetState):
    def __init__(self, sm):
        super().__init__(sm)
        self.id = StateID.WALK_RIGHT
        self.animation_name = "walk_right"
        
    def enter(self):
        super().enter()
        self.duration_frames = random.randint(3 * config.TARGET_FPS, 6 * config.TARGET_FPS)
        
    def update(self):
        # Trigger movement system right
        self.state_machine.context.movement.move_right()
        if self.state_machine.context.movement.is_at_right_edge():
            return StateID.IDLE
        return super().update()

class RollLeftState(PetState):
    def __init__(self, sm):
        super().__init__(sm)
        self.id = StateID.ROLL_LEFT
        self.animation_name = "roll_left"
        
    def enter(self):
        super().enter()
        self.duration_frames = random.randint(4 * config.TARGET_FPS, 7 * config.TARGET_FPS)
        
    def update(self):
        self.state_machine.context.movement.roll_left()
        if self.state_machine.context.movement.is_at_left_edge():
            return StateID.IDLE
        return super().update()

class RollRightState(PetState):
    def __init__(self, sm):
        super().__init__(sm)
        self.id = StateID.ROLL_RIGHT
        self.animation_name = "roll_right"
        
    def enter(self):
        super().enter()
        self.duration_frames = random.randint(4 * config.TARGET_FPS, 7 * config.TARGET_FPS)
        
    def update(self):
        self.state_machine.context.movement.roll_right()
        if self.state_machine.context.movement.is_at_right_edge():
            return StateID.IDLE
        return super().update()

class SleepState(PetState):
    def __init__(self, sm):
        super().__init__(sm)
        self.id = StateID.SLEEP
        self.animation_name = "sleep"
        self.duration_frames = 0 # Sleeps until interrupted
        
    def enter(self):
        super().enter()
        # Panda stays put — no drifting while asleep
        self.state_machine.context.movement.stop()

class DragState(PetState):
    def __init__(self, sm):
        super().__init__(sm)
        self.id = StateID.DRAG
        self.animation_name = "drag"
        self.duration_frames = 0 # Dragged until released

class FallState(PetState):
    def __init__(self, sm):
        super().__init__(sm)
        self.id = StateID.FALL
        self.animation_name = "fall"
        self.duration_frames = 0
        
    def update(self):
        # Check movement system if grounded
        if self.state_machine.context.movement.is_grounded():
            return StateID.IDLE
        self.state_machine.context.movement.fall()
        return super().update()

class TalkState(PetState):
    def __init__(self, sm):
        super().__init__(sm)
        self.id = StateID.TALK
    def enter(self):
        super().enter()
        self.duration_frames = int(3.0 * config.TARGET_FPS)

class EatState(PetState):
    def __init__(self, sm):
        super().__init__(sm)
        self.id = StateID.EAT
    def enter(self):
        super().enter()
        self.duration_frames = int(3.0 * config.TARGET_FPS)

class HappyState(PetState):
    def __init__(self, sm):
        super().__init__(sm)
        self.id = StateID.HAPPY
    def enter(self):
        super().enter()
        self.duration_frames = int(3.0 * config.TARGET_FPS)


# Add a simple mapping to get state instances
def get_all_states(sm):
    return {
        StateID.IDLE: IdleState(sm),
        StateID.WALK_LEFT: WalkLeftState(sm),
        StateID.WALK_RIGHT: WalkRightState(sm),
        StateID.SLEEP: SleepState(sm),
        StateID.DRAG: DragState(sm),
        StateID.FALL: FallState(sm),
        StateID.TALK: TalkState(sm),
        StateID.EAT: EatState(sm),
        StateID.HAPPY: HappyState(sm),
        StateID.ROLL_LEFT: RollLeftState(sm),
        StateID.ROLL_RIGHT: RollRightState(sm),
        StateID.STAY_CALM: StayCalmState(sm)
    }
