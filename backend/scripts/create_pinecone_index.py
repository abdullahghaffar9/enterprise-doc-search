"""
Create Pinecone index if missing. Uses logging (no emojis) for Windows compat.
"""
import logging
import os

from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

api_key = os.getenv("PINECONE_API_KEY")
index_name = os.getenv("PINECONE_INDEX_NAME", "developer-quickstart-py")

pc = Pinecone(api_key=api_key)

if not pc.list_indexes() or index_name not in pc.list_indexes():
    logger.info("Creating Pinecone index: %s", index_name)
    pc.create_index(
        name=index_name,
        dimension=384,
        metric="cosine",
        spec={
            "serverless": {
                "cloud": "aws",
                "region": "us-east-1",
            },
        },
    )
    logger.info("Index created.")
else:
    logger.info("Index '%s' already exists.", index_name)
