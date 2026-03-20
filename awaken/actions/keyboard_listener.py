import logging
from threading import Event, Lock

from pynput.keyboard import Listener


class KeyboardListener(Listener):
    def __init__(
        self,
        system_activity: Event,
        user_activity: Event,
        lock: Lock,
        *,
        ignore_keyboard_events: Event | None = None,
        emulating_wake: Event | None = None,
    ):
        self._log = logging.getLogger(__class__.__name__)
        self._user_activity = user_activity
        self._system_activity = system_activity
        self._lock = lock
        self._ignore_keyboard_events = ignore_keyboard_events
        self._emulating_wake = emulating_wake
        super().__init__(on_press=self._act)

    def _act(self, *args) -> None:
        if (
            self._ignore_keyboard_events is not None
            and self._ignore_keyboard_events.is_set()
        ):
            return
        if self._user_activity.is_set():
            return
        self._system_activity.set()
        in_wake = (
            self._emulating_wake is not None and self._emulating_wake.is_set()
        )
        if not self._lock.locked() or in_wake:
            self._user_activity.set()
