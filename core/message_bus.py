# core/message_bus.py
import simpy
import random

class Network:
    """
    Simulates network transport with optional delay and loss.
    """
    def __init__(self, env, metrics, delay_mean=0.1, delay_std=0.05, loss_prob=0.01):
        self.env = env
        self.metrics = metrics
        self.delay_mean = delay_mean
        self.delay_std = delay_std
        self.loss_prob = loss_prob

    def send(self, src: str, dst, msg: dict):
        """
        Deliver message to destination service inbox after network delay.
        """
        delay = max(0.0, random.gauss(self.delay_mean, self.delay_std))
        if random.random() < self.loss_prob:
            self.metrics.log_event(f"{self.env.now:.3f}: NETWORK drop {msg} from {src} -> {dst.name}")
            return  # message lost
        self.env.process(self._deliver(dst, msg, src, delay))

    def _deliver(self, dst, msg: dict, src: str, delay: float):
        yield self.env.timeout(delay)
        self.metrics.log_event(f"{self.env.now:.3f}: NETWORK delivered {msg} from {src} -> {dst.name} after {delay:.3f}s")
        yield dst.inbox.put((msg, src, self.env.now, delay))


class PubSubBroker:
    """
    Simulates a broker for topic-based publish/subscribe.
    """
    def __init__(self, env, name: str, network: Network, metrics):
        self.env = env
        self.name = name
        self.network = network
        self.metrics = metrics
        self.topics = {}  # topic -> list of subscribers

    def subscribe(self, service, topic: str):
        if topic not in self.topics:
            self.topics[topic] = []
        self.topics[topic].append(service)
        self.metrics.log_event(f"{self.env.now:.3f}: BROKER {service.name} subscribed to {topic}")

    def publish(self, src: str, topic: str, payload: dict):
        """
        Publish a message to all subscribers of a topic.
        """
        subscribers = self.topics.get(topic, [])
        self.metrics.log_event(f"{self.env.now:.3f}: BROKER publishing {topic} to {len(subscribers)} subs")
        msg = {"type": topic, "payload": payload}
        for sub in subscribers:
            self.network.send(src, sub, msg)
