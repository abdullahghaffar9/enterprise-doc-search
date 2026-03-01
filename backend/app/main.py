

from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from backend directory (parent of app directory)
# Configuration is loaded early to ensure all env variables are available
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
print(f"[DEBUG] Loading .env from: {env_path}")
print(f"[DEBUG] .env exists: {env_path.exists()}")
print(f"[DEBUG] PINECONE_API_KEY from env: {os.environ.get('PINECONE_API_KEY')}")

"""
AI Document QA API: upload PDFs, query via RAG.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import query, upload
from app.config import get_settings
from app.logging_config import setup_logging

setup_logging(level="INFO")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield


def _make_app() -> FastAPI:
    # Factory function keeps app creation testable and isolated from module-level side effects
    app = FastAPI(title="AI Document QA API", lifespan=lifespan)
    
    # Get CORS origins from settings
    settings = get_settings()
    cors_origins = settings.cors_origins_list()
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins if cors_origins else ["*"],  # Allow all if not configured
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
    app.include_router(query.router, prefix="/api/query", tags=["Query"])

    @app.get("/health")
    def health_check() -> dict:
        # Lightweight liveness probe used by deployment platforms (Render, Railway, etc.)
        return {"status": "healthy"}

    return app


app = _make_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=get_settings().port)
