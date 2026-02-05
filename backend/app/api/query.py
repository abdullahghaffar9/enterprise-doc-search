"""
Query documents: vector search -> rerank -> LLM answer.
Uses schemas, structured error handling, and logging.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException

from app.schemas import QueryRequest, QueryResponse, SourceDoc
from app.services.llm import LLMService
from app.services.rerank import RerankService
from app.services.vector import VectorService

logger = logging.getLogger(__name__)

router = APIRouter()
vector_service = VectorService()
rerank_service = RerankService()
llm_service = LLMService()


def _to_source_docs(docs: List[Dict[str, Any]]) -> List[SourceDoc]:
    return [
        SourceDoc(
            text=d.get("text", ""),
            score=d.get("score"),
            metadata=d.get("metadata"),
        )
        for d in docs
    ]



@router.post("/", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    try:
        # 1. Vector Search
        results = await vector_service.search(
            request.query, 
            k=20 if getattr(request, 'rerank', False) else 5
        )
        
        if not results:
            return QueryResponse(
                answer="No relevant information found.",
                sources=[]
            )

        # 2. Select Top Results (Skip Rerank if it fails, or just take top 5)
        top_docs = results[:5]

        # 3. Format Output as "Search Results"
        formatted_answer = "### 🔍 Top Search Results\n\n"
        for i, doc in enumerate(top_docs, 1):
            text = doc['metadata'].get('text', 'No text content')
            formatted_answer += f"**Result {i}** (Score: {doc.get('score', 0):.2f}):\n> {text}\n\n---\n\n"

        return QueryResponse(
            answer=formatted_answer,
            sources=[
                SourceDoc(
                    text=doc['metadata'].get('text', ''),
                    metadata=doc['metadata'],
                    score=doc.get('score', 0.0)
                ) for doc in top_docs
            ]
        )

    except Exception as e:
        print(f"❌ Search Error: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Search failed: {str(e)}")
