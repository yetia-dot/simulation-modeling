# data_gen/latency.py
from .config import CONFIG
from .distributions import clipped_normal

def sample_auth_latency():
    return clipped_normal(CONFIG["auth_delay_mean"], CONFIG["auth_delay_std"], min_val=10)

def sample_pubsub_latency():
    return clipped_normal(CONFIG["pubsub_delay_mean"], CONFIG["pubsub_delay_std"], min_val=5)
