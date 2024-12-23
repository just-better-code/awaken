import logging

from pynput.keyboard import Listener
from threading import Event, Lock


class KeyboardListener:
    def __init__(self, system_activity : Event, user_activity : Event, lock : Lock):
        self._log = logging.getLogger(__class__.__name__)
        self._user_activity = user_activity
        self._system_activity = system_activity
        self._lock = lock
        self._listener = Listener(on_press=self._act, daemon=True, )

    def _act(self, *args):
        self._system_activity.set()
        if not self._lock.locked():
            self._user_activity.set()

    def start(self):
        if not self._listener.is_alive():
            self._listener.start()
            self._log.debug('Thread is started')


