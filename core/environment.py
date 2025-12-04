# core/environment.py
import simpy
import random
from config import RANDOM_SEED

def create_env(seed: int = RANDOM_SEED) -> simpy.Environment:
    """
    Create a SimPy environment with reproducible random seed.
    """
    random.seed(seed)
    env = simpy.Environment()
    return env
