import queue
from datetime import datetime
from logging import Logger
from threading import Event, Lock, Thread

import pyautogui as gui
from npyscreen import NPSAppManaged

from awaken import Actor, Scheduler
from awaken.dto.app_config import AppConfig
from awaken.host_profile import describe_host_lines
from awaken.tui.main_form import MainForm


class App(NPSAppManaged):
    """Halfdelay interval (tenths of a sec): UI thread runs while_waiting for log drain."""

    keypress_timeout_default = 5

    def __init__(self, args: AppConfig, log: Logger):
        super().__init__()
        self._args = args
        self._log = log
        self._config_lock = Lock()
        self._ui_log_queue: queue.Queue[str] = queue.Queue(maxsize=500)
        self._user_activity = Event()
        self._system_activity = Event()
        self._stop = Event()
        self._emulating_wake = Event()
        self._actor = Actor(
            self._system_activity,
            self._user_activity,
            self._args["speed"],
            self._args["random"],
            emulating_wake=self._emulating_wake,
        )
        self._scheduler = Scheduler(
            self._system_activity,
            self._user_activity,
            self._args["idle"],
            self._args["delay"],
            on_user_return_after_idle=self._on_user_return_after_idle,
        )
        self._actor.set_wheel_clicks(self._args["wheel_clicks"])
        # Daemon: worker can block on PyAutoGUI/pynput under Wayland; exit must not hang on join.
        self._main = Thread(target=self._perform, daemon=True)

    def onStart(self) -> None:
        self._args_form = self.addForm(
            "MAIN",
            MainForm,
            data=self._args,
            name="Stay awake",
            platform_lines=describe_host_lines(),
            idle_monitor_label=self._scheduler.idle_monitor_label,
            log_queue=self._ui_log_queue,
        )
        self._main.start()

    def while_waiting(self) -> None:
        form = getattr(self, "_args_form", None)
        if form is None:
            return
        if hasattr(form, "parse_editable_config"):
            parsed = form.parse_editable_config()
            if parsed is not None:
                with self._config_lock:
                    self._args.update(parsed)
                    self._scheduler.set_thresholds(parsed["idle"], parsed["delay"])
                    self._actor.set_motion_params(parsed["speed"], parsed["random"])
                    self._actor.set_wheel_clicks(parsed["wheel_clicks"])
        if hasattr(form, "refresh_idle_timers"):
            form.refresh_idle_timers()
        if hasattr(form, "drain_log_queue"):
            form.drain_log_queue()

    def onCleanExit(self) -> None:
        self._stop.set()
        self._actor.shutdown()
        self._main.join(timeout=2.0)

    def _perform(self) -> None:
        self._enqueue_ui_log("*** Lets work ***")
        self._enqueue_ui_log("Worker started; polling every 1s.")
        while not self._stop.is_set():
            self._scheduler.ping()
            if self._scheduler.is_must_wake_up():
                with self._config_lock:
                    dist = int(self._args["dist"])
                    key = str(self._args["key"])
                self._emulating_wake.set()
                try:
                    try:
                        self._actor.move_cursor(dist)
                        self._actor.press_key(key)
                        self._actor.nudge_wheel()
                    except gui.FailSafeException:
                        self._enqueue_ui_log(
                            "PyAutoGUI failsafe (corner). Lower dist (px) if this persists."
                        )
                    except Exception as e:
                        self._enqueue_ui_log(
                            f"Wake error: {type(e).__name__}: {e}"
                        )
                finally:
                    self._emulating_wake.clear()
                self._scheduler.notify_wake_completed()
            if self._stop.wait(timeout=1.0):
                break
        self._enqueue_ui_log("Worker stopping.")

    def _enqueue_ui_log(self, message: str) -> None:
        line = f"{datetime.now().strftime('%H:%M:%S')} {message}"
        try:
            self._ui_log_queue.put_nowait(line)
        except queue.Full:
            pass

    def _on_user_return_after_idle(self, idle_span_s: float, session_idle_s: float) -> None:
        self._enqueue_ui_log(
            f"User back after {idle_span_s:.1f}s user-idle "
            f"(session idle sum {session_idle_s:.1f}s)"
        )
