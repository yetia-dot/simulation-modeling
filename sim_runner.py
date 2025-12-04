# sim_runner.py
import simpy
import random
import os
import csv
import sys
from datetime import datetime, timezone
from config import SIM_TIME, PLAYER_ARRIVAL_RATE, RANDOM_SEED, USE_CSV_DATA, CSV_DATA_PATH
from utils.generators import poisson_interarrival, sample_player
from utils.metrics import MetricsCollector
from services.storage import Storage
from services.pubsub import PubSub
from services.player_service import PlayerService
from services.matchmaking_service import MatchmakingService
from services.game_logic_service import GameLogicService
from pathlib import Path
# -------------------------
# Synthetic player spawner
# -------------------------

sys.path.append(str(Path(__file__).parent.resolve()))

def spawn_players(env, player_service, max_players=100):
    """
    Spawns synthetic players at random intervals, sends to PlayerService inbox.
    """
    player_id = 1
    while env.now < SIM_TIME and player_id <= max_players:
        inter = poisson_interarrival(PLAYER_ARRIVAL_RATE)
        yield env.timeout(inter)
        p = sample_player(player_id)

        # Publish a player_arrival event to PlayerService
        player_service.inbox.put(
            ({"type": "player_arrival", "payload": {"player": p}}, "sim_runner", env.now, 0)
        )
        player_id += 1

# -------------------------
# CSV-driven player spawner
# -------------------------
class CSVPlayer:
    """
    Lightweight player class for CSV input, allows dynamic arrival_time.
    """
    def __init__(self, player_id, skill, name, arrival_time):
        self.id = player_id
        self.skill = skill
        self.name = name
        self.arrival_time = arrival_time

    def to_dict(self):
        return {
            "id": self.id,
            "skill": self.skill,
            "name": self.name,
            "arrival_time": getattr(self, "arrival_time", None)
        }

def spawn_players_from_csv(env, broker):
    players_file = os.path.join(CSV_DATA_PATH, "players.csv")
    with open(players_file, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            player = CSVPlayer(
                player_id=int(row["player_id"]),
                skill=int(row.get("skill", 50)),
                name=row.get("name", f"player_{row['player_id']}"),
                arrival_time=float(row["arrival_time"])
            )
            # Schedule player according to arrival_time
            yield env.timeout(max(0, player.arrival_time - env.now))

            # Publish a player_arrival event
            broker.publish(
                topic="player_arrival",
                message={"type": "player_arrival", "payload": {"player": player}},
                publisher_name="sim_runner"
            )

# -------------------------
# Simulation runner
# -------------------------
def run_once(out_dir):
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

    # Start player spawners
    if USE_CSV_DATA:
        ("[INFO] Using CSV-driven input from", CSV_DATA_PATH)
        env.process(spawn_players_from_csv(env, pubsub))
    else:
        ("[INFO] Using synthetic random arrivals")
        env.process(spawn_players(env, player_service))

    # Run simulation
    env.run(until=SIM_TIME)
    metrics_file = metrics.save()
    (f"Run complete. Metrics: {metrics_file}")

# -------------------------
# Entry point
# -------------------------
if __name__ == "__main__":
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join("outputs", f"run_{ts}")
    run_once(out_dir)
