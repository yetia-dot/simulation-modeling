# data_gen/config.py
import numpy as np

CONFIG = {
    # Player arrivals per minute (Poisson λ)
    "arrival_rate_per_min": 120,  # 2 players/sec

    # Match duration distribution (seconds)
    "match_duration_mean": 180,   # avg 3 min
    "match_duration_std": 60,

    # Turn duration (seconds)
    "turn_mean": 5.0,
    "turn_std": 1.5,

    # Pub/Sub message latency (ms)
    "pubsub_delay_mean": 80,
    "pubsub_delay_std": 20,

    # Authentication latency (ms)
    "auth_delay_mean": 90,
    "auth_delay_std": 30,

    # Dropout probability per player
    "dropout_prob": 0.03,

    # Number of players to generate
    "num_players": 5000,

    # Seed for reproducibility
    "seed": 42
}

np.random.seed(CONFIG["seed"])
