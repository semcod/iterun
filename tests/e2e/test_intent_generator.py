"""Tests for LLM intent YAML generation and validation loop."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dsl.schema import EXAMPLE_YAML, get_json_schema, validate_yaml_document
from generator.intent_generator import IntentGenerator, extract_yaml_from_llm
from generator.pipeline import run_pipeline


class TestSchema:
    def test_json_schema_has_intent(self):
        schema = get_json_schema()
        assert "INTENT" in schema["$defs"] or "properties" in schema

    def test_example_yaml_valid(self):
        doc, errors = validate_yaml_document(EXAMPLE_YAML)
        assert not errors
        assert doc is not None
        assert doc.INTENT.name == "user-api"

    def test_invalid_yaml_rejected(self):
        bad = "INTENT:\n  name: BAD NAME\n  goal: x\nIMPLEMENTATION:\n  actions: []\n"
        doc, errors = validate_yaml_document(bad)
        assert errors


class TestExtractYaml:
    def test_strips_fences(self):
        raw = "```yaml\n" + EXAMPLE_YAML + "\n```"
        assert extract_yaml_from_llm(raw).startswith("INTENT:")

    def test_plain_yaml(self):
        assert extract_yaml_from_llm(EXAMPLE_YAML).startswith("INTENT:")


class TestIntentGenerator:
    def test_generate_success_mock(self):
        gateway = MagicMock()
        gateway.complete.return_value = {"success": True, "content": "[MOCK]", "mock": True}
        gen = IntentGenerator(gateway=gateway, max_iterations=3)
        result = gen.generate("Create a REST API for user management")
        assert result.success
        assert result.yaml_content
        assert result.ir is not None
        assert result.ir.intent.name == "user-api"

    def test_retry_on_invalid_llm_output(self):
        gateway = MagicMock()
        gateway.complete.side_effect = [
            {
                "success": True,
                "content": "not yaml at all",
                "model": "test",
            },
            {
                "success": True,
                "content": "[MOCK]",
                "mock": True,
                "model": "test",
            },
        ]
        gen = IntentGenerator(gateway=gateway, max_iterations=3)
        result = gen.generate("Create a REST API for user management")
        assert result.success
        assert len(result.attempts) == 2

    def test_fails_after_max_iterations(self):
        gateway = MagicMock()
        gateway.complete.return_value = {
            "success": True,
            "content": "garbage",
            "model": "test",
        }
        gen = IntentGenerator(gateway=gateway, max_iterations=2)
        result = gen.generate("broken")
        assert not result.success
        assert len(result.attempts) == 2


class TestPipeline:
    def test_pipeline_generate_only(self, tmp_path):
        gateway = MagicMock()
        gateway.complete.return_value = {"success": True, "content": "[MOCK]", "mock": True}
        gen = IntentGenerator(gateway=gateway)
        # patch via run_pipeline internal - use mock gateway through env
        import generator.pipeline as pipe_mod
        original = pipe_mod.IntentGenerator
        pipe_mod.IntentGenerator = lambda **kw: IntentGenerator(gateway=gateway, **kw)
        try:
            result = run_pipeline(
                "Create a REST API for user management",
                output_dir=tmp_path,
                execute=False,
            )
        finally:
            pipe_mod.IntentGenerator = original
        assert result.success
        assert (tmp_path / "intent.yaml").is_file()
        assert (tmp_path / "app.py").is_file()
