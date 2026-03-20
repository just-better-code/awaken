import argparse
import logging

from awaken.dto.app_config import AppConfig
from awaken.tui.app import App


def _probability(value: str) -> float:
    x = float(value)
    if not 0.0 <= x <= 1.0:
        raise argparse.ArgumentTypeError("must be between 0 and 1")
    return x


def _non_negative_int(value: str) -> int:
    n = int(value)
    if n < 0:
        raise argparse.ArgumentTypeError("must be >= 0")
    return n


def main() -> None:
    logging.basicConfig()
    logging.root.setLevel(logging.ERROR)
    log = logging.getLogger("Main")
    log.info("*** Program is started ***")
    args = parse_args()
    tui = App(args, log)
    tui.run()


def parse_args(argv: list[str] | None = None) -> AppConfig:
    parser = argparse.ArgumentParser(description="Stay Awake application")
    parser.add_argument(
        "--idle",
        type=int,
        default=60,
        help="Seconds of user inactivity before wake actions (default: 60)",
    )
    parser.add_argument(
        "--delay",
        type=int,
        default=30,
        help="Seconds of system inactivity (legacy / fallback) between checks (default: 30)",
    )
    parser.add_argument("--key", type=str, default="shift", help="Key to press")
    parser.add_argument(
        "--dist",
        type=int,
        default=500,
        help="Cursor move distance in pixels (each axis)",
    )
    parser.add_argument(
        "--speed",
        type=int,
        default=10,
        help="Cursor move speed scale (higher = faster per segment, default: 10)",
    )
    parser.add_argument(
        "--random",
        type=_probability,
        default=0.5,
        metavar="P",
        help="Probability (0–1) of using a random easing curve vs linear (default: 0.5)",
    )
    parser.add_argument(
        "--wheel-clicks",
        type=_non_negative_int,
        default=10,
        metavar="N",
        help="Mouse wheel magnitude per wake: +N then −N clicks (0 = off, default: 10)",
    )
    ns = parser.parse_args(argv)

    return AppConfig(
        idle=ns.idle,
        delay=ns.delay,
        key=ns.key,
        dist=ns.dist,
        speed=ns.speed,
        random=ns.random,
        wheel_clicks=ns.wheel_clicks,
    )


if __name__ == "__main__":
    main()
