import math
import random
from typing import List

import pytweening as tw
from pyautogui import Point


class Tweening:
    _EASINGS = (
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
    )

    @classmethod
    def points(cls, start: Point, end: Point, random_coef: float) -> List[Point]:
        num = cls._points_num(start, end)
        tween = cls._pick_tween(random_coef)
        points = []
        for n in range(0, num + 1):
            point = tw.getPointOnLine(*start, *end, tween(n / num))
            points.append(Point(int(point[0]), int(point[1])))

        return points

    @classmethod
    def _points_num(cls, start: Point, end: Point) -> int:
        dist = math.dist(list(start), list(end))
        # At least 1 so n/num in points() is always defined (avoid div by zero).
        return max(1, int(dist / 10))

    @classmethod
    def _pick_tween(cls, random_coef: float):
        if random.random() < random_coef:
            return random.choice(cls._EASINGS)
        return tw.linear

    @classmethod
    def wheel_click_chunks(cls, total: int, random_coef: float) -> List[int]:
        """Split *total* wheel clicks into segment sizes (sum == total).

        Uses the same random-vs-linear easing pick as cursor paths, then samples a
        monotonic eased progress curve to obtain varying chunk sizes.
        """
        total = int(total)
        if total <= 0:
            return []
        steps = max(1, min(total, max(2, total // 3)))
        easing = cls._pick_tween(random_coef)
        mono_t: list[float] = []
        acc = 0.0
        for i in range(steps + 1):
            u = float(easing(i / steps))
            u = max(0.0, min(1.0, u))
            acc = max(acc, u)
            mono_t.append(acc)
        end = mono_t[-1]
        if end < 1e-9:
            return [total]
        cum = [t / end * total for t in mono_t]
        raw_d = [cum[i + 1] - cum[i] for i in range(steps)]
        s = sum(raw_d)
        if s <= 1e-9:
            return [total]
        scaled = [max(0.0, d / s * total) for d in raw_d]
        ints = [int(x) for x in scaled]
        drift = total - sum(ints)
        j = 0
        while drift > 0:
            ints[j % len(ints)] += 1
            drift -= 1
            j += 1
        while drift < 0:
            if ints[j % len(ints)] > 0:
                ints[j % len(ints)] -= 1
                drift += 1
            j += 1
        out = [x for x in ints if x > 0]
        return out if out else [total]

    @classmethod
    def wheel_step_time_weights(cls, n: int, random_coef: float) -> List[float]:
        """Non-linear pacing weights for *n* wheel steps; sum == n, mean 1 (like cursor rhythm)."""
        n = int(n)
        if n <= 0:
            return []
        if n == 1:
            return [1.0]
        easing = cls._pick_tween(random_coef)
        mono_t: list[float] = []
        acc = 0.0
        for i in range(n + 1):
            u = float(easing(i / n))
            u = max(0.0, min(1.0, u))
            acc = max(acc, u)
            mono_t.append(acc)
        end = mono_t[-1]
        if end < 1e-9:
            return [1.0] * n
        cum = [t / end for t in mono_t]
        raw = [max(1e-9, cum[i + 1] - cum[i]) for i in range(n)]
        s = sum(raw)
        return [x / s * n for x in raw]

    @classmethod
    def _validate(cls, n: float) -> None:
        if not 0.0 <= n <= 1.0:
            raise ValueError("Argument must be between 0.0 and 1.0.")
