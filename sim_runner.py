# sim_runner.py (FINAL FIXED VERSION)
import simpy
import random
import os
import csv
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

from config import SIM_TIME, PLAYER_ARRIVAL_RATE, RANDOM_SEED, USE_CSV_DATA, CSV_DATA_PATH
from utils.generators import poisson_interarrival, sample_player
from utils.metrics import MetricsCollector
from services.storage import Storage
from services.pubsub import PubSub
from services.player_service import PlayerService
from services.matchmaking_service import MatchmakingService
from services.game_logic_service import GameLogicService

# Fix import resolution
sys.path.append(str(Path(__file__).parent.resolve()))


# ---------------------------------------------------------
# Synthetic player spawner
# ---------------------------------------------------------
def spawn_players(env, broker, max_players=100):
    player_id = 1
    while env.now < SIM_TIME and player_id <= max_players:
        inter = poisson_interarrival(PLAYER_ARRIVAL_RATE)
        yield env.timeout(inter)
        p = sample_player(player_id)

        broker.publish(
            topic="player_arrival",
            message={"type": "player_arrival", "payload": {"player": p}},
            publisher_name="sim_runner"
        )
        player_id += 1


# ---------------------------------------------------------
# CSV-driven player spawner
# ---------------------------------------------------------
class CSVPlayer:
    def __init__(self, player_id, skill, name, arrival_time):
        self.id = player_id
        self.skill = skill
        self.name = name
        self.arrival_time = arrival_time


def spawn_players_from_csv(env, broker):
    players_file = os.path.join(CSV_DATA_PATH, "players.csv")
    if not os.path.exists(players_file):
        raise FileNotFoundError(f"CSV players file not found: {players_file}")

    with open(players_file, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            player = CSVPlayer(
                player_id=int(row["player_id"]),
                skill=int(row.get("skill", 50)),
                name=row.get("name", f"player_{row['player_id']}"),
                arrival_time=float(row["arrival_time"])
            )

            wait = max(0, player.arrival_time - env.now)
            if wait > 0:
                yield env.timeout(wait)

            broker.publish(
                topic="player_arrival",
                message={"type": "player_arrival", "payload": {"player": player}},
                publisher_name="sim_runner"
            )


# ---------------------------------------------------------
# Simulation runner
# ---------------------------------------------------------
def run_once(out_dir):

    # Ensure output directory exists
    os.makedirs(out_dir, exist_ok=True)
    print(f"[INFO] Outputs directory created: {out_dir}")

    random.seed(RANDOM_SEED)
    env = simpy.Environment()

    metrics = MetricsCollector(out_dir)
    storage = Storage(env)
    pubsub = PubSub(env, metrics)

    # Create service nodes
    game_logic = GameLogicService(
        env=env,
        name="GameLogic",
        storage=storage,
        network=None,
        broker=pubsub,
        metrics=metrics
    )

    player_service = PlayerService(
        env=env,
        name="PlayerService",
        storage=storage,
        network=None,
        broker=pubsub,
        metrics=metrics
    )

    matchmaking = MatchmakingService(
        env=env,
        name="matchmaking",
        storage=storage,
        network=None,
        broker=pubsub,
        metrics=metrics,
        match_creator_node=game_logic
    )

    # ---------------------------
    # Start player spawners
    # ---------------------------
    try:
        if USE_CSV_DATA:
            print(f"[INFO] Using CSV-driven input from {CSV_DATA_PATH}")
            if not os.path.isdir(CSV_DATA_PATH):
                raise Exception(f"CSV_DATA_PATH is not a directory: {CSV_DATA_PATH}")
            env.process(spawn_players_from_csv(env, pubsub))
        else:
            print("[INFO] Using synthetic random arrivals")
            env.process(spawn_players(env, pubsub))
    except Exception as e:
        print("[ERROR] Failed to start spawners:", e)
        traceback.print_exc()
        raise

    # ---------------------------
    # Run simulation
    # ---------------------------
    try:
        print(f"[INFO] Starting simulation for SIM_TIME={SIM_TIME} ...")
        env.run(until=SIM_TIME)
        print("[INFO] Simulation time reached.")
    except Exception as e:
        print("[ERROR] Simulation runtime error:", e)
        traceback.print_exc()
        raise

    # ---------------------------
    # Graceful shutdown + flush
    # ---------------------------
    try:
        print("[INFO] Flushing pending matchmaking items...")
        matchmaking.flush_remaining()

        print("[INFO] Running environment to drain remaining tasks...")
        # run until no more events
        draining = True
        while draining:
            prev_time = env.now
            env.step()  # run one event
            draining = (env.now != prev_time)

    except Exception as e:
        print("[WARN] Error during post-run flush:", e)

    # ---------------------------
    # Save metrics
    # ---------------------------
    try:
        metrics_file = metrics.save()
        print(f"[OK] Metrics saved to: {metrics_file}")
        return metrics_file
    except Exception as e:
        print("[ERROR] Failed to save metrics:", e)
        traceback.print_exc()
        raise


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------
if __name__ == "__main__":
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join("outputs", f"run_{ts}")

    try:
        run_once(out_dir)
    except Exception as e:
        print("[FATAL] run_once raised an exception.")
        sys.exit(1)
