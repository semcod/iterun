"""
ITERUN: Feedback Loop
LLM-powered iterative refinement of intents.
"""

import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from ir.models import IntentIR, Action, ActionType
from ai_gateway.gateway import AIGateway, get_gateway
from ai_gateway.model_catalog import GatewayConfig


@dataclass
class FeedbackSuggestion:
    """A single improvement suggestion."""
    type: str  # 'action', 'config', 'security', 'performance'
    description: str
    action_code: Optional[str] = None  # DSL action string if applicable
    priority: str = "medium"  # low, medium, high
    auto_apply: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "description": self.description,
            "action_code": self.action_code,
            "priority": self.priority,
            "auto_apply": self.auto_apply
        }


@dataclass
class FeedbackResult:
    """Result of feedback loop iteration."""
    success: bool = True
    suggestions: List[FeedbackSuggestion] = field(default_factory=list)
    applied_changes: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    model_used: Optional[str] = None
    tokens_used: int = 0
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "suggestions": [s.to_dict() for s in self.suggestions],
            "applied_changes": self.applied_changes,
            "warnings": self.warnings,
            "model_used": self.model_used,
            "tokens_used": self.tokens_used,
            "error": self.error
        }


class FeedbackLoop:
    """
    LLM-powered feedback loop for iterative intent refinement.
    Uses AI Gateway to suggest and apply improvements.
    """
    
    SYSTEM_PROMPT = """You are an expert software architect helping to improve intent definitions for a DSL-based deployment system.

The system uses these action types:
- api.expose METHOD /path - Expose HTTP endpoint
- db.create table_name - Create database table
- db.add_column table column type - Add column
- shell.exec command - Execute shell command
- rest.call METHOD url - Call external API
- file.create path - Create file

Analyze intents and suggest improvements focusing on:
1. Missing functionality (additional endpoints, error handling)
2. Security (authentication, validation, rate limiting)
3. Performance (caching, async operations)
4. Best practices (health checks, metrics, logging)

Always respond in valid JSON format."""

    def __init__(self, gateway: AIGateway = None, model: str = None):
        self.gateway = gateway or get_gateway()
        self.model = model or self.gateway.config.default_model
    
    def analyze(self, ir: IntentIR, focus: str = None) -> FeedbackResult:
        """
        Analyze intent and generate improvement suggestions.
        
        Args:
            ir: IntentIR to analyze
            focus: Optional focus area ('security', 'performance', 'features')
            
        Returns:
            FeedbackResult with suggestions
        """
        result = FeedbackResult()
        
        prompt = self._build_analysis_prompt(ir, focus)
        
        response = self.gateway.complete(
            prompt,
            model=self.model,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.7
        )
        
        if not response["success"]:
            result.success = False
            result.error = response.get("error", "Unknown error")
            return result
        
        result.model_used = response.get("model")
        if response.get("usage"):
            result.tokens_used = response["usage"].get("total_tokens", 0)
        
        # Parse suggestions from response
        suggestions = self._parse_suggestions(response["content"])
        result.suggestions = suggestions
        
        return result
    
    def apply_suggestions(
        self,
        ir: IntentIR,
        suggestions: List[FeedbackSuggestion],
        auto_only: bool = True
    ) -> FeedbackResult:
        """
        Apply suggestions to the intent.
        
        Args:
            ir: IntentIR to modify
            suggestions: List of suggestions to apply
            auto_only: Only apply suggestions marked as auto_apply
            
        Returns:
            FeedbackResult with applied changes
        """
        result = FeedbackResult()
        
        for suggestion in suggestions:
            if auto_only and not suggestion.auto_apply:
                continue
            
            if suggestion.action_code:
                try:
                    action = self._parse_action(suggestion.action_code)
                    if action:
                        ir.implementation.actions.append(action)
                        result.applied_changes.append(
                            f"Added action: {suggestion.action_code}"
                        )
                except Exception as e:
                    result.warnings.append(
                        f"Failed to apply '{suggestion.action_code}': {e}"
                    )
        
        if result.applied_changes:
            ir.add_iteration(
                {"auto_applied": [s.to_dict() for s in suggestions if s.auto_apply]},
                source="feedback_loop"
            )
        
        return result
    
    def iterate(
        self,
        ir: IntentIR,
        user_feedback: str = None,
        focus: str = None,
        auto_apply: bool = False
    ) -> FeedbackResult:
        """
        Perform one iteration of the feedback loop.
        
        Args:
            ir: IntentIR to improve
            user_feedback: Optional user feedback to incorporate
            focus: Focus area for improvements
            auto_apply: Automatically apply high-priority suggestions
            
        Returns:
            FeedbackResult with suggestions and applied changes
        """
        # First, analyze
        analysis = self.analyze(ir, focus)
        
        if not analysis.success:
            return analysis
        
        # Incorporate user feedback if provided
        if user_feedback:
            feedback_suggestions = self._process_user_feedback(ir, user_feedback)
            analysis.suggestions.extend(feedback_suggestions)
        
        # Auto-apply if requested
        if auto_apply:
            apply_result = self.apply_suggestions(
                ir,
                analysis.suggestions,
                auto_only=False
            )
            analysis.applied_changes = apply_result.applied_changes
            analysis.warnings.extend(apply_result.warnings)
        
        return analysis
    
    def suggest_next_steps(self, ir: IntentIR) -> List[str]:
        """Get list of suggested next steps for the intent."""
        suggestions = []
        
        # Check for common missing elements
        actions = [a.type for a in ir.implementation.actions]
        endpoints = [a.target for a in ir.implementation.actions if a.type == ActionType.API_EXPOSE]
        
        if not any("/health" in (e or "") for e in endpoints):
            suggestions.append("Add health check endpoint: api.expose GET /health")
        
        if not any("/ping" in (e or "") for e in endpoints):
            suggestions.append("Add ping endpoint: api.expose GET /ping")
        
        if ir.implementation.framework == "fastapi":
            if not any("/docs" in (e or "") for e in endpoints):
                suggestions.append("FastAPI includes /docs automatically for OpenAPI")
        
        if len(ir.implementation.actions) < 3:
            suggestions.append("Consider adding more endpoints for a complete API")
        
        if not ir.dry_run_logs:
            suggestions.append("Run dry-run to see generated code and validate intent")
        
        if ir.iteration_count == 0:
            suggestions.append("Use 'iterate' command to refine the intent with LLM assistance")
        
        return suggestions
    
    def _build_analysis_prompt(self, ir: IntentIR, focus: str = None) -> str:
        """Build prompt for analysis."""
        prompt = f"""Analyze this intent and suggest improvements:

## Intent
- Name: {ir.intent.name}
- Goal: {ir.intent.goal}
- Description: {ir.intent.description or 'N/A'}

## Environment
- Runtime: {ir.environment.runtime.value}
- Base Image: {ir.environment.base_image}

## Implementation
- Language: {ir.implementation.language}
- Framework: {ir.implementation.framework or 'None'}
- Actions ({len(ir.implementation.actions)}):
"""
        for action in ir.implementation.actions:
            prompt += f"  - {action.type.value} {action.method or ''} {action.target or ''}\n"
        
        if focus:
            prompt += f"\n## Focus Area: {focus}\n"
            prompt += f"Please prioritize suggestions related to {focus}.\n"
        
        prompt += """
## Response Format
Respond with a JSON object:
{
  "suggestions": [
    {
      "type": "action|config|security|performance",
      "description": "What to improve",
      "action_code": "api.expose GET /new-endpoint",
      "priority": "low|medium|high",
      "auto_apply": false
    }
  ],
  "summary": "Brief summary of analysis"
}"""
        
        return prompt
    
    def _parse_suggestions(self, content: str) -> List[FeedbackSuggestion]:
        """Parse suggestions from LLM response."""
        suggestions = []
        
        try:
            # Extract JSON from response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            data = json.loads(content.strip())
            
            for s in data.get("suggestions", []):
                suggestions.append(FeedbackSuggestion(
                    type=s.get("type", "action"),
                    description=s.get("description", ""),
                    action_code=s.get("action_code"),
                    priority=s.get("priority", "medium"),
                    auto_apply=s.get("auto_apply", False)
                ))
        
        except json.JSONDecodeError:
            # Fallback: extract action suggestions from raw text
            lines = content.split("\n")
            for line in lines:
                if "api.expose" in line or "db.create" in line:
                    suggestions.append(FeedbackSuggestion(
                        type="action",
                        description=line.strip(),
                        action_code=self._extract_action(line)
                    ))
        
        return suggestions
    
    def _extract_action(self, text: str) -> Optional[str]:
        """Extract action code from text."""
        for action_type in ["api.expose", "db.create", "db.add_column", "shell.exec", "rest.call", "file.create"]:
            if action_type in text:
                start = text.find(action_type)
                # Find end of action (newline or end of string)
                end = text.find("\n", start)
                if end == -1:
                    end = len(text)
                return text[start:end].strip()
        return None
    
    def _parse_action(self, action_str: str) -> Optional[Action]:
        """Parse action string into Action object."""
        from parser.dsl_parser import DSLParser
        parser = DSLParser()
        return parser._parse_action(action_str)
    
    def _process_user_feedback(
        self,
        ir: IntentIR,
        feedback: str
    ) -> List[FeedbackSuggestion]:
        """Process natural language user feedback."""
        prompt = f"""Convert this user feedback into actionable suggestions:

User feedback: "{feedback}"

Current intent: {ir.intent.name}
Current actions: {[a.target for a in ir.implementation.actions]}

Respond with JSON:
{{
  "suggestions": [
    {{
      "type": "action",
      "description": "description",
      "action_code": "api.expose GET /endpoint",
      "priority": "high",
      "auto_apply": true
    }}
  ]
}}"""
        
        response = self.gateway.complete(
            prompt,
            model=self.model,
            system_prompt="Convert user feedback to DSL actions. Be concise.",
            temperature=0.5
        )
        
        if response["success"] and response["content"]:
            return self._parse_suggestions(response["content"])
        
        return []


def create_feedback_loop(model: str = None) -> FeedbackLoop:
    """Create a new FeedbackLoop instance."""
    return FeedbackLoop(model=model)


def analyze_intent(ir: IntentIR, focus: str = None) -> FeedbackResult:
    """Convenience function to analyze an intent."""
    loop = FeedbackLoop()
    return loop.analyze(ir, focus)
