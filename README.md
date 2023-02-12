# textual_clock

The `main` branch of this repository contains the code for the raspberry as well as the iOS companion application and documentation.

The branches `raspberry_xx` contain only the code for each raspberry. They are intended to be checked out on the corresponding raspberry. They can diverge but will probably not during normal operation.

## Setup of the Raspberry

1. Install Raspbian image, with Wi-Fi and ssh enabled, with as name `textualclock`, so that it appears as such on the network.
2. set your username and pwd
3. install the stuff in `raspberry_install.sh`
4. clone this repo in the home folder
5. modify `/etc/rc.local` and add `sudo sh /home/<username>/textual_clock/start.sh`
6. setup the scheduled reboot:
   1. execute `sudo crontab -e`
   2. (select your editor if this is the first time. I advise to use nano)
   3. at the very end of the file, add these two lines to schedule reboot at 11:59am and 11:59pm (here I advise only the midnight one):
      1. `59 11 * * * /sbin/reboot`
      2. `59 23 * * * /sbin/reboot`
7. On the raspberry, checkout to the correct `raspberry_xx` branch.
