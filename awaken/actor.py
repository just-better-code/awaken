from threading import Event
from awaken.actions import *


class Actor:
    def __init__(self, interrupt : Event):
        self._interrupt = interrupt

    def move_cursor(self, dist : int, speed: int = 10, rand_k: float = 0.5):
        action = Cursor(self._interrupt)
        while not self._interrupt.is_set():
            action.move(dist, dist, speed, rand_k)
            action.move(-dist, -dist, speed, rand_k)

    def press_key(self, key : str):
        action = Keyboard(self._interrupt)
        while not self._interrupt.is_set():
            action.press(key)
