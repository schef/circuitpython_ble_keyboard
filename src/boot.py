import supervisor
import usb_cdc
import storage
import time
import board
import digitalio

print("[APP_BOOT]: start")

led_1 = digitalio.DigitalInOut(board.P0_06)
led_1.direction = digitalio.Direction.OUTPUT
led_2 = digitalio.DigitalInOut(board.P0_26)
led_2.direction = digitalio.Direction.OUTPUT

led_2.value = True
time.sleep(0.1)
led_2.value = False
time.sleep(0.1)
led_1.value = True
time.sleep(0.1)
led_1.value = False
time.sleep(0.1)

led_2.deinit()
led_1.deinit()

button_2 = digitalio.DigitalInOut(board.P0_15)
button_2.direction = digitalio.Direction.INPUT
button_2.pull = None
button_2_pressed = not button_2.value
button_2.deinit()

if button_2_pressed:
    print("[APP_BOOT] BUTTON_2 pressed: enable USB")
    usb_cdc.enable(console=True, data=False)
else:
    print("[APP_BOOT] BUTTON_2 not pressed: disable USB")
    usb_cdc.disable()
    storage.disable_usb_drive()

print("[APP_BOOT]: end")
