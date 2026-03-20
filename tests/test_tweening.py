import pytest
from pyautogui import Point

from awaken.actions.tweening import Tweening


def test_points_num_never_zero_for_coincident_points() -> None:
    p = Point(5, 5)
    num = Tweening._points_num(p, p)
    assert num >= 1


def test_points_covers_endpoints_linear() -> None:
    start = Point(0, 0)
    end = Point(30, 0)
    pts = Tweening.points(start, end, random_coef=0.0)
    assert pts[0] == start
    assert pts[-1] == end


def test_wheel_click_chunks_empty() -> None:
    assert Tweening.wheel_click_chunks(0, random_coef=0.0) == []


def test_wheel_click_chunks_sum_matches_total_linear() -> None:
    for total in (1, 3, 10, 25):
        chunks = Tweening.wheel_click_chunks(total, random_coef=0.0)
        assert sum(chunks) == total
        assert all(c > 0 for c in chunks)


def test_wheel_step_time_weights_sum_and_positive_linear() -> None:
    for n in (1, 2, 5, 12):
        w = Tweening.wheel_step_time_weights(n, random_coef=0.0)
        assert len(w) == n
        assert sum(w) == pytest.approx(n)
        assert all(x > 0 for x in w)
