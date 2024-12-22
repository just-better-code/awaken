import pyautogui as gui

from awaken.actions.keyboard_listener import KeyboardListener
from threading import Event, Lock


class Keyboard:
    def __init__(self, interrupt: Event):
        self._interrupt = interrupt
        self._lock = Lock()
        self._listener = KeyboardListener(self._interrupt, self._lock)

    def press(self, key: str) -> None:
        if not self._interrupt.is_set() :
            with self._lock: gui.press(key)
