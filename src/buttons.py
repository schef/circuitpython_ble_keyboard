import common
import common_pins

on_state_change_cb = None
buttons = []
button_pins = [
    common_pins.BUTTON_1,
    common_pins.BUTTON_2,
]

class Button:
    def __init__(self, id, name, active_high):
        print(f"[BUTTONS]: create object {name}")
        self.input = common.create_input(id)
        self.name = name
        self.state = None
        self.active_high = active_high

    def check(self):
        state = self.input.value()
        if self.active_high:
            state = int(not state)
        if state != self.state:
            self.state = state
            print("[BUTTONS]: %s -> %d" % (self.name, self.state))
            if on_state_change_cb is not None:
                on_state_change_cb(self.name, self.state)

def get_state_by_name(name) -> bool | None:
    for button in buttons:
        if button.name == name:
            return button.state
    return None

def get_button_by_name(name) -> Button | None:
    for button in buttons:
        if button.name == name:
            return button
    return None

def register_on_state_change_callback(cb):
    print("[BUTTONS]: register on state change cb")
    global on_state_change_cb
    on_state_change_cb = cb

def init():
    print("[BUTTONS]: init")
    for pin in button_pins:
        buttons.append(Button(id = pin.id, name = pin.name, active_high = pin.active_high))

def action():
    for button in buttons:
        button.check()
