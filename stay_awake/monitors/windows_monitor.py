from abc import ABC

from . import Monitor
from .info import LastInputInfo
from ctypes import *
import sys


class WindowsMonitor(Monitor, ABC):
    @classmethod
    def validate(cls) -> None:
        if sys.platform != 'win32':
            raise OSError('Not a windows')

    def get_idle_time(self) -> float:
        info = LastInputInfo()
        info.cbSize = sizeof(info)

        if windll.user32.GetLastInputInfo(byref(info)):
            return (windll.kernel32.GetTickCount() - info.dwTime) / 1e3
        else:
            return 0.0
