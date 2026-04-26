# Execute these commands on the Raspberry Pi's terminal

sudo apt update
sudo apt install -y \
python3-venv python3-pip python3-dev \
build-essential swig git \
python3-lgpio python3-rpi-lgpio

git clone https://github.com/samuelchassot/textual_clock.git

cd ~/textual_clock

python3 -m venv venv --system-site-packages

source venv/bin/activate

pip install \
rpi_ws281x==5.0.0 \
adafruit-circuitpython-neopixel==6.3.21 \
adafruit-blinka==9.1.0

pip install -r requirements.txt