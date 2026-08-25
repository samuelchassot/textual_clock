from flask import Flask, request, jsonify
import os
import clock
import threading

app = Flask(__name__)
clock_thread = None

HOST = "0.0.0.0"
PORT = 4242

CURRENT_COLOR_FILE_PATH = "res/color.current"
SEPARATOR = ";"
DEFAULT_COLOR = (255, 255, 255)


@app.route("/liveness", methods=["GET"])
def liveness():
    liveness = {"liveness": True}
    return jsonify(liveness), 200


@app.route("/reboot", methods=["POST"])
def restart():
    os.system("echo Rebooting the system...")
    os.system("sudo reboot")
    return "Rebooting..."

@app.route("/test", methods=["POST"])
def test():
    with open("test.txt", "w") as f:
        f.write("Testing!")
        f.close()
    return "Starting test mode..."

@app.route("/pull", methods=["POST"])
def pull():
    os.system("echo Pulling the latest code...")
    os.system("git pull")
    return "Code updated!"


@app.route("/color", methods=["GET"])
def color_get():
    (r, g, b) = read_current_color()
    color = {"color_r": r, "color_g": g, "color_b": b}
    return jsonify(color), 200


@app.route("/color", methods=["POST"])
def color_post():
    print(request.get_data())
    color = request.get_json()
    print("Received JSON color: ", color)
    if color == None:
        return "ERROR", 400
    color_tuple = (color["color_r"], color["color_g"], color["color_b"])
    store_color(color_tuple)
    return "Color stored", 200

@app.route("/update_style", methods=["POST"])
def update_style_post():
    print(request.get_data())
    update_style = request.get_json()
    print("Received JSON update style: ", update_style)
    if update_style == None or "update_style" not in update_style:
        return "ERROR", 400
    update_style_str = update_style["update_style"]
    if clock_update_update_style(update_style_str):
        return "Update style stored", 200
    else:
        return "ERROR: Invalid update style", 400
    
@app.route("/update_style", methods=["GET"])
def update_style_get():
    update_style = clk.read_current_update_style()
    return jsonify({"update_style": update_style.value}), 200

@app.route("/update_style/options", methods=["GET"])
def update_style_options():
    options = clk.update_style_options()
    return jsonify({"update_style_options": options}), 200

@app.route("/special_time_periods", methods=["POST"])
def special_time_periods_post():
    print(request.get_data())
    periods = request.get_json()
    print("Received JSON special time periods: ", periods)
    if periods == None:
        return "ERROR", 400

    special_periods = []
    for period in periods:
        start_time = (period["start_hour"], period["start_minute"])
        end_time = (period["end_hour"], period["end_minute"])
        color = (period["color_r"], period["color_g"], period["color_b"])
        special_periods.append(clock.TimePeriod(start_time, end_time, color))

    clk.update_special_time_periods(special_periods)
    return "Special time periods stored", 200


def store_color(color_tuple: tuple[int, int, int]) -> None:
    with open(CURRENT_COLOR_FILE_PATH, "w") as f:
        to_write = (
            str(color_tuple[0])
            + SEPARATOR
            + str(color_tuple[1])
            + SEPARATOR
            + str(color_tuple[2])
        )
        print("Writing color: " + to_write)
        f.write(to_write)
        f.close()

def clock_update_update_style(update_style_str: str) -> bool:
    try:
        clk.update_current_update_style(update_style_str)
        print("Updated clock update style to: " + update_style_str)
        return True
    except ValueError:
        print("Invalid update style received: " + update_style_str)
        return False


def read_current_color() -> tuple[int, int, int]:
    try:
        with open(CURRENT_COLOR_FILE_PATH, "r") as f:
            l = f.readline()
            print("Read color line: " + l)
            rgb = l.split(SEPARATOR)
            return (int(rgb[0]), int(rgb[1]), int(rgb[2]))
    except Exception as e:
        print("ERROR: cannot read the current color!\n", e)
        with open(CURRENT_COLOR_FILE_PATH, "w") as f:
            to_write = (
                str(DEFAULT_COLOR[0])
                + SEPARATOR
                + str(DEFAULT_COLOR[1])
                + SEPARATOR
                + str(DEFAULT_COLOR[2])
            )
            print("Writing default color: " + to_write)
            f.write(to_write)
            f.close()
        return DEFAULT_COLOR


if __name__ == "__main__":
    clock_display = os.environ.get("CLOCK_DISPLAY", "led")

    print("CLOCK_DISPLAY: " + clock_display)

    if clock_display == "screen":
        import pygame
        from screen_display import DisplayScreen

        SCREEN_SIZE = 720
        pygame.init()
        surface = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE), pygame.FULLSCREEN | pygame.NOFRAME)
        pygame.mouse.set_visible(False)
        display = DisplayScreen(cols=11, rows=10, screen_width=SCREEN_SIZE, screen_height=SCREEN_SIZE, surface=surface)
    else:
        import board
        import neopixel
        from led_display import DisplayLed

        n_leds_per_line = 11
        n_leds = n_leds_per_line * 10 + 4
        pixels = neopixel.NeoPixel(board.D18, n_leds)
        display = DisplayLed(n_leds_per_line, pixels)

    clk = clock.Clock(display)
    if clock_display == "screen":
        display.set_style_options(clk.update_style_options())
    refresh_rate_seconds = 5
    delay_between_words_seconds = 0.2
    flask_thread = threading.Thread(target=lambda: app.run(host=HOST, port=PORT), daemon=True)
    flask_thread.start()
    clk.run_loop(refresh_rate_seconds, delay_between_words_seconds)
