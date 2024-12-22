import pyautogui as gui
import random
import math

from awaken.actions.mouse_listener import MouseListener
from threading import Event, Lock
from pyautogui import Point
from typing import List


class Cursor:
    def __init__(self, interrupt: Event):
        self._current = gui.position()
        self._interrupt = interrupt
        self._lock = Lock()
        self._listener = MouseListener(self._interrupt, self._lock)

    def move(self, x: int, y: int, speed: float = 10, rand_k: float = 0.5) -> None:
        for step in self._steps(x, y):
            if self._interrupt.is_set():
                break
            offset = (-int(self._current.x - step.x), -int(self._current.y - step.y))
            with self._lock:
                gui.move(*offset, self._duration(speed, rand_k), _pause=True)
            self._current = gui.position()
            self._check(step)

    def _check(self, step):
        if self._current != step:
            self._interrupt.set()

    @classmethod
    def _duration(cls, speed: float, rand_k: float) -> float:
        delta = rand_k * speed
        speed = random.uniform(speed - delta, speed + delta)

        return 1 / speed

    def _steps(self, x, y) -> List[Point]:
        num = self._steps_num(x, y)
        point = Point(self._current.x + x, self._current.y + y)
        steps = [gui.getPointOnLine(*self._current, *point, gui.linear(n / num)) for n in range(1, num)]

        return [Point(int(step[0]), int(step[1])) for step in steps]

    def _steps_num(self, x, y) -> int:
        dist = math.dist(list(self._current), [x, y])

        return int(dist / 10)


