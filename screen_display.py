import pygame

from display import Display


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
