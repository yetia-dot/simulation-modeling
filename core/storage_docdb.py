# core/storage_docdb.py
import simpy
import random
from config import STORAGE_WRITE_MEAN, STORAGE_WRITE_STD

class DocumentDB:
    """
    Simulated document-style database (MongoDB-like).
    """
    def __init__(self, env: simpy.Environment):
        self.env = env
        self.store = {}  # key -> dict

    def write(self, key: str, doc: dict):
        """
        Simulate a document write with delay.
        """
        delay = max(0.0, random.gauss(STORAGE_WRITE_MEAN, STORAGE_WRITE_STD))
        yield self.env.timeout(delay)
        self.store[key] = doc

    def read(self, key: str):
        return self.store.get(key, None)
