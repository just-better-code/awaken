import pytest

from awaken.system_idle_monitors.kde_wayland_monitor import KdeWaylandIdleMonitor


def test_kde_validate_requires_wayland(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("XDG_SESSION_TYPE", raising=False)
    with pytest.raises(OSError, match="Wayland"):
        KdeWaylandIdleMonitor.validate()

    monkeypatch.setenv("XDG_SESSION_TYPE", "x11")
    with pytest.raises(OSError, match="Wayland"):
        KdeWaylandIdleMonitor.validate()

    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    KdeWaylandIdleMonitor.validate()
