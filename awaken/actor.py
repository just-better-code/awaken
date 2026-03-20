import logging
import time
from threading import Event, Lock

from awaken.actions.cursor import Cursor
from awaken.actions.keyboard import Keyboard
from awaken.actions.keyboard_listener import KeyboardListener
from awaken.actions.mouse_listener import MouseListener
from awaken.actions.wheel_scroll import WheelScroll

# Let pynput drain OS-queued move/scroll events after PyAutoGUI (avoids flagging our own input).
_SYNTHETIC_MOUSE_GRACE_S = 0.05


class Actor:
    def __init__(
        self,
        system_activity: Event,
        user_activity: Event,
        speed: int,
        random_coef: float,
        *,
        emulating_wake: Event | None = None,
    ):
        self._log = logging.getLogger(__class__.__name__)
        self._user_activity = user_activity
        self._system_activity = system_activity
        self._speed = speed
        self._random_coef = random_coef
        self._wheel_clicks = 0
        self._ignore_mouse_events = Event()
        self._ignore_keyboard_events = Event()
        self._keyboard_lock = Lock()
        self._keyboard_listener = KeyboardListener(
            self._system_activity,
            self._user_activity,
            self._keyboard_lock,
            ignore_keyboard_events=self._ignore_keyboard_events,
            emulating_wake=emulating_wake,
        )
        self._keyboard_listener.start()
        self._mouse_lock = Lock()
        self._mouse_listener = MouseListener(
            self._system_activity,
            self._user_activity,
            self._mouse_lock,
            ignore_mouse_events=self._ignore_mouse_events,
            emulating_wake=emulating_wake,
        )
        self._mouse_listener.start()
        self._log.info("*** Actor is waked up ***")

    def move_cursor(self, dist: int) -> None:
        self._log.debug("Move cursor is triggered")
        action = Cursor(
            self._user_activity,
            self._mouse_lock,
            self._speed,
            self._random_coef,
        )
        if self._user_activity.is_set():
            return
        self._ignore_mouse_events.set()
        try:
            self._log.debug(f"Move cursor to {dist} is triggered")
            action.move(dist, dist)
            self._log.debug(f"Move cursor to -{dist} is triggered")
            action.move(-dist, -dist)
        finally:
            time.sleep(_SYNTHETIC_MOUSE_GRACE_S)
            self._ignore_mouse_events.clear()

    def press_key(self, key: str) -> None:
        self._log.debug("Press key is triggered")
        action = Keyboard(self._user_activity, self._keyboard_lock)
        if self._user_activity.is_set():
            return
        self._log.debug("Press keyboard is triggered")
        self._ignore_keyboard_events.set()
        try:
            action.press(key)
        finally:
            time.sleep(_SYNTHETIC_MOUSE_GRACE_S)
            self._ignore_keyboard_events.clear()

    def set_wheel_clicks(self, clicks: int) -> None:
        self._wheel_clicks = max(0, int(clicks))

    def nudge_wheel(self) -> None:
        n = self._wheel_clicks
        if n == 0 or self._user_activity.is_set():
            return
        self._log.debug("Wheel scroll nudge (%s clicks each way)", n)
        self._ignore_mouse_events.set()
        try:
            WheelScroll(
                self._user_activity,
                self._mouse_lock,
                self._speed,
                self._random_coef,
            ).nudge_down_then_up(n)
        finally:
            time.sleep(_SYNTHETIC_MOUSE_GRACE_S)
            self._ignore_mouse_events.clear()

    def set_motion_params(self, speed: int, random_coef: float) -> None:
        self._speed = max(1, int(speed))
        r = float(random_coef)
        self._random_coef = min(1.0, max(0.0, r))

    def shutdown(self) -> None:
        self._keyboard_listener.stop()
        self._mouse_listener.stop()
        self._keyboard_listener.join()
        self._mouse_listener.join()
