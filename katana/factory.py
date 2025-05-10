"""
Katana Game Benchmark Automation Framework - Game Factory

This module provides a factory for creating game benchmark instances.
"""
import logging
import importlib
import json
from pathlib import Path

logger = logging.getLogger("katana")

class GameFactory:
    """Factory for creating game benchmark instances"""
    
    @staticmethod
    def get_available_games():
        """Get list of available game implementations
        
        Returns:
            list: List of available game IDs
        """
        games_dir = Path(__file__).parent / "games"
        games = []
        
        for game_dir in games_dir.iterdir():
            if game_dir.is_dir() and (game_dir / "benchmark.py").exists():
                games.append(game_dir.name)
        
        return games
    
    @staticmethod
    def create_benchmark(game_id):
        """Create a benchmark instance for the specified game
        
        Args:
            game_id (str): ID of the game to benchmark
            
        Returns:
            GameBenchmark: Game-specific benchmark instance
        """
        game_id = game_id.lower()
        
        try:
            # Load game-specific benchmark module
            module_path = f"katana.games.{game_id}.benchmark"
            logger.info(f"🔍 Loading benchmark module: {module_path}")
            
            module = importlib.import_module(module_path)
            
            # Look for game-specific benchmark class
            class_name = f"{game_id.upper()}Benchmark"
            if not hasattr(module, class_name):
                # Try with title cased name
                class_name = f"{game_id.title()}Benchmark"
                
            if hasattr(module, class_name):
                benchmark_class = getattr(module, class_name)
                logger.info(f"✅ Found benchmark class: {class_name}")
            else:
                # Default: assume the benchmark class is the first class in the module
                for name, obj in module.__dict__.items():
                    if isinstance(obj, type) and "Benchmark" in name:
                        benchmark_class = obj
                        class_name = name
                        logger.info(f"✅ Found benchmark class: {class_name}")
                        break
                else:
                    raise ValueError(f"No benchmark class found in module {module_path}")
            
            # Create and return instance
            logger.info(f"🚀 Creating benchmark instance for {game_id}")
            return benchmark_class()
            
        except (ImportError, ModuleNotFoundError) as e:
            logger.error(f"❌ Failed to import benchmark module for game '{game_id}': {str(e)}")
            raise ValueError(f"Game '{game_id}' not supported or implementation not found")
        except Exception as e:
            logger.error(f"❌ Error creating benchmark for game '{game_id}': {str(e)}")
            raise
    
    @staticmethod
    def get_available_presets(game_id):
        """Get list of available graphics presets for a game
        
        Args:
            game_id (str): ID of the game
            
        Returns:
            dict: Dictionary of preset_id -> preset_name mappings
        """
        game_id = game_id.lower()
        presets_dir = Path(__file__).parent / "presets" / game_id
        
        if not presets_dir.exists():
            logger.warning(f"⚠️ No presets directory found for {game_id}")
            return {}
        
        # Look for presets.json file that defines available presets
        presets_file = presets_dir / "presets.json"
        if not presets_file.exists():
            logger.warning(f"⚠️ No presets.json found for {game_id}")
            return {}
        
        try:
            with open(presets_file, "r") as f:
                presets_data = json.load(f)
                return presets_data.get("presets", {})
        except Exception as e:
            logger.error(f"❌ Failed to load presets for {game_id}: {e}")
            return {}
    
    @staticmethod
    def get_preset_data(game_id, preset_id):
        """Get data for a specific graphics preset
        
        Args:
            game_id (str): ID of the game
            preset_id (str): ID of the preset
            
        Returns:
            dict: Preset configuration data
        """
        game_id = game_id.lower()
        preset_file = Path(__file__).parent / "presets" / game_id / f"{preset_id}.json"
        
        if not preset_file.exists():
            logger.error(f"❌ Preset file not found: {preset_file}")
            return {}
        
        try:
            with open(preset_file, "r") as f:
                preset_data = json.load(f)
                return preset_data
        except Exception as e:
            logger.error(f"❌ Failed to load preset data: {e}")
            return {}
    
    @staticmethod
    def apply_preset(game_id, preset_id, benchmark=None):
        """Apply a graphics preset to a game
        
        Args:
            game_id (str): ID of the game
            preset_id (str): ID of the preset
            benchmark (GameBenchmark, optional): Benchmark instance
            
        Returns:
            bool: True if preset was applied successfully
        """
        # Get preset data
        preset_data = GameFactory.get_preset_data(game_id, preset_id)
        if not preset_data:
            return False
        
        # If a benchmark instance is provided, try to use it
        if benchmark:
            # Check if the benchmark has a method to apply presets
            if hasattr(benchmark, 'apply_preset'):
                return benchmark.apply_preset(preset_data)
        
        # Otherwise, try to load game-specific preset module
        try:
            preset_module_path = f"katana.games.{game_id}.presets"
            preset_module = importlib.import_module(preset_module_path)
            
            # Look for apply_preset function
            if hasattr(preset_module, 'apply_preset'):
                return preset_module.apply_preset(preset_data)
            
            logger.error(f"❌ No apply_preset function found in {preset_module_path}")
            return False
            
        except (ImportError, ModuleNotFoundError):
            logger.error(f"❌ No preset module found for {game_id}")
            return False
        except Exception as e:
            logger.error(f"❌ Error applying preset: {e}")
            return False