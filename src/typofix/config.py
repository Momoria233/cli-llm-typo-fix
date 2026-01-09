import json
import os
from pathlib import Path
from typing import Dict, Optional

CONFIG_DIR = Path.home() / ".typofix"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "api_key": "",
    "model": "gpt-4o-mini",
    "base_url": "https://api.openai.com/v1"
}

def load_config() -> Dict[str, str]:
    """Load configuration from disk."""
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG.copy()
    
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_CONFIG.copy()

def save_config(config: Dict[str, str]) -> None:
    """Save configuration to disk."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

def get_api_key() -> Optional[str]:
    """Get API key from environment variable or config."""
    # Env var takes precedence
    env_key = os.getenv("OPENAI_API_KEY")
    if env_key:
        return env_key
    
    config = load_config()
    return config.get("api_key")

def get_model() -> str:
    """Get model from config."""
    config = load_config()
    return config.get("model", DEFAULT_CONFIG["model"])

def get_base_url() -> str:
    """Get base URL from config."""
    config = load_config()
    return config.get("base_url", DEFAULT_CONFIG["base_url"])
