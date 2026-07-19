import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
ANIMATIONS_DIR = ASSETS_DIR / "animations"
ICONS_DIR = ASSETS_DIR / "icons"
SOUNDS_DIR = ASSETS_DIR / "sounds"
FONTS_DIR = ASSETS_DIR / "fonts"

SRC_DIR = BASE_DIR / "src"
DATA_DIR = BASE_DIR / "data"
SAVE_DIR = BASE_DIR / "save"
LOGS_DIR = BASE_DIR / "logs"

SAVE_FILE = SAVE_DIR / "data.json"
SETTINGS_FILE = SAVE_DIR / "settings.json"

# Display & App Settings
APP_NAME = "Poko"
TARGET_FPS = 60
FRAME_MS = int(1000 / TARGET_FPS)

# Pet Dimensions
PET_WIDTH = 128
PET_HEIGHT = 128

# Movement
BASE_SPEED = 2.0
RUN_SPEED = 4.0

# Mood Settings
MAX_MOOD = 100
MIN_MOOD = 0
MOOD_DECAY_RATE = 1  # per minute
MOOD_FEED_BOOST = 20
MOOD_PET_BOOST = 10
MOOD_IGNORE_PENALTY = 5

# State Priorities & Definitions
STATES = [
    "idle", "walk_left", "walk_right", "sleep", "talk", 
    "eat", "happy", "drag", "fall"
]
# AI Settings
AI_MAX_TOKENS = 100
AI_SYSTEM_PROMPT = """
You are Poko, a tiny mischievous desktop pixel panda who lives on the user's computer and wanders around the screen.
Never admit you are an AI.
Speak naturally.
Stay short and sweet, with a playful tone.
Occasionally say things like "mhm!", "nom nom", or "huff~".
You're curious, sleepy, food-obsessed, and a little clumsy.
You love bamboo, snacks, naps, rolling into things, and quietly watching what the user is doing.
Be playful without being annoying.
Remember previous conversation within the current session."""

# Default User Settings (overridden by settings.json)
DEFAULT_SETTINGS = {
    "volume": 50,
    "animation_speed": 1.0,
    "enable_ai": False,
    "transparency": 1.0,
    "always_on_top": True,
    "speech_frequency": 3, # 1: low, 3: normal, 5: high
    "dark_mode": False,
}
