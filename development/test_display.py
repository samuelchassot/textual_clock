#!/usr/bin/env python3
"""
Fullscreen checkerboard test for the 720x720 display.
Board is 11 columns x 10 rows; press Q or Escape to quit.
"""

import sys
import pygame

COLS = 11
ROWS = 10
SCREEN_W = 720
SCREEN_H = 720


def draw_checkerboard(surface: pygame.Surface) -> None:
    for row in range(ROWS):
        y0 = round(row * SCREEN_H / ROWS)
        y1 = round((row + 1) * SCREEN_H / ROWS)
        for col in range(COLS):
            x0 = round(col * SCREEN_W / COLS)
            x1 = round((col + 1) * SCREEN_W / COLS)
            white = (col + row) % 2 == 0
            color = (255, 255, 255) if white else (0, 0, 0)
            pygame.draw.rect(surface, color, (x0, y0, x1 - x0, y1 - y0))


def main() -> None:
    pygame.init()

    flags = pygame.FULLSCREEN | pygame.NOFRAME
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), flags)
    pygame.display.set_caption("Display Test")
    pygame.mouse.set_visible(False)

    draw_checkerboard(screen)
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    pygame.quit()
                    sys.exit()

        pygame.time.wait(100)


if __name__ == "__main__":
    main()
