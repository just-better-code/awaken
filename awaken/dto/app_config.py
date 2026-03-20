from typing import TypedDict


class AppConfig(TypedDict):
    idle: int
    delay: int
    key: str
    dist: int
    speed: int
    random: float
    wheel_clicks: int
