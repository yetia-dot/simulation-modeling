# services/auth.py
import simpy

class AuthService:
    def __init__(self, env, storage, metrics):
        self.env = env
        self.storage = storage
        self.metrics = metrics

    def authenticate(self, player):
        """
        Simulate player authentication and record latency.
        """
        start = self.env.now
        # Simulate writing last-seen to storage
        data = {
            "id": player.id,
            "name": getattr(player, "name", f"player_{player.id}"),
            "skill": getattr(player, "skill", 50)
        }
        yield self.env.process(self.storage.write(f"player:{player.id}", data))
        latency = self.env.now - start
        self.metrics.record("auth_latency", latency, timestamp=self.env.now, player_id=player.id)
        self.metrics.log_event(f"{self.env.now:.3f}: AUTH success player={player.id}")
        return True
