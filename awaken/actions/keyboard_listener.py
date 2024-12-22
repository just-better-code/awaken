import threading

from pynput.keyboard import Listener
from threading import Event, Lock


class KeyboardListener:
    def __init__(self, interrupt : Event, lock : Lock):
        self._interrupt = interrupt
        self._lock = lock
        listener = Listener(on_press=self._activate)
        self._thread = threading.Thread(target=listener.start, daemon=True)

    def _activate(self, *args):
        if not self._lock.locked():
            self._interrupt.set()

    def start(self):
        if not self._thread.is_alive():
            self._thread.start()

