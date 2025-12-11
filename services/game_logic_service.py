import simpy
import random
from typing import Any, List
from config import AVG_TURNS_PER_MATCH, AVG_TIME_PER_TURN, TURN_TIME_STD

class GameLogicService:
    """
    Game logic service node.
    Subscribes to "match_created".
    Simulates turn processing and publishes "turn_completed".
    """

    def __init__(self, env, name, storage, network, broker, metrics):
        self.env = env
        self.name = name
        self.storage = storage
        self.network = network
        self.broker = broker
        self.metrics = metrics
        self.inbox = simpy.Store(env)

        # subscribe to match_created
        self.broker.subscribe("match_created", self)

        self.env.process(self._run())

    # -------------------------------------------------------------
    # Helper to create turn_completed message
    # -------------------------------------------------------------
    def _make_turn_message(self, match_id, turn, by, ts):
        return {"type": "turn_completed", "payload": {"match_id": match_id, "turn": turn, "by": by, "ts": ts}}

    # -------------------------------------------------------------
    # Logging (unified with other services)
    # -------------------------------------------------------------
    def _log(self, msg: str):
        s = f"{self.env.now:.3f}: [GAMELOGIC] {msg}"
        print(s)
        # Structured metrics event with timestamp
        self.metrics.log_event(
            event_type="game_logic_log",
            payload={"message": msg},
            timestamp=self.env.now
        )

    # -------------------------------------------------------------
    # PubSub inbox entry
    # -------------------------------------------------------------
    def notify(self, topic, msg, src):
        return self.inbox.put((msg, src))

    # -------------------------------------------------------------
    # Main message loop
    # -------------------------------------------------------------
    def _run(self):
        while True:
            msg, src = yield self.inbox.get()
            mtype = msg.get("type")

            if mtype == "match_created":
                yield self.env.process(self._handle_match(msg["payload"]))
            elif mtype == "turn_submitted":
                # if you handle external turn submissions
                yield self.env.process(self._handle_turn_submission(msg["payload"]))
            else:
                self._log(f"unknown_message type={mtype} from={src}")

    # -------------------------------------------------------------
    # Handle new match created
    # -------------------------------------------------------------
    def _handle_match(self, payload: dict):
        match_id = payload["match_id"]
        players = payload.get("players", [])
        start_ts = self.env.now

        self._log(f"match_start id={match_id}")

        # determine number of turns
        num_turns = max(1, int(random.gauss(AVG_TURNS_PER_MATCH, 2)))

        # normalize player objects
        processed_players: List[Any] = []
        for p in players:
            if hasattr(p, "id"):
                processed_players.append(p)
            else:
                class _P: pass
                tmp = _P()
                tmp.id = p
                processed_players.append(tmp)

        # ---------------------------------------------------------
        # Turn loop
        # ---------------------------------------------------------
        for turn in range(1, num_turns + 1):
            current = processed_players[(turn - 1) % len(processed_players)]
            turn_start = self.env.now

            # simulate turn processing
            think_time = max(0.01, random.gauss(AVG_TIME_PER_TURN, TURN_TIME_STD))
            yield self.env.timeout(think_time)

            # persist turn state
            yield self.env.process(
                self.storage.write(f"{match_id}:turn:{turn}", {"player": current.id, "ts": self.env.now})
            )

            # publish turn_completed
            payload_msg = self._make_turn_message(match_id, turn, current.id, self.env.now)
            self.broker.publish(
                topic="turn_completed",
                message=payload_msg,
                publisher_name="GameLogicService"
            )

            # metrics & logging
            turn_latency = self.env.now - turn_start
            self.metrics.record(
                "turn_latency",
                turn_latency,
                timestamp=self.env.now,
                match_id=match_id,
                turn=turn
            )
            self._log(f"turn_complete match={match_id} turn={turn} by={current.id} latency={turn_latency:.3f}")

        # ---------------------------------------------------------
        # Match finished
        # ---------------------------------------------------------
        duration = self.env.now - start_ts
        self.metrics.record(
            "match_duration",
            duration,
            timestamp=self.env.now,
            match_id=match_id,
            turns=num_turns
        )
        self._log(f"match_end id={match_id} duration={duration:.3f} turns={num_turns}")
