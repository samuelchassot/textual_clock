from enum import Enum
from math import floor
import os
import random
import time


def lerp_color(c1: tuple[int, int, int], c2: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    """Interpolation linéaire entre deux couleurs RGB, t ∈ [0,1]."""
    t = max(0.0, min(1.0, t))
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )


WORD_DEFS = {
    'IL':      [(0, 0,  1)],
    'EST':     [(0, 3,  5)],
    'DEUX':    [(0, 7, 10)],
    'QUATRE':  [(1, 0,  5)],
    'TROIS':   [(1, 6, 10)],
    'NEUF':    [(2, 0,  3)],
    'UNE':     [(2, 4,  6)],
    'SEPT':    [(2, 7, 10)],
    'HUIT':    [(3, 0,  3)],
    'SIX':     [(3, 4,  6)],
    'CINQ_H':  [(3, 7, 10)],
    'MIDI':    [(4, 0,  3)],
    'DIX_H':   [(4, 2,  4)],
    'MINUIT':  [(4, 5, 10)],
    'ONZE':    [(5, 0,  3)],
    'HEURE':   [(5, 5,  9)],
    'HEURES':  [(5, 5, 10)],
    'MOINS':   [(6, 0,  4)],
    'LE':      [(6, 6,  7)],
    'DIX_M':   [(6, 8, 10)],
    'ET_Q':    [(7, 0,  1)],
    'QUART':   [(7, 3,  7)],
    'VINGT':   [(8, 0,  4)],
    'CINQ_M':  [(8, 6,  9)],
    'ET_D':    [(9, 0,  1)],
    'DEMIE':   [(9, 3,  7)],
}

HOUR_MAP = {
    1:  ['UNE',    'HEURE'],
    2:  ['DEUX',   'HEURES'],
    3:  ['TROIS',  'HEURES'],
    4:  ['QUATRE', 'HEURES'],
    5:  ['CINQ_H', 'HEURES'],
    6:  ['SIX',    'HEURES'],
    7:  ['SEPT',   'HEURES'],
    8:  ['HUIT',   'HEURES'],
    9:  ['NEUF',   'HEURES'],
    10: ['DIX_H',  'HEURES'],
    11: ['ONZE',   'HEURES'],
}

MINUTE_WORDS = {
    0:  [],
    5:  ['CINQ_M'],
    10: ['DIX_M'],
    15: ['ET_Q', 'QUART'],
    20: ['VINGT'],
    25: ['VINGT', 'CINQ_M'],
    30: ['ET_D', 'DEMIE'],
    35: ['MOINS', 'VINGT', 'CINQ_M'],
    40: ['MOINS', 'VINGT'],
    45: ['MOINS', 'QUART'],
    50: ['MOINS', 'DIX_M'],
    55: ['MOINS', 'CINQ_M'],
}

class UPDATE_STYLE(Enum):
    SIMPLE = "simple"
    MATRIX = "matrix"

    def from_str(label: str):
        if label == "simple":
            return UPDATE_STYLE.SIMPLE
        elif label == "matrix":
            return UPDATE_STYLE.MATRIX
        else:
            raise NotImplementedError(f"Unknown update style: {label}") 
class TimeProvider:
    def get_current_time(self) -> time.struct_time:
        return time.localtime()
    
class TimePeriod:
    def __init__(self, start_time: tuple[int, int], end_time: tuple[int, int], color: tuple[int, int, int]) -> None:
        self.start_time = start_time
        self.end_time = end_time
        self.color = color

class DisplayLed: 

    def __init__(self, n_leds_per_line: int, led_array) -> None:
        self.n_leds_per_line = n_leds_per_line
        self.pixels = led_array
        self.n_lines = (len(led_array) - 4) // n_leds_per_line
        assert len(led_array) == 114
        self.color_off = (0, 0, 0)
        self.color_on = (255, 255, 255)
        self.debug_characters = [
            "I", "L", "N", "E", "S", "T", "O", "D", "E", "U", "X",
            "Q", "U", "A", "T", "R", "E", "T", "R", "O", "I", "S",
            "N", "E", "U", "F", "U", "N", "E", "S", "E", "P", "T",
            "H", "U", "I", "T", "S", "I", "X", "C", "I", "N", "Q",
            "M", "I", "D", "I", "X", "M", "I", "N", "U", "I", "T",
            "O", "N", "Z", "E", "R", "H", "E", "U", "R", "E", "S",
            "M", "O", "I", "N", "S", "O", "L", "E", "D", "I", "X",
            "E", "T", "R", "Q", "U", "A", "R", "T", "P", "R", "D",
            "V", "I", "N", "G", "T", "-", "C", "I", "N", "Q", "U",
            "E", "T", "S", "D", "E", "M", "I", "E", "P", "A", "M",
        ]
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
    #
    # BUT the LEDs are soldered in a back and forth motion, which gives these indices:

    #   111                                            112
    #       0   1   2   3   4   5   6   7   8   9   10
    #       21  20  19  18  17  16  15  14  13  12  11
    #       22  23  24  25  26  27  28  29  30  31  32
    #       43  42  41  40  39  38  37  36  35  34  33
    #       44  45  46  47  48  49  50  51  52  53  54
    #       65  64  63  62  61  60  59  58  57  56  55
    #       66  67  68  69  70  71  72  73  74  75  76
    #       87  86  85  84  83  82  81  80  79  78  77
    #       88  89  90  91  92  93  94  95  96  97  98
    #       109 108 107 106 105 104 103 102 101 100 99
    #   110                                            113

    # So we offer the function to_physical_index(i, j) that makes the conversion from the virtual index i.e., line and column, to the physical index in the led array.
    # Use 
    #         (-1, 1): top left 
    #         (-1, 2): top right
    #         (-1, 3): bottom right
    #         (-1, 4): bottom left
    #       
    #       for the 4 corner LEDs, which indicate the minutes after the nearest 5 minutes mark.
        
    def to_physical_index(self, i: int, j: int) -> int:
        if i == -1:
            return int(self.n_leds_per_line * self.n_lines + (j % 4))
            # if j == 1:
            #     return int(self.n_leds_per_line * self.n_lines + (j % 4))
            # elif j == 2:
            #     return int(self.n_leds_per_line * self.n_lines + 2)
            # elif j == 3:
            #     return int(self.n_leds_per_line * self.n_lines + 3)
            # elif j == 4:
            #     return int(self.n_leds_per_line * self.n_lines)
        if i % 2 == 0:
            return int(i * self.n_leds_per_line + j)
        else:
            return int(i * self.n_leds_per_line + (self.n_leds_per_line - j - 1))


    def turn_off_all(self):
        self.pixels.fill(self.color_off)
    
    def turn_on_all(self, color: tuple[int, int, int]):
        self.pixels.fill(color)
    
    def turn_off(self, indices: list[tuple[int, int]]):
        for i, j in indices:
            index = self.to_physical_index(i, j)
            self.pixels[index] = self.color_off


    def turn_on(self, indices: list[tuple[int, int]]):
        """Turn on the LEDs at the positions given by the tuples in the list. The tuple gives the line then the column.
           Use 
             (-1, 1): top left 
             (-1, 2): top right
             (-1, 3): bottom right
             (-1, 4): bottom left
           
           for the 4 corner LEDs, which indicate the minutes after the nearest 5 minutes mark.
        
        """

        debug_str = ""
        for i, j in indices:
            index = self.to_physical_index(i, j)
            self.pixels[index] = self.color_on
            if index >= 0 and index < len(self.debug_characters):
                debug_str += self.debug_characters[index]
            else:
                if i == -1:
                    debug_str += f"corner{j}"
                else:
                    debug_str += f"({i},{j})"
        return debug_str

class Clock:
    ANIM_MS    = 40     # intervalle de frame (~25 fps)
    ANIM_TOTAL = 10.0   # durée totale en secondes
    LOCK_AFTER = 3.0    # début du figement des lettres cibles
    LOCK_END   = 8.0    # toutes les cellules cibles figées à ce point
    FADE_CELL  = 1.2    # durée du fondu vert→cible par cellule (secondes)

    RAIN_HEAD = (223, 255, 223)
    RAIN_C1   = (  0, 255,  65)
    RAIN_C2   = (  0, 192,  48)
    RAIN_C3   = (  0, 128,  32)
    RAIN_C4   = (  0,  69,  16)
    RAIN_DARK = (  0,  24,   0)

    def __init__(self, display: DisplayLed, time_provider: TimeProvider = TimeProvider()) -> None:
        self.time_provider = time_provider
        self.CURRENT_COLOR_FILE_PATH = "res/color.current"
        self.UPDATE_STYLE_FILE_PATH = "res/update_style.current"
        self.SPECIAL_TIME_PERIODS_FILE_PATH = "res/special_time_periods.txt"
        self.SPECIAL_TIME_PERIODS = self.load_special_time_periods()
        self.SEPARATOR = ";"
        self.DEFAULT_COLOR = (255, 255, 255)

        self.display = display


        self.color_off = (0, 0, 0)
        self.color_on = self.DEFAULT_COLOR

        self.last_h_five_min_residual_minutes_color: tuple[int, int, int, tuple[int, int, int]] = (
            0,
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
            print("WARNING: cannot read the current color! Using default color.\n", e)
            return self.DEFAULT_COLOR
    
    def update_current_update_style(self, update_style_str: str):
        try:
            update_style = UPDATE_STYLE.from_str(update_style_str)
            with open(self.UPDATE_STYLE_FILE_PATH, "w") as f:
                f.write(update_style.value)
        except ValueError:
            print("Invalid update style received: " + update_style_str)
        except Exception as e:
            print("ERROR: cannot write the update style to file!\n", e)

    def read_current_update_style(self) -> UPDATE_STYLE:
        try:
            with open(self.UPDATE_STYLE_FILE_PATH, "r") as f:
                style_str = f.readline().strip()
                return UPDATE_STYLE.from_str(style_str)
        except Exception as e:
            print("WARNING: cannot read the update style! Using default style (SIMPLE).\n", e)
            try:
                with open(self.UPDATE_STYLE_FILE_PATH, "w") as f:
                    f.write(UPDATE_STYLE.SIMPLE.value)
            except Exception as e:
                print("ERROR: cannot write the default update style to file!\n", e)
            return UPDATE_STYLE.SIMPLE
    def update_style_options(self) -> list[str]:
        return [style.value for style in UPDATE_STYLE]

        
    def load_special_time_periods(self):
        special_periods = []
        try:
            with open(self.SPECIAL_TIME_PERIODS_FILE_PATH, "r") as f:
                for line in f:
                    parts = line.strip().split(self.SEPARATOR)
                    if len(parts) == 7:
                        start_hour, start_minute, end_hour, end_minute, r, g, b = map(int, parts)
                        special_periods.append(TimePeriod((start_hour, start_minute), (end_hour, end_minute), (r, g, b)))
        except Exception as e:
            print("ERROR: cannot load special time periods!\n", e)
        return special_periods

    def store_special_time_periods(self, special_periods: list[TimePeriod]):
        try:
            with open(self.SPECIAL_TIME_PERIODS_FILE_PATH, "w") as f:
                for period in special_periods:
                    line = f"{period.start_time[0]}{self.SEPARATOR}{period.start_time[1]}{self.SEPARATOR}{period.end_time[0]}{self.SEPARATOR}{period.end_time[1]}{self.SEPARATOR}{period.color[0]}{self.SEPARATOR}{period.color[1]}{self.SEPARATOR}{period.color[2]}\n"
                    f.write(line)
        except Exception as e:
            print("ERROR: cannot store special time periods!\n", e)
        
    def update_special_time_periods(self, new_periods: list[TimePeriod]):
        self.SPECIAL_TIME_PERIODS = new_periods
        self.store_special_time_periods(new_periods)

    def get_current_hour(self) -> int:
        """
        returns the current hour as an int, between 0 and 23, 0 is midnight.
        """
        return self.time_provider.get_current_time().tm_hour

    def get_current_nearest_quarter(self) -> int:
        """
        returns the nearest quarter, between 0 and 3.
        0 is the hour sharp, so betwee XX:52:30 and XX+1:07:29
        """
        minutes =  self.time_provider.get_current_time().tm_min +  self.time_provider.get_current_time().tm_sec / 60.0
        return int((minutes + 7.5) // 15) % 4
    
    def get_current_quarter(self) -> int:
        """
        returns the current quarter, between 0 and 3.
        0 is the hour sharp, so betwee XX:00:00 and XX:14:59, 1 is between XX:15:00 and XX:29:59, etc.
        """
        minutes =  self.time_provider.get_current_time().tm_min +  self.time_provider.get_current_time().tm_sec / 60.0
        return int(minutes // 15) % 4

    def get_current_nearest_five_minutes(self) -> int:
        """
        returns the nearest 5 minutes mark, between 0 and 11.
        0 is the hour sharp, so between XX:57:30 and XX+1:02:29"""
        minutes =  self.time_provider.get_current_time().tm_min +  self.time_provider.get_current_time().tm_sec / 60.0
        return int((minutes + 2.5) // 5) % 12
    
    def get_current_five_minutes(self) -> int:
        """
        returns the nearest 5 minutes mark, between 0 and 11.
        0 is the hour sharp, so between XX:00:00 and XX:04:59, 1 is between XX:05:00 and XX:09:59, etc. """
        minutes =  self.time_provider.get_current_time().tm_min +  self.time_provider.get_current_time().tm_sec / 60.0
        return int(minutes // 5) % 12
    
    def get_current_minute_after_five_minutes(self) -> int:
        """
        returns the number of minutes after the last 5 minutes mark, between 0 and 4.
        So for example, if it's XX:17:30, it will return 2, because it's 2 minutes after the nearest 5 minutes mark which is XX:15:00.
        """
        minutes =  self.time_provider.get_current_time().tm_min
        return minutes - self.get_current_five_minutes()*5
    
    def get_am_pm(self) -> int:
        """
        returns 0 if it's before midday (AM), 1 if it's after midday (PM).
        """
        return 0 if self.time_provider.get_current_time().tm_hour < 12 else 1

    def anything_changed_except_corners(self, old_tuple: tuple[int, int, int, tuple[int, int, int]]) -> bool:
        return self.last_h_five_min_residual_minutes_color[0] != old_tuple[0] or self.last_h_five_min_residual_minutes_color[1] != old_tuple[1] or self.last_h_five_min_residual_minutes_color[3] != old_tuple[3] 

    def run_loop(self, refresh_rate_seconds: int = 5, delay_between_words_seconds: float = 0.2):
        print("Start of the clock")
        while True:
             # check if file test.txt exists
            reload = False
            if os.path.exists("test.txt"):
                print("Test mode activated!")
                self.test_loop()
                os.remove("test.txt")
                self.display.turn_off_all()
                reload = True
            current_update_style = self.read_current_update_style()
            if current_update_style == UPDATE_STYLE.MATRIX:
                self.update_clock_matrix()
            else:
                self.update_clock(delay_between_words_seconds, reload)
            time.sleep(refresh_rate_seconds)

    def test_loop(self):
        print("turning off")
        self.display.turn_off_all()
        time.sleep(0.8)
        print("turning on")
        self.color_on = self.read_current_color()
        self.display.color_on = self.color_on

        for i in range(self.display.n_lines):
            for j in range(self.display.n_leds_per_line):
                # physical_index = to_physical_index(i, j, n_leds_per_line)
                # print(f"Setting LED at line {i}, position {j} (physical index {physical_index})")
                self.display.turn_on([(i,j)])
                time.sleep(0.5)
        
        # turn on the 4 corners
        for i in range(1, 5):
            self.display.turn_on([(-1,i)])
            time.sleep(0.5)
            
        time.sleep(2)
        self.display.turn_off_all()
        time.sleep(0.8)
        for i in range(10):
            self.display.turn_on_all(self.color_on)
            time.sleep(0.8)
            self.display.turn_off_all()
            time.sleep(0.8)
           
    def update_clock(self, delay_between_words_seconds: float = 0.2, reload = False):
        h = self.get_current_hour()
        five_minutes = self.get_current_five_minutes()
        residual_minutes = self.get_current_minute_after_five_minutes()
        minutes = five_minutes*5 + residual_minutes

        # Because we show "25 to 10" for 9:35 for example
        if five_minutes > 6:
            h += 1
        self.color_on = self.read_current_color()

        # Check if we are in a special time period
        for period in self.SPECIAL_TIME_PERIODS:
            if (h >= period.start_time[0] and h <= period.end_time[0]) and (minutes >= period.start_time[1] and minutes <= period.end_time[1]):
                self.color_on = period.color
                break
        self.display.color_on = self.color_on

        assert(residual_minutes >= 0 and residual_minutes < 5)

        old_tuple = self.last_h_five_min_residual_minutes_color
        self.last_h_five_min_residual_minutes_color = (h, five_minutes, residual_minutes, self.color_on)

        print(f"now: {self.last_h_five_min_residual_minutes_color[0]}h, 5 minutes: {self.last_h_five_min_residual_minutes_color[1]}, residual minutes: {self.last_h_five_min_residual_minutes_color[2]}, color: {self.last_h_five_min_residual_minutes_color[3]}")
        print(f"previous: {old_tuple[0]}h, 5 minutes: {old_tuple[1]}, residual minutes: {old_tuple[2]}, color: {old_tuple[3]}")
        if self.anything_changed_except_corners(old_tuple) or reload:
            self.display.turn_off_all()
            print(f"Color: {self.color_on}")
            self.show_il_est()
            time.sleep(delay_between_words_seconds)
            self.show_hour(h)
            time.sleep(delay_between_words_seconds)
            self.show_five_minutes(five_minutes)
            time.sleep(delay_between_words_seconds)
            # if self.get_am_pm() == 0:
            #     self.show_am()
            # else:
            #     self.show_pm()
        if self.last_h_five_min_residual_minutes_color[2] != old_tuple[2] or self.last_h_five_min_residual_minutes_color[3] != old_tuple[3] or reload:
            self.show_minutes_after_five_minutes(residual_minutes)


    def update_clock_matrix(self):
        def _matrix_cells(eff_hour: int, disp_min: int) -> list[tuple[int, int]]:
            cells = []
            cells.extend(self._to_turn_on_word('IL'))
            cells.extend(self._to_turn_on_word('EST'))

            if eff_hour == 0:
                cells.extend(self._to_turn_on_word('MINUIT'))
            elif eff_hour == 12:
                cells.extend(self._to_turn_on_word('MIDI'))
            else:
                h = eff_hour % 12
                h_word = HOUR_MAP[h][0]
                heure_word = HOUR_MAP[h][1]
                cells.extend(self._to_turn_on_word(h_word))
                cells.extend(self._to_turn_on_word(heure_word))

            for w in MINUTE_WORDS.get(disp_min, []):
                cells.extend(self._to_turn_on_word(w))

            # Tiret du VINGT-CINQ
            if disp_min in (25, 35):
                cells.append((8, 5))

            return cells

        def _matrix_rain(target_cells: list[tuple[int, int]]) -> None:
            """Falling-character animation from word_clock_matrix_tkinter.py, ported to LEDs.
            Ends with target_cells lit in self.color_on and all other letter cells off."""
            nrows = self.display.n_lines
            ncols = self.display.n_leds_per_line
            pixels = self.display.pixels
            target_color = self.color_on
            target_set = set(target_cells)

            drop_y = [random.uniform(-nrows * 0.7, 0) for _ in range(ncols)]
            drop_speed = [random.uniform(3.0, 5.5) for _ in range(ncols)]
            lock_q = list(target_set)
            random.shuffle(lock_q)
            locked: dict[tuple[int, int], float] = {}   # cell -> instant où elle s'est figée

            # auto_write triggers a strip refresh on every pixel assignment — far too
            # slow at ~110 writes per frame. Batch the frame and call show() once.
            prev_auto = getattr(pixels, "auto_write", None)
            if prev_auto is not None:
                pixels.auto_write = False

            try:
                t0 = time.time()
                dt = self.ANIM_MS / 1000.0
                while True:
                    t = time.time() - t0
                    if t >= self.ANIM_TOTAL:
                        break

                    # Ralentissement progressif de la pluie dès le début du figement
                    if t < self.LOCK_AFTER:
                        speed_mult = 1.0
                    else:
                        raw = 1.0 - (t - self.LOCK_AFTER) / (self.LOCK_END - self.LOCK_AFTER)
                        speed_mult = max(0.04, raw)

                    for c in range(ncols):
                        drop_y[c] += drop_speed[c] * dt * speed_mult
                        if drop_y[c] > nrows + 9:
                            drop_y[c] = random.uniform(-2, 0)
                            drop_speed[c] = random.uniform(3.0, 5.5)

                    if t >= self.LOCK_AFTER and lock_q:
                        phase = min(1.0, (t - self.LOCK_AFTER) / (self.LOCK_END - self.LOCK_AFTER))
                        n_target = int(phase * len(target_set))
                        while len(locked) < n_target and lock_q:
                            cell = lock_q.pop(0)
                            locked[cell] = t

                    # Fondu des cellules non-cibles vers l'éteint (dernière seconde)
                    rain_fade = min(1.0, max(0.0, (t - self.LOCK_END) / (self.ANIM_TOTAL - self.LOCK_END))) \
                                if t > self.LOCK_END else 0.0

                    for r in range(nrows):
                        for c in range(ncols):
                            cell = (r, c)
                            if cell in locked:
                                # Fondu vert → cible avec lissage (smoothstep)
                                age = t - locked[cell]
                                f = min(1.0, age / self.FADE_CELL)
                                f = f * f * (3 - 2 * f)   # smoothstep
                                color = lerp_color(self.RAIN_C1, target_color, f)
                            else:
                                dist = drop_y[c] - r
                                if 0.0 <= dist < 0.7:
                                    rain_color = self.RAIN_HEAD
                                elif 0.7 <= dist < 2.5:
                                    rain_color = self.RAIN_C1
                                elif 2.5 <= dist < 4.5:
                                    rain_color = self.RAIN_C2
                                elif 4.5 <= dist < 6.5:
                                    rain_color = self.RAIN_C3
                                elif 6.5 <= dist < 9.0:
                                    rain_color = self.RAIN_C4
                                elif dist >= 9.0:
                                    rain_color = self.RAIN_DARK
                                else:
                                    rain_color = self.color_off
                                # Estompe vers l'éteint en fin d'animation
                                color = lerp_color(rain_color, self.color_off, rain_fade) \
                                        if rain_fade > 0 else rain_color
                            pixels[self.display.to_physical_index(r, c)] = color

                    if hasattr(pixels, "show"):
                        pixels.show()
                    time.sleep(dt)
            finally:
                if prev_auto is not None:
                    pixels.auto_write = prev_auto

            self.display.turn_off_all()
            self.display.turn_on(list(target_set))
        tested = False
        if os.path.exists("test.txt"):
            print("Test mode activated!")
            self.test_loop()
            os.remove("test.txt")
            self.display.turn_off_all()
            tested = True

        now = self.time_provider.get_current_time()
        hour = now.tm_hour
        minute = now.tm_min

        disp_min = (minute // 5) * 5
        corner_leds = minute % 5
        eff_hour = (hour + 1) % 24 if disp_min >= 35 else hour
        five_minutes = disp_min // 5

        self.color_on = self.read_current_color()
        for period in self.SPECIAL_TIME_PERIODS:
            if (eff_hour >= period.start_time[0] and eff_hour <= period.end_time[0]) and (disp_min >= period.start_time[1] and disp_min <= period.end_time[1]):
                self.color_on = period.color
                break
        self.display.color_on = self.color_on

        old_tuple = self.last_h_five_min_residual_minutes_color
        self.last_h_five_min_residual_minutes_color = (eff_hour, five_minutes, corner_leds, self.color_on)

        print(f"now: {eff_hour}h, 5 minutes: {five_minutes}, residual minutes: {corner_leds}, color: {self.color_on}")
        print(f"previous: {old_tuple[0]}h, 5 minutes: {old_tuple[1]}, residual minutes: {old_tuple[2]}, color: {old_tuple[3]}")

        if self.anything_changed_except_corners(old_tuple) or tested:
            cells = _matrix_cells(eff_hour, disp_min)
            print(f"Animating {len(cells)} target cells")
            _matrix_rain(cells)

        if self.last_h_five_min_residual_minutes_color[2] != old_tuple[2] or self.last_h_five_min_residual_minutes_color[3] != old_tuple[3] or tested:
            self.show_minutes_after_five_minutes(corner_leds)

    def _to_turn_on_word(self, word: str) -> list[tuple[int, int]]:
        cells = []
        for row, c0, c1 in WORD_DEFS[word]:
            for col in range(c0, c1 + 1):
                cells.append((row, col))
        return cells

    def show_hour(self, h: int):
        to_turn_on = []
        if h == 0 or h == 24:
            to_turn_on.extend(self._to_turn_on_word("MINUIT"))
        elif h == 12:
            to_turn_on.extend(self._to_turn_on_word("MIDI"))
        else:
            assert h > 0 and h < 24 and h != 12
            for w in HOUR_MAP[h % 12]:
                to_turn_on.extend(self._to_turn_on_word(w))
        return self.display.turn_on(to_turn_on)
       

    def show_five_minutes(self, c: int):
        """
        c is between 0 and 11, and indicates how many 5 minutes we have after the hour.
         0 means it's the hour sharp, 1 means it's between XX:05 and XX:09, etc.
         We show the minutes in a way that makes sense in French.
        """
        if c == 0:
            # Nothing
            pass
        else:
            words = MINUTE_WORDS.get(c*5, [])
            to_turn_on = []
            for w in words:
                to_turn_on.extend(self._to_turn_on_word(w))
            return self.display.turn_on(to_turn_on)
    def show_minutes_after_five_minutes(self, c: int):
        self.display.turn_off([(-1, 1), (-1, 2), (-1, 3), (-1, 4)])
        to_turn_on = []
        if c >= 1:
            to_turn_on.append((-1, 1))
        if c >= 2:
            to_turn_on.append((-1, 2))
        if c >= 3:
            to_turn_on.append((-1, 3))
        if c >= 4:
            to_turn_on.append((-1, 4))
        return self.display.turn_on(to_turn_on)


    def show_il_est(self):
        to_turn_on = []
        to_turn_on.extend(self._to_turn_on_word("IL"))
        to_turn_on.extend(self._to_turn_on_word("EST"))
        return self.display.turn_on(to_turn_on)

    