"""
Smoke test: import app, hit /health. Uses logging (no emojis) for Windows compat.
"""
from __future__ import annotations

import logging
import os
import sys

from fastapi.testclient import TestClient

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_startup() -> None:
    logger.info("----------------------------------------------------------------")
    logger.info("SMOKE TEST: Attempting to import FastAPI App...")
    try:
        from app.main import app
        logger.info("SUCCESS: App imported successfully.")
    except ImportError as e:
        logger.error("CRITICAL: Import failed. %s", e)
        sys.exit(1)
    except Exception as e:
        logger.error("CRITICAL: App failed to initialize. %s", e)
        sys.exit(1)

    logger.info("SMOKE TEST: Checking Health Endpoint...")
    client = TestClient(app)
    try:
        response = client.get("/health")
        if response.status_code == 200:
            logger.info("SUCCESS: Health Check Passed: %s", response.json())
        else:
            logger.error("FAILURE: Health Check returned %s", response.status_code)
            sys.exit(1)
    except Exception as e:
        logger.error("CRITICAL: Could not contact endpoint. %s", e)
        sys.exit(1)

    logger.info("----------------------------------------------------------------")
    logger.info("SYSTEM READY FOR DEPLOYMENT")


if __name__ == "__main__":
    test_startup()
