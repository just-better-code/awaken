import logging

from threading import Event
from time import time


class Scheduler:
    def __init__(self, activity : Event,user_activity : Event, idle : int, delay: int):
        self._log = logging.getLogger(__name__)
        self._log.info('*** Scheduler is waked up ***')
        self._user_activity = user_activity
        self._activity = activity
        self._init_ts = time()
        self._user_activity_ts = time()
        self._activity_ts = time()
        self._idle = idle
        self._delay = delay

    def is_must_wake_up(self):
        self._define_activity()
        first_idle = time() - self._user_activity_ts
        middle_idle = time() - self._activity_ts

        return first_idle > self._idle and middle_idle > self._delay

    def _define_activity(self) -> None:
        if self._user_activity.is_set():
            self._user_activity_ts = time()
            self._user_activity.clear()
            self._log.debug('Detected user activity')
        if self._activity.is_set():
            self._activity_ts = time()
            self._activity.clear()
            self._log.debug('Detected activity')
