import logging
from typing import Optional, Type

from awaken.system_idle_monitors.gnome_wayland_monitor import GnomeWaylandIdleMonitor
from awaken.system_idle_monitors.kde_wayland_monitor import KdeWaylandIdleMonitor
from awaken.system_idle_monitors.monitor import Monitor
from awaken.system_idle_monitors.os_x_monitor import OsXMonitor
from awaken.system_idle_monitors.windows_monitor import WindowsMonitor
from awaken.system_idle_monitors.x_11_monitor import X11Monitor


class MonitorFactory:
    _log = logging.getLogger("MonitorFactory")

    @classmethod
    def build(cls) -> Optional[Monitor]:
        monitor, _lines = cls.build_with_probe_log()
        return monitor

    @classmethod
    def build_with_probe_log(cls) -> tuple[Optional[Monitor], list[str]]:
        """Try each monitor in order; return chosen instance and human-readable probe lines."""
        lines: list[str] = []
        last_exc: BaseException | None = None
        for monitor_class in cls.list():
            name = monitor_class.__name__
            lines.append(f"Try {name}...")
            try:
                monitor_class.validate()
                monitor = monitor_class()
                monitor.get_idle_time()
                lines.append(f"  -> OK, using {name}")
                return monitor, lines
            except Exception as err:
                last_exc = err
                msg = str(err).strip().split("\n", maxsplit=1)[0]
                if len(msg) > 70:
                    msg = msg[:67] + "..."
                lines.append(f"  -> skip: {msg}")
                cls._log.debug(
                    "Idle monitor %s not available",
                    name,
                    exc_info=True,
                )
        lines.append("  -> No native idle monitor (legacy listener timestamps).")
        if last_exc is not None:
            cls._log.info(
                "No system idle monitor could be initialized (%s)",
                last_exc,
            )
        return None, lines

    @classmethod
    def list(cls) -> list[Type[Monitor]]:
        return [
            WindowsMonitor,
            GnomeWaylandIdleMonitor,
            KdeWaylandIdleMonitor,
            X11Monitor,
            OsXMonitor,
        ]
