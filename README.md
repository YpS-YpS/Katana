Katana Game Benchmark Automation Framework
Katana is a modular, extensible framework for automating game benchmarks. It provides a standardized approach to launching games, navigating to benchmark modes, executing benchmarks, and collecting results.

Features
Modular Architecture: Clean separation between detection, interaction, and game-specific logic
Extensible Design: Easy to add support for new games
Robust Detection: Advanced image recognition with retries and region-based matching
Standardized Results: Consistent result format across different games
Comprehensive Logging: Detailed logging with timestamps and emoji markers
Requirements
Python 3.8+
OpenCV
PyAutoGUI
PyGetWindow
Colorama
Installation
bash
# Clone the repository*
git clone https://github.com/intel-gaming/katana.git
cd katana

# Install dependencies
pip install -r requirements.txt
Usage
Command Line Interface
bash
# List available games
python -m katana.main --list

# Run CS2 benchmark with default settings
python -m katana.main --game cs2

# Run CS2 benchmark with custom settings
python -m katana.main --game cs2 --runs 5 --cooldown 60
Interactive Mode
If you don't provide command line arguments, Katana will prompt you interactively:

bash
python -m katana.main
As a Library
python
from katana.factory import GameFactory

# Create benchmark instance for CS2
benchmark = GameFactory.create_benchmark("cs2")

# Run benchmark series
results = benchmark.run_benchmark_series(run_count=3, cooldown=120)

# Access results
for result in results:
    print(f"Run {result.run_id}: {result.avg_fps} FPS")
Directory Structure
katana/
  ├── core/                 # Core framework components
  │   ├── benchmark.py      # Base benchmark class
  │   ├── detection.py      # Image recognition utilities
  │   └── interaction.py    # UI interaction utilities
  ├── games/                # Game-specific implementations
  │   ├── cs2/              # Counter-Strike 2
  │   │   ├── assets/       # Image assets for template matching
  │   │   ├── benchmark.py  # CS2-specific benchmark implementation
  │   │   └── config.py     # CS2-specific configuration
  │   └── ... (other games)
  ├── factory.py            # Factory for creating benchmark instances
  └── main.py               # Command line interface
Adding Support for New Games
To add support for a new game:

Create a new directory in katana/games/ named after your game (e.g., katana/games/valorant/)
Create an assets directory inside it for image assets
Create a config.py file with game-specific configuration
Create a benchmark.py file that implements the GameBenchmark interface
Add required image assets to the assets directory
See the CS2 implementation for a reference.

Result Format
Benchmark results are saved as JSON files in the results directory. Each run generates a JSON file with standardized fields:

json
{
  "game_id": "cs2",
  "run_id": 1,
  "timestamp": "20250509_123456",
  "duration": 60.5,
  "avg_fps": 120.3,
  "min_fps": 95.2,
  "max_fps": 145.8,
  "screenshot_path": "results/screenshots/cs2_benchmark_result_run1_20250509_123456.png",
  "raw_data": {}
}
Screenshots of benchmark results are saved in the results/screenshots directory.

License
Copyright © 2025 Intel Corporation. All rights reserved.

