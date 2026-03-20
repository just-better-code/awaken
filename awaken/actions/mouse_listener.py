import logging
from threading import Event, Lock

from pynput.mouse import Listener


class MouseListener(Listener):
    def __init__(
        self,
        system_activity: Event,
        user_activity: Event,
        lock: Lock,
        *,
        ignore_mouse_events: Event | None = None,
        emulating_wake: Event | None = None,
    ):
        self._log = logging.getLogger(__class__.__name__)
        self._user_activity = user_activity
        self._system_activity = system_activity
        self._lock = lock
        self._ignore_mouse_events = ignore_mouse_events
        self._emulating_wake = emulating_wake
        super().__init__(on_move=self._act, on_click=self._act, on_scroll=self._act)

    def _act(self, *args) -> None:
        if self._ignore_mouse_events is not None and self._ignore_mouse_events.is_set():
            return
        # Always mark system activity: if user_activity is already set we used to return
        # early and never refreshed system idle (legacy / Wayland looked like a dumb timer).
        self._system_activity.set()
        if self._user_activity.is_set():
            return
        in_wake = (
            self._emulating_wake is not None and self._emulating_wake.is_set()
        )
        if not self._lock.locked() or in_wake:
            self._user_activity.set()
