import asyncio
import common
import buttons
import leds
import logic

def init():
    print("[RUNNER]: init")

    buttons.init()
    buttons.action()
    leds.init()
    logic.init()

async def main():
    init()
    tasks = []
    tasks.append(asyncio.create_task(common.loop_async("BUTTONS", buttons.action)))
    tasks.append(asyncio.create_task(common.loop_async("LEDS", leds.action)))
    tasks.append(asyncio.create_task(logic.action()))
    #tasks.append(asyncio.create_task(process_time_measure()))
    for task in tasks:
        await task
    print("[RUNNER]: Error: loop task finished!")

def run():
    asyncio.run(main())
