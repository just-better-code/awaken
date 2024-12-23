import logging

from typing import Optional
from . import *


class MonitorFactory:
    _log = logging.getLogger('MonitorFactory')

    @classmethod
    def build(cls) -> Optional["Monitor"]:
        for monitor_class in cls.list():
            try:
                monitor_class.validate()
                monitor = monitor_class()
                monitor.get_idle_time()

                return monitor
            except Exception as err:
                cls._log.info(str(err))

    @classmethod
    def list(cls) -> list:
        return [
            WindowsMonitor,
            GnomeWaylandIdleMonitor,
            X11Monitor,
            OsXMonitor,
        ]
