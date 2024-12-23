import subprocess
import re
import sys

from . import Monitor


class OsXMonitor(Monitor):
    @classmethod
    def validate(cls) -> None:
        if sys.platform != 'darwin':
            raise OSError('MacOs system not detected')

    def get_idle_time(self) -> float:
        cmd = ["ioreg", "-c", "IOHIDSystem"]
        result = subprocess.check_output(cmd, text=True)
        match = re.search(r'HIDIdleTime" = (\d+)', result)
        idle_time = float(match.group(1)) / 1e9 if match else 0.0

        return idle_time