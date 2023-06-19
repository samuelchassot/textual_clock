import board
import neopixel
import time


n_leds_per_line = 11
n_leds = n_leds_per_line * 10
pixels = neopixel.NeoPixel(board.D18, n_leds)

while True:
    for i in range(n_leds):
        pixels.fill((0, 0, 0))
        pixels[i] = (255, 255, 255)
        time.sleep(0.8)
