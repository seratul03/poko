import sys
import random
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, QPoint

import config
from src.utils.logger import get_logger
from src.pet.pet_window import PetWindow
from src.pet.states import StateID
from src.pet.state_machine import StateMachine, AppContext
from src.animations.asset_loader import load_animations
from src.animations.animator import Animator
from src.systems.movement import MovementSystem
from src.systems.save_system import SaveSystem
from src.systems.memory import MemorySystem
from src.systems.mood import MoodSystem
from src.systems.sleep import SleepSystem
from src.systems.mouse_tracking import MouseTrackingSystem
from src.systems.sound import SoundSystem
from src.ui.speech_bubble import SpeechBubble
from src.ui.settings_window import SettingsWindow
from src.ui.chat_window import ChatWindow
from src.ai.llm_chat import LLMChat

logger = get_logger(__name__)

# ── Idle dialogue pool ─────────────────────────────────────────────────────────
# Each entry is (activity_text, speech_text).  Either can be None to skip that bubble.
_IDLE_DIALOGUE: list[tuple[str | None, str | None]] = [
    ("*looks around curiously*",   "Do you ever feel like someone's watching you?"),
    ("*rolls around a little*",    "mhm~ so fluffy here on the desktop."),
    ("*sniffs the air*",           "Is that bamboo I smell? ...no. Just pixels. Sigh."),
    ("*stretches arms wide*",      "huff~ that nap was PERFECT."),
    ("*peeks at the taskbar*",     "What are all those apps doing down there?"),
    ("*yawns enormously*",         "nom... zzzz... wait I'm awake."),
    ("*sits very still*",          "I am meditating. Do not disturb."),
    ("*taps the screen*",          "Hello? Anyone in there?"),
    ("*does a little spin*",       "Wheee! ...okay I'm dizzy now."),
    (None,                         "Feed me. I know you have snacks."),
    (None,                         "Your cursor went by really fast just now."),
    ("*stares at your wallpaper*", "Nice wallpaper. Very roomy."),
    ("*flops onto side*",          "I'm not lazy. I'm conserving energy."),
    (None,                         "Did you know bamboo grows 90 cm a day? Just saying."),
    ("*rolls into a ball*",        "huff huff... okay that was enough exercise."),
]

_SLEEP_DIALOGUE: list[tuple[str | None, str | None]] = [
    ("*curls up tighter*",   "zzz... nom nom... bamboo dream..."),
    ("*snores softly*",      "zZzZz..."),
    ("*twitches an ear*",    "zzz... not now..."),
]

_HAPPY_DIALOGUE: list[tuple[str | None, str | None]] = [
    ("*bounces excitedly*",  "This is the BEST day ever!!"),
    ("*wiggles tail*",       "mhm mhm mhm~ so happy right now!"),
]

_SAD_DIALOGUE: list[tuple[str | None, str | None]] = [
    ("*droops ears*",        "...nobody feeds me anymore."),
    ("*sighs deeply*",       "huff... it's fine. I'm fine."),
]


class NekoApp:
    def __init__(self, app: QApplication):
        self.app = app
        logger.info("Initializing NekoApp")

        # 1. Initialize UI
        self.pet_window  = PetWindow()
        self.speech_bubble = SpeechBubble(self.pet_window)

        # 2. Initialize Data Systems
        self.save_system = SaveSystem()
        self.memory      = MemorySystem(self.save_system)
        self.mood        = MoodSystem(self.save_system)

        # 3. Initialize Animations
        animations   = load_animations()
        self.animator = Animator(animations)

        # 4. Initialize Hardware / External Systems
        self.mouse_tracking = MouseTrackingSystem()
        self.sound          = SoundSystem()

        # Apply initial settings
        settings_window_temp = SettingsWindow(None)
        initial_settings = settings_window_temp.settings
        self.sound.set_volume(initial_settings.get("volume", 50) / 100.0)

        # 5. Initialize AI
        self.ai = None
        if initial_settings.get("enable_ai", False):
            self.ai = LLMChat(self.memory)

        # 6. Initialize App Context and State Machine
        self.context                  = AppContext()
        self.context.movement         = MovementSystem(self.pet_window)
        self.context.animator         = self.animator
        self.context.mood             = self.mood
        self.context.sleep            = SleepSystem(None)
        self.context.memory           = self.memory
        self.context.sound            = self.sound
        self.context.ai               = self.ai
        self.context.speech_bubble    = self.speech_bubble
        self.context.pet_window       = self.pet_window
        self.context.mouse_tracking   = self.mouse_tracking

        self.state_machine = StateMachine(self.context)
        self.context.sleep.state_machine = self.state_machine

        self.pet_window.action_callback = self.handle_action

        # ── Main update loop ───────────────────────────────────────────────
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update)
        self.update_timer.start(config.FRAME_MS)

        # ── Random idle speech timer ───────────────────────────────────────
        # First idle dialogue fires between 15–30 seconds after startup
        self._idle_speech_timer = QTimer()
        self._idle_speech_timer.setSingleShot(True)
        self._idle_speech_timer.timeout.connect(self._speak_idle)
        self._schedule_next_idle_speech()

        # Lazy-loaded windows
        self.settings_window = None
        self.chat_window     = None

    # ── Idle speech scheduling ─────────────────────────────────────────────────

    def _schedule_next_idle_speech(self):
        """Schedule the next idle speech between 30 and 90 seconds from now."""
        delay_ms = random.randint(30_000, 90_000)
        self._idle_speech_timer.start(delay_ms)

    def _speak_idle(self):
        state = self.state_machine.current_state
        state_id = state.id if state else StateID.IDLE

        if state_id == StateID.SLEEP:
            pool = _SLEEP_DIALOGUE
        elif state_id == StateID.HAPPY:
            pool = _HAPPY_DIALOGUE
        elif self.mood.get_mood_state() in ("sad", "angry"):
            pool = _SAD_DIALOGUE
        else:
            pool = _IDLE_DIALOGUE

        activity_txt, speech_txt = random.choice(pool)

        messages = []
        if activity_txt:
            messages.append(activity_txt)
        if speech_txt:
            messages.append(speech_txt)

        if messages:
            self.speech_bubble.queue_messages(messages, duration_ms=5000)

        self._schedule_next_idle_speech()

    # ── Action handler ─────────────────────────────────────────────────────────

    def handle_action(self, action_name: str):
        if action_name == "feed":
            self.mood.feed()
            self.memory.increment_feed()
            self.sound.play("eat")
            self.context.sleep.reset_idle_timer()
            self.state_machine.change_state(StateID.EAT)
            self.speech_bubble.queue_messages([
                "*spots the food and waddles over*",
                "nom nom nom~ SO good!!",
            ])

        elif action_name == "pet":
            self.mood.pet()
            self.memory.increment_pet()
            self.sound.play("purr")
            self.context.sleep.reset_idle_timer()
            self.state_machine.change_state(StateID.HAPPY)
            self.speech_bubble.queue_messages([
                "*melts into a happy puddle*",
                "mhm~ right there... purrr~",
            ])

        elif action_name == "drag_start":
            self.state_machine.change_state(StateID.DRAG)
            self.context.sleep.reset_idle_timer()
            self.speech_bubble.queue_messages(["*flails dramatically*"])

        elif action_name == "drag_end":
            self.state_machine.change_state(StateID.FALL)
            self.speech_bubble.queue_messages([
                "*plummets*",
                "WAAAAAH—",
            ])

        elif action_name == "chat":
            if not self.chat_window:
                self.chat_window = ChatWindow(self.context)
            self.chat_window.show()
            self.chat_window.raise_()
            self.context.sleep.reset_idle_timer()
            
        elif action_name == "stay_calm":
            self.state_machine.change_state(StateID.STAY_CALM)
            self.context.sleep.reset_idle_timer()
            self.speech_bubble.queue_messages([
                "...",
                "*stares into your soul*"
            ])

        elif action_name == "settings":
            if not self.settings_window:
                self.settings_window = SettingsWindow(self.context)
            self.settings_window.show()
            self.settings_window.raise_()

    def run(self):
        logger.info("Running NekoApp")
        self.pet_window.show()

    def update(self):
        if self.mouse_tracking.check_and_reset_moving():
            self.context.sleep.reset_idle_timer()

        self.state_machine.update()
        self.context.movement.update()
        self.mood.update()
        self.context.sleep.update()
        self.save_system.update()
        self.animator.update()

        if self.state_machine.current_state:
            self.pet_window.set_state(self.state_machine.current_state.id.value)
            
        self.pet_window.mood_state = self.mood.get_mood_state()
        self.pet_window.update_pet()

        # ── Position speech bubble (clamped to screen) ─────────────────────
        bubble_x = self.pet_window.x() + (self.pet_window.width() - self.speech_bubble.width()) // 2
        bubble_y = self.pet_window.y() - self.speech_bubble.height() - 10

        if self.pet_window.screen():
            sg = self.pet_window.screen().availableGeometry()
            bubble_x = max(sg.left(), min(bubble_x, sg.right()  - self.speech_bubble.width()  + 1))
            bubble_y = max(sg.top(),  min(bubble_y, sg.bottom() - self.speech_bubble.height() + 1))

        self.speech_bubble.move(bubble_x, bubble_y)
