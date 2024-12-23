from time import sleep

import pyautogui as gui
import random
import math
import logging

from threading import Event, Lock
from pyautogui import Point
from typing import List


class Cursor:
    def __init__(self, user_activity: Event, lock: Lock):
        self._log = logging.getLogger(__class__.__name__)
        self._current = gui.position()
        self._user_activity = user_activity
        self._lock = lock


    def move(self, x: int, y: int, speed: float = 10, rand_k: float = 0.5) -> None:
        points = self._points(x, y)
        for n in range(1, len(points)):
            step = points[n]
            if self._user_activity.is_set():
                self._log.debug('Breaking movement because of user activity')
                break
            offset = (-int(self._current.x - step.x), -int(self._current.y - step.y))
            with self._lock:
                gui.move(*offset, self._duration(speed, rand_k), _pause=False)
            self._current = gui.position()
            self._check(points)

    def _check(self, steps):
        if self._current not in steps:
            self._log.debug(f'Mouse position {self._current} not in {steps}')
            self._user_activity.set()

    @classmethod
    def _duration(cls, speed: float, rand_k: float) -> float:
        delta = rand_k * speed
        speed = random.uniform(speed - delta, speed + delta)

        return 1 / speed

    def _points(self, x, y) -> List[Point]:
        num = self._points_num(x, y)
        destination = Point(self._current.x + x, self._current.y + y)
        points = [gui.getPointOnLine(*self._current, *destination, gui.linear(n / num)) for n in range(0, num)]

        return [Point(int(step[0]), int(step[1])) for step in points]

    def _points_num(self, x, y) -> int:
        dist = math.dist(list(self._current), [x, y])

        return int(dist / 10)

