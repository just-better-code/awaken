import logging
import math
from threading import Event, Lock

import pyautogui as gui
from pyautogui import Point

from awaken.actions.tweening import Tweening


class Cursor:
    def __init__(self, user_activity: Event, lock: Lock, speed: int, random_coef: float):
        self._log = logging.getLogger(__class__.__name__)
        self._current = gui.position()
        self._user_activity = user_activity
        self._lock = lock
        self._speed = max(1, speed)
        self._random_coef = random_coef

    def move(self, x: int, y: int) -> None:
        destination = Point(self._current.x + x, self._current.y + y)
        points = Tweening.points(self._current, destination, self._random_coef)
        for point in points:
            if self._user_activity.is_set():
                self._log.debug("Breaking movement because of user activity")
                break
            offset = (point.x - self._current.x, point.y - self._current.y)
            with self._lock:
                gui.move(*offset, self._duration_to(point), _pause=False)
            self._current = gui.position()
            self._check(points)

    def _check(self, steps):
        if self._current not in steps:
            self._log.debug(f"Mouse position {self._current} not in {steps}")
            self._user_activity.set()

    def _duration_to(self, dest: Point) -> float:
        segment = math.dist(
            (float(self._current.x), float(self._current.y)),
            (float(dest.x), float(dest.y)),
        )
        if segment < 1e-6:
            return 0.001
        # Higher speed => shorter duration; scale tuned for small per-step segments.
        return max(0.001, min(2.0, segment / (self._speed * 100.0)))
