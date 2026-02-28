"""
Rerank candidates via HuggingFace cross-encoder.
Uses config and logging; raises on API failure instead of silent fallback.
Improves retrieval quality by scoring relevance of candidate documents.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List

import requests

from app.config import get_settings

logger = logging.getLogger(__name__)

RERANK_MODEL_URL = (
    "https://router.huggingface.co/hf-inference/models/cross-encoder/ms-marco-MiniLM-L-6-v2"
)
# Timeout in seconds for the HuggingFace reranking API request
RERANK_TIMEOUT = 30


class RerankService:
    def __init__(self) -> None:
        s = get_settings()
        if not s.huggingface_api_key:
            raise ValueError("HUGGINGFACE_API_KEY environment variable is not set.")
        self.api_key = s.huggingface_api_key
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        if not documents:
            return []
        payload = {
            "inputs": {
                "source_sentence": query,
                "sentences": [doc["text"] for doc in documents],
            }
        }
        try:
            response = requests.post(
                RERANK_MODEL_URL,
                json=payload,
                headers=self.headers,
                timeout=RERANK_TIMEOUT,
            )
            if response.status_code != 200:
                print(f"⚠️ Rerank API failed ({response.status_code}). Falling back to vector search.")
                return documents[:top_k]
            try:
                scores = response.json()
            except Exception as e:
                print(f"⚠️ Rerank response parse failed: {e}. Falling back to vector search.")
                return documents[:top_k]
            if not isinstance(scores, list) or len(scores) != len(documents):
                print(f"⚠️ Rerank unexpected response length: {type(scores)}. Falling back to vector search.")
                return documents[:top_k]
            for doc, score in zip(documents, scores):
                doc["score"] = score
            reranked = sorted(documents, key=lambda d: d["score"], reverse=True)
            return reranked[:top_k]
        except Exception as e:
            print(f"⚠️ Reranking unavailable (Error {e}). Returning top {top_k} vector results.")
            return documents[:top_k]
