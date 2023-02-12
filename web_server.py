from flask import Flask, request, jsonify
import os

app = Flask(__name__)

HOST = "textualclock.local"
PORT = 4242

CURRENT_COLOR_FILE_PATH = "res/color.current"
SEPARATOR = ";"
DEFAULT_COLOR = (255, 255, 255)


@app.route("/reboot", methods=["POST"])
def restart():
    os.system("echo Rebooting the system...")
    os.system("sudo reboot")
    return "Rebooting..."


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


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=True)
