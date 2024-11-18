import ctypes
import ctypes.util
import logging
import sys
import re
import subprocess
from ctypes import *
from typing import List, Type, Any

logger = logging.getLogger(name="idle_time")


class IdleMonitor:
    subclasses: List[Type["IdleMonitor"]] = []

    def __init__(self, *, idle_threshold: int = 120) -> None:
        self.idle_threshold = idle_threshold

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        cls.subclasses.append(cls)

    @classmethod
    def get_monitor(cls, **kwargs) -> "IdleMonitor":
        for monitor_class in cls.subclasses:
            try:
                return monitor_class(**kwargs)
            except Exception:
                logger.warning("Could not load %s", monitor_class, exc_info=True)
        raise RuntimeError("Could not find a working monitor.")

    def get_idle_time(self) -> float:
        raise NotImplementedError()

    def is_idle(self) -> bool:
        return self.get_idle_time() > self.idle_threshold


"""
Idle monitor for systems running Windows.
"""
if sys.platform == 'win32':
    class WindowsIdleMonitor(IdleMonitor):
        def get_idle_time(self) -> float:
            class LASTINPUTINFO(Structure):
                _fields_ = [
                    ('cbSize', c_uint),
                    ('dwTime', c_int),
                ]

            lastInputInfo = LASTINPUTINFO()
            lastInputInfo.cbSize = sizeof(lastInputInfo)
            if windll.user32.GetLastInputInfo(byref(lastInputInfo)):
                millis = windll.kernel32.GetTickCount() - lastInputInfo.dwTime
                return millis / 1e3
            else:
                return 0


"""
Idle monitor for systems running Mac OS.
"""
if sys.platform == 'darwin':
    class OsXIdleMonitor(IdleMonitor):
        def get_idle_time(self) -> int:
            cmd = ["ioreg", "-c", "IOHIDSystem"]
            result = subprocess.check_output(cmd, text=True)
            match = re.search(r'HIDIdleTime" = (\d+)', result)
            idle_time = float(match.group(1)) / 1e9 if match else 0
            return idle_time


"""
Idle monitor for systems running X11.
"""
if ctypes.util.find_library('X11') is not None:
    class X11IdleMonitor(IdleMonitor):

        def __init__(self, **kwargs) -> None:
            super().__init__(**kwargs)

            class XScreenSaverInfo(ctypes.Structure):
                _fields_ = [
                    ("window", ctypes.c_ulong),  # screen saver window
                    ("state", ctypes.c_int),  # off, on, disabled
                    ("kind", ctypes.c_int),  # blanked, internal, external
                    ("since", ctypes.c_ulong),  # milliseconds
                    ("idle", ctypes.c_ulong),  # milliseconds
                    ("event_mask", ctypes.c_ulong),
                ]  # events

            lib_x11 = self._load_lib("X11")
            # specify required types
            lib_x11.XOpenDisplay.argtypes = [ctypes.c_char_p]
            lib_x11.XOpenDisplay.restype = ctypes.c_void_p
            lib_x11.XDefaultRootWindow.argtypes = [ctypes.c_void_p]
            lib_x11.XDefaultRootWindow.restype = ctypes.c_uint32
            # fetch current settings
            self.display = lib_x11.XOpenDisplay(None)
            self.root_window = lib_x11.XDefaultRootWindow(self.display)

            self.lib_xss = self._load_lib("Xss")
            # specify required types
            self.lib_xss.XScreenSaverQueryInfo.argtypes = [
                ctypes.c_void_p,
                ctypes.c_uint32,
                ctypes.POINTER(XScreenSaverInfo),
            ]
            self.lib_xss.XScreenSaverQueryInfo.restype = ctypes.c_int
            self.lib_xss.XScreenSaverAllocInfo.restype = ctypes.POINTER(XScreenSaverInfo)
            # allocate memory for idle information
            self.xss_info = self.lib_xss.XScreenSaverAllocInfo()

        def get_idle_time(self) -> float:
            self.lib_xss.XScreenSaverQueryInfo(self.display, self.root_window, self.xss_info)
            return self.xss_info.contents.idle / 1000

        def _load_lib(self, name: str) -> Any:
            path = ctypes.util.find_library(name)
            if path is None:
                raise OSError(f"Could not find library `{name}`")
            return ctypes.cdll.LoadLibrary(path)
