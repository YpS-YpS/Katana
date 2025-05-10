"""
Katana Game Benchmark Automation Framework - Core Detection Module

This module provides image recognition capabilities using OpenCV.
It includes functions for template matching with various strategies
and reliability improvements like retries and regional matching.
"""
import cv2
import numpy as np
import pyautogui
import time
import logging
from pathlib import Path

logger = logging.getLogger("katana")

class ImageDetector:
    """Class for detecting UI elements using template matching"""
    
    def __init__(self, assets_dir=None):
        """Initialize the detector
        
        Args:
            assets_dir (Path, optional): Directory containing image assets
        """
        self.assets_dir = Path(assets_dir) if assets_dir else None
    
    def take_screenshot(self, region=None):
        """Take a screenshot and convert it to OpenCV format
        
        Args:
            region (tuple, optional): Region to capture (left, top, width, height)
            
        Returns:
            numpy.ndarray: Screenshot as OpenCV BGR image
        """
        if region:
            screen = pyautogui.screenshot(region=region)
        else:
            screen = pyautogui.screenshot()
        return cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)
    
    def find_template(self, template_path, threshold=0.8, region=None):
        """Find a template image on the screen
        
        Args:
            template_path (str): Path to template image
            threshold (float): Confidence threshold (0.0-1.0)
            region (tuple, optional): Region to search in (left, top, width, height)
            
        Returns:
            tuple or None: (x, y) coordinates of match center if found, None otherwise
        """
        template_path = Path(template_path)
        if not template_path.is_file():
            if self.assets_dir and (self.assets_dir / template_path).is_file():
                template_path = self.assets_dir / template_path
            else:
                logger.error(f"❌ Template not found: {template_path}")
                return None
        
        # Take screenshot and prepare for matching
        screen = self.take_screenshot(region)
        template = cv2.imread(str(template_path))
        
        # Check if template dimensions are larger than screenshot
        if template.shape[0] > screen.shape[0] or template.shape[1] > screen.shape[1]:
            logger.error(f"❌ Template {template_path.name} ({template.shape[:2]}) is larger than screenshot ({screen.shape[:2]})")
            return None
        
        # Perform template matching
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        
        # Check if match confidence is above threshold
        if max_val >= threshold:
            # Calculate center of the match
            h, w = template.shape[:2]
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            
            # If search was in a region, adjust coordinates
            if region:
                center_x += region[0]
                center_y += region[1]
            
            logger.info(f"✅ Match found for {template_path.name} at ({center_x}, {center_y}) with confidence {max_val:.2f}")
            return center_x, center_y
        else:
            logger.warning(f"⚠️ No match found for {template_path.name} (max confidence {max_val:.2f})")
            return None
    
    def find_template_with_retry(self, template_path, initial_threshold=0.8, min_threshold=0.6, 
                                max_retries=3, region=None, check_interval=1):
        """Find a template with progressively lower thresholds
        
        Args:
            template_path (str): Path to template image
            initial_threshold (float): Initial confidence threshold
            min_threshold (float): Minimum acceptable threshold
            max_retries (int): Maximum number of retry attempts
            region (tuple, optional): Region to search in (left, top, width, height)
            check_interval (float): Time between retry attempts in seconds
            
        Returns:
            tuple or None: (x, y) coordinates of match center if found, None otherwise
        """
        template_path = Path(template_path)
        template_name = template_path.name
        
        # Calculate threshold step based on range and retries
        threshold_step = (initial_threshold - min_threshold) / max_retries if max_retries > 0 else 0
        
        for attempt in range(max_retries + 1):
            current_threshold = initial_threshold - (attempt * threshold_step)
            
            logger.info(f"🔍 Looking for {template_name} (attempt {attempt+1}/{max_retries+1}, threshold: {current_threshold:.2f})")
            match = self.find_template(template_path, threshold=current_threshold, region=region)
            
            if match:
                if attempt > 0:
                    logger.info(f"✅ Found {template_name} on retry attempt {attempt+1} with threshold {current_threshold:.2f}")
                return match
            
            if attempt < max_retries:
                time.sleep(check_interval)
        
        logger.warning(f"❌ Failed to find {template_name} after {max_retries+1} attempts")
        return None
    
    def wait_for_template(self, template_path, timeout=30, check_interval=1, threshold=0.8, region=None):
        """Wait until a template appears on screen or timeout
        
        Args:
            template_path (str): Path to template image
            timeout (int): Maximum time to wait in seconds
            check_interval (float): Time between checks in seconds
            threshold (float): Confidence threshold (0.0-1.0)
            region (tuple, optional): Region to search in (left, top, width, height)
            
        Returns:
            tuple or None: (x, y) coordinates of match center if found, None otherwise
        """
        template_path = Path(template_path)
        template_name = template_path.name
        start_time = time.time()
        
        logger.info(f"⏳ Waiting for {template_name} (timeout: {timeout}s)...")
        
        while time.time() - start_time < timeout:
            match = self.find_template(template_path, threshold=threshold, region=region)
            if match:
                elapsed = time.time() - start_time
                logger.info(f"✅ Found {template_name} after {elapsed:.1f}s")
                return match
            
            time.sleep(check_interval)
        
        elapsed = time.time() - start_time
        logger.warning(f"⌛ Timeout after {elapsed:.1f}s waiting for {template_name}")
        return None
    
    def wait_for_any_template(self, template_paths, timeout=30, check_interval=1, threshold=0.8, region=None):
        """Wait until any of the templates appears on screen or timeout
        
        Args:
            template_paths (list): List of paths to template images
            timeout (int): Maximum time to wait in seconds
            check_interval (float): Time between checks in seconds
            threshold (float): Confidence threshold (0.0-1.0)
            region (tuple, optional): Region to search in (left, top, width, height)
            
        Returns:
            tuple: (template_path, (x, y)) of the first template found, or (None, None) on timeout
        """
        template_paths = [Path(p) for p in template_paths]
        template_names = [p.name for p in template_paths]
        start_time = time.time()
        
        logger.info(f"⏳ Waiting for any of {template_names} (timeout: {timeout}s)...")
        
        while time.time() - start_time < timeout:
            for template_path in template_paths:
                match = self.find_template(template_path, threshold=threshold, region=region)
                if match:
                    elapsed = time.time() - start_time
                    logger.info(f"✅ Found {template_path.name} after {elapsed:.1f}s")
                    return template_path, match
            
            time.sleep(check_interval)
        
        elapsed = time.time() - start_time
        logger.warning(f"⌛ Timeout after {elapsed:.1f}s waiting for any of {template_names}")
        return None, None