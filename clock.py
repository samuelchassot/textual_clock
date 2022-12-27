import board
import neopixel
import random
import time

n_leds = 3
pixels = neopixel.NeoPixel(board.D18, n_leds)

color_warm_white = (255, 140, 100)
color_red = (255, 0, 0)
color_blue = (0, 0, 255)
off = (0, 0, 0)


def slow_on(led_n, target_tuple):
    (targetR, targetG, targetB) = target_tuple
    for i in range(129):
        r = min(2 * i, targetR)
        g = min(2 * i, targetG)
        b = min(2 * i, targetB)
        pixels[led_n] = (r, g, b)
        time.sleep(0.005)


print("Start of the clock")

pixels.fill(off)

while True:

    slow_on(0, color_red)
    slow_on(1, color_red)
    slow_on(2, color_red)
    time.sleep(2)
    pixels.fill(off)
    time.sleep(0.5)
