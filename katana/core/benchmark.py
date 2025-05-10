"""
Katana Game Benchmark Automation Framework - Core Benchmark Module

This module provides the base class for all game benchmark implementations.
It defines the common interface and default behaviors that specific game
benchmark classes should implement or override.
"""
import time
import subprocess
from pathlib import Path
import logging
from abc import ABC, abstractmethod

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("katana_benchmark.log")
    ]
)
logger = logging.getLogger("katana")

class BenchmarkResult:
    """Container for benchmark results with standardized format"""
    
    def __init__(self, game_id, run_id):
        """Initialize a new benchmark result container"""
        self.game_id = game_id
        self.run_id = run_id
        self.timestamp = time.strftime("%Y%m%d_%H%M%S")
        self.duration = None
        self.avg_fps = None
        self.min_fps = None
        self.max_fps = None
        self.screenshot_path = None
        self.raw_data = {}
    
    def to_json(self):
        """Convert results to JSON format"""
        import json
        return json.dumps({
            "game_id": self.game_id,
            "run_id": self.run_id,
            "timestamp": self.timestamp,
            "duration": self.duration,
            "avg_fps": self.avg_fps,
            "min_fps": self.min_fps,
            "max_fps": self.max_fps,
            "screenshot_path": str(self.screenshot_path) if self.screenshot_path else None,
            "raw_data": self.raw_data
        }, indent=2)
    
    def save(self, output_dir=None):
        """Save results to file"""
        output_dir = output_dir or Path("results")
        output_dir.mkdir(exist_ok=True, parents=True)
        
        result_path = output_dir / f"{self.game_id}_run{self.run_id}_{self.timestamp}.json"
        with open(result_path, "w") as f:
            f.write(self.to_json())
        
        logger.info(f"✅ Results saved to: {result_path}")
        return result_path

class GameBenchmark(ABC):
    """Base class for all game benchmark implementations"""
    
    def __init__(self, game_id, game_name, window_title=None, assets_dir=None, configs=None):
        """Initialize the benchmark with game-specific parameters
        
        Args:
            game_id (str): Unique identifier for the game (e.g., Steam app ID)
            game_name (str): Human-readable name of the game
            window_title (str, optional): Window title for focusing
            assets_dir (Path, optional): Directory containing image assets
            configs (dict, optional): Additional configuration parameters
        """
        self.game_id = game_id
        self.game_name = game_name
        self.window_title = window_title or game_name
        self.assets_dir = Path(assets_dir) if assets_dir else Path(__file__).parent.parent / "games" / game_id.lower() / "assets"
        self.configs = configs or {}
        self.results = []
        self.benchmark_start_time = None
        self.benchmark_end_time = None
        self.benchmark_duration = None
        
        # Ensure assets directory exists
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        
        # Create screenshot directory
        self.screenshot_dir = Path("results/screenshots")
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"🎮 Initialized {self.game_name} benchmark")
    
    def check_assets(self, required_assets):
        """Verify all required image assets exist
        
        Args:
            required_assets (list): List of required asset filenames
            
        Returns:
            bool: True if all assets exist, False otherwise
        """
        missing = [f for f in required_assets if not (self.assets_dir / f).is_file()]
        if missing:
            logger.error(f"❌ Missing asset files:")
            for f in missing:
                logger.error(f" - {f}")
            logger.error(f"📂 Please place all assets in: {self.assets_dir.resolve()}")
            return False
        logger.info(f"✅ All required assets found in {self.assets_dir}")
        return True
    
    def launch_steam_game(self):
        """Launch the game via Steam"""
        logger.info(f"🚀 Launching {self.game_name} via Steam (ID: {self.game_id})...")
        subprocess.Popen(['start', f'steam://rungameid/{self.game_id}'], shell=True)
        # Wait for game to start (adjustable in subclasses)
        time.sleep(self.configs.get("launch_wait_time", 30))
    
    def launch(self):
        """Launch the game - default uses Steam"""
        launcher = self.configs.get("launcher", "steam")
        if launcher == "steam":
            return self.launch_steam_game()
        else:
            logger.error(f"❌ Unsupported launcher: {launcher}")
            raise NotImplementedError(f"Launcher '{launcher}' not implemented")
    
    @abstractmethod
    def focus_game_window(self):
        """Focus the game window - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    def wait_until_ready(self):
        """Wait until the game is ready for interaction"""
        pass
    
    @abstractmethod
    def navigate_to_benchmark(self):
        """Navigate through game menus to the benchmark"""
        pass
    
    @abstractmethod
    def start_benchmark(self):
        """Start the benchmark execution"""
        pass
    
    @abstractmethod
    def collect_results(self, run_id=0):
        """Collect benchmark results
        
        Args:
            run_id (int): ID of the current benchmark run
            
        Returns:
            BenchmarkResult: Container with benchmark results
        """
        pass
    
    @abstractmethod
    def teardown(self):
        """Clean up after benchmark completion"""
        pass
    
    def execute_benchmark_run(self, run_id=0, is_dry_run=False):
        """Execute a complete benchmark run
        
        Args:
            run_id (int): ID of the current benchmark run
            is_dry_run (bool): Whether this is a dry run
            
        Returns:
            BenchmarkResult: Container with benchmark results
        """
        try:
            logger.info(f"📊 ===== Starting Run {run_id} {'(Dry Run)' if is_dry_run else ''} =====")
            
            self.launch()
            self.focus_game_window()
            self.wait_until_ready()
            self.navigate_to_benchmark()
            self.start_benchmark()
            
            result = self.collect_results(run_id)
            
            if is_dry_run and hasattr(self, 'benchmark_duration'):
                logger.info(f"⏱️ Measured benchmark duration: {self.benchmark_duration:.2f} seconds")
            
            self.teardown()
            
            if result:
                self.results.append(result)
                result.save()
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error during benchmark run {run_id}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def run_benchmark_series(self, run_count=3, cooldown=120):
        """Run a series of benchmark tests
        
        Args:
            run_count (int): Number of benchmark runs to perform
            cooldown (int): Cooldown time between runs in seconds
            
        Returns:
            list: List of BenchmarkResult objects
        """
        logger.info(f"📦 ======= Starting {self.game_name} Benchmark Series ========")
        logger.info(f"📌 Config -> Total Runs: {run_count}, Cooldown: {cooldown}s")
        
        # Run 0: Dry run for duration discovery
        logger.info("\n⏱️ ===== Starting Run 0 (Duration Measurement) =====")
        dry_run_result = self.execute_benchmark_run(run_id=0, is_dry_run=True)
        
        if not hasattr(self, 'benchmark_duration') or self.benchmark_duration is None:
            logger.error("❌ Failed to determine benchmark duration in dry run")
            return self.results
        
        known_duration = self.benchmark_duration
        logger.info(f"🧊 Cooling down for {cooldown} seconds...\n")
        time.sleep(cooldown)
        
        # Subsequent benchmark runs
        for i in range(1, run_count + 1):
            self.execute_benchmark_run(run_id=i, is_dry_run=False)
            
            if i < run_count:
                logger.info(f"🧊 Cooling down for {cooldown} seconds...\n")
                time.sleep(cooldown)
        
        logger.info(f"✅ All {run_count} runs completed for {self.game_name}.\n")
        return self.results