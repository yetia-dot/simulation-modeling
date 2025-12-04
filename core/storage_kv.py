# core/storage_kv.py
import simpy
import random
from config import STORAGE_WRITE_MEAN, STORAGE_WRITE_STD

class KeyValueDB:
    """
    Simulated key-value store (PostgreSQL-like).
    """
    def __init__(self, env: simpy.Environment):
        self.env = env
        self.store = {}  # key -> value

    def write(self, key: str, value):
        """
        Simulate a key-value write with delay.
        """
        delay = max(0.0, random.gauss(STORAGE_WRITE_MEAN, STORAGE_WRITE_STD))
        yield self.env.timeout(delay)
        self.store[key] = value

    def read(self, key: str):
        return self.store.get(key, None)
