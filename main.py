from evdev import UInput, InputDevice, categorize, ecodes as evHandler
from pathlib import Path
import time
import subprocess
import threading
import re

absolute_dir = Path(__file__).parent.resolve()


class DeviceHandler:
    def find_devices(self) -> list:
        devices = []
        raw_devices = subprocess.run(
            ["cat", "/proc/bus/input/devices"], capture_output=True, text=True
        )

        lines = raw_devices.stdout.split("\n")
        text = ""

        for line in lines:
            if line == "":
                devices.append(text)
                text = ""

                continue

            text += line + "\n"

        return devices

    def predict_device(self, search_device: str, devices: list) -> str:
        found_device = ""
        explicit_search = search_device not in ["mouse", "keyboard"]

        for device in devices:
            if explicit_search:
                coincidence = re.search('Name="(.*?)"', device)

                if coincidence and coincidence.group() == f"Name={search_device}":
                    found_device = device
                    break

                continue

            if search_device.lower() in device.lower():
                found_device = device
                break

        device_info = found_device.split("\n")

        for x in device_info:
            if x.startswith("H"):
                found_device = x[12:]
                break

        parts = found_device.split(" ")
        handler = ""

        for x in parts:
            if x.startswith("event") or x.startswith("mouse"):
                handler = x
                break

        return "/dev/input/" + handler


class VirtualMouse:
    def __init__(
        self, cap: dict = {evHandler.EV_KEY: (evHandler.BTN_LEFT, evHandler.BTN_RIGHT)}
    ) -> None:
        self.virtual_mouse = UInput(events=cap, name="Virtual-Mouse", vendor=0x1234)  # type: ignore

    def emulate_click(self) -> None:
        self.virtual_mouse.write(evHandler.EV_KEY, evHandler.BTN_LEFT, 1)
        self.virtual_mouse.syn()

        time.sleep(0.01)

        self.virtual_mouse.write(evHandler.EV_KEY, evHandler.BTN_LEFT, 0)
        self.virtual_mouse.syn()


class MouseTracker:
    def __init__(self, dev: str, virtual_mouse, config: dict) -> None:
        self.Device = InputDevice(dev)
        self.VirtualMouse = virtual_mouse

        self.Config = config

        self.IsPressing = False
        self.CanPress = True

    def listen_mouse_device(self) -> None:
        for event in self.Device.read_loop():
            if event.type == evHandler.EV_KEY and event.code == evHandler.BTN_RIGHT:
                self.IsPressing = event.value == 1

    def process_press(self) -> None:
        click_delay_ms = float(self.Config["CLICK_DELAY_MS"])

        while True:
            if not self.CanPress:
                continue

            time.sleep(click_delay_ms / 1000)

            if self.IsPressing:
                thread = threading.Thread(target=self.VirtualMouse.emulate_click)
                thread.start()

    def create_mouse_thread(self) -> None:
        listen_thread = threading.Thread(target=self.listen_mouse_device)
        listen_thread.start()

        process_thread = threading.Thread(target=self.process_press)
        process_thread.start()


class KeyboardTracker:
    def __init__(self, dev: str, mouse: MouseTracker) -> None:
        self.Device = InputDevice(dev)
        self.MouseDevice = mouse

    def listen_keyboard_device(self) -> None:
        alt_pressed = False

        for event in self.Device.read_loop():
            if event.type == evHandler.EV_KEY:
                key_event = categorize(event)

                if key_event.scancode in [  # type: ignore
                    evHandler.KEY_LEFTALT,
                    evHandler.KEY_RIGHTALT,
                ]:
                    if key_event.keystate == key_event.key_down:  # type: ignore
                        alt_pressed = True

                    elif key_event.keystate == key_event.key_up:  # type: ignore
                        alt_pressed = False

                if (
                    key_event.scancode == evHandler.KEY_T  # type: ignore
                    and key_event.keystate == 1  # type: ignore
                    and alt_pressed
                ):
                    self.MouseDevice.CanPress = not self.MouseDevice.CanPress

    def create_keyboard_thread(self) -> None:
        thread = threading.Thread(target=self.listen_keyboard_device)
        thread.start()


dHandler = DeviceHandler()


def main() -> None:
    with open(absolute_dir / "config", "r") as f:
        config = f.read().split("\n")

    config_list = {}

    for x in config:
        if x == "":
            continue

        parts = x.split("=")
        config_list[parts[0]] = parts[1]

    device_list = dHandler.find_devices()

    virtual_mouse = VirtualMouse()

    mouse_device = dHandler.predict_device(
        config_list["MOUSE_DEVICE"]
        if "MOUSE_DEVICE" in config_list and config_list["MOUSE_DEVICE"] != "Unknown"
        else "mouse",
        device_list,
    )
    mouse_tracker = MouseTracker(mouse_device, virtual_mouse, config_list)

    keyboard_device = dHandler.predict_device(
        config_list["KEYBOARD_DEVICE"]
        if "KEYBOARD_DEVICE" in config_list
        and config_list["KEYBOARD_DEVICE"] != "Unknown"
        else "keyboard",
        device_list,
    )
    keyboard_tracker = KeyboardTracker(keyboard_device, mouse_tracker)

    mouse_tracker.create_mouse_thread()
    keyboard_tracker.create_keyboard_thread()


if __name__ == "__main__":
    main()
