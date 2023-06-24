import board
import neopixel
import time


n_leds_per_line = 11
n_leds = n_leds_per_line * 10
pixels = neopixel.NeoPixel(board.D18, n_leds)

while True:
    pixels.fill((0, 0, 0))
    time.sleep(2)
    for i in range(n_leds):
        pixels[i] = (255, 0, 0)
        time.sleep(0.8)
