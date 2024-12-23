import logging

from threading import Event
from time import time
from typing import Optional

from awaken.system_idle_monitors import Monitor
from awaken.system_idle_monitors.monitor_factory import MonitorFactory


class Scheduler:
    def __init__(self, system_activity : Event,user_activity : Event, idle : int, delay: int):
        self._log = logging.getLogger(__class__.__name__)
        self._user_activity = user_activity
        self._system_activity = system_activity
        self._system_idle_monitor = self._build_idle_monitor()
        self._init_ts = time()
        self._user_activity_ts = time()
        self._system_activity_ts = time()
        self._idle = idle
        self._delay = delay

    def _build_idle_monitor(self) -> Optional["Monitor"]:
        monitor = MonitorFactory.build()
        if monitor is None:
            self._log.info('Cant initialize proper system idle monitor. Using legacy mode')
        else:
            self._log.info(f'Using {monitor.__class__.__name__} for system idle monitoring')

        return monitor

    def is_must_wake_up(self) -> bool:
        return self._user_idle() > self._idle and self._system_idle() > self._delay

    def ping(self) -> None:
        if self._user_activity.is_set():
            self._user_activity_ts = time()
            self._user_activity.clear()
            self._log.debug('Detected user activity')
        if self._system_activity.is_set():
            self._system_activity_ts = time()
            self._system_activity.clear()
            self._log.debug('Detected system activity')

    def _system_idle(self) -> float:
        if self._system_idle_monitor is not None:
            return self._system_idle_monitor.get_idle_time()
        return time() - self._system_activity_ts

    def _user_idle(self) -> float:
        return time() - self._user_activity_ts