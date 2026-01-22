import time
import digitalio
import analogio
import asyncio

def get_millis():
    #return time.monotonic_ns() // 1_000_000
    return int(time.monotonic_ns() / 1000 / 1000)

def millis_passed(timestamp):
    return get_millis() - timestamp

def create_output(pin):
    gpio_out = digitalio.DigitalInOut(pin)
    gpio_out.direction = digitalio.Direction.OUTPUT
    return gpio_out

def create_input(pin, pull = None):
    gpio_in = digitalio.DigitalInOut(pin)
    gpio_in.direction = digitalio.Direction.INPUT
    gpio_in.pull = pull
    return gpio_in

def create_analog_input(pin):
    analog_in = analogio.AnalogIn(pin)
    return analog_in

async def loop_async(name, action, timeout=10):
    print("[%s]: start loop_async" % (name))
    bigest = 0
    while True:
        timestamp = get_millis()
        action()
        timepassed = millis_passed(timestamp)
        if timepassed >= timeout:
            if timepassed > bigest:
                bigest = timepassed
            print("[%s]: timeout warning %d ms with bigest %d" % (name, timepassed, bigest))
        await asyncio.sleep(0.01)

async def process_time_measure(timeout=20):
    print("[RUNNER]: start process_time_measure")
    timestamp = get_millis()
    bigest = 0
    while True:
        await asyncio.sleep(0)
        timepassed = millis_passed(timestamp)
        if timepassed >= timeout:
            if timepassed > bigest:
                bigest = timepassed
            print("[RUNNER]: timeout warning %d ms with bigest %d" % (timepassed, bigest))
        timestamp = get_millis()
