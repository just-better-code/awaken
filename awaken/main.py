import argparse
import logging

from awaken.tui.app import App

def main() -> None:
    logging.basicConfig()
    logging.root.setLevel(logging.ERROR)
    log = logging.getLogger('Main')
    log.info('*** Program is started ***')
    args = parse_args()
    tui = App(args, log)
    tui.run()


def parse_args() -> dict:
    parser = argparse.ArgumentParser(description="Stay Awake application")
    parser.add_argument("--idle", type=int, default=60, help="Time to first activate (default: 180)")
    parser.add_argument("--delay", type=int, default=30, help="Time between actions (default: 30)")
    parser.add_argument("--key", type=str, default='shift', help="Key to press")
    parser.add_argument("--dist", type=int, default=500, help="Distance for cursor")
    parser.add_argument("--speed", type=int, default=10, help="Speed of cursor moving")
    parser.add_argument("--random", type=float, default=0.5, help="Random coefficient (0 : 1)")
    args = parser.parse_args()

    return {
        'idle': args.idle,
        'delay': args.delay,
        'key': args.key,
        'dist': args.dist,
        'speed': args.speed,
        'random': args.random
    }

if __name__ == "__main__":
    main()



