import common
import common_pins
import time

leds = []
led_pins = [
    common_pins.LED_1,
    common_pins.LED_2,
]

class Led:
    def __init__(self, id, name, active_high):
        print(f"[LEDS]: create object {name}")
        self.output = common.create_output(id)
        self.active_high = active_high
        self.state = None
        self.set_state(0)
        self.name = name

    def set_state(self, state):
        if self.active_high:
            if state:
                self.output.value = False
            else:
                self.output.value = True
        else:
            if state:
                self.output.value = True
            else:
                self.output.value = False
        self.state = state

    def get_state(self):
        return self.state

def set_state_by_name(name, state):
    print("[LEDS]: set_state_by_name(%s, %s)" % (name, state))
    for led in leds:
        if led.name == name:
            led.set_state(state)

def get_state_by_name(name) -> bool | None:
    for led in leds:
        if led.name == name:
            return led.state
    return None

def get_led_by_name(name) -> Led | None:
    for led in leds:
        if led.name == name:
            return led
    return None

def init_leds():
    for pin in led_pins:
        leds.append(Led(id = pin.id, name = pin.name, active_high = pin.active_high))

def init():
    print("[LEDS]: init")
    init_leds()
    action()

def boot_display():
    led = get_led_by_name(common_pins.LED_1.name)
    if led is not None:
        led.set_state(1)
        time.sleep(0.1)
        led.set_state(0)
        time.sleep(0.1)
        led.set_state(1)
        time.sleep(0.1)
        led.set_state(0)
        time.sleep(0.3)

def action():
    pass
