from abc import ABC, abstractmethod


class Display(ABC):

    color_off: tuple[int, int, int]
    color_on: tuple[int, int, int]

    @abstractmethod
    def turn_off_all(self) -> None: ...

    @abstractmethod
    def turn_on_all(self, color: tuple[int, int, int]) -> None: ...

    @abstractmethod
    def turn_off(self, indices: list[tuple[int, int]]) -> None: ...

    @abstractmethod
    def turn_on(self, indices: list[tuple[int, int]]) -> str: ...
