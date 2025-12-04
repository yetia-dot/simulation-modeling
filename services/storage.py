import simpy
import random
from config import STORAGE_WRITE_MEAN, STORAGE_WRITE_STD

class Storage:
    """
    Simple document-style storage with simulated write latency.
    Fully instrumented with logging + metrics in the unified format.
    """

    def __init__(self, env: simpy.Environment, metrics=None, name="storage"):
        self.env = env
        self.metrics = metrics
        self.name = name
        self.store = {}

    def _log(self, msg: str):
        msg_str = f"{self.env.now:.3f}: STORAGE {msg}"
        (msg_str)
        if self.metrics:
            self.metrics.log_event(msg_str)

    def write(self, key, value):
        """
        Returns ONLY the generator process — callers wrap in env.process().
        """
        return self._do_write(key, value)

    def read(self, key):
        val = self.store.get(key, None)
        self._log(f"READ key={key} -> {val}")
        return val

    def _do_write(self, key, value):
        latency = max(0.01, random.gauss(STORAGE_WRITE_MEAN, STORAGE_WRITE_STD))
        start = self.env.now

        yield self.env.timeout(latency)
        self.store[key] = value

        duration = self.env.now - start
        self._log(f"WRITE key={key} latency={duration:.3f} value={value}")

        if self.metrics:
            self.metrics.record(
                "storage_write_latency",
                duration,
                timestamp=self.env.now,
                key=key
            )

        return True
