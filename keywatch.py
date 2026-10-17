#!/usr/bin/env python3
"""Keyboard watcher daemon.

Runs permanently as a systemd service (root). Detects two 3-key chords:

  Ctrl + T + E   stop the clock service, launch the original Tetris game
  Ctrl + C + L   kill Tetris (if running), start the clock service

All three keys of each chord must be held simultaneously to trigger.
"""
import os
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
CLOCK_ROOT = os.path.dirname(os.path.abspath(__file__))
TETRIS_DIR = os.path.join(CLOCK_ROOT, "Tetris")

_tetris_proc: "subprocess.Popen | None" = None


def _display_user():
    """Return pwd entry for the primary display user (first UID >= 1000)."""
    import pwd
    for uid in range(1000, 1010):
        try:
            info = pwd.getpwuid(uid)
            if os.path.isdir(info.pw_dir):
                return info
        except KeyError:
            pass
    return None


def _gui_env() -> dict:
    """Build an environment suitable for launching a GUI app from a root daemon."""
    env = os.environ.copy()
    env["DISPLAY"] = ":0"

    user = _display_user()
    if user:
        env["HOME"] = user.pw_dir
        xauth = os.path.join(user.pw_dir, ".Xauthority")
        if os.path.exists(xauth):
            env["XAUTHORITY"] = xauth
        runtime = f"/run/user/{user.pw_uid}"
        if os.path.isdir(runtime):
            env["XDG_RUNTIME_DIR"] = runtime
            for name in os.listdir(runtime):
                if name.startswith("wayland-"):
                    env["WAYLAND_DISPLAY"] = name
                    break

    return env


def _launch_tetris() -> None:
    global _tetris_proc
    if _tetris_proc is not None and _tetris_proc.poll() is None:
        print("Tetris already running, ignoring")
        return
    print("Ctrl+T+E: stopping clock, launching Tetris")
    subprocess.run(["systemctl", "stop", CLOCK_SERVICE], check=False)
    time.sleep(0.5)

    user = _display_user()
    kwargs: dict = dict(cwd=TETRIS_DIR, env=_gui_env())
    if user:
        kwargs["user"] = user.pw_name  # drop root, run as display user

    _tetris_proc = subprocess.Popen([sys.executable, "tetris.py"], **kwargs)


def _launch_clock() -> None:
    global _tetris_proc
    if _tetris_proc is not None and _tetris_proc.poll() is None:
        print("Ctrl+C+L: killing Tetris")
        _tetris_proc.kill()
        _tetris_proc.wait()
    _tetris_proc = None
    print("Ctrl+C+L: starting clock")
    subprocess.run(["systemctl", "start", CLOCK_SERVICE], check=False)


def _find_keyboards() -> list:
    devices = []
    for path in evdev.list_devices():
        try:
            dev = evdev.InputDevice(path)
            caps = dev.capabilities().get(ecodes.EV_KEY, [])
            if ecodes.KEY_T in caps and ecodes.KEY_E in caps and ecodes.KEY_C in caps:
                devices.append(dev)
        except Exception:
            pass
    return devices


def _watch(devices: list) -> None:
    fd_map = {dev.fd: dev for dev in devices}
    held: set = set()

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

                    if key.keystate in (evdev.KeyEvent.key_down, evdev.KeyEvent.key_hold):
                        held.add(event.code)
                    else:
                        held.discard(event.code)

                    if key.keystate == evdev.KeyEvent.key_down:
                        ctrl = (
                            ecodes.KEY_LEFTCTRL in held
                            or ecodes.KEY_RIGHTCTRL in held
                        )
                        if ctrl and ecodes.KEY_T in held and ecodes.KEY_E in held:
                            _launch_tetris()
                        elif ctrl and ecodes.KEY_C in held and ecodes.KEY_L in held:
                            _launch_clock()
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
        print(f"Watching: {', '.join(d.name for d in devices)}")
        _watch(devices)
        for dev in devices:
            try:
                dev.close()
            except Exception:
                pass
        time.sleep(1)


if __name__ == "__main__":
    main()
