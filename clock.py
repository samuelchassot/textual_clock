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


def get_current_nearest_quarter() -> int:
    """
    returns the nearest quarter, between 0 and 3.
    0 is the hour sharp, so betwee XX:52:30 and XX+1:07:29
    """
    minutes = time.localtime().tm_min + time.localtime().tm_sec / 60.0
    return int((minutes + 7.5) // 15) % 4


def get_current_nearest_five_minutes() -> int:
    """
    returns the nearest 5 minutes mark, between 0 and 11.
    0 is the hour sharp, so between XX:57:30 and XX+1:02:29"""
    minutes = time.localtime().tm_min + time.localtime().tm_sec / 60.0
    return int((minutes + 2.5) // 5) % 12


def run():
    print("Start of the clock")
    last_h_five_min_color: tuple[int, int, tuple[int, int, int]] = (0, 0, (0, 0, 0))

    while True:
        h = get_current_hour()
        five_minutes = get_current_nearest_five_minutes()
        color = read_current_color()

        # test code ---------------------------------- BEGIN ->
        t_str = ""
        t_str += "il est "
        t_str += str(h)
        t_str += " "
        t_str += str(five_minutes)
        print(t_str, " in color = ", color)
        # test code ---------------------------------- END

        new_tuple = (h, five_minutes, color)
        if last_h_five_min_color != new_tuple:
            show_hour(h)
            time.sleep(0.3)
            show_five_minutes(five_minutes)
            last_h_five_min_color = new_tuple
        time.sleep(10)


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


def show_five_minutes(c: int):
    if c == 0:
        # Nothing
        None
    elif c == 1:
        show_cinq_min()
    elif c == 2:
        show_dix_min()
    elif c == 3:
        show_et_above()
        time.sleep(0.4)
        show_quart()
    elif c == 4:
        show_vingt_min()
    elif c == 5:
        show_vingt_min()
        time.sleep(0.5)
        show_dash_min()
        time.sleep(0.4)
        show_cinq_min()
    elif c == 6:
        if random.randint(0, 1000) % 2 == 0:
            show_et_above()
        else:
            show_et_below()
        time.sleep(0.4)
        show_demie()
    elif c == 7:
        show_moins()
        time.sleep(0.4)
        show_vingt_min()
        time.sleep(0.5)
        show_dash_min()
        time.sleep(0.4)
        show_cinq_min()

    elif c == 8:
        show_moins()
        time.sleep(0.2)
        show_vingt_min()
    elif c == 9:
        show_moins()
        time.sleep(0.5)
        show_quart()
    elif c == 10:
        show_moins()
        time.sleep(0.4)
        show_dix_min()
    elif c == 11:
        show_moins()
        time.sleep(0.4)
        show_cinq_min()


# LEDS helper functions

# Letters on the clock:
#
# I L N E S T O D E U X
# Q U A T R E T R O I S
# N E U F U N E S E P T
# H U I T S I X C I N Q
# M I D I X M I N U I T
# O N Z E R H E U R E S
# M O I N S O L E D I X
# E T R Q U A R T P R D
# V I N G T - C I N Q U
# E T S D E M I E P A M


def turn_off():
    pixels.fill(off)


def show_il_est():
    None


# Hours functions
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


# Minutes functions
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


run()
