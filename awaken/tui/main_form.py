import queue
from typing import TYPE_CHECKING, Any

from npyscreen import (
    FormBaseNew,
    MiniButtonPress,
    TitleCombo,
    TitleMultiLine,
    TitleText,
    wgwidget,
)

if TYPE_CHECKING:
    from awaken.dto.app_config import AppConfig


def _field_text(widget: Any) -> str:
    v = getattr(widget, "value", None)
    if v is None:
        return ""
    return str(v).strip()


def _key_choice_list(current: str) -> tuple[list[str], int]:
    """Ordered keys for pyautogui.press; current config is always selectable."""
    normalized = str(current).strip().lower() or "shift"
    choices = [
        "shift",
        "ctrl",
        "alt",
        "space",
        "tab",
        "enter",
        "return",
        "esc",
        "backspace",
        "delete",
        "home",
        "end",
        "pageup",
        "pagedown",
        "left",
        "right",
        "up",
        "down",
    ]
    choices += [f"f{i}" for i in range(1, 13)]
    if normalized not in choices:
        choices = [normalized] + choices
    return choices, choices.index(normalized)


def _combo_key_string(widget: Any) -> str | None:
    """TitleCombo stores selected index in .value."""
    idx = getattr(widget, "value", None)
    if idx is None or idx == "":
        return None
    if not isinstance(idx, int):
        try:
            idx = int(idx)
        except (TypeError, ValueError):
            return None
    vals = getattr(widget, "values", None)
    if not vals or idx < 0 or idx >= len(vals):
        return None
    s = str(vals[idx]).strip()
    return s or None


class MainForm(FormBaseNew):
    _LOG_MAX_LINES = 5

    def __init__(
        self,
        parentApp=None,
        *,
        data: "AppConfig",
        platform_lines: list[str],
        idle_monitor_label: str,
        log_queue: "queue.Queue[str]",
        **kwargs,
    ):
        self._data = data
        self._platform_lines = list(platform_lines)
        self._platform_lines.append("")
        self._platform_lines.append(f"Idle detection: {idle_monitor_label}")
        self._log_queue = log_queue
        self._log_lines: list[str] = []
        self._log_widget: TitleText | None = None
        self._user_idle_title: TitleText | None = None
        self._system_idle_title: TitleText | None = None
        self._session_idle_title: TitleText | None = None
        self._stay_awake_title: TitleText | None = None
        self._w_idle: TitleText | None = None
        self._w_delay: TitleText | None = None
        self._w_key: TitleCombo | None = None
        self._w_wheel: TitleText | None = None
        self._w_dist: TitleText | None = None
        self._w_speed: TitleText | None = None
        self._w_random: TitleText | None = None
        super().__init__(parentApp=parentApp, **kwargs)

    def set_up_exit_condition_handlers(self) -> None:
        super().set_up_exit_condition_handlers()
        self.how_exited_handers[wgwidget.EXITED_ESCAPE] = self.h_escape_quit_app

    def h_escape_quit_app(self, *args: object) -> None:
        self.editing = False
        try:
            self._widgets__[self.editw].editing = False
        except (AttributeError, IndexError, TypeError):
            pass
        try:
            self._widgets__[self.editw].entry_widget.editing = False
        except (AttributeError, IndexError, TypeError):
            pass
        self.parentApp.setNextForm(None)

    def create(self) -> None:
        pad_h = self.curses_pad.getmaxyx()[0]
        host_max = min(5, max(2, pad_h - 20))
        self.add(
            TitleMultiLine,
            name="Host",
            max_height=host_max,
            relx=1,
            values=self._platform_lines,
            editable=False,
            scroll_exit=False,
        )
        self._user_idle_title = self.add(
            TitleText,
            name="User idle",
            value="—",
            editable=False,
            begin_entry_at=18,
        )
        self._system_idle_title = self.add(
            TitleText,
            name="System idle",
            value="—",
            editable=False,
            begin_entry_at=18,
        )
        self._session_idle_title = self.add(
            TitleText,
            name="Session idle",
            value="—",
            editable=False,
            begin_entry_at=18,
        )
        self._stay_awake_title = self.add(
            TitleText,
            name="Stay-awake",
            value="—",
            editable=False,
            begin_entry_at=18,
        )
        d = self._data
        be = 14
        self._w_idle = self.add(
            TitleText,
            name="idle (s)",
            value=str(d.get("idle", "")),
            begin_entry_at=be,
        )
        self._w_delay = self.add(
            TitleText,
            name="delay (s)",
            value=str(d.get("delay", "")),
            begin_entry_at=be,
        )
        key_choices, key_idx = _key_choice_list(str(d.get("key", "shift")))
        self._w_key = self.add(
            TitleCombo,
            name="key",
            values=key_choices,
            value=key_idx,
            begin_entry_at=be,
        )
        self._w_wheel = self.add(
            TitleText,
            name="wheel",
            value=str(int(d.get("wheel_clicks", 10))),
            begin_entry_at=be,
        )
        self._w_dist = self.add(
            TitleText,
            name="dist (px)",
            value=str(d.get("dist", "")),
            begin_entry_at=be,
        )
        self._w_speed = self.add(
            TitleText,
            name="speed",
            value=str(d.get("speed", "")),
            begin_entry_at=be,
        )
        self._w_random = self.add(
            TitleText,
            name="random",
            value=str(d.get("random", "")),
            begin_entry_at=be,
        )

        def quit_app() -> None:
            self.editing = False
            self.parentApp.setNextForm(None)

        self.add(
            MiniButtonPress,
            name=" Quit ",
            when_pressed_function=quit_app,
            relx=1,
        )
        # Single-line TitleText only: TitleMultiLine/MultiLine often crashes on short pads (height False).
        self._log_widget = self.add(
            TitleText,
            name="Log",
            value="",
            editable=False,
            begin_entry_at=6,
        )

    def parse_editable_config(self) -> dict[str, Any] | None:
        """Return a full config dict if all fields are valid; otherwise None."""
        if not all(
            (
                self._w_idle,
                self._w_delay,
                self._w_key,
                self._w_wheel,
                self._w_dist,
                self._w_speed,
                self._w_random,
            )
        ):
            return None
        try:
            idle = int(_field_text(self._w_idle))
            delay = int(_field_text(self._w_delay))
            dist = int(_field_text(self._w_dist))
            speed = int(_field_text(self._w_speed))
            rnd_s = _field_text(self._w_random).replace(",", ".")
            rnd = float(rnd_s)
            key = _combo_key_string(self._w_key)
            if not key:
                return None
            wheel_clicks = int(_field_text(self._w_wheel))
            if wheel_clicks < 0:
                return None
            return {
                "idle": max(1, idle),
                "delay": max(1, delay),
                "key": key,
                "dist": max(1, dist),
                "speed": max(1, speed),
                "random": min(1.0, max(0.0, rnd)),
                "wheel_clicks": wheel_clicks,
            }
        except (ValueError, TypeError):
            return None

    def refresh_idle_timers(self) -> None:
        if (
            self._user_idle_title is None
            or self._system_idle_title is None
            or self._session_idle_title is None
            or self._stay_awake_title is None
        ):
            return
        sched = getattr(self.parentApp, "_scheduler", None)
        if sched is None:
            return
        u = sched.user_idle_seconds()
        s = sched.system_idle_seconds()
        sess = sched.session_user_idle_total()
        need_u = self._data["idle"]
        need_s = self._data["delay"]
        self._user_idle_title.value = f"{u:.1f}s  (wake if >{need_u}s)"
        self._system_idle_title.value = f"{s:.1f}s  (wake if >{need_s}s)"
        self._session_idle_title.value = f"{sess:.1f}s  (sum of idle spans)"
        em = getattr(self.parentApp, "_emulating_wake", None)
        if em is not None and em.is_set():
            self._stay_awake_title.value = "emitting (cursor / key / wheel)"
        elif u >= float(need_u):
            self._stay_awake_title.value = f"armed — user idle ≥ {need_u}s"
        else:
            self._stay_awake_title.value = "standby — below user-idle threshold"
        self._user_idle_title.display()
        self._system_idle_title.display()
        self._session_idle_title.display()
        self._stay_awake_title.display()

    def drain_log_queue(self) -> None:
        if self._log_widget is None:
            return
        changed = False
        while True:
            try:
                msg = self._log_queue.get_nowait()
            except queue.Empty:
                break
            self._log_lines.append(msg)
            while len(self._log_lines) > self._LOG_MAX_LINES:
                self._log_lines.pop(0)
            changed = True
        if changed:
            self._log_widget.value = self._log_text_for_widget()
            self._log_widget.display()

    def _log_text_for_widget(self) -> str:
        if not self._log_lines:
            return ""
        joined = " · ".join(self._log_lines[-self._LOG_MAX_LINES :])
        if len(joined) > 240:
            return "…" + joined[-237:]
        return joined
