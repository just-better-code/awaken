import sys

from . import Monitor
from awaken.dto import LastInputInfo
from ctypes import *


class WindowsMonitor(Monitor):
    @classmethod
    def validate(cls) -> None:
        if sys.platform != 'win32':
            raise OSError('Windows not detected')

    def get_idle_time(self) -> float:
        info = LastInputInfo()
        info.cbSize = sizeof(info)

        if windll.user32.GetLastInputInfo(byref(info)):
            return (windll.kernel32.GetTickCount() - info.dwTime) / 1e3
        else:
            return 0.0
