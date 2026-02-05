
import os
import logging
from typing import List, Optional
from pinecone import Pinecone
from fastembed import TextEmbedding

logger = logging.getLogger(__name__)

class VectorService:
    def __init__(self):
        try:
            logger.info("[VectorService] Initializing Pinecone...")
            self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
            logger.info("[VectorService] Pinecone client created.")
            self.index_name = os.getenv("PINECONE_INDEX_NAME")
            if self.index_name is None:
                raise ValueError("PINECONE_INDEX_NAME environment variable is not set.")
            logger.info(f"[VectorService] Index name: {self.index_name}")
            self.index = self.pc.Index(self.index_name)
            logger.info("[VectorService] Pinecone index initialized.")

            # LAZY LOAD FastEmbed Model (ONNX Runtime) - loaded only on first use
            # This saves significant memory during app startup (critical for Render Free Tier 512MB limit)
            self.model: Optional[TextEmbedding] = None
            logger.info("[VectorService] FastEmbed model will be loaded on first use (lazy loading enabled).")
        except Exception as e:
            logger.error(f"[VectorService] Initialization failed: {str(e)}")
            raise e

    def _load_model(self):
        """Load the FastEmbed model lazily on first use."""
        if self.model is None:
            logger.info("[VectorService] Loading FastEmbed model (BAAI/bge-small-en-v1.5)...")
            self.model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
            logger.info("[VectorService] FastEmbed model loaded successfully.")

    def clear_index(self):
        """
        Delete all vectors in the Pinecone index.
        """
        print("[VectorService] Deleting all vectors in the index...")
        self.index.delete(delete_all=True)
        print("[VectorService] Index cleared.")

    async def embed_chunks(self, chunks: List[str]) -> List[List[float]]:
        """
        Generates embeddings locally using FastEmbed (ONNX Runtime).
        Handles generator output from TextEmbedding.embed().
        """
        try:
            self._load_model()  # Lazy load model on first use
            assert self.model is not None, "Model should be loaded by _load_model()"
            # FastEmbed returns a generator, convert to list then to standard Python lists
            embeddings_generator = self.model.embed(chunks)
            embeddings_list = list(embeddings_generator)
            # Convert numpy arrays to standard Python lists for Pinecone compatibility
            embeddings = [emb.tolist() if hasattr(emb, 'tolist') else list(emb) for emb in embeddings_list]
            logger.debug(f"Generated {len(embeddings)} embeddings")
            return embeddings
        except Exception as e:
            logger.error(f"❌ Embedding Error: {str(e)}")
            raise e

    async def upsert_chunks(self, chunks_data: List[dict]):
        """
        Embeds and upserts chunks to Pinecone.
        Skips and logs empty/whitespace chunks. Raises if none valid.
        """
        try:
            valid_chunks = []
            for chunk in chunks_data:
                if not chunk.get("text", "").strip():
                    print(f"⚠️ Skipped empty chunk {chunk.get('id', '[no id]')}")
                    continue
                valid_chunks.append(chunk)
            if not valid_chunks:
                raise ValueError("No valid text chunks to upload.")

            # Use deterministic IDs: filename_chunk_{i}
            for i, chunk in enumerate(valid_chunks):
                filename = chunk.get("filename", "file")
                chunk["id"] = f"{filename}_chunk_{i}"

            texts = [chunk["text"] for chunk in valid_chunks]
            embeddings = await self.embed_chunks(texts)

            vectors = []
            for i, chunk in enumerate(valid_chunks):
                # Ensure text is in metadata
                if "text" not in chunk.get("metadata", {}):
                    chunk.setdefault("metadata", {})["text"] = chunk["text"]
                vectors.append({
                    "id": chunk["id"],
                    "values": embeddings[i],
                    "metadata": chunk["metadata"]
                })

            # Upsert in batches of 100
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                self.index.upsert(vectors=batch)
                print(f"Upserted batch {i//batch_size + 1}")

            return len(vectors)
        except Exception as e:
            print(f"❌ Upsert Failed: {str(e)}")
            raise e

    async def search(self, query: str, k: int = 5):
        """
        Searches Pinecone using a locally generated query embedding via FastEmbed.
        """
        try:
            self._load_model()  # Lazy load model on first use
            assert self.model is not None, "Model should be loaded by _load_model()"
            # 1. Embed Query Locally using FastEmbed
            query_embeddings = list(self.model.embed([query]))
            query_embedding = query_embeddings[0]
            # Convert numpy array to list if needed
            query_embedding = query_embedding.tolist() if hasattr(query_embedding, 'tolist') else list(query_embedding)
            
            logger.debug(f"Generated query embedding with dimension {len(query_embedding)}")
            
            # 2. Query Pinecone
            result = self.index.query(
                vector=query_embedding,
                top_k=k,
                include_metadata=True
            )
            logger.info(f"Query result: {result}")
            # If result is a dict, try to access 'matches' key; else, use getattr
            if isinstance(result, dict):
                matches = result["matches"] if "matches" in result else None
            else:
                matches = getattr(result, "matches", None)
            logger.info(f"Query returned {len(matches) if matches else 0} matches")
            return matches
        except Exception as e:
            logger.error(f"❌ Search Failed: {str(e)}")
            raise e
