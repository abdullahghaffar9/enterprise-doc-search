"""
Upload PDF documents: validate, ingest, upsert to vector store.
Business logic lives in services; routes handle HTTP only.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas import UploadResponse
from app.services.ingestion import process_pdf
from app.services.vector import VectorService

logger = logging.getLogger(__name__)

router = APIRouter()
vector_service = VectorService()


@router.post("", response_model=UploadResponse, status_code=200)
async def upload_document(file: UploadFile = File(...)) -> UploadResponse:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        content = await file.read()
    except Exception as e:
        logger.exception("Failed to read uploaded file %s", file.filename)
        raise HTTPException(status_code=400, detail="Failed to read file.") from e

    try:
        chunks = process_pdf(content, file.filename)
    except ValueError as e:
        logger.warning("Ingestion validation failed for %s: %s", file.filename, e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.exception("PDF processing failed for %s", file.filename)
        raise HTTPException(status_code=422, detail="PDF processing failed.") from e

    if not chunks:
        raise HTTPException(
            status_code=400,
            detail="The PDF appears to be empty or image-only. Use a text-based PDF.",
        )

    try:
        await vector_service.upsert_chunks(chunks)
    except Exception as e:
        logger.exception("Vector upsert failed for %s", file.filename)
        raise HTTPException(status_code=503, detail="Document indexing failed. Try again later.") from e

    logger.info("Uploaded %s: %d chunks", file.filename, len(chunks))
    return {"status": "success", "filename": file.filename, "chunks": len(chunks)}
