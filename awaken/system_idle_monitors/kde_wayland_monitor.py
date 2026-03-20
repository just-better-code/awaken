import os

from jeepney import DBusAddress, new_method_call
from jeepney.io.blocking import open_dbus_connection

from awaken.system_idle_monitors.monitor import Monitor


class KdeWaylandIdleMonitor(Monitor):
    """
    KDE Plasma (and compatible sessions) on Wayland: idle time via session D-Bus.

    See e.g. ``gdbus call --session --dest org.kde.KIdleTime --object-path /KIdleTime
    --method org.kde.KIdleTime.getIdleTime``.
    """

    @classmethod
    def validate(cls) -> None:
        if os.getenv("XDG_SESSION_TYPE", "").lower() != "wayland":
            raise OSError("KDE Wayland idle monitor requires a Wayland session")

    def __init__(self) -> None:
        address = DBusAddress(
            "/KIdleTime",
            "org.kde.KIdleTime",
            "org.kde.KIdleTime",
        )
        self.connection = open_dbus_connection("SESSION")
        self.message = new_method_call(address, "getIdleTime")

    def get_idle_time(self) -> float:
        reply = self.connection.send_and_get_reply(self.message)
        idle_ms = reply[0]
        return float(idle_ms) / 1000.0
