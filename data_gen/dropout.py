# data_gen/dropout.py
import numpy as np
from .config import CONFIG

def sample_dropout():
    """Return True if a player drops mid-match."""
    return np.random.random() < CONFIG["dropout_prob"]
