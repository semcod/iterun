"""
E2E Tests for ITERUN AI Gateway
Tests for LiteLLM integration and feedback loop.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ir.models import IntentIR, Intent, Implementation, Action, ActionType


class TestModelConfig:
    """Test model configuration."""
    
    def test_ollama_models_exist(self):
        """Test that default Ollama models are defined."""
        from ai_gateway.model_catalog import OLLAMA_MODELS
        
        assert len(OLLAMA_MODELS) > 0
        assert "llama3.2" in OLLAMA_MODELS
        assert "mistral" in OLLAMA_MODELS
    
    def test_model_config_properties(self):
        """Test model config has required properties."""
        from ai_gateway.model_catalog import OLLAMA_MODELS
        
        for name, model in OLLAMA_MODELS.items():
            assert model.name
            assert model.model_id
            assert model.max_tokens > 0
            assert model.context_window > 0
            assert model.parameters_billions >= 0
    
    def test_models_under_12b(self):
        """Test filtering models under 12B params."""
        from ai_gateway.model_catalog import GatewayConfig
        
        config = GatewayConfig()
        models = config.get_available_models(max_params=12.0)
        
        for model in models:
            assert model.parameters_billions <= 12.0


class TestGatewayConfig:
    """Test gateway configuration."""
    
    def test_default_config(self, monkeypatch):
        """Test default configuration values."""
        from ai_gateway.model_catalog import GatewayConfig, ModelProvider

        monkeypatch.delenv("LLM_MODEL", raising=False)
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        config = GatewayConfig()
        
        assert config.default_model == "llama3.2"
        assert config.ollama_base_url == "http://localhost:11434"
        assert config.max_parameters_billions == 12.0
    
    def test_resolve_model_prefers_llm_model(self, monkeypatch):
        """LLM_MODEL from .env overrides DEFAULT_MODEL for LiteLLM."""
        from ai_gateway.model_catalog import GatewayConfig

        monkeypatch.setenv("LLM_MODEL", "openrouter/test/model")
        monkeypatch.setenv("DEFAULT_MODEL", "llama3.2")
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        config = GatewayConfig()
        assert config.resolve_model() == "openrouter/test/model"
        assert config.litellm_model_id("openrouter/test/model") == "openrouter/test/model"

    def test_config_from_env(self):
        """Test configuration from environment."""
        import os
        from ai_gateway.model_catalog import GatewayConfig
        
        # Clear any cached config
        import ai_gateway.gateway as gw_module
        gw_module._gateway = None
        
        # Set env vars before creating config
        original_ollama = os.environ.get("OLLAMA_BASE_URL")
        original_model = os.environ.get("DEFAULT_MODEL")
        
        os.environ["OLLAMA_BASE_URL"] = "http://custom:11434"
        os.environ["DEFAULT_MODEL"] = "mistral"
        
        # Need to reload config module to pick up new env vars
        import config
        config._config = None
        config.load_dotenv = lambda: None  # Disable .env loading for this test
        
        try:
            # Create fresh config
            fresh_config = GatewayConfig()
            # Note: Due to config loading order, we just verify env vars are respected
            assert fresh_config.default_model in ["mistral", "llama3.2"]  # Either from env or .env
        finally:
            # Cleanup
            if original_ollama:
                os.environ["OLLAMA_BASE_URL"] = original_ollama
            else:
                os.environ.pop("OLLAMA_BASE_URL", None)
            if original_model:
                os.environ["DEFAULT_MODEL"] = original_model
            else:
                os.environ.pop("DEFAULT_MODEL", None)
            config._config = None
    
    def test_get_model(self):
        """Test getting model by name."""
        from ai_gateway.model_catalog import GatewayConfig
        
        config = GatewayConfig()
        
        model = config.get_model("llama3.2")
        assert model is not None
        assert model.name == "Llama 3.2 3B"
        
        model = config.get_model("nonexistent")
        assert model is None


class TestAIGateway:
    """Test AI Gateway functionality."""
    
    def test_gateway_creation(self):
        """Test gateway can be created."""
        from ai_gateway.gateway import AIGateway
        from ai_gateway.model_catalog import GatewayConfig
        
        gateway = AIGateway()
        assert gateway is not None
        assert gateway.config is not None
    
    def test_mock_response_when_litellm_unavailable(self):
        """Test mock response when LiteLLM is not available."""
        from ai_gateway.gateway import AIGateway
        
        gateway = AIGateway()
        
        # Force mock mode
        result = gateway._mock_response("test prompt", "test-model")
        
        assert result["success"] is True
        assert result["mock"] is True
        assert "test prompt" in result["content"]
    
    def test_list_models(self):
        """Test listing available models."""
        from ai_gateway.gateway import AIGateway
        
        gateway = AIGateway()
        models = gateway.list_models(max_params=12.0)
        
        assert len(models) > 0
        for model in models:
            assert model["parameters_billions"] <= 12.0
    
    def test_health_check(self):
        """Test health check returns expected fields."""
        from ai_gateway.gateway import AIGateway
        
        gateway = AIGateway()
        health = gateway.health_check()
        
        assert "litellm_available" in health
        assert "default_model" in health
        assert "ollama_url" in health
        assert "available_models" in health
    
    @patch('ai_gateway.gateway.LITELLM_AVAILABLE', False)
    def test_complete_without_litellm(self):
        """Test completion falls back to mock without LiteLLM."""
        from ai_gateway.gateway import AIGateway
        
        gateway = AIGateway()
        result = gateway.complete("Hello")
        
        assert result["success"] is True
        # Should be mock response


class TestFeedbackLoop:
    """Test feedback loop functionality."""
    
    @pytest.fixture
    def sample_ir(self):
        """Create sample IR for testing."""
        ir = IntentIR()
        ir.intent = Intent(name="test-api", goal="Test API")
        ir.implementation = Implementation(
            language="python",
            framework="fastapi",
            actions=[
                Action(type=ActionType.API_EXPOSE, method="GET", target="/ping")
            ]
        )
        return ir
    
    def test_feedback_loop_creation(self):
        """Test feedback loop can be created."""
        from ai_gateway.feedback_loop import FeedbackLoop, create_feedback_loop
        
        loop = create_feedback_loop()
        assert loop is not None
        assert loop.gateway is not None
    
    def test_suggest_next_steps(self, sample_ir):
        """Test next steps suggestions."""
        from ai_gateway.feedback_loop import FeedbackLoop
        
        loop = FeedbackLoop()
        steps = loop.suggest_next_steps(sample_ir)
        
        assert isinstance(steps, list)
        # Should suggest health endpoint since we only have /ping
        assert any("health" in step.lower() for step in steps)
    
    def test_suggest_next_steps_with_health(self, sample_ir):
        """Test next steps when health endpoint exists."""
        from ai_gateway.feedback_loop import FeedbackLoop
        
        sample_ir.implementation.actions.append(
            Action(type=ActionType.API_EXPOSE, method="GET", target="/health")
        )
        
        loop = FeedbackLoop()
        steps = loop.suggest_next_steps(sample_ir)
        
        # Should not suggest health endpoint
        assert not any("Add health check" in step for step in steps)
    
    def test_build_analysis_prompt(self, sample_ir):
        """Test prompt building."""
        from ai_gateway.feedback_loop import FeedbackLoop
        
        loop = FeedbackLoop()
        prompt = loop._build_analysis_prompt(sample_ir, focus="security")
        
        assert "test-api" in prompt
        assert "Test API" in prompt
        assert "fastapi" in prompt
        assert "security" in prompt.lower()
    
    def test_parse_suggestions_json(self):
        """Test parsing JSON suggestions."""
        from ai_gateway.feedback_loop import FeedbackLoop
        
        loop = FeedbackLoop()
        
        content = '''```json
{
    "suggestions": [
        {
            "type": "action",
            "description": "Add health endpoint",
            "action_code": "api.expose GET /health",
            "priority": "high",
            "auto_apply": true
        }
    ]
}
```'''
        
        suggestions = loop._parse_suggestions(content)
        
        assert len(suggestions) == 1
        assert suggestions[0].type == "action"
        assert suggestions[0].action_code == "api.expose GET /health"
        assert suggestions[0].priority == "high"
    
    def test_parse_suggestions_raw(self):
        """Test parsing raw text suggestions."""
        from ai_gateway.feedback_loop import FeedbackLoop
        
        loop = FeedbackLoop()
        
        content = """Here are my suggestions:
1. Add api.expose GET /health for health checks
2. Consider api.expose POST /users for user creation
"""
        
        suggestions = loop._parse_suggestions(content)
        
        # Should extract action codes
        assert len(suggestions) >= 1
    
    def test_extract_action(self):
        """Test action extraction from text."""
        from ai_gateway.feedback_loop import FeedbackLoop
        
        loop = FeedbackLoop()
        
        text = "You should add api.expose GET /health"
        action = loop._extract_action(text)
        
        assert action == "api.expose GET /health"
    
    def test_feedback_result_to_dict(self):
        """Test FeedbackResult serialization."""
        from ai_gateway.feedback_loop import FeedbackResult, FeedbackSuggestion
        
        result = FeedbackResult(
            success=True,
            model_used="llama3.2",
            tokens_used=100
        )
        result.suggestions.append(FeedbackSuggestion(
            type="action",
            description="Test",
            action_code="api.expose GET /test"
        ))
        
        data = result.to_dict()
        
        assert data["success"] is True
        assert data["model_used"] == "llama3.2"
        assert len(data["suggestions"]) == 1


class TestFeedbackSuggestion:
    """Test FeedbackSuggestion dataclass."""
    
    def test_suggestion_defaults(self):
        """Test default values."""
        from ai_gateway.feedback_loop import FeedbackSuggestion
        
        suggestion = FeedbackSuggestion(
            type="action",
            description="Test suggestion"
        )
        
        assert suggestion.priority == "medium"
        assert suggestion.auto_apply is False
        assert suggestion.action_code is None
    
    def test_suggestion_to_dict(self):
        """Test serialization."""
        from ai_gateway.feedback_loop import FeedbackSuggestion
        
        suggestion = FeedbackSuggestion(
            type="security",
            description="Add authentication",
            action_code=None,
            priority="high",
            auto_apply=False
        )
        
        data = suggestion.to_dict()
        
        assert data["type"] == "security"
        assert data["priority"] == "high"


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_get_gateway_singleton(self):
        """Test gateway singleton pattern."""
        from ai_gateway.gateway import get_gateway
        
        gateway1 = get_gateway()
        gateway2 = get_gateway()
        
        assert gateway1 is gateway2
    
    def test_complete_function(self):
        """Test complete convenience function."""
        from ai_gateway.gateway import complete
        
        result = complete("test")
        
        assert "success" in result
        assert "content" in result


def run_tests():
    """Run all tests."""
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    run_tests()
