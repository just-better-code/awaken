import logging

from pynput.keyboard import Listener
from threading import Event, Lock


class KeyboardListener(Listener):
    def __init__(self, system_activity : Event, user_activity : Event, lock : Lock):
        self._log = logging.getLogger(__class__.__name__)
        self._user_activity = user_activity
        self._system_activity = system_activity
        self._lock = lock
        super().__init__(on_press=self._act)

    def _act(self, *args) -> None:
        if self._user_activity.is_set():
            return
        self._system_activity.set()
        if not self._lock.locked():
            self._user_activity.set()
