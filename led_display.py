from display import Display


class DisplayLed(Display):

    def __init__(self, n_leds_per_row: int, led_array) -> None:
        assert len(led_array) == 114
        self.pixels = led_array
        self.cols = n_leds_per_row
        self.rows = (len(led_array) - 4) // n_leds_per_row
        self.color_off = (0, 0, 0)
        self.auto_commit = True
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
        if hasattr(self.pixels, "auto_write"):
            self.pixels.auto_write = False

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
    # LEDs are soldered in a back-and-forth pattern:
    #
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
        """Convert virtual (row, col) to physical LED index.
        Use (-1, 1..4) for the four corner minute LEDs:
          (-1, 1): top-left   (-1, 2): top-right
          (-1, 3): bottom-right  (-1, 4): bottom-left
        """
        if i == -1:
            return int(self.cols * self.rows + (j % 4))
        if i % 2 == 0:
            return int(i * self.cols + j)
        else:
            return int(i * self.cols + (self.cols - j - 1))

    def commit(self) -> None:
        if hasattr(self.pixels, "show"):
            self.pixels.show()

    def turn_off_all(self) -> None:
        self.pixels.fill(self.color_off)
        if self.auto_commit:
            self.commit()

    def turn_on_all(self, color: tuple[int, int, int]) -> None:
        self.pixels.fill(color)
        if self.auto_commit:
            self.commit()

    def turn_off(self, indices: list[tuple[int, int]]) -> None:
        for i, j in indices:
            self.pixels[self.to_physical_index(i, j)] = self.color_off
        if self.auto_commit:
            self.commit()

    def turn_on(self, indices: list[tuple[int, int]], color: tuple[int, int, int]) -> str:
        """Turn on LEDs at the given (row, col) positions with the given color.
        Use (-1, 1..4) for the four corner minute LEDs.
        """
        debug_str = ""
        for i, j in indices:
            index = self.to_physical_index(i, j)
            self.pixels[index] = color
            if 0 <= index < len(self.debug_characters):
                debug_str += self.debug_characters[index]
            else:
                debug_str += f"corner{j}" if i == -1 else f"({i},{j})"
        if self.auto_commit:
            self.commit()
        return debug_str
