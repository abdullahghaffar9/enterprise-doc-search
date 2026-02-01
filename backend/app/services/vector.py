
import os
from typing import List
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

class VectorService:
    def __init__(self):
        print("[VectorService] Initializing Pinecone...")
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        print("[VectorService] Pinecone client created.")
        self.index_name = os.getenv("PINECONE_INDEX_NAME")
        print(f"[VectorService] Index name: {self.index_name}")
        self.index = self.pc.Index(self.index_name)
        print("[VectorService] Pinecone index initialized.")

        # 2. Initialize Local Embedding Model (CPU compatible)
        print("[VectorService] Loading local embedding model (all-MiniLM-L6-v2)...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        print("[VectorService] Embedding model loaded.")

    def clear_index(self):
        """
        Delete all vectors in the Pinecone index.
        """
        print("[VectorService] Deleting all vectors in the index...")
        self.index.delete(delete_all=True)
        print("[VectorService] Index cleared.")

    async def embed_chunks(self, chunks: List[str]) -> List[List[float]]:
        """
        Generates embeddings locally.
        """
        try:
            # model.encode returns a numpy array, convert to list for Pinecone
            embeddings = self.model.encode(chunks)
            return embeddings.tolist()
        except Exception as e:
            print(f"❌ Embedding Error: {str(e)}")
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
        Searches Pinecone using a locally generated query embedding.
        """
        try:
            # 1. Embed Query Locally
            query_embedding = self.model.encode([query])[0].tolist()
            
            # 2. Query Pinecone
            result = self.index.query(
                vector=query_embedding,
                top_k=k,
                include_metadata=True
            )
            return result.matches
        except Exception as e:
            print(f"❌ Search Failed: {str(e)}")
            raise e
