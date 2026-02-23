"""
Pydantic request/response schemas for all API endpoints.
Defines data contracts for upload, query, and other operations.
"""
from __future__ import annotations

from typing import Any, List, Optional

from pydantic import BaseModel, Field


# ----- Upload -----
class UploadResponse(BaseModel):
    status: str = "success"
    filename: str
    chunks: int


# ----- Query -----
class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="User question")


class SourceDoc(BaseModel):
    text: str
    score: Optional[float] = None
    metadata: Optional[dict[str, Any]] = None


class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceDoc] = Field(default_factory=list)
