# textual_clock

The `main` branch of this repository contains the code for the raspberry as well as the iOS companion application and documentation.

The branches `raspberry_xx` contain only the code for each raspberry. They are intended to be checked out on the corresponding raspberry. They can diverge but will probably not during normal operation.

## Setup of the Raspberry

1. Install Raspbian image, with Wi-Fi and ssh enabled, with as name `textualclock`, so that it appears as such on the network.
2. set your username and pwd
3. install the stuff in `raspberry_install.sh`
4. clone this repo in the home folder
5. create a systemd service to run the `start.sh` script at startup. Create a file `textual_clock.service` in `/etc/systemd/system/` (replace `<username>` with your username).
   For the **LED clock** (Raspberry Pi with NeoPixel strip):
```
[Unit]
Description=Clock service
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
Restart=always
RestartSec=1
User=root
ExecStart=sh /home/<username>/textual_clock/start.sh /home/<username>/textual_clock led

[Install]
WantedBy=multi-user.target
```
   For the **desk/screen clock** (Raspberry Pi with display):
```
[Unit]
Description=Clock service
After=network.target graphical-session.target
StartLimitIntervalSec=0

[Service]
Type=simple
RestartSec=1
User=sam
Environment=XDG_RUNTIME_DIR=/run/user/1000
Environment=WAYLAND_DISPLAY=wayland-0
ExecStart=sh /home/<username>/textual_clock/start.sh /home/<username>/textual_clock screen

[Install]
WantedBy=graphical.target
```
   Enable the service with `sudo systemctl enable textual_clock.service`
6. create the keyboard watcher service (required for Tetris and for restarting the clock with `Ctrl+F1`). Create a file `textual_clock_keywatch.service` in `/etc/systemd/system/` (replace `<username>` with your username):
```
[Unit]
Description=Clock keyboard watcher
After=graphical.target
StartLimitIntervalSec=0

[Service]
Type=simple
Restart=always
RestartSec=2
User=root
ExecStart=/home/<username>/textual_clock/venv/bin/python /home/<username>/textual_clock/keywatch.py

[Install]
WantedBy=graphical.target
```
   1. enable the service with `sudo systemctl enable textual_clock_keywatch.service`
   2. note: `evdev` (used by keywatch) is installed automatically by `start.sh` on first run. Start the clock service at least once before starting the keywatch service so the venv and dependencies are in place.
7. setup the scheduled reboot:
   1. execute `sudo crontab -e`
   2. (select your editor if this is the first time. I advise to use nano)
   3. at the very end of the file, add these two lines to schedule reboot at 11:59am and 11:59pm (here I advise only the midnight one):
      1. `59 11 * * * /sbin/reboot`
      2. `59 23 * * * /sbin/reboot`
8. On the raspberry, checkout to the correct `raspberry_xx` branch.

## Tetris easter egg (screen display only)

Press `F1` while the clock is running to launch the original Tetris game. The clock pauses and Tetris starts full screen. You can play as many games as you like in one session — each completed or quit game is automatically saved as a pending trace. When you quit Tetris entirely (back to the Tetris home screen, then close the window), the clock resumes and shows a review dialog to keep or discard each recorded game as a clock transition animation (tetris style).

Press `Ctrl+F1` at any time — even when the clock is not running — to start the clock service.
