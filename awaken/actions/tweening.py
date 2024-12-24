import math
import random
import pytweening as tw
from pyautogui import Point
from typing import List

class Tweening:
    @classmethod
    def points(cls, start : Point, end : Point) -> List[Point]:
        num = cls._points_num(start, end)
        tween = cls._random()
        points = []
        for n in range(0, num + 1):
            point = tw.getPointOnLine(*start, *end, tween(n / num))
            points.append(Point(int(point[0]), int(point[1])))

        return points

    @classmethod
    def _points_num(cls, start : Point, end : Point) -> int:
        dist = math.dist(list(start), list(end))

        return int(dist / 10)

    @classmethod
    def _random(cls):
        return random.choice((
            tw.linear,
            tw.easeInQuad,
            tw.easeOutQuad,
            tw.easeInOutQuad,
            tw.easeInCubic,
            tw.easeOutCubic,
            tw.easeInOutCubic,
            tw.easeInQuart,
            tw.easeOutQuart,
            tw.easeInOutQuart,
            tw.easeInQuint,
            tw.easeOutQuint,
            tw.easeInOutQuint,
            tw.easeInSine,
            tw.easeOutSine,
            tw.easeInOutSine,
            tw.easeInExpo,
            tw.easeOutExpo,
            tw.easeInOutExpo,
            tw.easeInCirc,
            tw.easeOutCirc,
            tw.easeInOutCirc,
            tw.easeInBounce,
            tw.easeOutBounce,
            tw.easeInOutBounce,
            tw.easeInBack,
            tw.easeOutBack,
            tw.easeInOutBack,
        ))

    @classmethod
    def _validate(cls, n: float) -> None:
        if not 0.0 <= n <= 1.0:
            raise ValueError("Argument must be between 0.0 and 1.0.")
