from typing import Callable

import pygame

from display import Display

DOUBLE_CLICK_MS = 400

BUTTON_W   = 440
BUTTON_H   = 90
BUTTON_GAP = 24


class _MenuButton:
    def __init__(self, label: str, on_select: Callable[[], None]) -> None:
        self.label = label
        self.on_select = on_select


class _MenuDropdown:
    def __init__(
        self,
        label: str,
        options: Callable[[], list[str]],
        current_value: Callable[[], str],
        on_select: Callable[[str], None],
    ) -> None:
        self.label = label
        self.options = options
        self.current_value = current_value
        self.on_select = on_select


class DisplayScreen(Display):

    def __init__(self, cols: int, rows: int, screen_width: int, screen_height: int, surface: pygame.Surface) -> None:
        self.surface = surface
        self.cols = cols
        self.rows = rows
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.color_off = (0, 0, 0)
        self.auto_commit = True
        self.debug_characters = [
            ["I", "L", "N", "E", "S", "T", "O", "D", "E", "U", "X"],
            ["Q", "U", "A", "T", "R", "E", "T", "R", "O", "I", "S"],
            ["N", "E", "U", "F", "U", "N", "E", "S", "E", "P", "T"],
            ["H", "U", "I", "T", "S", "I", "X", "C", "I", "N", "Q"],
            ["M", "I", "D", "I", "X", "M", "I", "N", "U", "I", "T"],
            ["O", "N", "Z", "E", "R", "H", "E", "U", "R", "E", "S"],
            ["M", "O", "I", "N", "S", "O", "L", "E", "D", "I", "X"],
            ["E", "T", "R", "Q", "U", "A", "R", "T", "P", "R", "D"],
            ["V", "I", "N", "G", "T", "-", "C", "I", "N", "Q", "U"],
            ["E", "T", "S", "D", "E", "M", "I", "E", "P", "A", "M"],
        ]
        self._last_click_ms = 0
        self._quit_requested = False
        self._menu_items: list[_MenuButton | _MenuDropdown] = []
        self._double_click_callback: Callable[[], None] | None = None
        pygame.font.init()
        self._menu_font = pygame.font.SysFont(None, 56)

    # Letters on the clock:
    #
    #    0 1 2 3 4 5 6 7 8 9 10
    # 0  I L N E S T O D E U X
    # 1  Q U A T R E T R O I S
    # 2  N E U F U N E S E P T
    # 3  H U I T S I X C I N Q
    # 4  M I D I X M I N U I T
    # 5  O N Z E R H E U R E S
    # 6  M O I N S O L E D I X
    # 7  E T R Q U A R T P R D
    # 8  V I N G T - C I N Q U
    # 9  E T S D E M I E P A M

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def _draw_cell(self, i: int, j: int, color: tuple[int, int, int]) -> None:
        y0 = round(i * self.screen_height / self.rows)
        y1 = round((i + 1) * self.screen_height / self.rows)
        x0 = round(j * self.screen_width / self.cols)
        x1 = round((j + 1) * self.screen_width / self.cols)
        pygame.draw.rect(self.surface, color, (x0, y0, x1 - x0, y1 - y0))

    def commit(self) -> None:
        pygame.display.flip()

    def turn_off_all(self) -> None:
        self.surface.fill(self.color_off)
        if self.auto_commit:
            self.commit()

    def turn_on_all(self, color: tuple[int, int, int]) -> None:
        self.surface.fill(color)
        if self.auto_commit:
            self.commit()

    def turn_off(self, indices: list[tuple[int, int]]) -> None:
        for i, j in indices:
            self._draw_cell(i, j, self.color_off)
        if self.auto_commit:
            self.commit()

    def turn_on(self, indices: list[tuple[int, int]], color: tuple[int, int, int]) -> str:
        """Turn on cells at the given (row, col) positions with the given color.
        Corner LEDs are not supported on this display.
        """
        debug_str = ""
        for i, j in indices:
            self._draw_cell(i, j, color)
            if 0 <= i < len(self.debug_characters) and 0 <= j < len(self.debug_characters[i]):
                debug_str += self.debug_characters[i][j]
            else:
                debug_str += f"corner{j} (unsupported)" if i == -1 else f"({i},{j})"
        if self.auto_commit:
            self.commit()
        return debug_str

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------

    def poll_events(self) -> str | None:
        if self._quit_requested:
            return "quit"
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_q, pygame.K_ESCAPE):
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                now = pygame.time.get_ticks()
                if now - self._last_click_ms < DOUBLE_CLICK_MS:
                    if self._double_click_callback:
                        self._double_click_callback()
                else:
                    self._last_click_ms = now
        return None

    # ------------------------------------------------------------------
    # Menu infrastructure
    # ------------------------------------------------------------------

    def add_menu_button(self, label: str, on_select: Callable[[], None]) -> None:
        self._menu_items.append(_MenuButton(label, on_select))

    def add_menu_dropdown(
        self,
        label: str,
        options: Callable[[], list[str]],
        current_value: Callable[[], str],
        on_select: Callable[[str], None],
    ) -> None:
        self._menu_items.append(_MenuDropdown(label, options, current_value, on_select))

    def set_double_click_callback(self, callback: Callable[[], None]) -> None:
        self._double_click_callback = callback

    def open_menu(self) -> None:
        entries = []
        for item in self._menu_items:
            if isinstance(item, _MenuDropdown):
                current = item.current_value()
                label = f"{item.label}: {current} >" if current else f"{item.label} >"
            else:
                label = item.label
            entries.append((label, item))

        chosen = self._run_button_menu(entries)
        if chosen is None:
            return

        if isinstance(chosen, _MenuButton):
            chosen.on_select()
        elif isinstance(chosen, _MenuDropdown):
            current = chosen.current_value()
            sub_entries = [
                (f"> {opt.capitalize()}" if opt == current else f"  {opt.capitalize()}", opt)
                for opt in chosen.options()
            ]
            selected = self._run_button_menu(sub_entries)
            if selected is not None:
                chosen.on_select(selected)

    def _run_button_menu(self, items: list[tuple[str, object]]) -> object | None:
        """Overlay a button menu and block until the user picks an entry or dismisses.
        Returns the action object of the chosen item, or None if dismissed.
        """
        saved = self.surface.copy()

        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        self.surface.blit(overlay, (0, 0))

        total_h = len(items) * BUTTON_H + (len(items) - 1) * BUTTON_GAP
        start_y = (self.screen_height - total_h) // 2
        buttons = []
        for i, (label, action) in enumerate(items):
            x = (self.screen_width - BUTTON_W) // 2
            y = start_y + i * (BUTTON_H + BUTTON_GAP)
            rect = pygame.Rect(x, y, BUTTON_W, BUTTON_H)
            pygame.draw.rect(self.surface, (50, 50, 50), rect, border_radius=14)
            pygame.draw.rect(self.surface, (200, 200, 200), rect, 2, border_radius=14)
            text = self._menu_font.render(label, True, (255, 255, 255))
            self.surface.blit(text, text.get_rect(center=rect.center))
            buttons.append((rect, action))

        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._quit_requested = True
                    self.surface.blit(saved, (0, 0))
                    pygame.display.flip()
                    return None
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.surface.blit(saved, (0, 0))
                    pygame.display.flip()
                    return None
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for rect, action in buttons:
                        if rect.collidepoint(event.pos):
                            self.surface.blit(saved, (0, 0))
                            pygame.display.flip()
                            return action
                    self.surface.blit(saved, (0, 0))
                    pygame.display.flip()
                    return None
            pygame.time.wait(50)
