"""
Katana Game Benchmark Automation Framework - CS2 Benchmark Implementation

This module implements the CS2-specific benchmark workflow.
"""
import time
import logging
import pyautogui
from pathlib import Path

from ...core.benchmark import GameBenchmark, BenchmarkResult
from ...core.detection import ImageDetector
from ...core.interaction import GameInteractor
from .config import GAME_ID, GAME_NAME, WINDOW_TITLE, REQUIRED_ASSETS, CONFIG

logger = logging.getLogger("katana")

class CS2Benchmark(GameBenchmark):
    """Counter-Strike 2 benchmark implementation"""
    
    def __init__(self):
        """Initialize the CS2 benchmark"""
        super().__init__(
            game_id=GAME_ID,
            game_name=GAME_NAME,
            window_title=WINDOW_TITLE,
            configs=CONFIG
        )
        
        # Set the correct assets directory path
        self.assets_dir = Path(__file__).parent / "assets"
        
        # Initialize detector and interactor
        self.detector = ImageDetector(self.assets_dir)
        self.interactor = GameInteractor(self.assets_dir, self.detector)
        
        # Verify required assets
        self.check_assets(REQUIRED_ASSETS)
        
    def focus_game_window(self):
        """Focus the CS2 window"""
        return self.interactor.focus_window(self.window_title)
    
    def wait_until_ready(self):
        """Wait until CS2 main screen is ready"""
        logger.info("⏳ Waiting for CS2 main screen to appear...")
        
        # Press ESC a couple times to close any dialogs
        self.interactor.press_key('esc', presses=3, interval=1)
        
        # Wait for Play tab to appear
        found = self.detector.wait_for_template(
            "play_tab.png", 
            timeout=CONFIG.get("template_timeout", 40)
        )
        
        if found:
            logger.info("✅ Main screen detected")
            return True
        else:
            logger.error("❌ Main screen not detected within timeout")
            return False
    
    def navigate_to_benchmark(self):
        """Navigate to the CS2 benchmark map"""
        logger.info("🧭 Navigating to CS2 benchmark map...")
        
        # Step 1: Click Play tab
        logger.info("🧭 [Step 1] Clicking PLAY tab")
        play_clicked = self.interactor.click_template_with_retry("play_tab.png")
        if not play_clicked:
            logger.error("❌ Failed to click PLAY tab")
            return False
        
        # Step 2: Click Workshop tab
        logger.info("🧱 [Step 2] Looking for Workshop Maps tab")
        workshop_found = self.detector.wait_for_template(
            "workshop_tab.png", 
            timeout=20, 
            check_interval=2
        )
        
        if workshop_found:
            self.interactor.click_template("workshop_tab.png")
        else:
            logger.error("❌ Workshop tab not found")
            return False
        
        # Step 3: Select the benchmark map
        logger.info("🗺️ [Step 3] Selecting CS2 FPS Benchmark map")
        benchmark_found = self.detector.wait_for_template(
            "cs2_fps_benchmark.png", 
            timeout=20, 
            check_interval=2
        )
        
        if benchmark_found:
            self.interactor.click_template("cs2_fps_benchmark.png")
        else:
            logger.error("❌ CS2 FPS Benchmark map not found")
            return False
        
        return True
    
    def start_benchmark(self):
        """Start the benchmark execution"""
        logger.info("🎯 Starting benchmark execution...")
        
        # Click the GO button
        go_found = self.detector.wait_for_template(
            "go_button.png", 
            timeout=15, 
            check_interval=2
        )
        
        if go_found:
            self.interactor.click_template("go_button.png")
        else:
            logger.error("❌ GO button not found")
            return False
        
        # Wait for benchmark to visually begin
        logger.info("🧠 Waiting for benchmark to visually begin...")
        benchmark_started = self.detector.wait_for_template(
            "benchmark_first_frame.png", 
            timeout=20, 
            check_interval=1
        )
        
        if benchmark_started:
            self.benchmark_start_time = time.time()
            logger.info("✅ Visual benchmark start confirmed")
            return True
        else:
            logger.error("❌ Failed to detect benchmark start frame")
            return False
    
    def collect_results(self, run_id=0):
        """Collect benchmark results
        
        Args:
            run_id (int): ID of the current benchmark run
            
        Returns:
            BenchmarkResult: Container with benchmark results
        """
        logger.info(f"📥 [Run {run_id}] Capturing benchmark results...")
        
        # Create result container
        result = BenchmarkResult(self.game_id, run_id)
        
        # For run_id=0 (dry run), wait for benchmark end screen
        if run_id == 0:
            benchmark_end = self.detector.wait_for_template(
                "benchmark_end_screen.png", 
                timeout=124, 
                check_interval=3
            )
            
            if benchmark_end:
                self.benchmark_end_time = time.time()
                duration = self.benchmark_end_time - self.benchmark_start_time
                self.benchmark_duration = duration
                
                logger.info(f"⏱️ [Run {run_id}] Benchmark duration: {duration:.2f} seconds")
                result.duration = duration
                
                # Wait a moment for results to display fully
                time.sleep(12)
                
                # Take screenshot of results
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                screenshot_path = self.interactor.take_screenshot(
                    f"cs2_benchmark_result_run{run_id}_{timestamp}.png"
                )
                result.screenshot_path = screenshot_path
                
            else:
                logger.error(f"❌ [Run {run_id}] End screen not detected. Cannot measure duration.")
                return None
        
        # For subsequent runs, use known duration from dry run
        else:
            if not hasattr(self, 'benchmark_duration') or self.benchmark_duration is None:
                logger.error(f"❌ [Run {run_id}] Known duration not available. Cannot continue.")
                return None
            
            known_duration = self.benchmark_duration
            
            logger.info(f"📥 [Run {run_id}] Timed collection: sleeping for {known_duration:.2f}s + 7s buffer...")
            time.sleep(known_duration + 12)
            
            # Here you could add code to capture performance metrics with external tools
            # For example: PresentMon, FRAPS, etc.
            # TODO: Implement integration with performance monitoring tools
            
            # Take screenshot of results
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            screenshot_path = self.interactor.take_screenshot(
                f"cs2_benchmark_result_run{run_id}_{timestamp}.png"
            )
            result.screenshot_path = screenshot_path
            result.duration = known_duration
        
        return result
    
    def teardown(self):
        """Clean up after benchmark completion"""
        logger.info("🧹 Initiating CS2 shutdown sequence...")
        
        # Give time for any final screens to display
        time.sleep(10)
        
        # Toggle console off with ~ key
        logger.info("🗙 Toggling console off...")
        self.interactor.press_key('`')
        time.sleep(1)
        
        # Click on power button to open exit menu
        logger.info("🔋 Clicking the power icon...")
        time.sleep(3)
        
        power_found = self.detector.wait_for_template(
            "power_button.png", 
            timeout=10
        )
        
        if power_found:
            self.interactor.click_template("power_button.png")
            time.sleep(2)
        else:
            logger.warning("⚠️ Power button not found")
        
        # Click Quit button to exit CS2
        logger.info("🚪 Clicking Quit to exit CS2...")
        
        quit_found = self.detector.wait_for_template(
            "quit_button.png", 
            timeout=10
        )
        
        if quit_found:
            self.interactor.click_template("quit_button.png")
            logger.info("✅ CS2 exited")
        else:
            logger.warning("⚠️ Quit button not found. You may need to exit manually.")
            
            # Try to force close with Alt+F4
            logger.info("🔄 Trying to force exit with Alt+F4...")
            pyautogui.hotkey('alt', 'f4')
        
        # Wait for the game to fully close
        time.sleep(5)
        return True