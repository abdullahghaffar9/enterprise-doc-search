import sys
import os
from dotenv import load_dotenv
load_dotenv()
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))
from services.vector import VectorService

if __name__ == "__main__":
    vector_service = VectorService()
    vector_service.clear_index()
    print("Pinecone index cleared.")