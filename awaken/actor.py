import logging

from threading import Event, Lock
from awaken.actions import *
from awaken.actions.keyboard_listener import KeyboardListener
from awaken.actions.mouse_listener import MouseListener


class Actor:
    def __init__(self, activity : Event, user_activity : Event):
        self._log = logging.getLogger(__name__)
        self._user_activity = user_activity
        self._activity = activity
        self._keyboard_lock = Lock()
        self._keyboard_listener = KeyboardListener(self._activity, self._user_activity, self._keyboard_lock)
        self._keyboard_listener.start()
        self._mouse_lock = Lock()
        self._mouse_listener = MouseListener(self._activity, self._user_activity, self._mouse_lock)
        self._mouse_listener.start()
        self._log.info('*** Actor is waked up ***')

    def move_cursor(self, dist : int, speed: int = 10, rand_k: float = 0.5):
        self._log.debug('Actor move cursor is triggered')
        action = Cursor(self._user_activity, self._mouse_lock)
        if not self._user_activity.is_set():
            self._log.debug(f'Action move cursor to {dist} is triggered')
            action.move(dist, dist, speed, rand_k)
            self._log.debug(f'Action move cursor to -{dist} is triggered')
            action.move(-dist, -dist, speed, rand_k)

    def press_key(self, key : str):
        self._log.debug('Actor press key is triggered')
        action = Keyboard(self._user_activity, self._keyboard_lock)
        if not self._user_activity.is_set():
            self._log.debug('Action press keyboard is triggered')
            action.press(key)
