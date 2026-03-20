import logging
import random
import time
from threading import Event, Lock

import pyautogui as gui

from awaken.actions.tweening import Tweening

_WHEEL_CLICK_EQUIV_PX = 32.0
_WHEEL_SPEED_DIVISOR = 70.0


class WheelScroll:
    """Mouse wheel nudges; PyAutoGUI positive scroll = up, negative = down."""

    def __init__(
        self,
        user_activity: Event,
        lock: Lock,
        speed: int,
        random_coef: float,
    ):
        self._log = logging.getLogger(__class__.__name__)
        self._user_activity = user_activity
        self._lock = lock
        self._speed = max(1, int(speed))
        self._random_coef = float(random_coef)

    def nudge_down_then_up(self, total_clicks: int) -> None:
        n = int(total_clicks)
        if n <= 0 or self._user_activity.is_set():
            return
        chunks = Tweening.wheel_click_chunks(n, self._random_coef)
        m = len(chunks)
        time_weights = Tweening.wheel_step_time_weights(m, self._random_coef)
        if len(time_weights) != m:
            time_weights = [1.0] * m
        self._log.debug("Wheel chunks (down then up): %s", chunks)

        self._run_phase(chunks, time_weights, sign=-1)
        self._run_phase(chunks, time_weights, sign=1)

    def _run_phase(self, chunks: list[int], time_weights: list[float], *, sign: int) -> None:
        for i, d in enumerate(chunks):
            if self._user_activity.is_set():
                return
            with self._lock:
                gui.scroll(sign * d, _pause=False)
            if i < len(chunks) - 1:
                self._sleep_pace(d, time_weights[i])

    def _sleep_pace(self, chunk_clicks: int, time_weight: float) -> None:
        segment = float(chunk_clicks) * _WHEEL_CLICK_EQUIV_PX
        base = max(
            0.012,
            min(2.0, segment / (self._speed * _WHEEL_SPEED_DIVISOR)),
        )
        delay = base * max(0.05, time_weight)
        if self._random_coef > 0.0 and random.random() < self._random_coef:
            delay *= random.uniform(0.5, 1.55)
        delay = float(max(0.0, delay))
        if delay > 0.0:
            t_end = time.monotonic() + delay
            while True:
                if self._user_activity.is_set():
                    return
                left = t_end - time.monotonic()
                if left <= 0.0:
                    break
                time.sleep(min(left, 0.05))
