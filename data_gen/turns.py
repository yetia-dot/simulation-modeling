# data_gen/turns.py
import numpy as np
from .config import CONFIG
from .distributions import clipped_normal

def generate_turn_durations(num_turns):
    """Return a list of turn durations for a match."""
    return [
        clipped_normal(CONFIG["turn_mean"], CONFIG["turn_std"], min_val=0.1)
        for _ in range(num_turns)
    ]

def estimate_turn_count(match_duration):
    """Convert continuous match time to discrete turns."""
    avg_turn = CONFIG["turn_mean"]
    return max(1, int(match_duration / avg_turn))
