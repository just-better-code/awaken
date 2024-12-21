import argparse

from stay_awake.monitors import Monitor
from stay_awake.monitors.monitor_factory import MonitorFactory

def main() -> None:
    parser = argparse.ArgumentParser(description="Stay Awake application")
    parser.add_argument(
        "--iddle-time",
        type=int,
        default=0,
        help="Idle time in seconds (default: 0)"
    )
    args = parser.parse_args()
    idle_time = args.iddle_time





    monitor: Monitor = MonitorFactory.build()


if __name__ == "__main__":
    main()

