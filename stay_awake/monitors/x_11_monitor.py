from . import Monitor
from stay_awake.dto import *
from abc import ABC
from ctypes import cdll, util, c_void_p, c_char_p, c_uint32, POINTER, c_int
from typing import Any

import os


class X11Monitor(Monitor, ABC):
    @classmethod
    def validate(cls) -> None:
        if os.getenv('XDG_SESSION_TYPE', '').lower() != 'x11':
            raise OSError('Not a x11')

    def __init__(self) -> None:
        x11 = self.load_lib("X11")
        x11.XOpenDisplay.argtypes = [c_char_p]
        x11.XOpenDisplay.restype = c_void_p
        x11.XDefaultRootWindow.argtypes = [c_void_p]
        x11.XDefaultRootWindow.restype = c_uint32
        self.display = x11.XOpenDisplay(None)
        self.root_window = x11.XDefaultRootWindow(self.display)

        self.xss = self.load_lib("Xss")
        self.xss.XScreenSaverQueryInfo.argtypes = [
            c_void_p,
            c_uint32,
            POINTER(XScreenSaverInfo),
        ]
        self.xss.XScreenSaverQueryInfo.restype = c_int
        self.xss.XScreenSaverAllocInfo.restype = POINTER(XScreenSaverInfo)
        self.xss_info = self.xss.XScreenSaverAllocInfo()

    def get_idle_time(self) -> float:
        self.xss.XScreenSaverQueryInfo(self.display, self.root_window, self.xss_info)

        return self.xss_info.contents.idle / 1000

    def load_lib(self, name: str) -> Any:
        path = util.find_library(name)
        if path is None:
            raise OSError(f"Could not find library `{name}`")

        return cdll.LoadLibrary(path)
