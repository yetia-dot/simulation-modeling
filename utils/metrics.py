import os
import time
from collections import defaultdict
from typing import Any, Dict
import pandas as pd

class MetricsCollector:
    """
    Collects simulation metrics and event logs.
    Saves metrics to CSV and events to a log file.
    """
    def __init__(self, out_dir: str):
        self.out_dir = out_dir
        os.makedirs(out_dir, exist_ok=True)
        self.reset()

    def reset(self):
        self.metrics: defaultdict[str, list] = defaultdict(list)
        self.events: list[str] = []

    def record(self, metric_name: str, value: Any, timestamp: float = None, **meta: Dict[str, Any]):
        """
        Record a metric value with optional timestamp and metadata.
        """
        ts = timestamp if timestamp is not None else time.time()
        self.metrics[metric_name].append((ts, value, meta or {}))

    def log_event(self, event: str):
        """
        Log a simulation event as a string.
        """
        self.events.append(event)

    def save(self) -> str:
        """
        Save metrics to CSV and events to a log file.
        Returns the path to the metrics CSV file.
        """
        # Flatten metrics into rows
        rows = []
        for key, values in self.metrics.items():
            for ts, val, meta in values:
                row = {"metric": key, "timestamp": ts, "value": val}
                if meta:
                    row.update(meta)
                rows.append(row)

        # Save metrics CSV
        df = pd.DataFrame(rows)
        metric_file = os.path.join(self.out_dir, "metrics.csv")
        df.to_csv(metric_file, index=False)

        # Save event logs
        events_file = os.path.join(self.out_dir, "events.log")
        with open(events_file, "w") as f:
            for ev in self.events:
                f.write(f"{ev}\n")

        return metric_file
