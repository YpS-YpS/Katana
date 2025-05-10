"""
Katana Game Benchmark Automation Framework - Core Interaction Module

This module provides user interface interaction capabilities using PyAutoGUI.
It includes functions for clicking, typing, and other interactions.
"""
import pyautogui
import pygetwindow as gw
import time
import logging
from pathlib import Path
from .detection import ImageDetector

logger = logging.getLogger("katana")

# Configure PyAutoGUI for safety
pyautogui.FAILSAFE = True  # Move mouse to corner to abort
pyautogui.PAUSE = 0.1  # Small pause between PyAutoGUI actions

class GameInteractor:
    """Class for interacting with game UI elements"""
    
    def __init__(self, assets_dir=None, detector=None):
        """Initialize the interactor
        
        Args:
            assets_dir (Path, optional): Directory containing image assets
            detector (ImageDetector, optional): Image detector instance to use
        """
        self.assets_dir = Path(assets_dir) if assets_dir else None
        self.detector = detector or ImageDetector(assets_dir)
    
    def focus_window(self, window_title):
        """Focus a window by its title
        
        Args:
            window_title (str): Title of the window to focus
            
        Returns:
            bool: True if window was focused, False otherwise
        """
        logger.info(f"🪟 Trying to focus window: '{window_title}'")
        
        # Look for any window containing the title
        windows = gw.getWindowsWithTitle(window_title)
        
        if not windows:
            logger.error(f"❌ No window with title '{window_title}' found")
            return False
        
        try:
            # Use the first window found
            window = windows[0]
            window.activate()
            time.sleep(1)  # Wait for window to become active
            
            # Confirm if the window became active
            if window.isActive:
                logger.info(f"✅ Window '{window_title}' is now active")
                return True
            else:
                logger.warning(f"⚠️ Tried to activate '{window_title}', but it's not in focus")
                return False
        except Exception as e:
            logger.error(f"⚠️ Window activation error: {e}")
            return False
    
    def click(self, x, y, button='left', clicks=1, interval=0.0, duration=0.25):
        """Click at the specified coordinates
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            button (str): Mouse button ('left', 'middle', 'right')
            clicks (int): Number of clicks
            interval (float): Time between clicks in seconds
            duration (float): Move duration in seconds
            
        Returns:
            bool: True if click was performed
        """
        logger.info(f"🖱️ Clicking at ({x}, {y}) with {button} button")
        
        try:
            pyautogui.moveTo(x, y, duration=duration)
            pyautogui.click(x=x, y=y, button=button, clicks=clicks, interval=interval)
            time.sleep(0.5)  # Wait for click to register
            return True
        except Exception as e:
            logger.error(f"❌ Click failed: {e}")
            return False
    
    def click_template(self, template_path, threshold=0.8, region=None, wait_disappear=False, 
                      disappear_timeout=10, click_offset=(0, 0), **click_kwargs):
        """Find and click on a template image
        
        Args:
            template_path (str): Path to template image
            threshold (float): Confidence threshold (0.0-1.0)
            region (tuple, optional): Region to search in (left, top, width, height)
            wait_disappear (bool): Whether to wait for template to disappear after click
            disappear_timeout (int): Timeout for template to disappear in seconds
            click_offset (tuple): (x, y) offset from template center to click
            **click_kwargs: Additional arguments for click method
            
        Returns:
            bool: True if template was found and clicked, False otherwise
        """
        template_path = Path(template_path)
        logger.info(f"🖱️ Searching and clicking: {template_path.name}")
        
        # Find the template
        match = self.detector.find_template(template_path, threshold=threshold, region=region)
        
        if not match:
            logger.error(f"❌ Failed to find template: {template_path.name}")
            return False
        
        # Apply click offset
        x, y = match
        x += click_offset[0]
        y += click_offset[1]
        
        # Perform the click
        success = self.click(x, y, **click_kwargs)
        
        # Wait for template to disappear if requested
        if success and wait_disappear:
            start_time = time.time()
            logger.info(f"⏳ Waiting for {template_path.name} to disappear...")
            
            while time.time() - start_time < disappear_timeout:
                if self.detector.find_template(template_path, threshold=threshold, region=region) is None:
                    logger.info(f"✅ Template {template_path.name} disappeared after click")
                    return True
                time.sleep(0.5)
            
            logger.warning(f"⚠️ Template {template_path.name} did not disappear after click")
        
        return success
    
    def click_template_with_retry(self, template_path, max_retries=3, **kwargs):
        """Find and click on a template with retries
        
        Args:
            template_path (str): Path to template image
            max_retries (int): Maximum number of retry attempts
            **kwargs: Additional arguments for click_template method
            
        Returns:
            bool: True if template was found and clicked, False otherwise
        """
        template_path = Path(template_path)
        
        for attempt in range(max_retries + 1):
            if attempt > 0:
                logger.info(f"🔄 Retry attempt {attempt}/{max_retries} for clicking {template_path.name}")
            
            result = self.click_template(template_path, **kwargs)
            if result:
                return True
            
            if attempt < max_retries:
                time.sleep(1)  # Wait before retrying
        
        logger.error(f"❌ Failed to click {template_path.name} after {max_retries + 1} attempts")
        return False
    
    def type_text(self, text, interval=0.05):
        """Type text with the keyboard
        
        Args:
            text (str): Text to type
            interval (float): Time between keypresses in seconds
            
        Returns:
            bool: True if typing was performed
        """
        logger.info(f"⌨️ Typing: {text}")
        
        try:
            pyautogui.write(text, interval=interval)
            return True
        except Exception as e:
            logger.error(f"❌ Typing failed: {e}")
            return False
    
    def press_key(self, key, presses=1, interval=0.1):
        """Press a keyboard key
        
        Args:
            key (str): Key to press (e.g., 'enter', 'esc', 'f1')
            presses (int): Number of presses
            interval (float): Time between presses in seconds
            
        Returns:
            bool: True if key press was performed
        """
        logger.info(f"⌨️ Pressing key: {key} ({presses} times)")
        
        try:
            pyautogui.press(key, presses=presses, interval=interval)
            return True
        except Exception as e:
            logger.error(f"❌ Key press failed: {e}")
            return False
    
    def take_screenshot(self, filename=None, region=None):
        """Take a screenshot and save it to file
        
        Args:
            filename (str, optional): Filename to save screenshot to
            region (tuple, optional): Region to capture (left, top, width, height)
            
        Returns:
            str: Path to the saved screenshot
        """
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
        
        try:
            screenshot_path = Path("results/screenshots") / filename
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            
            pyautogui.screenshot(str(screenshot_path), region=region)
            logger.info(f"📸 Screenshot saved to: {screenshot_path}")
            return str(screenshot_path)
        except Exception as e:
            logger.error(f"❌ Screenshot failed: {e}")
            return None