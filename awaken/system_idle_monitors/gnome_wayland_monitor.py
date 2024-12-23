from . import Monitor
from jeepney import DBusAddress, new_method_call
from jeepney.io.blocking import open_dbus_connection

import os


class GnomeWaylandIdleMonitor(Monitor):
    @classmethod
    def validate(cls) -> None:
        if os.getenv('XDG_SESSION_TYPE', '').lower() != 'wayland':
            raise OSError('Gnome wayland based system not detected')

    def __init__(self) -> None:
        address = DBusAddress(
            '/org/gnome/Mutter/IdleMonitor/Core',
            'org.gnome.Mutter.IdleMonitor',
            'org.gnome.Mutter.IdleMonitor',
        )
        self.connection = open_dbus_connection('SESSION')
        self.message = new_method_call(address, 'GetIdletime')

    def get_idle_time(self) -> float:
        reply = self.connection.send_and_get_reply(self.message)
        idle_time = reply[0]

        return idle_time / 1000
