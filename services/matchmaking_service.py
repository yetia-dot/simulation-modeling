import simpy
import random
from collections import deque
from typing import Any
from config import PLAYERS_PER_MATCH, MATCHMAKING_BATCH_TIMEOUT
from utils.helpers import make_message

class MatchmakingService:
    def __init__(self, env, name, storage, network, broker, metrics, match_creator_node=None):
        self.env = env
        self.name = name
        self.storage = storage
        self.network = network
        self.broker = broker
        self.metrics = metrics
        self.queue = deque()
        self.inbox = simpy.Store(env)
        self.match_creator_node = match_creator_node

        broker.subscribe("player_authenticated", self)
        self.env.process(self._run())
        self.env.process(self._flush_loop())

    # -------------------------------------------------------------
    def notify(self, topic, msg, src):
        return self.inbox.put((msg, src))

    # -------------------------------------------------------------
    def _enqueue(self, player: Any):
        self.queue.append(player)
        self.metrics.record("queue_length", len(self.queue
        ), timestamp=self.env.now)
        print(f"[MATCHMAKING] Queue add player_id={player.id} queue_len={len(self.queue)}")

    # -------------------------------------------------------------
    def _create_match_from_queue(self):
        while len(self.queue) >= PLAYERS_PER_MATCH:
            players = [self.queue.popleft() for _ in range(PLAYERS_PER_MATCH)]
            match_id = f"match-{int(self.env.now*1000)}-{random.randint(1000,9999)}"
            self.metrics.record("matches_created", 1, timestamp=self.env.now, match_id=match_id)
            print(f"[MATCHMADE] id={match_id} players={[p.id for p in players]}")

            # Persist match metadata
            yield self.env.process(
                self.storage.write(f"match:{match_id}", {"players": [p.id for p in players], "ts": self.env.now})
            )

            # Publish match_created
            payload = make_message(match_id=match_id, players=players, ts=self.env.now)
            self.broker.publish(topic="match_created", message=payload, publisher_name="MatchmakingService")

            # Optional direct network send
            if self.match_creator_node and self.network:
                self.network.send(
                    src=self.name,
                    dst=self.match_creator_node,
                    msg={"type": "match_created", "payload": {"match_id": match_id, "players": players}}
                )

    # -------------------------------------------------------------
    def _run(self):
        while True:
            msg, src = yield self.inbox.get()
            mtype = msg.get("type")
            if mtype == "player_authenticated":
                player = msg["payload"]["player"]
                self._enqueue(player)
                yield self.env.process(self._create_match_from_queue())
            else:
                print(f"[MATCHMAKING] Unknown message type={mtype}")

    # -------------------------------------------------------------
    def _flush_loop(self):
        while True:
            yield self.env.timeout(MATCHMAKING_BATCH_TIMEOUT)
            # Flush any remaining matches in queue
            if len(self.queue) >= PLAYERS_PER_MATCH:
                yield self.env.process(self._create_match_from_queue())

    # -------------------------------------------------------------
    # Call at end of simulation to flush leftover players
    def flush_remaining(self):
        if self.queue:
            print(f"[MATCHMAKING] Flushing remaining {len(self.queue)} players")
            while len(self.queue) >= PLAYERS_PER_MATCH:
                self.env.process(self._create_match_from_queue())
