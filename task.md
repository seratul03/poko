# MASTER PROMPT — Build a Desktop AI Pet (Production Quality)

You are an expert Python software engineer, UI/UX designer, game developer, and software architect.

Your task is to build an entire desktop application from scratch.

Do NOT make a prototype.

Do NOT make placeholder code.

Do NOT leave TODOs.

Do NOT simplify unless absolutely necessary.

Every feature must be production-quality, modular, maintainable, and documented.

---

# Project Name

NekoDesk

A desktop virtual pet inspired by old desktop companions.

The application should run as a lightweight desktop application where a pixel-art cat lives on the user's desktop, walks around, sleeps, reacts to the mouse, talks, has moods, remembers interactions, and can optionally chat using Gemini.

The application should feel alive.

The codebase must be structured as if it will become an open-source project.

---

# Primary Goals

The pet should:

• Live on the desktop
• Always stay visible
• Have transparent background
• No window border
• Click-through disabled
• Stay above normal windows
• Be draggable
• Consume minimal RAM and CPU
• Run smoothly at 60 FPS

---

# Technology

Language

Python 3.12+

Framework

PySide6

Libraries

PySide6
Pillow
pynput
requests
google-generativeai
python-dotenv
pygame (only if absolutely necessary for sound)

Never use Tkinter.

Never use global variables.

---

# Architecture

Use OOP.

Use SOLID principles.

Keep every system independent.

Project structure should look like:

```text
NekoDesk/

main.py

config.py

requirements.txt

README.md

.env

assets/

animations/

icons/

sounds/

fonts/

src/

core/

pet/

ai/

ui/

animations/

systems/

utils/

data/

save/

logs/

tests/
```

Everything should have proper classes.

No massive files.

Each file should ideally remain under 300 lines.

---

# Systems To Build

The application should contain the following systems.

Animation System

State Machine

Movement System

Mood System

Memory System

Dialogue System

Mouse Tracking System

Sleep System

AI Chat System

Save System

Sound System

Configuration System

Speech Bubble System

Notification System

Asset Loader

Logging System

Settings Window

---

# Pet States

Implement a finite state machine.

Possible states

Idle

Walking Left

Walking Right

Sleeping

Yawning

Stretching

Talking

Following Mouse

Eating

Happy

Sad

Angry

Excited

Dragging

Falling

Thinking

Each state should define

Animation

Movement speed

Allowed transitions

Interrupt rules

Priority

---

# Animation System

Every animation must support

Frame timing

Looping

One-shot animations

Interruptible animations

Priority animations

Animation queue

Animation blending if possible

Support PNG frame folders.

Example

idle/

frame0.png

frame1.png

frame2.png

walk_left/

walk_right/

sleep/

eat/

angry/

happy/

talk/

etc.

---

# Movement

The pet should

Randomly wander

Pause randomly

Turn around naturally

Bounce from screen edges

Never leave the visible screen

Acceleration should feel natural.

Walking speed should not be constant.

Randomize

Speed

Duration

Waiting time

Direction

---

# Idle Behaviour

If nothing happens

Pet randomly

Looks around

Yawns

Scratches itself

Sits

Sleeps

Lies down

Random idle actions should occur.

---

# Sleep System

After inactivity

Pet falls asleep.

Sleeping animation loops.

Mouse click wakes pet.

Dragging wakes pet.

Speech wakes pet.

---

# Mood System

Mood value

0–100

Mood slowly changes.

Mood affected by

Petting

Ignoring

Feeding

Talking

Random events

Mood levels

Very Happy

Happy

Neutral

Bored

Sad

Angry

Mood influences

Movement

Dialogue

Animation frequency

Expressions

---

# Feeding System

User can

Right-click pet

Open menu

Choose

Fish

Milk

Cookie

Chicken

Treat

Pet walks to food.

Eating animation.

Mood increases.

Food disappears.

---

# Mouse Interaction

Pet notices mouse.

Sometimes

Looks at cursor

Runs toward cursor

Follows cursor briefly

Gets scared if cursor moves too quickly

Random curiosity behaviour.

---

# Speech Bubble

Speech bubble above pet.

Rounded rectangle.

Pixel font.

Fade in.

Fade out.

Typing animation.

Random dialogue.

Examples

Good morning.

Working again?

Need coffee?

Feed me.

I saw your cursor.

I like this wallpaper.

I'm sleepy.

Don't close me.

---

# Memory System

Pet remembers

How many days installed

Feed count

Pet count

Ignored count

Conversations

Favorite food

Last interaction

Current mood

Everything saved in JSON.

Automatically loaded.

---

# Save System

Auto-save every minute.

Save on exit.

Load automatically.

Never lose progress.

---

# Sound

Support

Meow

Purr

Sleep

Eat

Click

Happy

Angry

Volume control.

Mute option.

---

# AI Chat

Create a small chat window.

Chat icon opens panel.

User types.

Pet responds.

Gemini API.

Prompt

"You are a tiny mischievous desktop pixel cat.

Never admit you are an AI.

Speak naturally.

Maximum three short sentences.

Occasionally meow.

Be playful.

Remember previous conversation within current session."

Store API key in .env.

---

# Settings Window

Options

Volume

Animation speed

Enable AI

Transparency

Always on top

Language

Speech frequency

Mood decay speed

FPS

Dark mode

Reset pet

Export save

Import save

---

# Configuration

Everything configurable through config.py.

Never hardcode values.

---

# Asset Loader

Automatically discovers animations.

No manual registration.

If folder exists

Load animation.

If missing

Show warning.

Continue running.

---

# Logging

Create logs folder.

Log

Errors

Warnings

Startup

Shutdown

Loaded assets

Performance

Save events

---

# Performance

Target

RAM

<150 MB

CPU

<3% while idle

Smooth animation

No blocking operations.

Use background threads where appropriate.

Never freeze UI.

---

# UI

Pixel aesthetic.

Rounded speech bubbles.

Smooth fading.

Subtle shadows.

Simple settings panel.

No ugly widgets.

---

# Error Handling

Application must never crash because

Animation missing

Image missing

API unavailable

Network unavailable

Corrupt save

Invalid config

Handle everything gracefully.

---

# Documentation

Generate

README.md

Installation guide

Requirements

How to add animations

How to add sounds

How to create skins

How to enable Gemini

Project architecture

---

# Code Quality

Every class documented.

Every function typed.

Use dataclasses where useful.

Avoid duplicated code.

Use enums.

Use constants.

Follow PEP8.

---

# Future Extensibility

Architecture should support future additions without major rewrites.

Possible future features

Multiple pets

Inventory

Mini games

Achievements

Weather awareness

Music reactions

VS Code companion mode

Discord Rich Presence

Calendar reminders

Voice recognition

Different animal skins

Plugin system

Marketplace for skins

Online sharing

---

# Final Deliverable

Generate the complete application.

Do not merely explain the implementation.

Write the actual code.

Create every required file.

Generate every module.

Create requirements.txt.

Create README.md.

Generate placeholder assets where necessary.

Ensure the project runs after installing dependencies.

The final result should feel like a polished desktop companion application rather than a coding exercise.
