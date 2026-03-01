import io
from pypdf import PdfReader
from typing import List, Dict, Any
import re
import uuid
import logging

# PDF processing and text chunking utilities for document ingestion
def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Splits text into chunks of up to chunk_size, with optional overlap.
    Tries to split on paragraph, newline, sentence, or space boundaries.
    """
    # Try to split by paragraph, newline, sentence, then space
    seps = ['\n\n', '\n', '. ', ' ']
    for sep in seps:
        parts = text.split(sep)
        if len(parts) == 1:
            continue
        chunks = []
        current = ""
        for part in parts:
            if current:
                candidate = current + sep + part
            else:
                candidate = part
            if len(candidate) > chunk_size:
                if current:
                    chunks.append(current)
                    current = part
                else:
                    # Single word/part too long
                    chunks.append(part)
                    current = ""
            else:
                current = candidate
        if current:
            chunks.append(current)
        # Recursively split chunks that are still too large after the first pass
        result = []
        for chunk in chunks:
            if len(chunk) > chunk_size:
                result.extend(_chunk_text(chunk, chunk_size, overlap))
            else:
                result.append(chunk)
        break
    else:
        # Fallback: hard-split every chunk_size chars when no separator is found
        result = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

    # Add overlap: prepend the tail of the previous chunk to improve context continuity
    final_chunks = []
    for i, chunk in enumerate(result):
        if i > 0 and overlap > 0:
            prev = result[i - 1]
            overlap_text = prev[-overlap:] if len(prev) > overlap else prev
            chunk = overlap_text + chunk
        final_chunks.append(chunk.strip())
    return final_chunks

# Extracts text from every page of a PDF, cleans it, then partitions into chunks
def process_pdf(file_bytes: bytes, filename: str) -> List[Dict[str, Any]]:
    logger = logging.getLogger(__name__)
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
    except Exception as e:
        logger.error("Failed to read PDF: %s", e)
        raise ValueError(f"Failed to read PDF: {e}") from e
    pages = list(reader.pages)
    logger.debug("Extracted %d pages", len(pages))
    documents = []
    chunks_total = 0
    empty_pages = 0
    all_text = ""
    for i, page in enumerate(pages, start=1):
        try:
            text = page.extract_text()
            if text is None:
                text = ""
        except Exception:
            text = ""
        text = text.strip()
        if not text:
            logger.warning("Page %d is empty; possible scanned image", i)
            empty_pages += 1
            continue
        # --- PDF TEXT CLEANING ---
        # 1. Fix hyphenated line breaks (e.g., "intell-\n igence" -> "intelligence")
        text = text.replace('-\n', '')
        # 2. Replace all newlines with spaces
        text = text.replace('\n', ' ')
        # 3. Collapse multiple spaces to a single space
        text = re.sub(r'\s+', ' ', text).strip()
        if not text:
            logger.warning("Page %d is empty after cleaning; possible scanned image", i)
            empty_pages += 1
            continue
        all_text += text
        chunks = _chunk_text(text)
        logger.debug("Created %d text chunks", len(chunks))
        if len(chunks) == 0:
            logger.warning("No text found in %s; possible scanned image", filename)
        chunks_total += len(chunks)
        for idx, chunk_text in enumerate(chunks):
            documents.append({
                "id": f"{filename}_chunk_{idx}",
                "text": chunk_text,
                "metadata": {
                    "text": chunk_text,
                    "filename": filename,
                    "page_number": i,
                    "chunk_index": idx
                }
            })
    if len(all_text.strip()) < 10:
        logger.error("This PDF appears to be empty or scanned. No text could be extracted.")
        raise ValueError("This PDF appears to be empty or scanned. No text could be extracted.")
    logger.debug("Total chunks created: %d", chunks_total)
    return documents
