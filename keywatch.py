#!/usr/bin/env python3
"""Keyboard watcher daemon.

Runs permanently as a systemd service. Watches all connected keyboards for
Ctrl+F1 and starts the textual_clock systemd service when detected.

This lets you restart the clock from the physical keyboard even when the
clock process itself is not running (e.g. after a crash or a Tetris session
that did not return cleanly).
"""
import select
import subprocess
import sys
import time

try:
    import evdev
    from evdev import ecodes
except ImportError:
    print("evdev not available — install it with: pip install evdev")
    sys.exit(1)

CLOCK_SERVICE = "textual_clock.service"


def _find_keyboards() -> list[evdev.InputDevice]:
    devices = []
    for path in evdev.list_devices():
        try:
            dev = evdev.InputDevice(path)
            caps = dev.capabilities().get(ecodes.EV_KEY, [])
            if ecodes.KEY_F1 in caps and ecodes.KEY_LEFTCTRL in caps:
                devices.append(dev)
        except Exception:
            pass
    return devices


def _start_clock() -> None:
    print(f"Ctrl+F1 detected — starting {CLOCK_SERVICE}")
    subprocess.run(["systemctl", "start", CLOCK_SERVICE], check=False)


def _watch(devices: list[evdev.InputDevice]) -> None:
    """Watch devices until one disconnects or an error occurs."""
    fd_map = {dev.fd: dev for dev in devices}
    ctrl_held = False
    while True:
        try:
            readable, _, _ = select.select(fd_map, [], [], 2.0)
        except (ValueError, OSError):
            return
        for fd in readable:
            dev = fd_map[fd]
            try:
                for event in dev.read():
                    if event.type != ecodes.EV_KEY:
                        continue
                    key = evdev.categorize(event)
                    if key.keycode in ("KEY_LEFTCTRL", "KEY_RIGHTCTRL"):
                        ctrl_held = key.keystate != evdev.KeyEvent.key_up
                    if (
                        key.keycode == "KEY_F1"
                        and key.keystate == evdev.KeyEvent.key_down
                        and ctrl_held
                    ):
                        _start_clock()
            except OSError:
                return


def main() -> None:
    print("keywatch starting")
    while True:
        devices = _find_keyboards()
        if not devices:
            print("No keyboard found, retrying in 2s…")
            time.sleep(2)
            continue
        names = ", ".join(d.name for d in devices)
        print(f"Watching: {names}")
        _watch(devices)
        for dev in devices:
            try:
                dev.close()
            except Exception:
                pass
        time.sleep(1)


if __name__ == "__main__":
    main()
