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
            
            # Define expected config paths
            config_paths = [
                user_dir / "730" / "local" / "cfg" / "cs2_video.txt",
                user_dir / "730" / "local" / "cfg" / "video.cfg",
                user_dir / "730" / "local" / "cfg" / "video.txt"
            ]
            
            # Check if any exist
            for path in config_paths:
                if path.exists():
                    return path
            
            # If none exist, return the first path (we'll create it later)
            config_dir = user_dir / "730" / "local" / "cfg"
            if config_dir.exists():
                return config_paths[0]  # Return cs2_video.txt path
        
        # If no user directories found with CS2 installed, find the first valid user and create the path
        for user_dir in userdata_path.iterdir():
            if not user_dir.is_dir():
                continue
            
            # Create the path structure if it doesn't exist
            config_dir = user_dir / "730" / "local" / "cfg"
            config_dir.mkdir(parents=True, exist_ok=True)
            return config_dir / "cs2_video.txt"
        
        # Last resort - create in the first user directory
        logger.warning("⚠️ Creating new CS2 config directory structure")
        first_user_dir = next(userdata_path.iterdir(), None)
        if first_user_dir and first_user_dir.is_dir():
            config_dir = first_user_dir / "730" / "local" / "cfg"
            config_dir.mkdir(parents=True, exist_ok=True)
            return config_dir / "cs2_video.txt"
        
        logger.error("❌ Could not find a suitable location for CS2 config")
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
    
    def _create_initial_config(self, preset_data):
        """Create initial configuration file using preset data
        
        Args:
            preset_data (dict): Preset configuration data
            
        Returns:
            bool: True if config was created successfully
        """
        # Validate preset data
        if not preset_data:
            logger.error("❌ Empty preset data")
            return False
        
        # Create parent directories if they don't exist
        if self.config_path:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            logger.error("❌ No config path set")
            return False
        
        try:
            # Create a basic CS2 config structure
            config_content = '"video.cfg"\n{\n'
            
            # Add all settings from the preset
            for key, value in preset_data.items():
                # Skip metadata keys
                if key in ["name", "description"]:
                    continue
                
                # Convert to string representation
                if isinstance(value, bool):
                    value = "1" if value else "0"
                else:
                    value = str(value)
                
                # Add setting
                config_content += f'\t"{key}"\t\t"{value}"\n'
            
            # Close the config structure
            config_content += '}\n'
            
            # Write the config file
            with open(self.config_path, "w") as f:
                f.write(config_content)
            
            logger.info(f"✅ Created new config file at {self.config_path} with preset settings")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create initial config: {e}")
            return False
    
    def apply_preset(self, preset_data, backup=True):
        """Apply a preset to the CS2 video settings file
        
        Args:
            preset_data (dict): Preset configuration data
            backup (bool): Whether to backup current settings
            
        Returns:
            bool or str: True if preset was applied successfully, "no_changes" if no changes needed
        """
        # Check if config file exists
        if not self.config_path or not self.config_path.exists():
            logger.warning(f"⚠️ Config file not found: {self.config_path}")
            return self._create_initial_config(preset_data)
        
        # Validate preset data
        if not preset_data:
            logger.error("❌ Empty preset data")
            return False
        
        # Check for required settings
        required_settings = ["setting.defaultres", "setting.defaultresheight"]
        missing_settings = [s for s in required_settings if s not in preset_data]
        if missing_settings:
            logger.error(f"❌ Preset is missing required settings: {missing_settings}")
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
            
            # Count settings applied and already matching
            settings_applied = 0
            settings_already_match = 0
            total_settings = 0
            
            # Update settings
            for key, value in preset_data.items():
                # Skip metadata keys that aren't actual settings
                if key in ["name", "description"]:
                    continue
                
                total_settings += 1
                
                # Convert to string representation
                if isinstance(value, bool):
                    value = "1" if value else "0"
                else:
                    value = str(value)
                
                # Replace or add setting
                pattern = rf'"{key}"\s+"([^"]*)"'
                replacement = f'"{key}"\t\t"{value}"'
                
                # Check if setting exists and needs to be updated
                match = re.search(pattern, config_content)
                if match:
                    current_value = match.group(1)
                    if current_value != value:
                        # Value is different, update it
                        config_content = re.sub(pattern, replacement, config_content)
                        settings_applied += 1
                    else:
                        # Value already matches preset
                        settings_already_match += 1
                else:
                    # Setting doesn't exist, add it
                    config_content = config_content.replace("}", f'\t{replacement}\n}}')
                    settings_applied += 1
            
            # Write updated config only if changes were made
            if settings_applied > 0:
                with open(self.config_path, "w") as f:
                    f.write(config_content)
                
                logger.info(f"✅ Applied preset to CS2 config: {settings_applied} settings updated, {settings_already_match} already matched")
                return True
            else:
                logger.info(f"✓ All {settings_already_match} settings already match preset - no changes needed")
                return "no_changes"  # Special return value for no changes needed
                
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