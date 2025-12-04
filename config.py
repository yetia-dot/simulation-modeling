"""
Configuration parameters for the simulation.
Tweak these to run experiments.
"""
import math

# -----------------------
# Simulation parameters
# -----------------------
SIM_TIME = 60 * 5  # 5 minutes for test
RANDOM_SEED = 42

# -----------------------
# Player arrival
# -----------------------
PLAYER_ARRIVAL_RATE = 1/12.0  # ~5 players/min

# -----------------------
# Match parameters
# -----------------------
PLAYERS_PER_MATCH = 2        # head-to-head game
MATCHMAKING_BATCH_TIMEOUT = 10.0  # seconds before forcing a match from queued players
MATCHMAKER_CAPACITY = 4      # how many matches matchmaking can handle in parallel

# -----------------------
# Game parameters
# -----------------------
AVG_TURNS_PER_MATCH = 7
AVG_TIME_PER_TURN = 5.0      # seconds
TURN_TIME_STD = 1.5

# -----------------------
# Pub/Sub delays/loss
# -----------------------
PUBSUB_DELAY_MEAN = 0.5      # seconds
PUBSUB_DELAY_STD = 0.2
PUBSUB_LOSS_PROB = 0.02      # 2% message loss
PUBSUB_MAX_RETRIES = 3
PUBSUB_RETRY_DELAY = 1.0

# -----------------------
# Storage latencies
# -----------------------
STORAGE_WRITE_MEAN = 0.1
STORAGE_WRITE_STD = 0.05

# -----------------------
# CSV-driven simulation (new)
# -----------------------
USE_CSV_DATA = True
CSV_DATA_PATH = "data/output"  # folder containing players.csv, matches.csv, turns.csv
