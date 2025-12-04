# data_gen/generate_dataset.py
import csv
import numpy as np
from pathlib import Path
from data_gen.arrivals import generate_arrival_times
from data_gen.turns import generate_turn_durations, estimate_turn_count
from data_gen.latency import sample_auth_latency, sample_pubsub_latency
from data_gen.dropout import sample_dropout
from data_gen.config import CONFIG


def generate_dataset(outdir=None, seed: int = 42):
    """
    Generate synthetic dataset for the turn-based multiplayer simulation.
    Produces players.csv, matches.csv, and turns.csv.
    """

    np.random.seed(seed)  # Reproducibility

    # Default output folder: data/output/ under project root
    if outdir is None:
        outdir = Path(__file__).parent.parent / "data" / "output"
    else:
        outdir = Path(outdir)
    
    outdir.mkdir(parents=True, exist_ok=True)

    # -------------------------
    # 1. Player arrivals
    # -------------------------
    arrivals = generate_arrival_times()

    # -------------------------
    # 2. Create matches: pair players sequentially
    # -------------------------
    num_matches = len(arrivals) // 2
    players, matches, turns = [], [], []
    match_id, turn_id = 1, 1

    for i in range(num_matches):
        p1, p2 = i * 2, i * 2 + 1
        arrival1, arrival2 = arrivals[p1], arrivals[p2]

        # Authentication latency
        auth1, auth2 = sample_auth_latency(), sample_auth_latency()
        start_time = max(arrival1 + auth1, arrival2 + auth2)

        # Match duration (min 60s)
        match_duration = max(
            np.random.normal(CONFIG["match_duration_mean"], CONFIG["match_duration_std"]),
            60
        )

        # Number of turns & turn durations
        turn_count = estimate_turn_count(match_duration)
        turn_durations = generate_turn_durations(turn_count)

        # Dropout probability
        dropout = sample_dropout()

        # Store players
        players.extend([[p1, arrival1, auth1, match_id],
                        [p2, arrival2, auth2, match_id]])

        # Store match
        matches.append([match_id, p1, p2, start_time, match_duration, turn_count, dropout])

        # Store turns
        cumulative = start_time
        for t in range(turn_count):
            duration = turn_durations[t]
            pubsub_delay = sample_pubsub_latency()
            turns.append([turn_id, match_id, t + 1, cumulative, duration, pubsub_delay])
            cumulative += duration
            turn_id += 1

        match_id += 1

    # -------------------------
    # 3. Write CSVs
    # -------------------------
    csv_data = {
        "players.csv": (["player_id", "arrival_time", "auth_latency", "match_id"], players),
        "matches.csv": (["match_id", "p1", "p2", "start_time", "duration", "turns", "dropout"], matches),
        "turns.csv": (["turn_id", "match_id", "turn_index", "start_time", "duration", "pubsub_delay"], turns)
    }

    for fname, (header, rows) in csv_data.items():
        with open(outdir / fname, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows)

    print(f"[OK] Dataset generated in: {outdir.resolve()}")
    print(f" - players.csv ({len(players)} rows)")
    print(f" - matches.csv ({len(matches)} rows)")
    print(f" - turns.csv   ({len(turns)} rows)")


if __name__ == "__main__":
    generate_dataset()
