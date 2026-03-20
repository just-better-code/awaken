from threading import Event

import pytest

from awaken.scheduler import Scheduler


@pytest.fixture
def no_monitor(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("awaken.scheduler.MonitorFactory.build", lambda: None)


def test_is_must_wake_up_after_thresholds(
    monkeypatch: pytest.MonkeyPatch, no_monitor: None
) -> None:
    clock = {"t": 0.0}
    monkeypatch.setattr("awaken.scheduler.time", lambda: clock["t"])

    sa, ua = Event(), Event()
    s = Scheduler(sa, ua, idle=60, delay=30)
    clock["t"] = 50.0
    assert not s.is_must_wake_up()

    clock["t"] = 70.0
    assert s.is_must_wake_up()


def test_set_thresholds_changes_wake_condition(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("awaken.scheduler.MonitorFactory.build", lambda: None)
    clock = {"t": 0.0}
    monkeypatch.setattr("awaken.scheduler.time", lambda: clock["t"])
    s = Scheduler(Event(), Event(), idle=60, delay=30)
    clock["t"] = 50.0
    assert not s.is_must_wake_up()
    s.set_thresholds(40, 20)
    assert s.is_must_wake_up()


def test_idle_seconds_after_time_passes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("awaken.scheduler.MonitorFactory.build", lambda: None)
    clock = {"t": 1000.0}
    monkeypatch.setattr("awaken.scheduler.time", lambda: clock["t"])
    s = Scheduler(Event(), Event(), 60, 30)
    assert s.user_idle_seconds() == 0.0
    assert s.system_idle_seconds() == 0.0
    clock["t"] = 1005.5
    assert s.user_idle_seconds() == pytest.approx(5.5)
    assert s.system_idle_seconds() == pytest.approx(5.5)


def test_user_return_accumulates_session_and_callbacks(
    monkeypatch: pytest.MonkeyPatch, no_monitor: None
) -> None:
    clock = {"t": 1000.0}
    monkeypatch.setattr("awaken.scheduler.time", lambda: clock["t"])
    calls: list[tuple[float, float]] = []
    ua = Event()
    s = Scheduler(
        Event(),
        ua,
        60,
        30,
        on_user_return_after_idle=lambda sp, tot: calls.append((sp, tot)),
    )
    clock["t"] = 1030.0
    ua.set()
    s.ping()
    assert calls == [(30.0, 30.0)]
    assert s.session_user_idle_total() == pytest.approx(30.0)

    clock["t"] = 1065.0
    ua.set()
    s.ping()
    assert calls[-1] == (35.0, 65.0)
    assert s.session_user_idle_total() == pytest.approx(65.0)


def test_user_return_skips_short_span_for_callback(
    monkeypatch: pytest.MonkeyPatch, no_monitor: None
) -> None:
    clock = {"t": 100.0}
    monkeypatch.setattr("awaken.scheduler.time", lambda: clock["t"])
    calls: list[tuple[float, float]] = []
    ua = Event()
    s = Scheduler(
        Event(),
        ua,
        60,
        30,
        on_user_return_after_idle=lambda sp, tot: calls.append((sp, tot)),
    )
    clock["t"] = 100.3
    ua.set()
    s.ping()
    assert calls == []
    assert s.session_user_idle_total() == pytest.approx(0.3)


def test_user_return_no_callback_when_span_below_delay(
    monkeypatch: pytest.MonkeyPatch, no_monitor: None
) -> None:
    clock = {"t": 1000.0}
    monkeypatch.setattr("awaken.scheduler.time", lambda: clock["t"])
    calls: list[tuple[float, float]] = []
    ua = Event()
    s = Scheduler(
        Event(),
        ua,
        60,
        30,
        on_user_return_after_idle=lambda sp, tot: calls.append((sp, tot)),
    )
    clock["t"] = 1020.0
    ua.set()
    s.ping()
    assert calls == []
    assert s.session_user_idle_total() == pytest.approx(20.0)


def test_user_return_callback_when_span_equals_delay(
    monkeypatch: pytest.MonkeyPatch, no_monitor: None
) -> None:
    clock = {"t": 1000.0}
    monkeypatch.setattr("awaken.scheduler.time", lambda: clock["t"])
    calls: list[tuple[float, float]] = []
    ua = Event()
    s = Scheduler(
        Event(),
        ua,
        60,
        30,
        on_user_return_after_idle=lambda sp, tot: calls.append((sp, tot)),
    )
    clock["t"] = 1030.0
    ua.set()
    s.ping()
    assert calls == [(30.0, 30.0)]


def test_idle_monitor_label_legacy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("awaken.scheduler.MonitorFactory.build", lambda: None)
    s = Scheduler(Event(), Event(), 60, 30)
    assert s.idle_monitor_label == "Legacy (listener timestamps)"


def test_wayland_skips_os_idle_monitor_without_calling_factory(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")

    def boom() -> None:
        raise AssertionError("MonitorFactory.build should not run on Wayland")

    monkeypatch.setattr("awaken.scheduler.MonitorFactory.build", boom)
    s = Scheduler(Event(), Event(), 60, 30)
    assert s.idle_monitor_label == "Legacy (listener timestamps)"


def test_awaken_use_native_idle_forces_factory_on_wayland(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setenv("AWAKEN_USE_NATIVE_IDLE", "1")
    monkeypatch.setattr("awaken.scheduler.MonitorFactory.build", lambda: None)
    s = Scheduler(Event(), Event(), 60, 30)
    assert s.idle_monitor_label == "Legacy (listener timestamps)"
