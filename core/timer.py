# core/timer.py
import simpy

def wait(env: simpy.Environment, seconds: float):
    """
    Simple wrapper for a simulated delay.
    """
    yield env.timeout(seconds)

def retry(env: simpy.Environment, func, retries: int, delay: float):
    """
    Retry a SimPy process multiple times with delay.
    """
    for attempt in range(1, retries + 1):
        try:
            yield env.process(func())
            break
        except Exception as e:
            if attempt < retries:
                yield env.timeout(delay)
            else:
                raise e
