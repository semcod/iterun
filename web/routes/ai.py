"""AI Gateway API routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from web.schemas import AIChatRequest, AICompletionRequest, AISuggestRequest

router = APIRouter(tags=["ai"])

try:
    from ai_gateway.gateway import get_gateway
    from ai_gateway.feedback_loop import create_feedback_loop

    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


def _intents_store():
    from web.app import intents_store

    return intents_store


@router.get("/health")
async def health():
    return {"status": "healthy", "version": "0.1.0", "ai_available": AI_AVAILABLE}


@router.get("/api/ai/status")
async def ai_status():
    if not AI_AVAILABLE:
        return {
            "available": False,
            "error": "AI Gateway not installed. Run: pip install litellm",
        }
    gateway = get_gateway()
    health = gateway.health_check()
    return {
        "available": True,
        "litellm_available": health["litellm_available"],
        "ollama_connected": health.get("ollama_connected", False),
        "default_model": health["default_model"],
        "ollama_url": health["ollama_url"],
        "available_models": health["available_models"],
        "error": health.get("error"),
    }


@router.get("/api/ai/models")
async def list_models(max_params: float = 12.0):
    if not AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="AI Gateway not available")
    gateway = get_gateway()
    models = gateway.list_models(max_params)
    return {
        "models": models,
        "default": gateway.config.default_model,
        "max_parameters": max_params,
    }


@router.post("/api/ai/complete")
async def ai_complete(request: AICompletionRequest):
    if not AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="AI Gateway not available")
    gateway = get_gateway()
    result = gateway.complete(
        prompt=request.prompt,
        model=request.model,
        system_prompt=request.system_prompt,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
    )
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Completion failed"))
    return result


@router.post("/api/ai/chat")
async def ai_chat(request: AIChatRequest):
    if not AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="AI Gateway not available")
    gateway = get_gateway()
    prompt = request.message
    if request.context:
        prompt = f"{request.context}\n\nUser: {request.message}"
    result = gateway.complete(prompt, temperature=0.7)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Chat failed"))
    return {
        "response": result["content"],
        "model": result["model"],
        "usage": result.get("usage"),
    }


@router.post("/api/intents/{intent_id}/ai/suggest")
async def ai_suggest(intent_id: str, request: AISuggestRequest = None):
    if not AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="AI Gateway not available")
    store = _intents_store()
    if intent_id not in store:
        raise HTTPException(status_code=404, detail="Intent not found")
    ir = store[intent_id]
    focus = request.focus if request else None
    loop = create_feedback_loop()
    result = loop.analyze(ir, focus)
    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)
    return {
        "success": True,
        "suggestions": [s.to_dict() for s in result.suggestions],
        "model": result.model_used,
        "tokens_used": result.tokens_used,
        "next_steps": loop.suggest_next_steps(ir),
    }


@router.post("/api/intents/{intent_id}/ai/apply")
async def ai_apply_suggestions(intent_id: str):
    if not AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="AI Gateway not available")
    store = _intents_store()
    if intent_id not in store:
        raise HTTPException(status_code=404, detail="Intent not found")
    ir = store[intent_id]
    loop = create_feedback_loop()
    result = loop.iterate(ir, auto_apply=True)
    return {
        "success": True,
        "applied_changes": result.applied_changes,
        "warnings": result.warnings,
        "suggestions": [s.to_dict() for s in result.suggestions],
        "intent": ir.to_dict(),
    }


@router.post("/api/ai/generate-code")
async def generate_code(description: str, language: str = "python", framework: str = None):
    if not AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="AI Gateway not available")
    gateway = get_gateway()
    result = gateway.generate_code_snippet(description, language, framework)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Code generation failed"))
    return result
