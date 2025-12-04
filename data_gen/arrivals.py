# data_gen/arrivals.py
import numpy as np
from .config import CONFIG

def generate_arrival_times():
    """Generate player arrival timestamps using a Poisson process."""
    lam = CONFIG["arrival_rate_per_min"] / 60  # per-second rate
    num = CONFIG["num_players"]

    inter_arrivals = np.random.exponential(1 / lam, size=num)
    timestamps = np.cumsum(inter_arrivals)

    return timestamps
