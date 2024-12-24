import pyautogui as gui
import random
import math
import logging

from threading import Event, Lock
from pyautogui import Point
from typing import List

from awaken.actions.tweening import Tweening


class Cursor:
    def __init__(self, user_activity: Event, lock: Lock):
        self._log = logging.getLogger(__class__.__name__)
        self._current = gui.position()
        self._user_activity = user_activity
        self._lock = lock


    def move(self, x: int, y: int, speed: float = 10, rand_k: float = 0.5) -> None:
        points = self._points_to(x, y)
        for point in points:
            if self._user_activity.is_set():
                self._log.debug('Breaking movement because of user activity')
                break
            offset = (point.x - self._current.x, point.y - self._current.y)
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

    def _points_to(self, x, y) -> List[Point]:
        destination = Point(self._current.x + x, self._current.y + y)

        return Tweening.points(self._current, destination)

    def _points_num(self, x, y) -> int:
        dist = math.dist(list(self._current), [x, y])

        return int(dist / 10)

