# This is your main script.

import epd3in7
import connection
import uasyncio as asyncio
import time

from fb import Canvas
from fonts import sfpro30, sfpro50, font10
from state import temp, timestamp

fb = Canvas(epd3in7.EPD_WIDTH, epd3in7.EPD_HEIGHT)
epd = epd3in7.EPD()

w = epd3in7.EPD_WIDTH
h = epd3in7.EPD_HEIGHT

def clear():
    start = time.time()
    epd.init(0)
    epd.Clear(0xFF, 0)
    print('clear in {0} seconds'.format(time.time() - start))

def full():
    clear()

    # out
    fb.text('Ulkona', 10, 0, font10)

    # time
    fb.text('Kello', w - 100, 0, font10)

    # roof
    fb.line(10, 125, w // 2, 50)
    fb.line(w // 2, 50, w - 10, 125)
    fb.line(10, 125, 10, h - 10)
    fb.line(w - 10, 125, w - 10, h - 10)

    # upstairs
    fb.text_center('Ylakerta', 100, font10)
    fb.line(10, 200, w - 10, 200)

    # downstairs
    fb.text_center('Alakerta', 220, font10)
    fb.line(10, 320, w - 10, 320)

    # cellar
    fb.text_center('Patteri', 340, font10)
    fb.line(10, h - 10, w - 10, h - 10)

    epd.display_1Gray(fb.render())

def partial():
    # Wake up the screen from sleep
    epd.reset()

    # Deep sleep forgets the previous buffer and partial refresh cannot know changes. Put back the old state.
    epd.display_1Gray(fb.render(), False)

    fb.clear(10, 20, w // 2 - 50, 40)
    fb.text(temp('takapiha', 1), 10, 20, sfpro30)

    fb.clear(w - 100, 20, 80, 40)
    fb.text(timestamp(), w - 100, 20, sfpro30)

    fb.clear(30, 120, w - 60, 50)
    fb.text_center(temp('vintti', 1), 120, sfpro50)

    fb.clear(30, 240, w - 60, 50)
    fb.text_center(temp('indoor', 1), 240, sfpro50)

    fb.clear(30, 360, w - 60, 50)
    fb.text_center(temp('pannu', 1), 360, sfpro50)

    epd.display_1Gray(fb.render())

    epd.sleep()
    
async def main():
    asyncio.create_task(connection.start())
    full()

    while True:
        partial()
        await asyncio.sleep(60)

try:
    asyncio.run(main())
finally:
    print("EOF main.py")
    asyncio.new_event_loop()