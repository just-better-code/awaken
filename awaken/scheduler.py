from threading import Event
from time import time


class Scheduler:
    def __init__(self, interrupt : Event, idle : int, delay: int):
        self._interrupt = interrupt
        self._started = time()
        self._last_activity = time()
        self._last_emulation = time()
        self._idle = idle
        self._delay = delay

    def is_must_move(self):
        self._ping()
        first_idle = time() - self._last_activity
        middle_idle = time() - self._last_emulation

        return first_idle > self._idle and middle_idle > self._delay

    def moved(self):
        self._last_emulation = time()

    def _ping(self) -> None:
        if self._interrupt.is_set():
            self._last_activity = time()
            self._interrupt.clear()
