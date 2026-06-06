"""
ITERUN: Web Interface
FastAPI-based web UI for intent management.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

sys.path.insert(0, str(Path(__file__).parent.parent))

from ir.models import IntentIR
from web.routes import ai, intents, registry

try:
    from ai_gateway.gateway import get_gateway  # noqa: F401

    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

app = FastAPI(
    title="ITERUN",
    description="DSL-based intent execution system with iterative refinement",
    version="0.1.0",
)

intents_store: Dict[str, IntentIR] = {}

templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

app.include_router(registry.router)
app.include_router(intents.router)
app.include_router(ai.router)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render main dashboard."""
    return templates.TemplateResponse(
        request,
        "index.html",
        {"intents": list(intents_store.values())},
    )


def create_app() -> FastAPI:
    """Factory function for creating the app."""
    return app


if __name__ == "__main__":
    import uvicorn

    from config import get_config

    config = get_config()
    uvicorn.run(app, host=config.host, port=config.port)
