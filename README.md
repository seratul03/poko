# Kitty

Kitty is a desktop virtual pet companion application built with Python and PySide6. The pet lives on your desktop, walks around, reacts to your mouse, has a mood system, and can optionally chat with you using the Gemini AI.

## Installation

1. Make sure you have Python 3.12+ installed.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up the `.env` file with your `GEMINI_API_KEY` (if you want to enable the AI chat feature).

## Running the Application

To start the pet:
```bash
python main.py
```

### Animations
The pet is beautifully drawn procedurally by code! No external image sequences are required anymore. Watch it squish, sleep, and look around naturally.


### Sounds (Optional)
Place `.wav` files in `assets/sounds/`:
- `meow.wav`
- `purr.wav`
- `eat.wav`
- `click.wav`

## Features

- **Mood System:** The pet's mood changes over time based on interaction.
- **Mouse Tracking:** The pet will follow or react to your mouse cursor.
- **Save System:** Pet stats and memory are saved automatically to `save/data.json`.
- **AI Chat:** Chat with your pet using Gemini (requires API key).
