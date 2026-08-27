from enum import Enum
from math import floor
import os
import random
import sys
import time

from display import Display
from led_display import DisplayLed


def lerp_color(c1: tuple[int, int, int], c2: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    """Linear interpolation between two RGB colors, t ∈ [0,1]."""
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
    'TIRET':   [(8, 5,  5)],
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
    25: ['VINGT', 'TIRET', 'CINQ_M'],
    30: ['ET_D', 'DEMIE'],
    35: ['MOINS', 'VINGT', 'TIRET', 'CINQ_M'],
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

    def __init__(self, display: Display, time_provider: TimeProvider = TimeProvider()) -> None:
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
        self._current_style = self.read_current_update_style()

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

        self._should_quit = False
        self._should_restart = False
        self._force_reload = False
        self._setup_menu()

    def _setup_menu(self) -> None:
        self.display.add_menu_button("Quit", self._on_quit_selected)
        self.display.add_menu_button("Restart", self._on_restart_selected)
        self.display.add_menu_dropdown(
            "Style",
            options=self.update_style_options,
            current_value=self.current_update_style_value,
            on_select=self._on_update_style_selected,
        )
        self.display.set_double_click_callback(self._open_menu)

    def _open_menu(self) -> None:
        self.display.open_menu()

    def _on_quit_selected(self) -> None:
        self._should_quit = True

    def _on_restart_selected(self) -> None:
        self._should_restart = True

    def _on_update_style_selected(self, style_value: str) -> None:
        self.update_current_update_style(style_value)
        self._force_reload = True

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
        except (ValueError, NotImplementedError):
            print("Invalid update style received: " + update_style_str)
            return
        self._current_style = update_style
        try:
            with open(self.UPDATE_STYLE_FILE_PATH, "w") as f:
                f.write(update_style.value)
        except Exception as e:
            print("ERROR: cannot write the update style to file!\n", e)

    def current_update_style_value(self) -> str:
        return self._current_style.value

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
        last_update = time.time() - refresh_rate_seconds  # trigger an immediate first update
        while True:
            command = self.display.poll_events()
            if command == "quit" or self._should_quit:
                break
            if self._should_restart:
                os.execv(sys.executable, [sys.executable, os.path.abspath(sys.argv[0])])

            reload = False
            if self._force_reload:
                reload = True
                last_update = 0  # force immediate refresh with the new style
                self.last_h_five_min_residual_minutes_color = (0, 0, 0, (0, 0, 0))
                self._force_reload = False

            if os.path.exists("test.txt"):
                print("Test mode activated!")
                self.test_loop()
                os.remove("test.txt")
                self.display.turn_off_all()
                reload = True
                last_update = 0

            if reload or time.time() - last_update >= refresh_rate_seconds:
                current_update_style = self.read_current_update_style()
                if current_update_style == UPDATE_STYLE.MATRIX:
                    self.update_clock_matrix()
                else:
                    self.update_clock(delay_between_words_seconds, reload)
                last_update = time.time()

            time.sleep(0.1)

    def test_loop(self):
        print("turning off")
        self.display.turn_off_all()
        time.sleep(0.8)
        print("turning on")
        self.color_on = self.read_current_color()

        for i in range(self.display.rows):
            for j in range(self.display.cols):
                self.display.turn_on([(i, j)], self.color_on)
                time.sleep(0.5)

        # turn on the 4 corners
        for i in range(1, 5):
            self.display.turn_on([(-1, i)], self.color_on)
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

            return cells

        def _matrix_rain(target_cells: list[tuple[int, int]]) -> None:
            """Falling-character animation. Ends with target_cells lit in
            self.color_on and all other cells off."""
            nrows = self.display.rows
            ncols = self.display.cols
            target_color = self.color_on
            target_set = set(target_cells)

            drop_y = [random.uniform(-nrows * 0.7, 0) for _ in range(ncols)]
            drop_speed = [random.uniform(3.0, 5.5) for _ in range(ncols)]
            lock_q = list(target_set)
            random.shuffle(lock_q)
            locked: dict[tuple[int, int], float] = {}

            self.display.set_auto_commit(False)
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
                            self.display.turn_on([(r, c)], color)

                    self.display.commit()
                    time.sleep(dt)

                # Dernière frame: éteint tout puis allume la cible en un seul commit
                self.display.turn_off_all()
                for cell in target_set:
                    self.display.turn_on([cell], target_color)
                self.display.commit()
            finally:
                self.display.set_auto_commit(True)
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
        return self.display.turn_on(to_turn_on, self.color_on)


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
            return self.display.turn_on(to_turn_on, self.color_on)
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
        return self.display.turn_on(to_turn_on, self.color_on)


    def show_il_est(self):
        to_turn_on = []
        to_turn_on.extend(self._to_turn_on_word("IL"))
        to_turn_on.extend(self._to_turn_on_word("EST"))
        return self.display.turn_on(to_turn_on, self.color_on)

