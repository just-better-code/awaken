import logging
from threading import Event, Lock

import pyautogui as gui

# Synthetic Esc is delivered to the session (not only the terminal); on KDE it can
# trigger global handlers or crash-prone tools (e.g. Spectacle).
_DISALLOWED_WAKE_KEYS = frozenset({"esc", "escape"})


def sanitize_wake_key(key: str) -> str:
    k = str(key).strip().lower()
    if k in _DISALLOWED_WAKE_KEYS:
        return "shift"
    return k or "shift"


class Keyboard:
    def __init__(self, user_activity: Event, lock: Lock):
        self._log = logging.getLogger(__class__.__name__)
        self._user_activity = user_activity
        self._lock = lock

    def press(self, key: str) -> None:
        if not self._user_activity.is_set():
            key = sanitize_wake_key(key)
            with self._lock:
                self._log.debug(f"Triggering press key `{key}`")
                gui.press(key)
