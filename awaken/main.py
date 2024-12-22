import argparse

from threading import Event
from time import sleep
from awaken import *


def main() -> None:
    args = parse_args()
    interrupt = Event()
    actor = Actor(interrupt)
    scheduler = Scheduler(interrupt, args.get('idle'), args.get('delay'))
    while True:
        if scheduler.is_must_move():
            actor.move_cursor(args.get('dist'), args.get('speed'), args.get('rand_k'))
            actor.press_key(args.get('key'))
            scheduler.moved()
        sleep(1)


def parse_args() -> dict:
    parser = argparse.ArgumentParser(description="Stay Awake application")
    parser.add_argument("--idle", type=int, default=60, help="Time to first activate (default: 180)")
    parser.add_argument("--delay", type=int, default=30, help="Time between actions (default: 30)")
    parser.add_argument("--key", type=str, default='shift', help="Key to press")
    parser.add_argument("--dist", type=int, default=100, help="Distance for cursor")
    parser.add_argument("--speed", type=int, default=10, help="Speed of cursor moving")
    parser.add_argument("--randomness", type=float, default=0.5, help="Random coefficient (0 : 1)")
    args = parser.parse_args()

    return {
        'idle': args.idle,
        'delay': args.delay,
        'dist': args.dist,
        'speed': args.speed,
        'key': args.key,
        'rand_k': args.randomness
    }

if __name__ == "__main__":
    main()

