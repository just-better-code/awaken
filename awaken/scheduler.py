import logging
from collections.abc import Callable
from threading import Event
from time import time
from typing import Optional

from awaken.system_idle_monitors import Monitor
from awaken.system_idle_monitors.monitor_factory import MonitorFactory


class Scheduler:
    def __init__(
        self,
        system_activity: Event,
        user_activity: Event,
        idle: int,
        delay: int,
        *,
        on_user_return_after_idle: Optional[Callable[[float, float], None]] = None,
    ):
        self._log = logging.getLogger(__class__.__name__)
        self._user_activity = user_activity
        self._system_activity = system_activity
        self._on_user_return_after_idle = on_user_return_after_idle
        self._session_user_idle = 0.0
        self._system_idle_monitor = self._build_idle_monitor()
        self._user_activity_ts = time()
        self._system_activity_ts = time()
        self._idle = idle
        self._delay = delay
        # After a wake, OS idle monitors (e.g. KDE) often ignore synthetic input; without a
        # cooldown, is_must_wake_up stays true and the worker hammers the cursor every second.
        self._wake_grace_until = 0.0

    @property
    def idle_monitor_label(self) -> str:
        if self._system_idle_monitor is None:
            return "Legacy (listener timestamps)"
        return self._system_idle_monitor.__class__.__name__

    def _build_idle_monitor(self) -> Optional["Monitor"]:
        monitor = MonitorFactory.build()
        if monitor is None:
            self._log.info("Cant initialize proper system idle monitor. Using legacy mode")
        else:
            self._log.info(f"Using {monitor.__class__.__name__} for system idle monitoring")

        return monitor

    def is_must_wake_up(self) -> bool:
        if time() < self._wake_grace_until:
            return False
        return self._user_idle() > self._idle and self._system_idle() > self._delay

    def notify_wake_completed(self) -> None:
        """Call after each wake attempt so we do not re-enter while OS idle stays high."""
        self._wake_grace_until = time() + float(self._delay)
        self._system_activity.set()

    def ping(self) -> None:
        if self._user_activity.is_set():
            now = time()
            span = now - self._user_activity_ts
            self._session_user_idle += span
            self._user_activity_ts = now
            self._user_activity.clear()
            self._log.debug("Detected user activity")
            if (
                self._on_user_return_after_idle is not None
                and span >= self._delay
            ):
                self._on_user_return_after_idle(span, self._session_user_idle)
        if self._system_activity.is_set():
            self._system_activity_ts = time()
            self._system_activity.clear()
            self._log.debug("Detected system activity")

    def _system_idle(self) -> float:
        if self._system_idle_monitor is not None:
            return self._system_idle_monitor.get_idle_time()
        return time() - self._system_activity_ts

    def _user_idle(self) -> float:
        return time() - self._user_activity_ts

    def user_idle_seconds(self) -> float:
        """Seconds since last user input (keyboard/mouse) as tracked by listeners."""
        return self._user_idle()

    def session_user_idle_total(self) -> float:
        """Sum of completed user-idle spans (time between last activity and next)."""
        return self._session_user_idle

    def system_idle_seconds(self) -> float:
        """Seconds of system idle from OS monitor or listener-based fallback."""
        return self._system_idle()

    def set_thresholds(self, idle: int, delay: int) -> None:
        self._idle = max(1, int(idle))
        self._delay = max(1, int(delay))
