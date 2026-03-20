import pytest

from awaken.main import parse_args


def test_parse_args_defaults() -> None:
    cfg = parse_args([])
    assert cfg["idle"] == 60
    assert cfg["delay"] == 30
    assert cfg["key"] == "shift"
    assert cfg["dist"] == 500
    assert cfg["speed"] == 10
    assert cfg["random"] == 0.5
    assert cfg["wheel_clicks"] == 10


def test_parse_args_overrides() -> None:
    cfg = parse_args(
        [
            "--idle",
            "120",
            "--random",
            "0.25",
            "--speed",
            "20",
        ]
    )
    assert cfg["idle"] == 120
    assert cfg["random"] == 0.25
    assert cfg["speed"] == 20


def test_parse_args_random_out_of_range() -> None:
    with pytest.raises(SystemExit):
        parse_args(["--random", "1.1"])


def test_parse_args_wheel_clicks() -> None:
    assert parse_args(["--wheel-clicks", "0"])["wheel_clicks"] == 0
    assert parse_args(["--wheel-clicks", "25"])["wheel_clicks"] == 25


def test_parse_args_wheel_clicks_negative() -> None:
    with pytest.raises(SystemExit):
        parse_args(["--wheel-clicks", "-1"])


def test_parse_args_esc_wake_key_becomes_shift() -> None:
    assert parse_args(["--key", "esc"])["key"] == "shift"
    assert parse_args(["--key", "ESCAPE"])["key"] == "shift"
