import pyautogui as gui
import random
import logging
import math

from threading import Event, Lock
from pyautogui import Point
from typing import List, Tuple

from awaken.actions.tweening import Tweening


class Cursor:
    def __init__(self, user_activity: Event, lock: Lock):
        self._log = logging.getLogger(__class__.__name__)
        self._current = gui.position()
        self._user_activity = user_activity
        self._lock = lock


    def move(self, x: int, y: int) -> None:
        points = self._points_to(x, y)
        for point in points:
            if self._user_activity.is_set():
                self._log.debug('Breaking movement because of user activity')
                break
            offset = (point.x - self._current.x, point.y - self._current.y)
            with self._lock:
                gui.move(*offset, self._duration(offset), _pause=False)
            self._current = gui.position()
            self._check(points)

    def _check(self, steps):
        if self._current not in steps:
            self._log.debug(f'Mouse position {self._current} not in {steps}')
            self._user_activity.set()

    def _duration(self, offset: Tuple[float, float]) -> float:
        dist = math.dist(list(self._current), list(offset))

        return 10 / dist

    def _points_to(self, x, y) -> List[Point]:
        destination = Point(self._current.x + x, self._current.y + y)

        return Tweening.points(self._current, destination)
