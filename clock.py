import board
import neopixel
import random
import time

CURRENT_COLOR_FILE_PATH = "res/color.current"
SEPARATOR = ";"
DEFAULT_COLOR = (255, 255, 255)

n_leds = 3
pixels = neopixel.NeoPixel(board.D18, n_leds)
off = (0, 0, 0)


def read_current_color() -> tuple[int, int, int]:
    try:
        with open(CURRENT_COLOR_FILE_PATH, "r") as f:
            l = f.readline()
            print("Read color line: " + l)
            rgb = l.split(SEPARATOR)
            return (int(rgb[0]), int(rgb[1]), int(rgb[2]))
    except Exception as e:
        print("ERROR: cannot read the current color!\n", e)
        return DEFAULT_COLOR


def get_current_hour() -> int:
    """
    returns the current hour as an int, between 0 and 23, 0 is midnight.
    """
    return time.localtime().tm_hour


def get_current_nearest_quarter():
    """
    returns the nearest quarter, between 0 and 3.
    0 is the hour sharp, so betwee XX:52:30 and XX+1:07:29
    """
    minutes = time.localtime().tm_min + time.localtime().tm_sec / 60.0
    return ((minutes + 7.5) // 15) % 4


def get_current_nearest_five_minutes():
    """
    returns the nearest 5 minutes mark, between 0 and 11.
    0 is the hour sharp, so between XX:57:30 and XX+1:02:29"""
    minutes = time.localtime().tm_min + time.localtime().tm_sec / 60.0
    return ((minutes + 2.5) // 5) % 12


def run():
    print("Start of the clock")

    while True:
        h = get_current_hour()
        cinq_min = get_current_nearest_five_minutes()
        t_str = ""
        t_str += "il est "
        t_str += str(h)
        t_str += " "
        t_str += str(cinq_min)
        color = read_current_color()
        print(t_str, " in color = ", color)


def show_hour(h: int):
    if h == 0:
        show_minuit()
    elif h == 1 or h == 13:
        show_une()
    elif h == 2 or h == 14:
        show_deux()
    elif h == 3 or h == 15:
        show_trois()
    elif h == 4 or h == 16:
        show_quatre()
    elif h == 5 or h == 17:
        show_cinq()
    elif h == 6 or h == 18:
        show_six()
    elif h == 7 or h == 19:
        show_sept()
    elif h == 8 or h == 20:
        show_huit()
    elif h == 9 or h == 21:
        show_neuf()
    elif h == 10 or h == 22:
        show_dix()
    elif h == 11 or h == 23:
        show_onze()
    elif h == 12:
        show_midi()


# LEDS helper methods


def turn_off():
    pixels.fill(off)


def show_il_est():
    None


def show_une():
    None


def show_deux():
    None


def show_trois():
    None


def show_quatre():
    None


def show_cinq():
    None


def show_six():
    None


def show_sept():
    None


def show_huit():
    None


def show_neuf():
    None


def show_dix():
    None


def show_onze():
    None


def show_midi():
    None


def show_minuit():
    None


def show_heure():
    None


def show_heures():
    None


def show_moins():
    None


def show_et_above():
    None


def show_et_below():
    None


def show_cinq_min():
    None


def show_dix_min():
    None


def show_quart():
    None


def show_vingt_min():
    None


def show_dash_min():
    None


def show_demie():
    None
