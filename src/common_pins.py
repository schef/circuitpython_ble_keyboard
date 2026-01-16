import board

class Pin:
    def __init__(self, id, name, active_high):
        self.id = id
        self.name = name
        self.active_high = active_high

BUTTON_1 = Pin(board.P0_02, "BUTTON_1", True)
BUTTON_2 = Pin(board.P0_15, "BUTTON_2", True)
LED_1 = Pin(board.P0_06, "LED_1", True)
LED_2 = Pin(board.P0_26, "LED_2", True)
