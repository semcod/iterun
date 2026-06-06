"""
INTENT-ITERATIVE: AI Gateway
LiteLLM-based AI Gateway for LLM model access.
Default: Ollama with models up to 12B parameters.
"""

import os
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

MAX_3 = 3.0
MAX_3 = 3.8
MAX_6 = 6.7
MAX_7 = 7.0
MAX_8 = 8.0
MAX_9 = 9.0
MAX_12 = 12.0
MAX_14 = 14.0
CONSTANT_120 = 120
CONSTANT_4096 = 4096
MAX_8192 = 8192
CONSTANT_16384 = 16384
CONSTANT_32768 = 32768
CONSTANT_128000 = 128000


try:
    import litellm
    from litellm import completion, acompletion
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False

import sys

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

from ir.models import IntentIR


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
            "ollama_base_url": self.ollama_base_url,
            "max_parameters_billions": self.max_parameters_billions,
            "timeout": self.timeout,
            "available_models": [m.to_dict() for m in self.get_available_models()]
        }


class AIGateway:
    """
    AI Gateway using LiteLLM for unified model access.
    Default: Ollama with models up to 12B parameters.
    """
    
    def __init__(self, config: GatewayConfig = None):
        self.config = config or GatewayConfig()
        self._setup_litellm()
    
    def _setup_litellm(self):
        """Configure LiteLLM settings."""
        if not LITELLM_AVAILABLE:
            return
        
        # Set Ollama base URL
        os.environ["OLLAMA_API_BASE"] = self.config.ollama_base_url
        
        # Configure litellm
        litellm.set_verbose = False
        litellm.request_timeout = self.config.timeout
        litellm.num_retries = self.config.retry_count
        
        # Set API keys if available
        if self.config.openai_api_key:
            os.environ["OPENAI_API_KEY"] = self.config.openai_api_key
        if self.config.anthropic_api_key:
            os.environ["ANTHROPIC_API_KEY"] = self.config.anthropic_api_key
        if self.config.openrouter_api_key:
            os.environ["OPENROUTER_API_KEY"] = self.config.openrouter_api_key
    
    def complete(
        self,
        prompt: str,
        model: str = None,
        system_prompt: str = None,
        temperature: float = None,
        max_tokens: int = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate completion using specified model.
        
        Args:
            prompt: User prompt
            model: Model name (default from config)
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Dict with 'content', 'model', 'usage', 'success'
        """
        if not LITELLM_AVAILABLE:
            return self._mock_response(prompt, model)
        
        model_name = model or self.config.default_model
        model_config = self.config.get_model(model_name)
        
        if not model_config:
            # Try using model name directly
            model_id = f"ollama/{model_name}"
        else:
            model_id = model_config.model_id
            temperature = temperature or model_config.temperature
            max_tokens = max_tokens or model_config.max_tokens
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = completion(
                model=model_id,
                messages=messages,
                temperature=temperature or 0.7,
                max_tokens=max_tokens or 4096,
                **kwargs
            )
            
            return {
                "success": True,
                "content": response.choices[0].message.content,
                "model": model_id,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "finish_reason": response.choices[0].finish_reason
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": model_id,
                "content": None
            }
    
    async def acomplete(
        self,
        prompt: str,
        model: str = None,
        system_prompt: str = None,
        temperature: float = None,
        max_tokens: int = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Async version of complete."""
        if not LITELLM_AVAILABLE:
            return self._mock_response(prompt, model)
        
        model_name = model or self.config.default_model
        model_config = self.config.get_model(model_name)
        
        if not model_config:
            model_id = f"ollama/{model_name}"
        else:
            model_id = model_config.model_id
            temperature = temperature or model_config.temperature
            max_tokens = max_tokens or model_config.max_tokens
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = await acompletion(
                model=model_id,
                messages=messages,
                temperature=temperature or 0.7,
                max_tokens=max_tokens or 4096,
                **kwargs
            )
            
            return {
                "success": True,
                "content": response.choices[0].message.content,
                "model": model_id,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "finish_reason": response.choices[0].finish_reason
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": model_id,
                "content": None
            }
    
    def _mock_response(self, prompt: str, model: str = None) -> Dict[str, Any]:
        """Mock response when LiteLLM is not available."""
        return {
            "success": True,
            "content": f"[MOCK] LiteLLM not available. Would process: {prompt[:100]}...",
            "model": model or "mock",
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            "mock": True
        }
    
    def suggest_improvements(self, ir: IntentIR) -> Dict[str, Any]:
        """
        Use LLM to suggest improvements for an intent.
        
        Args:
            ir: Current IntentIR state
            
        Returns:
            Dict with suggestions
        """
        system_prompt = """You are an expert software architect helping to improve intent definitions.
Analyze the provided intent and suggest concrete improvements.
Focus on:
1. Missing endpoints or functionality
2. Security considerations
3. Performance optimizations
4. Best practices

Respond in JSON format with keys: 'suggestions', 'new_actions', 'warnings'"""
        
        prompt = f"""Analyze this intent and suggest improvements:

Name: {ir.intent.name}
Goal: {ir.intent.goal}
Language: {ir.implementation.language}
Framework: {ir.implementation.framework}
Current Actions:
{json.dumps([a.to_dict() for a in ir.implementation.actions], indent=2)}

Dry-run logs:
{chr(10).join(ir.dry_run_logs[-10:]) if ir.dry_run_logs else 'No logs yet'}

Provide suggestions in JSON format."""
        
        response = self.complete(prompt, system_prompt=system_prompt)
        
        if response["success"] and response["content"]:
            try:
                # Try to parse JSON from response
                content = response["content"]
                # Extract JSON if wrapped in markdown
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                suggestions = json.loads(content)
                return {
                    "success": True,
                    "suggestions": suggestions,
                    "model": response["model"],
                    "usage": response.get("usage")
                }
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "suggestions": {"raw": response["content"]},
                    "model": response["model"],
                    "usage": response.get("usage")
                }
        
        return response
    
    def generate_code_snippet(
        self,
        description: str,
        language: str = "python",
        framework: str = None
    ) -> Dict[str, Any]:
        """Generate code snippet based on description."""
        system_prompt = f"""You are an expert {language} developer.
Generate clean, production-ready code for the following request.
{f'Use the {framework} framework.' if framework else ''}
Only output the code, no explanations."""
        
        response = self.complete(description, system_prompt=system_prompt)
        
        if response["success"] and response["content"]:
            code = response["content"]
            # Clean up markdown code blocks
            if "```" in code:
                lines = code.split("```")
                if len(lines) >= 2:
                    code = lines[1]
                    if code.startswith(language):
                        code = code[len(language):].strip()
                    elif code.startswith("python") or code.startswith("javascript"):
                        code = code.split("\n", 1)[1] if "\n" in code else code
            
            return {
                "success": True,
                "code": code.strip(),
                "language": language,
                "model": response["model"]
            }
        
        return response
    
    def explain_error(self, error: str, context: str = None) -> Dict[str, Any]:
        """Explain an error and suggest fixes."""
        system_prompt = """You are a helpful debugging assistant.
Explain the error clearly and provide actionable fixes.
Be concise but thorough."""
        
        prompt = f"Error: {error}"
        if context:
            prompt += f"\n\nContext:\n{context}"
        
        return self.complete(prompt, system_prompt=system_prompt)
    
    def list_models(self, max_params: float = None) -> List[Dict[str, Any]]:
        """List available models."""
        models = self.config.get_available_models(max_params)
        return [m.to_dict() for m in models]
    
    def health_check(self) -> Dict[str, Any]:
        """Check if the AI Gateway is operational."""
        result = {
            "litellm_available": LITELLM_AVAILABLE,
            "default_model": self.config.default_model,
            "ollama_url": self.config.ollama_base_url,
            "available_models": len(self.config.get_available_models())
        }
        
        if LITELLM_AVAILABLE:
            # Try a simple completion
            test = self.complete("Say 'ok'", max_tokens=10)
            result["ollama_connected"] = test["success"]
            if not test["success"]:
                result["error"] = test.get("error")
        else:
            result["ollama_connected"] = False
            result["error"] = "LiteLLM not installed"
        
        return result


# Singleton instance
_gateway: Optional[AIGateway] = None


def get_gateway(config: GatewayConfig = None) -> AIGateway:
    """Get or create AIGateway singleton."""
    global _gateway
    if _gateway is None or config is not None:
        _gateway = AIGateway(config)
    return _gateway


def complete(prompt: str, **kwargs) -> Dict[str, Any]:
    """Convenience function for completion."""
    return get_gateway().complete(prompt, **kwargs)


def suggest_improvements(ir: IntentIR) -> Dict[str, Any]:
    """Convenience function for suggestions."""
    return get_gateway().suggest_improvements(ir)
