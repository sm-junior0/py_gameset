"""Configuration constants for FarmQuest."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSET_ROOT = PROJECT_ROOT / "assets"
DATA_ROOT = Path(__file__).resolve().parent / "data"

REFERENCE_WIDTH = 1280
REFERENCE_HEIGHT = 720
TARGET_FPS = 60
GRAVITY = -2200.0
PLAYER_SPEED = 320.0
PLAYER_JUMP_SPEED = 860.0
PLAYER_RESPAWN_Y = -260.0
WORLD_WIDTH = 5600.0
GROUND_Y = 120.0

AUDIO_PATHS = {
    "theme": ASSET_ROOT / "audio" / "original_event_theme.ogg",
    "legacy_theme": ASSET_ROOT / "audio" / "original_theme.ogg",
    "jump": ASSET_ROOT / "audio" / "jump.wav",
    "seed": ASSET_ROOT / "audio" / "seed_collect.wav",
    "soil": ASSET_ROOT / "audio" / "soil_prepare.wav",
    "plant": ASSET_ROOT / "audio" / "planting.wav",
    "water": ASSET_ROOT / "audio" / "watering.wav",
    "growth": ASSET_ROOT / "audio" / "growth.wav",
    "harvest": ASSET_ROOT / "audio" / "harvest.wav",
    "mill": ASSET_ROOT / "audio" / "milling.wav",
    "cook": ASSET_ROOT / "audio" / "cooking.wav",
    "complete": ASSET_ROOT / "audio" / "completion.wav",
}
