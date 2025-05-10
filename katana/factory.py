"""
Katana Game Benchmark Automation Framework - Game Factory

This module provides a factory for creating game benchmark instances.
"""
import logging
import importlib
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