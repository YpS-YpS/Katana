# Katana Game Benchmark Automation Framework

Katana is a modular, extensible framework for automating game benchmarks. It provides a standardized approach to launching games, navigating to benchmark modes, executing benchmarks, and collecting results.

## Features

- **Modular Architecture**: Clean separation between detection, interaction, and game-specific logic
- **Extensible Design**: Easy to add support for new games
- **Graphics Preset Management**: Support for customizable graphics settings presets
- **Resolution-Aware Detection**: Scale-invariant template matching for different resolutions
- **Robust Detection**: Advanced image recognition with retries and region-based matching
- **Standardized Results**: Consistent result format across different games
- **Comprehensive Logging**: Detailed logging with timestamps and emoji markers

## Requirements

- Python 3.8+
- OpenCV
- PyAutoGUI
- PyGetWindow
- Colorama
- Numpy

## Installation

```bash
# Clone the repository
git clone https://github.com/intel-gaming/katana.git
cd katana

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Command Line Interface

```bash
# List available games
python -m katana.main --list

# List available graphics presets for a game
python -m katana.main --game cs2 --list-presets

# Run benchmark with default settings
python -m katana.main --game cs2

# Run benchmark with a specific graphics preset
python -m katana.main --game cs2 --preset 1080p_high

# Run benchmark with custom parameters
python -m katana.main --game cs2 --runs 5 --cooldown 60 --preset 4k_high
```

### Interactive Mode

If you don't provide command line arguments, Katana will prompt you interactively:

```bash
python -m katana.main
```

### As a Library

```python
from katana.factory import GameFactory
from katana.core.presets import PresetManager
from katana.games.cs2.presets import CS2PresetAdapter

# Create preset manager
preset_manager = PresetManager()
preset_manager.register_adapter("cs2", CS2PresetAdapter())

# Apply a preset
preset_manager.apply_preset("cs2", "1080p_high")

# Create benchmark instance
benchmark = GameFactory.create_benchmark("cs2")

# Run benchmark series
results = benchmark.run_benchmark_series(run_count=3, cooldown=120)

# Access results
for result in results:
    print(f"Run {result.run_id}: {result.avg_fps} FPS")
```

## Directory Structure

```
katana/
  ├── core/                 # Core framework components
  │   ├── benchmark.py      # Base benchmark class
  │   ├── detection.py      # Image recognition utilities
  │   ├── interaction.py    # UI interaction utilities
  │   └── presets.py        # Graphics preset management
  ├── games/                # Game-specific implementations
  │   ├── cs2/              # Counter-Strike 2
  │   │   ├── assets/       # Image assets for template matching
  │   │   ├── benchmark.py  # CS2-specific benchmark implementation
  │   │   ├── config.py     # CS2-specific configuration
  │   │   └── presets.py    # CS2-specific preset adapter
  │   └── ... (other games)
  ├── presets/              # Graphics preset definitions
  │   ├── cs2/              # CS2 presets
  │   │   ├── presets.json  # Available presets definition
  │   │   ├── 1080p_high.json  # High settings at 1080p
  │   │   └── ... (other presets)
  │   └── ... (other games)
  ├── factory.py            # Factory for creating benchmark instances
  └── main.py               # Command line interface
```

## Graphics Presets

Katana supports customizable graphics presets to ensure consistent testing conditions:

1. **Preset Structure**: Each game has its own presets directory containing JSON files for different configurations
2. **Resolution Support**: Presets can define different resolutions (720p, 1080p, 1440p, 4K, etc.)
3. **Quality Levels**: Each resolution can have multiple quality levels (low, medium, high, ultra)
4. **Easy Configuration**: Create new presets by adding JSON files to the presets directory

### Example Preset File

```json
{
  "name": "1080p High Settings",
  "description": "1080p resolution with high quality settings",
  "setting.defaultres": 1920,
  "setting.defaultresheight": 1080,
  "setting.shaderquality": 1,
  "setting.r_texturefilteringquality": 5,
  "setting.msaa_samples": 8,
  "setting.videocfg_shadow_quality": 3,
  "setting.videocfg_texture_detail": 2,
  "setting.videocfg_particle_detail": 3
}
```

## Adding Support for New Games

To add support for a new game:

1. **Create Game Implementation**:
   - Create a new directory in `katana/games/` named after your game
   - Create an `assets` directory inside it for image assets
   - Create a `config.py` file with game-specific configuration
   - Create a `benchmark.py` file that implements the `GameBenchmark` interface
   - Create a `presets.py` file that extends the `PresetAdapter` class

2. **Define Presets**:
   - Create a new directory in `katana/presets/` named after your game
   - Create a `presets.json` file defining available presets
   - Create individual preset files for different resolutions and quality levels

3. **Register Preset Adapter**:
   - Update `get_preset_manager()` in `main.py` to register your new adapter

See the CS2 implementation for a reference.

## Result Format

Benchmark results are saved as JSON files in the `results` directory. Each run generates a JSON file with standardized fields:

```json
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
```

Screenshots of benchmark results are saved in the `results/screenshots` directory.

## License

Copyright © 2025 Intel Corporation. All rights reserved.