import random
from config import (
    PUBSUB_DELAY_MEAN, PUBSUB_DELAY_STD,
    PUBSUB_LOSS_PROB, PUBSUB_MAX_RETRIES, PUBSUB_RETRY_DELAY
)


class PubSub:
    """
    Simple broker simulation with delay + loss + retry.
    Uses unified log/event format and consistent message delivery across services.
    """

    def __init__(self, env, metrics):
        self.env = env
        self.metrics = metrics
        self.subscribers = {}  # topic -> list of subscriber objects

    # -------------------------------------------------------------
    # Subscription
    # -------------------------------------------------------------
    def subscribe(self, topic: str, subscriber):
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(subscriber)


    # -------------------------------------------------------------
    # Publish
    # -------------------------------------------------------------
    def publish(self, topic: str, message: dict, publisher_name: str):
        """
        publish(topic, message, publisher_name)
        """

        if topic not in self.subscribers:
            return

        for subscriber in self.subscribers[topic]:
            self.env.process(self._deliver(subscriber, topic, message))

    # -------------------------------------------------------------
    # Delivery Simulation
    # -------------------------------------------------------------
    def _deliver(self, subscriber, topic, message):
        retries = 0

        while retries <= PUBSUB_MAX_RETRIES:
            # Simulate network latency
            delay = max(0.0, random.gauss(PUBSUB_DELAY_MEAN, PUBSUB_DELAY_STD))
            yield self.env.timeout(delay)

            # Simulate message loss
            if random.random() < PUBSUB_LOSS_PROB:
                retries += 1

                self.metrics.record(
                    "pubsub_retry",
                    1,
                    timestamp=self.env.now,
                    topic=topic,
                    retries=retries
                )

                
                yield self.env.timeout(PUBSUB_RETRY_DELAY)
                continue

            # Successful delivery
            self.metrics.record(
                "pubsub_delivered",
                1,
                timestamp=self.env.now,
                topic=topic,
                delivered_to=str(subscriber)
            )

            
            # Correct message format for all updated services:
            subscriber.inbox.put((message, "PubSub"))

            break
