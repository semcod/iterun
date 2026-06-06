"""
ITERUN: AI Gateway
LiteLLM-based AI Gateway for LLM model access.
Default: Ollama with models up to 12B parameters.
"""

import os
import json
from typing import Any, Dict, List, Optional
from pathlib import Path

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


from ai_gateway.model_catalog import GatewayConfig

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
        
        model_name = self.config.resolve_model(model)
        model_config = self.config.get_model(model_name)
        model_id = self.config.litellm_model_id(model_name)
        if model_config:
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
        
        model_name = self.config.resolve_model(model)
        model_config = self.config.get_model(model_name)
        model_id = self.config.litellm_model_id(model_name)
        if model_config:
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
        effective = self.config.resolve_model()
        result = {
            "litellm_available": LITELLM_AVAILABLE,
            "default_model": self.config.default_model,
            "llm_model": self.config.llm_model,
            "effective_model": effective,
            "provider": self.config.default_provider.value,
            "openrouter_configured": bool(self.config.openrouter_api_key),
            "ollama_url": self.config.ollama_base_url,
            "available_models": len(self.config.get_available_models())
        }
        
        if LITELLM_AVAILABLE:
            test = self.complete("Say 'ok'", max_tokens=10)
            result["llm_connected"] = test["success"]
            result["ollama_connected"] = test["success"]  # backward compat
            if not test["success"]:
                result["error"] = test.get("error")
        else:
            result["llm_connected"] = False
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
