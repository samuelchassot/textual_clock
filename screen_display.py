import socket
import subprocess
from typing import Callable

import pygame

from display import Display


def _get_network_info() -> str:
    try:
        ssid = subprocess.check_output(["iwgetid", "-r"], text=True, timeout=1).strip() or "not connected"
    except Exception:
        ssid = "WiFi N/A"
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
        sock.close()
    except Exception:
        ip = "N/A"
    return f"{ssid}  •  {ip}"

DOUBLE_CLICK_MS = 400

BUTTON_W   = 440
BUTTON_H   = 90
BUTTON_GAP = 24
MARGIN_AROUND_CELLS_IN_PIXELS = 3


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


class _MenuColorPicker:
    def __init__(
        self,
        label: str,
        current_value: Callable[[], tuple[int, int, int]],
        on_select: Callable[[tuple[int, int, int]], None],
    ) -> None:
        self.label = label
        self.current_value = current_value
        self.on_select = on_select

    def run(self, display: "DisplayScreen") -> tuple[int, int, int] | None:
        import colorsys

        r, g, b = (c / 255.0 for c in self.current_value())
        h, s, v = colorsys.rgb_to_hsv(r, g, b)

        network_info = _get_network_info()
        saved = display.surface.copy()

        PAD   = 60
        SV_X  = PAD
        SV_Y  = 10
        SV_W  = display.screen_width - 2 * PAD
        SV_H  = 360
        HUE_X = PAD
        HUE_Y = SV_Y + SV_H + 12
        HUE_H = 44
        PRV_X = PAD
        PRV_Y = HUE_Y + HUE_H + 12
        PRV_H = 44
        BTN_Y = PRV_Y + PRV_H + 16
        BTN_H = 82
        BTN_W = (SV_W - 16) // 2

        def _sv_surface(hue: float) -> pygame.Surface:
            surf = pygame.Surface((SV_W, SV_H))
            hc = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            hr, hg, hb = int(hc[0] * 255), int(hc[1] * 255), int(hc[2] * 255)
            for x in range(SV_W):
                t = x / max(SV_W - 1, 1)
                pygame.draw.line(
                    surf,
                    (int(255 + (hr - 255) * t), int(255 + (hg - 255) * t), int(255 + (hb - 255) * t)),
                    (x, 0), (x, SV_H - 1),
                )
            overlay = pygame.Surface((SV_W, SV_H), pygame.SRCALPHA)
            for y in range(SV_H):
                alpha = int(255 * y / max(SV_H - 1, 1))
                pygame.draw.line(overlay, (0, 0, 0, alpha), (0, y), (SV_W - 1, y))
            surf.blit(overlay, (0, 0))
            return surf

        def _hue_surface() -> pygame.Surface:
            surf = pygame.Surface((SV_W, HUE_H))
            for x in range(SV_W):
                rc, gc, bc = colorsys.hsv_to_rgb(x / max(SV_W - 1, 1), 1.0, 1.0)
                pygame.draw.line(surf, (int(rc * 255), int(gc * 255), int(bc * 255)), (x, 0), (x, HUE_H - 1))
            return surf

        def _current_rgb() -> tuple[int, int, int]:
            rc, gc, bc = colorsys.hsv_to_rgb(h, s, v)
            return (int(rc * 255), int(gc * 255), int(bc * 255))

        def _redraw(sv_surf: pygame.Surface, hue_surf: pygame.Surface):
            overlay = pygame.Surface((display.screen_width, display.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 210))
            display.surface.blit(saved, (0, 0))
            display.surface.blit(overlay, (0, 0))

            # SV square
            display.surface.blit(sv_surf, (SV_X, SV_Y))
            pygame.draw.rect(display.surface, (80, 80, 80), (SV_X, SV_Y, SV_W, SV_H), 1)
            cx = max(SV_X, min(SV_X + SV_W - 1, int(SV_X + s * SV_W)))
            cy = max(SV_Y, min(SV_Y + SV_H - 1, int(SV_Y + (1 - v) * SV_H)))
            pygame.draw.circle(display.surface, (0, 0, 0), (cx, cy), 11, 2)
            pygame.draw.circle(display.surface, (255, 255, 255), (cx, cy), 9, 2)

            # Hue strip
            display.surface.blit(hue_surf, (HUE_X, HUE_Y))
            pygame.draw.rect(display.surface, (80, 80, 80), (HUE_X, HUE_Y, SV_W, HUE_H), 1)
            hx = max(HUE_X, min(HUE_X + SV_W - 1, int(HUE_X + h * SV_W)))
            pygame.draw.rect(display.surface, (0, 0, 0), (hx - 3, HUE_Y - 5, 6, HUE_H + 10))
            pygame.draw.rect(display.surface, (255, 255, 255), (hx - 2, HUE_Y - 4, 4, HUE_H + 8))

            # Color preview
            pygame.draw.rect(display.surface, _current_rgb(), (PRV_X, PRV_Y, SV_W, PRV_H))
            pygame.draw.rect(display.surface, (80, 80, 80), (PRV_X, PRV_Y, SV_W, PRV_H), 1)

            # Buttons: Cancel (left) | Validate (right)
            cancel_rect   = pygame.Rect(SV_X, BTN_Y, BTN_W, BTN_H)
            validate_rect = pygame.Rect(SV_X + BTN_W + 16, BTN_Y, BTN_W, BTN_H)
            accent     = display._accent_color()
            accent_dim = display._accent_color_dim()
            for rect, lbl in ((cancel_rect, "Cancel"), (validate_rect, "Validate")):
                pygame.draw.rect(display.surface, accent_dim, rect, border_radius=14)
                pygame.draw.rect(display.surface, accent, rect, 2, border_radius=14)
                text = display._menu_font.render(lbl, True, (255, 255, 255))
                display.surface.blit(text, text.get_rect(center=rect.center))

            info_text = display._info_font.render(network_info, True, (140, 140, 140))
            info_rect = info_text.get_rect(centerx=display.screen_width // 2, bottom=display.screen_height - 10)
            display.surface.blit(info_text, info_rect)

            pygame.display.flip()
            return cancel_rect, validate_rect

        sv_surf  = _sv_surface(h)
        hue_surf = _hue_surface()
        last_h   = h
        cancel_rect, validate_rect = _redraw(sv_surf, hue_surf)

        dragging_sv  = False
        dragging_hue = False

        while True:
            needs_redraw = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    display._quit_requested = True
                    display.surface.blit(saved, (0, 0))
                    pygame.display.flip()
                    return None

                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    display.surface.blit(saved, (0, 0))
                    pygame.display.flip()
                    return None

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = event.pos
                    if validate_rect.collidepoint(pos):
                        display.surface.blit(saved, (0, 0))
                        pygame.display.flip()
                        return _current_rgb()
                    if cancel_rect.collidepoint(pos):
                        display.surface.blit(saved, (0, 0))
                        pygame.display.flip()
                        return None
                    if SV_X <= pos[0] < SV_X + SV_W and SV_Y <= pos[1] < SV_Y + SV_H:
                        dragging_sv = True
                        s = max(0.0, min(1.0, (pos[0] - SV_X) / SV_W))
                        v = max(0.0, min(1.0, 1.0 - (pos[1] - SV_Y) / SV_H))
                        needs_redraw = True
                    elif HUE_X <= pos[0] < HUE_X + SV_W and HUE_Y <= pos[1] < HUE_Y + HUE_H:
                        dragging_hue = True
                        h = max(0.0, min(1.0, (pos[0] - HUE_X) / SV_W))
                        needs_redraw = True
                    else:
                        display.surface.blit(saved, (0, 0))
                        pygame.display.flip()
                        return None

                elif event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed()[0]:
                    pos = event.pos
                    if dragging_sv:
                        s = max(0.0, min(1.0, (pos[0] - SV_X) / SV_W))
                        v = max(0.0, min(1.0, 1.0 - (pos[1] - SV_Y) / SV_H))
                        needs_redraw = True
                    elif dragging_hue:
                        h = max(0.0, min(1.0, (pos[0] - HUE_X) / SV_W))
                        needs_redraw = True

                elif event.type == pygame.MOUSEBUTTONUP:
                    dragging_sv = False
                    dragging_hue = False

            if needs_redraw:
                if h != last_h:
                    sv_surf = _sv_surface(h)
                    last_h = h
                cancel_rect, validate_rect = _redraw(sv_surf, hue_surf)

            pygame.time.wait(16)


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
        self._pending_click_ms = 0
        self._quit_requested = False
        self._menu_items: list[_MenuButton | _MenuDropdown | _MenuColorPicker] = []
        self._single_click_callback: Callable[[], None] | None = None
        self._double_click_callback: Callable[[], None] | None = None
        self._get_accent_color_fn: Callable[[], tuple[int, int, int]] | None = None
        pygame.font.init()
        self._menu_font = pygame.font.SysFont(None, 56)
        self._info_font = pygame.font.SysFont(None, 28)

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
        y0 = round(i * self.screen_height / self.rows + MARGIN_AROUND_CELLS_IN_PIXELS)
        y1 = round((i + 1) * self.screen_height / self.rows - MARGIN_AROUND_CELLS_IN_PIXELS)
        x0 = round(j * self.screen_width / self.cols + MARGIN_AROUND_CELLS_IN_PIXELS)
        x1 = round((j + 1) * self.screen_width / self.cols - MARGIN_AROUND_CELLS_IN_PIXELS)
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

        now = pygame.time.get_ticks()
        if self._pending_click_ms > 0 and now - self._pending_click_ms >= DOUBLE_CLICK_MS:
            self._pending_click_ms = 0
            if self._single_click_callback:
                self._single_click_callback()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_q, pygame.K_ESCAPE):
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                now = pygame.time.get_ticks()
                if self._pending_click_ms > 0 and now - self._pending_click_ms < DOUBLE_CLICK_MS:
                    self._pending_click_ms = 0
                    if self._double_click_callback:
                        self._double_click_callback()
                else:
                    self._pending_click_ms = now
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

    def add_menu_color_picker(
        self,
        label: str,
        current_value: Callable[[], tuple[int, int, int]],
        on_select: Callable[[tuple[int, int, int]], None],
    ) -> None:
        self._menu_items.append(_MenuColorPicker(label, current_value, on_select))

    def set_single_click_callback(self, callback: Callable[[], None]) -> None:
        self._single_click_callback = callback

    def set_double_click_callback(self, callback: Callable[[], None]) -> None:
        self._double_click_callback = callback

    def set_get_accent_color_fn(self, fn: Callable[[], tuple[int, int, int]]) -> None:
        self._get_accent_color_fn = fn

    def _accent_color(self) -> tuple[int, int, int]:
        if self._get_accent_color_fn:
            return self._get_accent_color_fn()
        return (200, 200, 200)

    def _accent_color_dim(self) -> tuple[int, int, int]:
        r, g, b = self._accent_color()
        return (r // 6, g // 6, b // 6)

    def open_menu(self) -> None:
        entries = []
        for item in self._menu_items:
            if isinstance(item, _MenuDropdown):
                current = item.current_value()
                label = f"{item.label}: {current} >" if current else f"{item.label} >"
            elif isinstance(item, _MenuColorPicker):
                label = f"{item.label} >"
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
        elif isinstance(chosen, _MenuColorPicker):
            result = chosen.run(self)
            if result is not None:
                chosen.on_select(result)

    def _draw_network_info(self) -> None:
        info = _get_network_info()
        text = self._info_font.render(info, True, (140, 140, 140))
        rect = text.get_rect(centerx=self.screen_width // 2, bottom=self.screen_height - 10)
        self.surface.blit(text, rect)

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
            pygame.draw.rect(self.surface, self._accent_color_dim(), rect, border_radius=14)
            pygame.draw.rect(self.surface, self._accent_color(), rect, 2, border_radius=14)
            text = self._menu_font.render(label, True, (255, 255, 255))
            self.surface.blit(text, text.get_rect(center=rect.center))
            buttons.append((rect, action))

        self._draw_network_info()
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
