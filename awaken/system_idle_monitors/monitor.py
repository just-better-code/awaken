from abc import ABC, abstractmethod


class Monitor(ABC):
    @abstractmethod
    def get_idle_time(self) -> float:
        pass

    @classmethod
    @abstractmethod
    def validate(cls) -> None:
        pass