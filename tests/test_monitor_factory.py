import pytest

from awaken.system_idle_monitors.monitor_factory import MonitorFactory


def test_build_with_probe_log_returns_lines(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_list():
        class Fails:
            @classmethod
            def validate(cls) -> None:
                raise OSError("not here")

        class Works:
            @classmethod
            def validate(cls) -> None:
                pass

            def __init__(self) -> None:
                pass

            def get_idle_time(self) -> float:
                return 0.0

        return [Fails, Works]

    monkeypatch.setattr(MonitorFactory, "list", fake_list)
    m, lines = MonitorFactory.build_with_probe_log()
    assert m is not None
    blob = "\n".join(lines)
    assert "skip" in blob
    assert "OK" in blob
    assert "Works" in blob
