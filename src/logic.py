import buttons
import leds
import common_pins
import asyncio

import adafruit_ble
from adafruit_ble.advertising import Advertisement
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.standard.hid import HIDService
from adafruit_ble.services.standard.device_info import DeviceInfoService
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode


advertisement = None
ble = None
k = None

def on_buttons_state_change_cb(name, state):
        if name == common_pins.BUTTON_1.name:
            leds.get_led_by_name(common_pins.LED_1.name).set_state(state)
            if state:
                k.send(Keycode.LEFT_ARROW)
        elif name == common_pins.BUTTON_2.name:
            leds.get_led_by_name(common_pins.LED_2.name).set_state(state)
            if state:
                k.send(Keycode.RIGHT_ARROW)

def init():
    print("[LOGIC]: init")
    global advertisement, ble, k
    buttons.register_on_state_change_callback(on_buttons_state_change_cb)
    hid = HIDService()
    device_info = DeviceInfoService(software_revision=adafruit_ble.__version__, manufacturer="Adafruit Industries")
    advertisement = ProvideServicesAdvertisement(hid)
    advertisement.appearance = 961
    scan_response = Advertisement()
    scan_response.complete_name = "CircuitPython HID"
    ble = adafruit_ble.BLERadio()
    k = Keyboard(hid.devices)

async def action():
    print("[LOGIC]: action")
    print("[LOGIC]: action - start adv")
    ble.start_advertising(advertisement)
    while True:
        while not ble.connected:
            await asyncio.sleep(0)

        print("[LOGIC]: action - connected")
        while ble.connected:
            await asyncio.sleep(0)
        print("[LOGIC]: action - disconnected")

        print("[LOGIC]: action - start adv")
        ble.start_advertising(advertisement)
