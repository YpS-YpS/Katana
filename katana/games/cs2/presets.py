"""
Katana Game Benchmark Automation Framework - CS2 Preset Adapter

This module provides CS2-specific preset functionality.
"""
import time
import logging
import re
import shutil
from pathlib import Path

from ...core.presets import PresetAdapter

logger = logging.getLogger("katana")

class CS2PresetAdapter(PresetAdapter):
    """CS2-specific preset adapter"""
    
    def __init__(self, config_path=None):
        """Initialize the CS2 preset adapter
        
        Args:
            config_path (Path, optional): Path to the CS2 video settings file
        """
        super().__init__(config_path)
        
        # If config_path not provided, try to find it automatically
        if self.config_path is None:
            self.config_path = self._find_config_path()
        
        if self.config_path:
            logger.info(f"🎮 CS2 config path: {self.config_path}")
        else:
            logger.warning("⚠️ CS2 config path not found")
    
    def _find_config_path(self):
        """Find the CS2 video settings file automatically
        
        Returns:
            Path: Path to the video settings file
        """
        # Check common locations
        steam_path = self._find_steam_path()
        if not steam_path:
            logger.warning("⚠️ Could not find Steam path automatically")
            return None
        
        # Try to find the Steam ID of the current user
        userdata_path = steam_path / "userdata"
        if not userdata_path.exists():
            logger.warning(f"⚠️ Steam userdata directory not found: {userdata_path}")
            return None
        
        # Look for CS2 config in each user's directory
        for user_dir in userdata_path.iterdir():
            if not user_dir.is_dir():
                continue
            
            # Try the path provided
            cs2_cfg_path = user_dir / "730" / "local" / "cfg" / "cs2_video.txt"
            if cs2_cfg_path.exists():
                return cs2_cfg_path
            
            # Also check for other possible filenames
            alternate_paths = [
                user_dir / "730" / "local" / "cfg" / "video.cfg",
                user_dir / "730" / "local" / "cfg" / "video.txt"
            ]
            
            for path in alternate_paths:
                if path.exists():
                    return path
        
        logger.warning("⚠️ Could not find CS2 video settings file automatically")
        return None
    
    def _find_steam_path(self):
        """Find the Steam installation path
        
        Returns:
            Path: Path to the Steam directory
        """
        try:
            # Try to get from registry on Windows
            import os
            if os.name == 'nt':
                try:
                    import winreg
                    hkey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
                    steam_path = winreg.QueryValueEx(hkey, "SteamPath")[0]
                    winreg.CloseKey(hkey)
                    return Path(steam_path)
                except Exception as e:
                    logger.warning(f"⚠️ Could not find Steam path in registry: {e}")
            
            # Check common locations
            common_paths = [
                Path.home() / ".steam/steam" if hasattr(Path, 'home') else None,  # Linux
                Path.home() / "Library/Application Support/Steam" if hasattr(Path, 'home') else None,  # macOS
                Path("C:/Program Files (x86)/Steam"),  # Windows
                Path("C:/Program Files/Steam"),  # Windows
                Path("D:/Program Files (x86)/Steam"),  # Windows on D: drive
                Path("D:/Program Files/Steam")  # Windows on D: drive
            ]
            
            for path in common_paths:
                if path and path.exists():
                    return path
            
            return None
        except Exception as e:
            logger.error(f"❌ Error finding Steam path: {e}")
            return None
    
    def apply_preset(self, preset_data, backup=True):
        """Apply a preset to the CS2 video settings file
        
        Args:
            preset_data (dict): Preset configuration data
            backup (bool): Whether to backup current settings
            
        Returns:
            bool: True if preset was applied successfully
        """
        if not self.config_path or not self.config_path.exists():
            logger.error(f"❌ CS2 config file not found: {self.config_path}")
            return False
        
        # Backup current config if requested
        if backup:
            backup_path = self.backup_config()
            if not backup_path:
                logger.error("❌ Failed to backup current config")
                return False
        
        try:
            # Read current config
            with open(self.config_path, "r") as f:
                config_content = f.read()
            
            # Update settings
            for key, value in preset_data.items():
                # Skip metadata keys that aren't actual settings
                if key in ["name", "description"]:
                    continue
                
                # Convert to string representation
                if isinstance(value, bool):
                    value = "1" if value else "0"
                else:
                    value = str(value)
                
                # Replace or add setting
                pattern = rf'"{key}"\s+"[^"]*"'
                replacement = f'"{key}"\t\t"{value}"'
                
                if re.search(pattern, config_content):
                    # Replace existing setting
                    config_content = re.sub(pattern, replacement, config_content)
                else:
                    # Add new setting before the closing brace
                    config_content = config_content.replace("}", f'\t{replacement}\n}}')
            
            # Write updated config
            with open(self.config_path, "w") as f:
                f.write(config_content)
            
            logger.info(f"✅ Applied preset to CS2 config: {self.config_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to apply preset: {e}")
            
            # Try to restore backup if we have one
            if backup and backup_path:
                logger.info(f"🔄 Attempting to restore backup after failure")
                self.restore_backup(backup_path)
            
            return False
    
    def backup_config(self, backup_path=None):
        """Backup the current CS2 config
        
        Args:
            backup_path (Path, optional): Path to save the backup
            
        Returns:
            str or None: Path to the backup file, or None if backup failed
        """
        if not self.config_path or not self.config_path.exists():
            logger.error(f"❌ CS2 config file not found: {self.config_path}")
            return None
        
        if backup_path is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_path = self.config_path.parent / f"{self.config_path.name}.backup_{timestamp}"
        
        try:
            shutil.copy2(self.config_path, backup_path)
            logger.info(f"✅ Backed up CS2 config to: {backup_path}")
            return str(backup_path)
        except Exception as e:
            logger.error(f"❌ Failed to backup CS2 config: {e}")
            return None
    
    def restore_backup(self, backup_path):
        """Restore a CS2 config backup
        
        Args:
            backup_path (Path): Path to the backup file
            
        Returns:
            bool: True if backup was restored successfully
        """
        backup_path = Path(backup_path)
        if not backup_path.exists():
            logger.error(f"❌ Backup file not found: {backup_path}")
            return False
        
        try:
            shutil.copy2(backup_path, self.config_path)
            logger.info(f"✅ Restored CS2 config from backup: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to restore CS2 config: {e}")
            return False