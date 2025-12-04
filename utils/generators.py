import random
import json
import math
from typing import List
from config import RANDOM_SEED, PLAYER_ARRIVAL_RATE

# Seed RNG for reproducibility
random.seed(RANDOM_SEED)

class Player:
    def __init__(self, player_id: int, skill: int = None, name: str = None, arrival_time: float = None):
        self.id = player_id
        self.skill = skill if skill is not None else random.randint(1, 100)
        self.name = name if name is not None else f"player_{player_id}"
        self.arrival_time = arrival_time  # can be set later
        self.auth_latency = None          # optional extra attributes
        self.match_id = None

    def to_dict(self):
        return {
            "id": self.id,
            "skill": self.skill,
            "name": self.name,
            "arrival_time": self.arrival_time,
            "auth_latency": self.auth_latency,
            "match_id": self.match_id
        }

def sample_player(player_id: int) -> Player:
    """
    Generate a player with random skill level.
    """
    return Player(player_id)

def poisson_interarrival(lmbda: float) -> float:
    """
    Generate interarrival time (seconds) from a Poisson process.
    """
    u = random.random()
    return -math.log(1.0 - u) / lmbda

def load_players_to_file(n: int, path: str = "data/sample_players.json") -> List[Player]:
    """
    Generate n players and save to JSON file.
    """
    players = [sample_player(i) for i in range(1, n + 1)]
    with open(path, "w") as f:
        json.dump([p.to_dict() for p in players], f, indent=2)
    return players
