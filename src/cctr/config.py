"""Configuration management with XDG Base Directory support."""

import locale
import os
from pathlib import Path
from typing import Optional

import yaml


def get_xdg_config_home() -> Path:
    """Get XDG_CONFIG_HOME directory."""
    return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))


def get_xdg_data_home() -> Path:
    """Get XDG_DATA_HOME directory."""
    return Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))


def get_config_dir() -> Path:
    """Get cctr configuration directory."""
    config_dir = get_xdg_config_home() / "cctr"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_config_file() -> Path:
    """Get cctr configuration file path."""
    return get_config_dir() / "config.yaml"


def get_system_language() -> str:
    """Get system default language code."""
    try:
        # Get the system locale
        lang, _ = locale.getdefaultlocale()
        if lang:
            # Extract language code (e.g., 'ja_JP' -> 'ja')
            return lang.split("_")[0]
        return "en"
    except Exception:
        return "en"


class Config:
    """Configuration manager for cctr."""

    def __init__(self):
        self.config_file = get_config_file()
        self._config = self._load_config()

    def _load_config(self) -> dict:
        """Load configuration from file or create default."""
        if self.config_file.exists():
            with open(self.config_file, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        else:
            # Create default config
            default_config = {
                "native_language": get_system_language(),
                "default_model": "haiku",
            }
            self._save_config(default_config)
            return default_config

    def _save_config(self, config: dict) -> None:
        """Save configuration to file."""
        with open(self.config_file, "w", encoding="utf-8") as f:
            yaml.safe_dump(config, f, allow_unicode=True, default_flow_style=False)

    @property
    def native_language(self) -> str:
        """Get native language setting."""
        return self._config.get("native_language", get_system_language())

    @native_language.setter
    def native_language(self, value: str) -> None:
        """Set native language setting."""
        self._config["native_language"] = value
        self._save_config(self._config)

    @property
    def default_model(self) -> str:
        """Get default model setting."""
        return self._config.get("default_model", "haiku")

    @default_model.setter
    def default_model(self, value: str) -> None:
        """Set default model setting."""
        self._config["default_model"] = value
        self._save_config(self._config)

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get configuration value."""
        return self._config.get(key, default)

    def set(self, key: str, value: str) -> None:
        """Set configuration value."""
        self._config[key] = value
        self._save_config(self._config)
