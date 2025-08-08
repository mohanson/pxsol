import math
import threading
import time


class Limits:
    # Limits represents a rate limiter that controls resource allocation over time.

    def __init__(self, n: int, p: float) -> None:
        # Generate n tokens every p seconds.
        assert n > 0
        assert p > 0
        p = int(p * 10**9)
        g = math.gcd(n, p)
        self.addition = n // g
        self.capacity = n
        self.last = time.time_ns()
        self.lock = threading.Lock()
        self.size = n
        self.step = p // g

    def peek(self, n: int) -> bool:
        # Peek glances there are enough resources (n) available.
        with self.lock:
            cycles = (time.time_ns() - self.last) // self.step
            if cycles > 0:
                self.last += cycles * self.step
                self.size += cycles * self.addition
                self.size = min(self.size, self.capacity)
            return self.size >= n

    def wait(self, n: int) -> None:
        # Wait ensures there are enough resources (n) available, blocking if necessary.
        with self.lock:
            cycles = (time.time_ns() - self.last) // self.step
            if cycles > 0:
                self.last += cycles * self.step
                self.size += cycles * self.addition
                self.size = min(self.size, self.capacity)
            if self.size < n:
                cycles = (n - self.size + self.addition - 1) // self.addition
                time.sleep(self.step * cycles / (10 ** 9))
                self.last += cycles * self.step
                self.size += cycles * self.addition
            self.size -= n
            assert self.size <= self.capacity
