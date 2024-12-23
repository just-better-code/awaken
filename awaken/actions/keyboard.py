import pyautogui as gui
import logging

from threading import Event, Lock


class Keyboard:
    def __init__(self, user_activity: Event, lock: Lock):
        self._log = logging.getLogger(__class__.__name__)
        self._user_activity = user_activity
        self._lock = lock


    def press(self, key: str) -> None:
        if not self._user_activity.is_set() :
            with self._lock:
                self._log.debug(f'Triggering press key `{key}`')
                gui.press(key)
