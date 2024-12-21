import os
import sys
import logging

from . import WindowsMonitor, Monitor, OsXMonitor, GnomeWaylandIdleMonitor, X11Monitor


class MonitorFactory:
    logger = logging.getLogger('idle monitor')

    @classmethod
    def build(cls) -> "Monitor":
        for x in cls.list():
            try:
                x.validate()
                return x()
            except Exception as err:
                cls.logger.warning(str(err))

    @classmethod
    def list(cls) -> list:
        return [
            WindowsMonitor,
            GnomeWaylandIdleMonitor,
            X11Monitor,
            OsXMonitor,
        ]
