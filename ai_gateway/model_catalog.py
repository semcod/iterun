"""Model catalog and gateway configuration for the AI Gateway."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

class ModelProvider(Enum):
    """Supported model providers."""
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OPENROUTER = "openrouter"
    LOCAL = "local"


@dataclass
class ModelConfig:
    """Configuration for a specific model."""
    name: str
    provider: ModelProvider
    model_id: str
    max_tokens: int = 4096
    temperature: float = 0.7
    context_window: int = 8192
    parameters_billions: float = 0.0
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "provider": self.provider.value,
            "model_id": self.model_id,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "context_window": self.context_window,
            "parameters_billions": self.parameters_billions,
            "description": self.description
        }


# Default Ollama models (up to 12B parameters)
OLLAMA_MODELS: Dict[str, ModelConfig] = {
    "llama3.2": ModelConfig(
        name="Llama 3.2 3B",
        provider=ModelProvider.OLLAMA,
        model_id="ollama/llama3.2",
        max_tokens=4096,
        context_window=128000,
        parameters_billions=3.0,
        description="Meta Llama 3.2 3B - Fast and efficient"
    ),
    "llama3.2:1b": ModelConfig(
        name="Llama 3.2 1B",
        provider=ModelProvider.OLLAMA,
        model_id="ollama/llama3.2:1b",
        max_tokens=4096,
        context_window=128000,
        parameters_billions=1.0,
        description="Meta Llama 3.2 1B - Ultra lightweight"
    ),
    "llama3.1:8b": ModelConfig(
        name="Llama 3.1 8B",
        provider=ModelProvider.OLLAMA,
        model_id="ollama/llama3.1:8b",
        max_tokens=4096,
        context_window=128000,
        parameters_billions=8.0,
        description="Meta Llama 3.1 8B - Balanced performance"
    ),
    "mistral": ModelConfig(
        name="Mistral 7B",
        provider=ModelProvider.OLLAMA,
        model_id="ollama/mistral",
        max_tokens=4096,
        context_window=32768,
        parameters_billions=7.0,
        description="Mistral 7B - Fast inference"
    ),
    "mistral-nemo": ModelConfig(
        name="Mistral Nemo 12B",
        provider=ModelProvider.OLLAMA,
        model_id="ollama/mistral-nemo",
        max_tokens=4096,
        context_window=128000,
        parameters_billions=12.0,
        description="Mistral Nemo 12B - Best quality under 12B"
    ),
    "gemma2": ModelConfig(
        name="Gemma 2 9B",
        provider=ModelProvider.OLLAMA,
        model_id="ollama/gemma2",
        max_tokens=4096,
        context_window=8192,
        parameters_billions=9.0,
        description="Google Gemma 2 9B"
    ),
    "gemma2:2b": ModelConfig(
        name="Gemma 2 2B",
        provider=ModelProvider.OLLAMA,
        model_id="ollama/gemma2:2b",
        max_tokens=4096,
        context_window=8192,
        parameters_billions=2.0,
        description="Google Gemma 2 2B - Lightweight"
    ),
    "phi3": ModelConfig(
        name="Phi-3 Mini 3.8B",
        provider=ModelProvider.OLLAMA,
        model_id="ollama/phi3",
        max_tokens=4096,
        context_window=128000,
        parameters_billions=3.8,
        description="Microsoft Phi-3 Mini"
    ),
    "phi3:medium": ModelConfig(
        name="Phi-3 Medium 14B",
        provider=ModelProvider.OLLAMA,
        model_id="ollama/phi3:medium",
        max_tokens=4096,
        context_window=128000,
        parameters_billions=14.0,
        description="Microsoft Phi-3 Medium (over 12B limit)"
    ),
    "qwen2.5": ModelConfig(
        name="Qwen 2.5 7B",
        provider=ModelProvider.OLLAMA,
        model_id="ollama/qwen2.5",
        max_tokens=4096,
        context_window=32768,
        parameters_billions=7.0,
        description="Alibaba Qwen 2.5 7B"
    ),
    "qwen2.5:3b": ModelConfig(
        name="Qwen 2.5 3B",
        provider=ModelProvider.OLLAMA,
        model_id="ollama/qwen2.5:3b",
        max_tokens=4096,
        context_window=32768,
        parameters_billions=3.0,
        description="Alibaba Qwen 2.5 3B"
    ),
    "codellama": ModelConfig(
        name="Code Llama 7B",
        provider=ModelProvider.OLLAMA,
        model_id="ollama/codellama",
        max_tokens=4096,
        context_window=16384,
        parameters_billions=7.0,
        description="Meta Code Llama 7B - Code generation"
    ),
    "codegemma": ModelConfig(
        name="CodeGemma 7B",
        provider=ModelProvider.OLLAMA,
        model_id="ollama/codegemma",
        max_tokens=4096,
        context_window=8192,
        parameters_billions=7.0,
        description="Google CodeGemma 7B"
    ),
    "deepseek-coder": ModelConfig(
        name="DeepSeek Coder 6.7B",
        provider=ModelProvider.OLLAMA,
        model_id="ollama/deepseek-coder",
        max_tokens=4096,
        context_window=16384,
        parameters_billions=6.7,
        description="DeepSeek Coder 6.7B"
    ),
    "starcoder2": ModelConfig(
        name="StarCoder2 7B",
        provider=ModelProvider.OLLAMA,
        model_id="ollama/starcoder2",
        max_tokens=4096,
        context_window=16384,
        parameters_billions=7.0,
        description="BigCode StarCoder2 7B"
    ),
}


@dataclass
class GatewayConfig:
    """AI Gateway configuration."""
    default_provider: ModelProvider = ModelProvider.OLLAMA
    default_model: str = None
    llm_model: Optional[str] = None  # e.g. openrouter/deepseek/deepseek-v4-pro (from .env LLM_MODEL)
    ollama_base_url: str = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    max_parameters_billions: float = 12.0
    timeout: int = 120
    retry_count: int = 3
    
    # Custom models registry
    custom_models: Dict[str, ModelConfig] = field(default_factory=dict)
    
    def __post_init__(self):
        # Load from global config first, then environment
        try:
            from config import get_config
            app_config = get_config()
            self.ollama_base_url = self.ollama_base_url or app_config.ollama_base_url
            self.default_model = self.default_model or app_config.default_model
            self.llm_model = self.llm_model or app_config.llm_model
            self.timeout = app_config.ollama_timeout
            self.max_parameters_billions = app_config.max_model_params
            self.openai_api_key = app_config.openai_api_key
            self.anthropic_api_key = app_config.anthropic_api_key
            self.openrouter_api_key = app_config.openrouter_api_key
        except ImportError:
            pass
        
        # Fallback to environment variables
        self.ollama_base_url = self.ollama_base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.default_model = self.default_model or os.getenv("DEFAULT_MODEL", "llama3.2")
        self.openai_api_key = self.openai_api_key or os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = self.anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        self.openrouter_api_key = self.openrouter_api_key or os.getenv("OPENROUTER_API_KEY")
        # Live env wins over cached AppConfig (important for tests and .env edits)
        self.llm_model = os.getenv("LLM_MODEL") or self.llm_model

        if self.llm_model and self.llm_model.startswith("openrouter/"):
            self.default_provider = ModelProvider.OPENROUTER
        elif self.openrouter_api_key and not self.llm_model:
            self.default_provider = ModelProvider.OPENROUTER

    def resolve_model(self, explicit: str | None = None) -> str:
        """Effective model: CLI arg > LLM_MODEL (.env) > DEFAULT_MODEL (Ollama)."""
        if explicit:
            return explicit
        if self.llm_model:
            return self.llm_model
        return self.default_model

    def litellm_model_id(self, model_name: str) -> str:
        """Map config name to LiteLLM model id."""
        model_config = self.get_model(model_name)
        if model_config:
            return model_config.model_id
        # Full provider route from .env (openrouter/..., anthropic/..., etc.)
        if "/" in model_name:
            return model_name
        return f"ollama/{model_name}"
    
    def get_available_models(self, max_params: float = None) -> List[ModelConfig]:
        """Get all available models under parameter limit."""
        limit = max_params or self.max_parameters_billions
        models = []
        
        for model in OLLAMA_MODELS.values():
            if model.parameters_billions <= limit:
                models.append(model)
        
        for model in self.custom_models.values():
            if model.parameters_billions <= limit:
                models.append(model)
        
        return sorted(models, key=lambda m: m.parameters_billions)
    
    def get_model(self, name: str) -> Optional[ModelConfig]:
        """Get model configuration by name."""
        if name in OLLAMA_MODELS:
            return OLLAMA_MODELS[name]
        if name in self.custom_models:
            return self.custom_models[name]
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "default_provider": self.default_provider.value,
            "default_model": self.default_model,
            "llm_model": self.llm_model,
            "effective_model": self.resolve_model(),
            "ollama_base_url": self.ollama_base_url,
            "openrouter_configured": bool(self.openrouter_api_key),
            "max_parameters_billions": self.max_parameters_billions,
            "timeout": self.timeout,
            "available_models": [m.to_dict() for m in self.get_available_models()]
        }
