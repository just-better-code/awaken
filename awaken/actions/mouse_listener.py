import threading
import logging

from pynput.mouse import Listener
from threading import Event, Lock


class MouseListener:
    def __init__(self, activity : Event, user_activity : Event, lock : Lock):
        self._log = logging.getLogger(__name__)
        self._user_activity = user_activity
        self._activity = activity
        self._lock = lock
        self._listener = Listener(on_move=self._activate, on_click=self._activate, on_scroll=self._activate)
        self._thread = threading.Thread(target=self._listener.start, daemon=True)

    def _activate(self, *args):
        self._activity.set()
        if not self._lock.locked():
            self._user_activity.set()

    def start(self):
        if not self._thread.is_alive():
            self._thread.start()
            self._log.debug('Thread is started')


