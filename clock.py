import random
import time
import threading


class Clock:
    def __init__(self, n_leds_per_line, led_array) -> None:
        self.CURRENT_COLOR_FILE_PATH = "res/color.current"
        self.SEPARATOR = ";"
        self.DEFAULT_COLOR = (255, 255, 255)

        self.n_leds_per_line = n_leds_per_line
        self.pixels = led_array

        assert len(led_array) % n_leds_per_line == 0

        self.color_off = (0, 0, 0)
        self.color_on = self.DEFAULT_COLOR

        self.last_h_five_min_color: tuple[int, int, tuple[int, int, int]] = (
            0,
            0,
            (0, 0, 0),
        )

        # to debug, here is a list of the clock characters as the leds are ordered
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
        self.debug_characters: list[str] = [
            item for sub in self.debug_characters for item in sub
        ]

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
        th = threading.Thread(target=self.run_loop)
        th.start()

    def run_loop(self):
        print("Start of the clock")
        while True:
            h = self.get_current_hour()
            five_minutes = self.get_current_nearest_five_minutes()

            # Because we show "25 to 10" for 9:35 for example
            if five_minutes > 6:
                h += 1
            self.color_on = self.read_current_color()

            old_tuple = self.last_h_five_min_color
            self.last_h_five_min_color = (h, five_minutes, self.color_on)

            print("now: ", self.last_h_five_min_color, " old: ", old_tuple)
            if self.last_h_five_min_color != old_tuple:
                print(self.color_on)
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

    def turn_off(self):
        self.pixels.fill(self.color_off)

    def turn_on(self, indices: list[tuple[int, int]]):
        """Turn on the LEDs at the positions given by the tuples in the list. The tuple gives the line then the column."""

        debug_str = ""
        n_leds_per_line = 11
        for i, j in indices:
            index = i * n_leds_per_line + j
            self.pixels[index] = self.color_on
            debug_str += self.debug_characters[index]
        return debug_str

    def show_il_est(self):
        to_turn_on = []
        to_turn_on.append((0, 0))
        to_turn_on.append((0, 1))
        to_turn_on.append((0, 3))
        to_turn_on.append((0, 4))
        to_turn_on.append((0, 5))
        return self.turn_on(to_turn_on)

    # Hours functions
    def show_une(self):
        to_turn_on = []
        to_turn_on.append((2, 4))
        to_turn_on.append((2, 5))
        to_turn_on.append((2, 6))
        return self.turn_on(to_turn_on)

    def show_deux(self):
        to_turn_on = []
        to_turn_on.append((0, 7))
        to_turn_on.append((0, 8))
        to_turn_on.append((0, 9))
        to_turn_on.append((0, 10))
        return self.turn_on(to_turn_on)

    def show_trois(self):
        to_turn_on = []
        to_turn_on.append((1, 6))
        to_turn_on.append((1, 7))
        to_turn_on.append((1, 8))
        to_turn_on.append((1, 9))
        to_turn_on.append((1, 10))
        return self.turn_on(to_turn_on)

    def show_quatre(self):
        to_turn_on = []
        to_turn_on.append((1, 0))
        to_turn_on.append((1, 1))
        to_turn_on.append((1, 2))
        to_turn_on.append((1, 3))
        to_turn_on.append((1, 4))
        to_turn_on.append((1, 5))
        return self.turn_on(to_turn_on)

    def show_cinq(self):
        to_turn_on = []
        to_turn_on.append((3, 7))
        to_turn_on.append((3, 8))
        to_turn_on.append((3, 9))
        to_turn_on.append((3, 10))
        return self.turn_on(to_turn_on)

    def show_six(self):
        to_turn_on = []
        to_turn_on.append((3, 4))
        to_turn_on.append((3, 5))
        to_turn_on.append((3, 6))
        return self.turn_on(to_turn_on)

    def show_sept(self):
        to_turn_on = []
        to_turn_on.append((2, 7))
        to_turn_on.append((2, 8))
        to_turn_on.append((2, 9))
        to_turn_on.append((2, 10))
        return self.turn_on(to_turn_on)

    def show_huit(self):
        to_turn_on = []
        to_turn_on.append((3, 0))
        to_turn_on.append((3, 1))
        to_turn_on.append((3, 2))
        to_turn_on.append((3, 3))
        return self.turn_on(to_turn_on)

    def show_neuf(self):
        to_turn_on = []
        to_turn_on.append((2, 0))
        to_turn_on.append((2, 1))
        to_turn_on.append((2, 2))
        to_turn_on.append((2, 3))
        return self.turn_on(to_turn_on)

    def show_dix(self):
        to_turn_on = []
        to_turn_on.append((4, 2))
        to_turn_on.append((4, 3))
        to_turn_on.append((4, 4))
        return self.turn_on(to_turn_on)

    def show_onze(self):
        to_turn_on = []
        to_turn_on.append((5, 0))
        to_turn_on.append((5, 1))
        to_turn_on.append((5, 2))
        to_turn_on.append((5, 3))
        return self.turn_on(to_turn_on)

    def show_midi(self):
        to_turn_on = []
        to_turn_on.append((4, 0))
        to_turn_on.append((4, 1))
        to_turn_on.append((4, 2))
        to_turn_on.append((4, 3))
        return self.turn_on(to_turn_on)

    def show_minuit(self):
        to_turn_on = []
        to_turn_on.append((4, 5))
        to_turn_on.append((4, 6))
        to_turn_on.append((4, 7))
        to_turn_on.append((4, 8))
        to_turn_on.append((4, 9))
        to_turn_on.append((4, 10))
        return self.turn_on(to_turn_on)

    def show_heure(self):
        to_turn_on = []
        to_turn_on.append((5, 5))
        to_turn_on.append((5, 6))
        to_turn_on.append((5, 7))
        to_turn_on.append((5, 8))
        to_turn_on.append((5, 9))
        return self.turn_on(to_turn_on)

    def show_heures(self):
        to_turn_on = []
        to_turn_on.append((5, 5))
        to_turn_on.append((5, 6))
        to_turn_on.append((5, 7))
        to_turn_on.append((5, 8))
        to_turn_on.append((5, 9))
        to_turn_on.append((5, 10))
        return self.turn_on(to_turn_on)

    # Minutes functions
    def show_moins(self):
        to_turn_on = []
        to_turn_on.append((6, 0))
        to_turn_on.append((6, 1))
        to_turn_on.append((6, 2))
        to_turn_on.append((6, 3))
        to_turn_on.append((6, 4))
        return self.turn_on(to_turn_on)

    def show_et_above(self):
        to_turn_on = []
        to_turn_on.append((7, 0))
        to_turn_on.append((7, 1))
        return self.turn_on(to_turn_on)

    def show_et_below(self):
        to_turn_on = []
        to_turn_on.append((9, 0))
        to_turn_on.append((9, 1))
        return self.turn_on(to_turn_on)

    def show_cinq_min(self):
        to_turn_on = []
        to_turn_on.append((8, 6))
        to_turn_on.append((8, 7))
        to_turn_on.append((8, 8))
        to_turn_on.append((8, 9))
        return self.turn_on(to_turn_on)

    def show_dix_min(self):
        to_turn_on = []
        to_turn_on.append((6, 8))
        to_turn_on.append((6, 9))
        to_turn_on.append((6, 10))
        return self.turn_on(to_turn_on)

    def show_quart(self):
        to_turn_on = []
        to_turn_on.append((7, 3))
        to_turn_on.append((7, 4))
        to_turn_on.append((7, 5))
        to_turn_on.append((7, 6))
        to_turn_on.append((7, 7))
        return self.turn_on(to_turn_on)

    def show_vingt_min(self):
        to_turn_on = []
        to_turn_on.append((8, 0))
        to_turn_on.append((8, 1))
        to_turn_on.append((8, 2))
        to_turn_on.append((8, 3))
        to_turn_on.append((8, 4))
        return self.turn_on(to_turn_on)

    def show_dash_min(self):
        to_turn_on = []
        to_turn_on.append((8, 5))
        return self.turn_on(to_turn_on)

    def show_demie(self):
        to_turn_on = []
        to_turn_on.append((9, 3))
        to_turn_on.append((9, 4))
        to_turn_on.append((9, 5))
        to_turn_on.append((9, 6))
        to_turn_on.append((9, 7))
        return self.turn_on(to_turn_on)
