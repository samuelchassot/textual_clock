# DO NOT REMOVE, IT IS THE ENTRY POINT FOR THE CLOCK
cd /home/chsa/textual_clock/

# Check for internet connection
while true; do
  if ping -c 1 google.com; then
    echo "Internet is up. Proceeding..."
    break
  else
    echo "Waiting for internet connection..."
    # Sleep for 5 seconds before checking again
    sleep 5
  fi
done

# Your actual script starts here
git pull
sudo pip3 install -r requirements.txt
# sudo python3 clock_app.py
sudo python3 test_leds_irl.py