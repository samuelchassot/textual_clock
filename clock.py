import board
import neopixel
import random
import time


class Clock:
    def __init__(self) -> None:

        self.CURRENT_COLOR_FILE_PATH = "res/color.current"
        self.SEPARATOR = ";"
        self.DEFAULT_COLOR = (255, 255, 255)

        self.n_leds = 3
        self.pixels = neopixel.NeoPixel(board.D18, self.n_leds)
        self.off = (0, 0, 0)

        self.last_h_five_min_color: tuple[int, int, tuple[int, int, int]] = (
            0,
            0,
            (0, 0, 0),
        )

    def read_current_color(self) -> tuple[int, int, int]:
        try:
            with open(self.CURRENT_COLOR_FILE_PATH, "r") as f:
                l = f.readline()
                rgb = l.split(self.SEPARATOR)
                return (int(rgb[0]), int(rgb[1]), int(rgb[2]))
        except Exception as e:
            print("ERROR: cannot read the current color!\n", e)
            return self.DEFAULT_COLOR

    def get_current_hour(self) -> int:
        """
        returns the current hour as an int, between 0 and 23, 0 is midnight.
        """
        return time.localtime().tm_hour

    def get_current_nearest_quarter(self) -> int:
        """
        returns the nearest quarter, between 0 and 3.
        0 is the hour sharp, so betwee XX:52:30 and XX+1:07:29
        """
        minutes = time.localtime().tm_min + time.localtime().tm_sec / 60.0
        return int((minutes + 7.5) // 15) % 4

    def get_current_nearest_five_minutes(self) -> int:
        """
        returns the nearest 5 minutes mark, between 0 and 11.
        0 is the hour sharp, so between XX:57:30 and XX+1:02:29"""
        minutes = time.localtime().tm_min + time.localtime().tm_sec / 60.0
        return int((minutes + 2.5) // 5) % 12

    def run(self):
        print("Start of the clock")
        while True:
            h = self.get_current_hour()
            five_minutes = self.get_current_nearest_five_minutes()
            color = self.read_current_color()

            old_tuple = self.last_h_five_min_color
            self.last_h_five_min_color = (h, five_minutes, color)
            if self.last_h_five_min_color != old_tuple:
                print(color)
                self.show_il_est()
                time.sleep(0.2)
                self.show_hour(h)
                time.sleep(0.3)
                self.show_five_minutes(five_minutes)
            time.sleep(10)

    def show_hour(self, h: int):
        if h == 0:
            self.show_minuit()
        elif h == 1 or h == 13:
            self.show_une()
            time.sleep(0.4)
            self.show_heure()
        elif h == 2 or h == 14:
            self.show_deux()
            time.sleep(0.4)
            self.show_heures()
        elif h == 3 or h == 15:
            self.show_trois()
            time.sleep(0.4)
            self.show_heures()
        elif h == 4 or h == 16:
            self.show_quatre()
            time.sleep(0.4)
            self.show_heures()
        elif h == 5 or h == 17:
            self.show_cinq()
            time.sleep(0.4)
            self.show_heures()
        elif h == 6 or h == 18:
            self.show_six()
            time.sleep(0.4)
            self.show_heures()
        elif h == 7 or h == 19:
            self.show_sept()
            time.sleep(0.4)
            self.show_heures()
        elif h == 8 or h == 20:
            self.show_huit()
            time.sleep(0.4)
            self.show_heures()
        elif h == 9 or h == 21:
            self.show_neuf()
            time.sleep(0.4)
            self.show_heures()
        elif h == 10 or h == 22:
            self.show_dix()
            time.sleep(0.4)
            self.show_heures()
        elif h == 11 or h == 23:
            self.show_onze()
            time.sleep(0.4)
            self.show_heures()
        elif h == 12:
            self.show_midi()
            time.sleep(0.4)
            self.show_heures()

    def show_five_minutes(self, c: int):
        if c == 0:
            # Nothing
            pass
        elif c == 1:
            self.show_cinq_min()
        elif c == 2:
            self.show_dix_min()
        elif c == 3:
            self.show_et_above()
            time.sleep(0.4)
            self.show_quart()
        elif c == 4:
            self.show_vingt_min()
        elif c == 5:
            self.show_vingt_min()
            time.sleep(0.5)
            self.show_dash_min()
            time.sleep(0.4)
            self.show_cinq_min()
        elif c == 6:
            if random.randint(0, 1000) % 2 == 0:
                self.show_et_above()
            else:
                self.show_et_below()
            time.sleep(0.4)
            self.show_demie()
        elif c == 7:
            self.show_moins()
            time.sleep(0.4)
            self.show_vingt_min()
            time.sleep(0.5)
            self.show_dash_min()
            time.sleep(0.4)
            self.show_cinq_min()

        elif c == 8:
            self.show_moins()
            time.sleep(0.2)
            self.show_vingt_min()
        elif c == 9:
            self.show_moins()
            time.sleep(0.5)
            self.show_quart()
        elif c == 10:
            self.show_moins()
            time.sleep(0.4)
            self.show_dix_min()
        elif c == 11:
            self.show_moins()
            time.sleep(0.4)
            self.show_cinq_min()

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

    def turn_off(self):
        self.pixels.fill(self.off)

    def show_il_est(self):
        print("il_est")

    # Hours functions
    def show_une(self):
        print("une")

    def show_deux(self):
        print("deux")

    def show_trois(self):
        print("trois")

    def show_quatre(self):
        print("quatre")

    def show_cinq(self):
        print("cinq")

    def show_six(self):
        print("six")

    def show_sept(self):
        print("sept")

    def show_huit(self):
        print("huit")

    def show_neuf(self):
        print("neuf")

    def show_dix(self):
        print("dix")

    def show_onze(self):
        print("onze")

    def show_midi(self):
        print("midi")

    def show_minuit(self):
        print("minuit")

    def show_heure(self):
        print("heure")

    def show_heures(self):
        print("heures")

    # Minutes functions
    def show_moins(self):
        print("moins")

    def show_et_above(self):
        print("et_above")

    def show_et_below(self):
        print("et_below")

    def show_cinq_min(self):
        print("cinq_min")

    def show_dix_min(self):
        print("dix_min")

    def show_quart(self):
        print("quart")

    def show_vingt_min(self):
        print("vingt_min")

    def show_dash_min(self):
        print("dash_min")

    def show_demie(self):
        print("demie")
