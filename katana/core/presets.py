"""
Katana Game Benchmark Automation Framework - Core Presets Module

This module provides base classes and utilities for managing graphics presets.
"""
import json
import logging
import re
from pathlib import Path
from abc import ABC, abstractmethod

logger = logging.getLogger("katana")

class PresetManager:
    """Manages graphics presets for games"""
    
    def __init__(self, presets_dir=None):
        """Initialize the preset manager
        
        Args:
            presets_dir (Path, optional): Directory containing preset definitions
        """
        self.presets_dir = Path(presets_dir) if presets_dir else Path(__file__).parent.parent / "presets"
        self.adapters = {}  # Game ID -> PresetAdapter mapping
    
    def register_adapter(self, game_id, adapter):
        """Register a preset adapter for a game
        
        Args:
            game_id (str): Game identifier
            adapter (PresetAdapter): Adapter for the game
        """
        self.adapters[game_id] = adapter
        logger.info(f"🎮 Registered preset adapter for {game_id}")
    
    def get_available_presets(self, game_id):
        """Get available presets for a game
        
        Args:
            game_id (str): Game identifier
            
        Returns:
            dict: Dictionary of preset_id -> preset_name mappings
        """
        game_presets_dir = self.presets_dir / game_id
        if not game_presets_dir.exists():
            logger.warning(f"⚠️ No presets directory found for {game_id}")
            return {}
        
        presets_file = game_presets_dir / "presets.json"
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
    
    def get_preset_data(self, game_id, preset_id):
        """Get data for a specific preset
        
        Args:
            game_id (str): Game identifier
            preset_id (str): Preset identifier
            
        Returns:
            dict: Preset configuration data
        """
        preset_file = self.presets_dir / game_id / f"{preset_id}.json"
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
    
    def apply_preset(self, game_id, preset_id, backup=True):
        """Apply a preset to a game
        
        Args:
            game_id (str): Game identifier
            preset_id (str): Preset identifier
            backup (bool): Whether to backup current settings
            
        Returns:
            bool: True if preset was applied successfully
        """
        if game_id not in self.adapters:
            logger.error(f"❌ No preset adapter registered for {game_id}")
            return False
        
        # Get preset data
        preset_data = self.get_preset_data(game_id, preset_id)
        if not preset_data:
            return False
        
        # Apply preset
        adapter = self.adapters[game_id]
        result = adapter.apply_preset(preset_data, backup=backup)
        
        if result:
            logger.info(f"✅ Applied preset '{preset_id}' to {game_id}")
            
            # Get resolution from preset for logging
            if "setting.defaultres" in preset_data and "setting.defaultresheight" in preset_data:
                width = preset_data["setting.defaultres"]
                height = preset_data["setting.defaultresheight"]
                logger.info(f"📊 Resolution set to: {width}x{height}")
                
        else:
            logger.error(f"❌ Failed to apply preset '{preset_id}' to {game_id}")
        
        return result


class PresetAdapter(ABC):
    """Base class for game-specific preset adapters"""
    
    def __init__(self, config_path=None):
        """Initialize the preset adapter
        
        Args:
            config_path (Path, optional): Path to the game's config file
        """
        self.config_path = Path(config_path) if config_path else None
    
    @abstractmethod
    def apply_preset(self, preset_data, backup=True):
        """Apply a preset to the game's config
        
        Args:
            preset_data (dict): Preset configuration data
            backup (bool): Whether to backup current settings
            
        Returns:
            bool: True if preset was applied successfully
        """
        pass
    
    @abstractmethod
    def backup_config(self, backup_path=None):
        """Backup the current game config
        
        Args:
            backup_path (Path, optional): Path to save the backup
            
        Returns:
            str or None: Path to the backup file, or None if backup failed
        """
        pass
    
    @abstractmethod
    def restore_backup(self, backup_path):
        """Restore a config backup
        
        Args:
            backup_path (Path): Path to the backup file
            
        Returns:
            bool: True if backup was restored successfully
        """
        pass