"""
Katana Game Benchmark Automation Framework - CS2 Configuration

This module contains game-specific configuration for Counter-Strike 2 benchmarking.
"""

# Steam application ID for CS2
GAME_ID = "730"

# Game display name
GAME_NAME = "Counter-Strike 2"

# Window title to find and focus
WINDOW_TITLE = "Counter-Strike 2"

# Required image assets for template matching
REQUIRED_ASSETS = [
    "play_tab.png",
    "workshop_tab.png",
    "cs2_fps_benchmark.png",
    "go_button.png",
    "benchmark_first_frame.png",
    "benchmark_end_screen.png",
    "power_button.png",
    "quit_button.png"
]

# Configuration parameters
CONFIG = {
    "launcher": "steam",  # Game launcher to use
    "launch_wait_time": 40,  # Time to wait after launch before interaction
    "benchmark_map": "cs2_fps_benchmark",  # Name of benchmark map/mode
    "cooldown": 120,  # Default cooldown between runs in seconds
    "default_runs": 4,  # Default number of benchmark runs
    "template_threshold": 0.8,  # Default template matching threshold
    "template_timeout": 30,  # Default template detection timeout
    "process_name": "cs2.exe",  # Process name of the running game
    "steam_url": "steam://install/730",  # Steam protocol URL for direct installation
    "store_url": "https://store.steampowered.com/app/730/CounterStrike_2/",  # Web URL to the store page
}
