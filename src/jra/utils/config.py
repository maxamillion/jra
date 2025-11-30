"""Configuration management for JRA."""

import os
from pathlib import Path
from typing import Any, Dict

import tomli if hasattr(__builtins__, 'tomli') else tomllib
from dotenv import load_dotenv

from jra.utils.exceptions import ConfigValidationError


class Config:
    """Configuration manager with hierarchy support."""

    DEFAULT_CONFIG = {
        "evaluation": {
            "strict_mode": False,
            "default_format": "human",
            "enable_color": True,
            "show_timing": False,
        },
        "quality": {
            "completeness_weight": 0.30,
            "clarity_weight": 0.30,
            "formatting_weight": 0.20,
            "standards_weight": 0.20,
            "thresholds": {
                "excellent": 90.0,
                "good": 75.0,
                "acceptable": 60.0,
                "poor": 0.0,
            },
        },
        "output": {
            "max_recommendations": 10,
            "include_examples": True,
            "verbose_violations": True,
        },
        "batch": {
            "default_workers": 1,
            "continue_on_error": False,
            "show_progress": True,
        },
    }

    def __init__(self, config_path: Path | None = None) -> None:
        """Initialize configuration.
        
        Args:
            config_path: Optional path to config file
        """
        self._config: Dict[str, Any] = self.DEFAULT_CONFIG.copy()
        
        # Load .env file if present
        load_dotenv()
        
        # Load config file if provided or found
        if config_path:
            self._load_file(config_path)
        else:
            default_paths = [
                Path.home() / ".jra" / "config.toml",
                Path.cwd() / ".jra" / "config.toml",
            ]
            for path in default_paths:
                if path.exists():
                    self._load_file(path)
                    break
        
        # Override with environment variables
        self._load_env()

    def _load_file(self, path: Path) -> None:
        """Load configuration from TOML file."""
        try:
            with open(path, "rb") as f:
                # Python 3.11+ has tomllib in stdlib
                try:
                    import tomllib
                    file_config = tomllib.load(f)
                except ImportError:
                    import tomli
                    file_config = tomli.load(f)
                
                self._merge_config(file_config)
        except Exception as e:
            raise ConfigValidationError(
                f"Failed to load config from {path}",
                context={"path": str(path), "error": str(e)}
            )

    def _load_env(self) -> None:
        """Load configuration from environment variables."""
        if format_val := os.getenv("JRA_FORMAT"):
            self._config["evaluation"]["default_format"] = format_val
        
        if strict := os.getenv("JRA_STRICT"):
            self._config["evaluation"]["strict_mode"] = strict.lower() in ("true", "1", "yes")
        
        if os.getenv("NO_COLOR"):
            self._config["evaluation"]["enable_color"] = False

    def _merge_config(self, new_config: Dict[str, Any]) -> None:
        """Merge new configuration into existing."""
        for key, value in new_config.items():
            if isinstance(value, dict) and key in self._config:
                self._config[key].update(value)
            else:
                self._config[key] = value

    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value by dot-separated path.
        
        Args:
            key_path: Dot-separated key path (e.g., "quality.thresholds.good")
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key_path.split(".")
        value = self._config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value

    def set(self, key_path: str, value: Any) -> None:
        """Set configuration value by dot-separated path."""
        keys = key_path.split(".")
        config = self._config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value


# Global configuration instance
_config: Config | None = None


def get_config(config_path: Path | None = None) -> Config:
    """Get global configuration instance."""
    global _config
    if _config is None:
        _config = Config(config_path)
    return _config
