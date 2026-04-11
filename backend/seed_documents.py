"""
Load demo documents into PostgreSQL and ChromaDB using the same ingestion path as the API.

Usage (from this directory, with the backend virtualenv activated):

    python seed_documents.py

Set SEED_DEMO_DOCUMENTS_ON_STARTUP=true to run the same seed automatically when the API starts.
"""

from __future__ import annotations

import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def main() -> None:
    from app import models  # noqa: F401 — register models
    from app.db.session import Base, SessionLocal, engine
    from app.services.seed import seed_default_admin
    from app.services.seed_documents import seed_demo_documents

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_default_admin(db)
        stats = seed_demo_documents(db)
        print("Demo document seed:", stats)
        if stats["failed"]:
            sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
