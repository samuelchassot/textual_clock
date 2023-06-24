import board
import neopixel
import time

CURRENT_COLOR_FILE_PATH = "res/color.current"
SEPARATOR = ";"
DEFAULT_COLOR = (255, 255, 255)


def main():
    n_leds_per_line = 11
    n_leds = n_leds_per_line * 10
    pixels = neopixel.NeoPixel(board.D18, n_leds)

    while True:
        pixels.fill((0, 0, 0))
        time.sleep(2)
        for i in range(n_leds):
            pixels[i] = read_current_color()
            time.sleep(0.8)


def read_current_color() -> tuple[int, int, int]:
    try:
        with open(CURRENT_COLOR_FILE_PATH, "r") as f:
            l = f.readline()
            rgb = l.split(SEPARATOR)
            return (int(rgb[0]), int(rgb[1]), int(rgb[2]))
    except Exception as e:
        print("ERROR: cannot read the current color!\n", e)
        return DEFAULT_COLOR
