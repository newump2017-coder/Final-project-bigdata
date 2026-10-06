from pymongo import MongoClient
from config.settings import settings


class MongoManager:
    """Context manager for MongoDB connections."""

    def __init__(self):
        self.client = None
        self.db = None

    def __enter__(self):
        self.client = MongoClient(settings.MONGODB_URI)
        self.db = self.client[settings.DB_NAME]
        return self.db

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            self.client.close()


def get_db():
    """Return a MongoDB database handle (caller must close client)."""
    client = MongoClient(settings.MONGODB_URI)
    return client, client[settings.DB_NAME]
