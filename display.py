from abc import ABC, abstractmethod
from typing import Callable


class Display(ABC):
    """Abstract display interface.

    In auto-commit mode (the default), every drawing method stages and
    immediately commits its changes. When auto-commit is off, drawing methods
    only stage changes — commit() must be called explicitly to push them to
    the hardware or screen. Use set_auto_commit(False) before a multi-step
    animation and set_auto_commit(True) when done.

    Menu infrastructure: a Display only provides the mechanics of a menu
    (rendering buttons/dropdowns, running a modal loop, detecting a
    double-click). It has no notion of what any menu entry means — callers
    register entries and callbacks, then decide when to open the menu.
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

    @abstractmethod
    def poll_events(self) -> str | None:
        """Process pending input events. Returns 'quit' if the display was
        asked to close (window closed, quit key pressed, ...), otherwise
        None.
        """
        ...

    @abstractmethod
    def add_menu_button(self, label: str, on_select: Callable[[], None]) -> None:
        """Register a simple menu entry. on_select is called with no
        arguments when the user picks it."""
        ...

    @abstractmethod
    def add_menu_dropdown(
        self,
        label: str,
        options: Callable[[], list[str]],
        current_value: Callable[[], str],
        on_select: Callable[[str], None],
    ) -> None:
        """Register a menu entry that drills into a submenu of choices.
        options() and current_value() are called each time the menu is
        opened; on_select(value) is called with the chosen option.
        """
        ...

    @abstractmethod
    def open_menu(self) -> None:
        """Show the menu built from the registered entries and block until
        it is dismissed or an entry is chosen, invoking the relevant
        callback."""
        ...

    @abstractmethod
    def set_double_click_callback(self, callback: Callable[[], None]) -> None:
        """Register the callback invoked when the display detects a
        double-click."""
        ...

    @abstractmethod
    def set_single_click_callback(self, callback: Callable[[], None]) -> None:
        """Register the callback invoked when the display detects a
        single tap (fired after DOUBLE_CLICK_MS with no follow-up tap)."""
        ...

    @abstractmethod
    def add_menu_color_picker(
        self,
        label: str,
        current_value: Callable[[], tuple[int, int, int]],
        on_select: Callable[[tuple[int, int, int]], None],
    ) -> None:
        """Register a color-picker menu entry. Opens an HSV picker submenu;
        on_select(rgb) is called with the chosen (r, g, b) tuple."""
        ...
