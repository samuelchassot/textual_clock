# DO NOT REMOVE, IT IS THE ENTRY POINT FOR THE CLOCK
cd /home/chsa/textual_clock/

# Check for internet connection
# check 4 times with a 5 second interval
i=0
INTERNET_ACTIVE=0

while [ $i -lt 4 ]; do
  if ping -c 1 google.com >/dev/null 2>&1; then
    echo "Internet is up. Proceeding..."
    INTERNET_ACTIVE=1
    break
  else
    echo "Waiting for internet connection..."
    # Sleep for 5 seconds before checking again
    sleep 5
    i=$((i + 1))
  fi
done

# Your actual script starts here

# Check if a venv already exists, if not create one
if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
fi

if [ $INTERNET_ACTIVE -eq 1 ]; then
  echo "Internet connection established. Running updates..."
  git pull
  ./venv/bin/pip install -r requirements.txt
else
  echo "No internet connection. Skipping updates..."
fi

# Run app as root (ONLY here)
exec sudo venv/bin/python clock_app.py