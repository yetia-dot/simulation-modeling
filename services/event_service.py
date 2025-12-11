# services/event_service.py
import simpy

class EventService:
    """
    Event/Notification service node.

    Subscribes to turn_completed and match_created events and simulates client notification
    delivery. Logs everything for debugging and records metrics.
    """

    def __init__(self, env: simpy.Environment, name: str, network, metrics, broker):
        self.env = env
        self.name = name
        self.network = network
        self.metrics = metrics
        self.broker = broker
        self.inbox = simpy.Store(env)

        # subscribe to relevant topics
        self.broker.subscribe(self, "turn_completed")
        self.broker.subscribe(self, "match_created")

        (f"{self.env.now:.3f}: [EVENT] EventService '{self.name}' subscribed to topics turn_completed, match_created")

        self.env.process(self._run())

    def _log(self, msg: str):
        msg_str = f"{self.env.now:.3f}: EVENT {msg}"
        (msg_str)
        self.metrics.log_event(msg_str)

    def _run(self):
        while True:
            msg, src, ts_sent, net_delay = yield self.inbox.get()

            if not isinstance(msg, dict):
                self._log(f"ERROR: Received malformed message from {src}: {msg}")
                continue

            mtype = msg.get("type")
            payload = msg.get("payload", {})

            self._log(f"RECV from={src} type={mtype} payload={payload} delay={net_delay:.3f}")

            if mtype == "turn_completed":
                match_id = payload.get("match_id")
                turn = payload.get("turn")

                self._log(f"Notify clients: match={match_id} turn={turn} payload={payload}")

                # record delivery metric
                self.metrics.record(
                    "pub_delivery",
                    1,
                    timestamp=self.env.now,
                    topic=f"match-{match_id}:turn",
                    match_id=match_id,
                    turn=turn
                )

            elif mtype == "match_created":
                match_id = payload.get("match_id")

                self._log(f"Notify clients MATCH CREATED: match={match_id} payload={payload}")

                self.metrics.record(
                    "pub_match_created",
                    1,
                    timestamp=self.env.now,
                    topic="match_created",
                    match_id=match_id
                )

            else:
                self._log(f"unknown message type from={src}: {msg}")
