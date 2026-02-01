"""
Centralized configuration via environment variables.
Uses pydantic-settings for validation and safe defaults.
"""
from __future__ import annotations

from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from env. Never hardcode secrets."""
    # Groq model for answer generation
    groq_model: str = "llama3-8b-8192"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # HuggingFace generation model (LLM)
    hf_gen_model: str = "mistralai/Mistral-7B-Instruct-v0.3"

    # Pinecone (required for vector store)
    pinecone_api_key: str = ""
    pinecone_index_name: str = ""
    pinecone_region: str = "us-east-1"

    # HuggingFace (embeddings, rerank, optional LLM)
    huggingface_api_key: str = ""

    # Groq (optional, for answer polishing)
    groq_api_key: str = ""

    # Server
    port: int = 8000
    environment: str = "development"

    # CORS
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"

    def cors_origins_list(self) -> List[str]:
        if not self.allowed_origins.strip():
            return []
        return [x.strip() for x in self.allowed_origins.split(",") if x.strip()]



def get_settings() -> Settings:
    return Settings()
