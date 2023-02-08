from flask import Flask, request
import os

app = Flask(__name__)

@app.route("/reboot", methods=["POST"])
def restart():
    os.system("echo Rebooting the system...")
    os.system("sudo reboot")
    return "Rebooting..."

@app.route("/color", methods=["GET", "POST"])
def color():
    if request.method == "GET":
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        color = {"color_r": r, "color_g": g, "color_b": b}
        return jsonify(color)
    elif request.method == "POST":
        color = request.get_json()
        colors.append(color)
        return "Color added", 201


if __name__ == "__main__":
    app.run(debug=True)