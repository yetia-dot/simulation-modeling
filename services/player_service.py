# services/player_service.py
import simpy
import random
from config import STORAGE_WRITE_MEAN, STORAGE_WRITE_STD

class PlayerService:
    def __init__(self, env, name, storage, network, broker, metrics):
        self.env = env
        self.name = name
        self.storage = storage
        self.network = network
        self.broker = broker
        self.metrics = metrics
        self.inbox = simpy.Store(env)

        # Subscribe to input topic
        broker.subscribe("player_arrival", self)

        self.env.process(self._run())

    def __repr__(self):
        return "<PlayerService>"

    # ---------------------------------------------------------
    # Helper to create message dict
    # ---------------------------------------------------------
    def _make_message(self, player):
        return {"type": "player_authenticated", "payload": {"player": player}}

    # ---------------------------------------------------------
    # Handle inbound messages
    # ---------------------------------------------------------
    def notify(self, topic, message, src):
        """
        Called by PubSub whenever a 'player_arrival' message is published.
        """
        return self.inbox.put((message, src))

    # ---------------------------------------------------------
    # Logging
    # ---------------------------------------------------------
    def _log(self, msg: str):
        (f"{self.env.now:.3f}: [PLAYERSERVICE] {msg}")
        self.metrics.log_event(f"{self.env.now:.3f}: PLAYER {msg}")

    # ---------------------------------------------------------
    # Main message loop
    # ---------------------------------------------------------
    def _run(self):
        while True:
            msg, src = yield self.inbox.get()
            player = msg["payload"]["player"]
            yield self.env.process(self._handle_player_arrival(player))

    # ---------------------------------------------------------
    # Player arrival handler
    # ---------------------------------------------------------
    def _handle_player_arrival(self, player):
        try:
            pid = player.id

            # -------------------------
            # Simulate authentication using storage write delay as proxy
            # -------------------------
            auth_latency = max(0.01, random.gauss(STORAGE_WRITE_MEAN, STORAGE_WRITE_STD))
            yield self.env.timeout(auth_latency)

            # -------------------------
            # Write to storage
            # -------------------------
            key = f"player:{pid}"
            yield self.env.process(self.storage.write(key, player))

            # -------------------------
            # Publish authenticated player
            # -------------------------
            msg = self._make_message(player)

            self.broker.publish(
                topic="player_authenticated",
                message=msg,
                publisher_name="PlayerService"
            )

            self._log(f"player_authenticated id={pid}")

        except Exception as e:
            raise


