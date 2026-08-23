from abc import ABC, abstractmethod


class Display(ABC):
    """Abstract display interface.

    In auto-commit mode (the default), every drawing method stages and
    immediately commits its changes. When auto-commit is off, drawing methods
    only stage changes — commit() must be called explicitly to push them to
    the hardware or screen. Use set_auto_commit(False) before a multi-step
    animation and set_auto_commit(True) when done.
    """

    rows: int
    cols: int
    color_off: tuple[int, int, int]
    auto_commit: bool

    def set_auto_commit(self, enabled: bool) -> None:
        """Switch between auto-commit and manual-commit mode."""
        self.auto_commit = enabled

    @abstractmethod
    def commit(self) -> None:
        """Push all staged changes to the display."""
        ...

    @abstractmethod
    def turn_off_all(self) -> None: ...

    @abstractmethod
    def turn_on_all(self, color: tuple[int, int, int]) -> None: ...

    @abstractmethod
    def turn_off(self, indices: list[tuple[int, int]]) -> None: ...

    @abstractmethod
    def turn_on(self, indices: list[tuple[int, int]], color: tuple[int, int, int]) -> str: ...
