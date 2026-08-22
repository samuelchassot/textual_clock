# DO NOT REMOVE, IT IS THE ENTRY POINT FOR THE CLOCK

CLOCK_DISPLAY="${1:-led}"

if [ "$CLOCK_DISPLAY" != "led" ] && [ "$CLOCK_DISPLAY" != "screen" ]; then
  echo "Usage: $0 [led|screen]"
  exit 1
fi

cd /home/$(whoami)/textual_clock/

# Check for internet connection, 4 attempts with a 5 second interval
i=0
INTERNET_ACTIVE=0

while [ $i -lt 4 ]; do
  if ping -c 1 google.com >/dev/null 2>&1; then
    echo "Internet is up. Proceeding..."
    INTERNET_ACTIVE=1
    break
  else
    echo "Waiting for internet connection..."
    sleep 5
    i=$((i + 1))
  fi
done

# Check if a venv already exists, if not create one
if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
fi

if [ $INTERNET_ACTIVE -eq 1 ]; then
  echo "Internet connection established. Running updates..."
  git pull
  if [ "$CLOCK_DISPLAY" = "led" ]; then
    ./venv/bin/pip install -r requirements.txt
    ./venv/bin/pip install -r requirements-led.txt
  else
    ./venv/bin/pip install -r requirements.txt
  fi
else
  echo "No internet connection. Skipping updates..."
fi

# Run app as root (ONLY here)
exec sudo CLOCK_DISPLAY="$CLOCK_DISPLAY" venv/bin/python clock_app.py