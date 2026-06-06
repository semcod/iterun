"""
ITERUN: Configuration
Environment-based configuration for all components.
Loads from .env file if present.
"""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

try:
    from getv import EnvStore
    _HAS_GETV = True
except ImportError:
    _HAS_GETV = False


def load_dotenv(env_path: Path = None):
    """Load environment variables from .env file.

    Delegates to getv.EnvStore when available.
    Also loads getv app defaults (``getv use iterun llm PROFILE``).
    """
    # Load getv app defaults first (if configured)
    if _HAS_GETV:
        try:
            from getv import AppDefaults
            from getv.integrations.pydantic_env import load_profile_into_env
            defaults = AppDefaults("iterun")
            for category in ("llm", "devices"):
                profile = defaults.get(category)
                if profile:
                    load_profile_into_env(category, profile)
        except Exception:
            pass

    if env_path is None:
        env_path = Path(__file__).parent / ".env"
    
    if not env_path.exists():
        return
    
    if _HAS_GETV:
        store = EnvStore(env_path, auto_create=False)
        for key, value in store.items():
            if key not in os.environ:
                os.environ[key] = value
        return
    
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key not in os.environ:
                    os.environ[key] = value


# Load .env on module import
load_dotenv()

# Canonical DSL package filename written to workspace/generated/
PACKAGE_FILENAME = "iterun.yaml"


def get_env(key: str, default: str = None) -> Optional[str]:
    """Get environment variable."""
    return os.getenv(key, default)


def get_env_bool(key: str, default: bool = False) -> bool:
    """Get boolean environment variable."""
    value = os.getenv(key, str(default)).lower()
    return value in ("true", "1", "yes", "on")


def get_env_int(key: str, default: int = 0) -> int:
    """Get integer environment variable."""
    try:
        return int(os.getenv(key, str(default)))
    except ValueError:
        return default


def get_env_float(key: str, default: float = 0.0) -> float:
    """Get float environment variable."""
    try:
        return float(os.getenv(key, str(default)))
    except ValueError:
        return default


@dataclass
class AppConfig:
    """Main application configuration."""
    
    # General
    debug: bool = field(default_factory=lambda: get_env_bool("DEBUG", False))
    log_level: str = field(default_factory=lambda: get_env("LOG_LEVEL", "INFO"))
    
    # Web server
    host: str = field(default_factory=lambda: get_env("HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: get_env_int("PORT", 8080))
    
    # AI Gateway
    ai_enabled: bool = field(default_factory=lambda: get_env_bool("AI_ENABLED", True))
    default_model: str = field(default_factory=lambda: get_env("DEFAULT_MODEL", "llama3.2"))
    llm_model: Optional[str] = field(default_factory=lambda: get_env("LLM_MODEL"))
    max_model_params: float = field(default_factory=lambda: get_env_float("MAX_MODEL_PARAMS", 12.0))
    
    # Ollama
    ollama_base_url: str = field(default_factory=lambda: get_env("OLLAMA_BASE_URL", "http://localhost:11434"))
    ollama_timeout: int = field(default_factory=lambda: get_env_int("OLLAMA_TIMEOUT", 120))
    
    # Optional API keys
    openai_api_key: Optional[str] = field(default_factory=lambda: get_env("OPENAI_API_KEY"))
    anthropic_api_key: Optional[str] = field(default_factory=lambda: get_env("ANTHROPIC_API_KEY"))
    openrouter_api_key: Optional[str] = field(default_factory=lambda: get_env("OPENROUTER_API_KEY"))
    
    # Execution runtime: docker (default) | pactown (markpact sandboxes)
    runtime: str = field(default_factory=lambda: get_env("ITERUN_RUNTIME", "docker"))

    # Execution
    docker_enabled: bool = field(default_factory=lambda: get_env_bool("DOCKER_ENABLED", True))
    workspace_dir: str = field(default_factory=lambda: get_env("WORKSPACE_DIR", "/tmp/iterun"))
    auto_execute: bool = field(default_factory=lambda: get_env_bool("AUTO_EXECUTE", True))
    skip_iterun_confirmation: bool = field(default_factory=lambda: get_env_bool("SKIP_ITERUN_CONFIRMATION", True))
    
    # Docker container settings
    container_port: int = field(default_factory=lambda: get_env_int("CONTAINER_PORT", 8000))
    container_prefix: str = field(default_factory=lambda: get_env("CONTAINER_PREFIX", "intent"))
    
    # Validation & Auto-fix
    validate_after_execute: bool = field(default_factory=lambda: get_env_bool("VALIDATE_AFTER_EXECUTE", True))
    auto_fix_enabled: bool = field(default_factory=lambda: get_env_bool("AUTO_FIX_ENABLED", True))
    max_fix_iterations: int = field(default_factory=lambda: get_env_int("MAX_FIX_ITERATIONS", 3))
    startup_wait: int = field(default_factory=lambda: get_env_int("STARTUP_WAIT", 2))
    validation_timeout: int = field(default_factory=lambda: get_env_int("VALIDATION_TIMEOUT", 10))


# Global config instance
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get or create application config."""
    global _config
    if _config is None:
        _config = AppConfig()
    return _config


def reload_config() -> AppConfig:
    """Force reload configuration."""
    global _config
    load_dotenv()
    _config = AppConfig()
    return _config


def configure(**kwargs) -> AppConfig:
    """Configure application with custom settings."""
    global _config
    _config = AppConfig(**kwargs)
    return _config

