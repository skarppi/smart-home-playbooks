# This is your main script.

import epd3in7
import uasyncio as asyncio
import time

from fb import Canvas
from fonts import sfpro30, sfpro50, font10
from state import temp

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

    epd.init(1)
    epd.Clear(0xFF, 1)

    # out
    fb.text('Ulkona', 10, 0, font10)

    # roof
    fb.text_center('Ylakerta', 60, font10)
    fb.line(10, 100, w // 2, 10)
    fb.line(w // 2, 10, w - 10, 100)
    fb.line(10, 100, 10, 150)
    fb.line(w - 10, 100, w - 10, 150)

    # downstairs
    fb.text_center('Alakerta', 180, font10)
    fb.rect(10, 150, w - 20, 300)
    fb.rect(10, 150, w - 20, 150)

    # cellar
    fb.text_center('Patteri', 330, font10)
    fb.line(w - 10, 130, w - 10, 300)

def partial():
    fb.clear(10, 20, 100, 40)
    fb.clear(20, 90, w - 40, 80)
    fb.clear(20, 200, w - 40, 80)
    fb.clear(20, 350, w - 40, 80)

    fb.text(temp('takapiha', 1), 10, 20, sfpro30)
    fb.text_center(temp('vintti', 1), 80, sfpro50)
    fb.text_center(temp('indoor', 1), 200, sfpro50)
    fb.text_center(temp('pannu', 2), 350, sfpro50)

    start = time.time()
    epd.display_1Gray(fb.render())
    print('render in {0} seconds'.format(time.time() - start))

async def render_loop():
    while True:
        partial()

        await asyncio.sleep(58)

async def main():
    full()
    
    await render_loop()

try:
    asyncio.run(main())
finally:
    print("EOF main.py")
    asyncio.new_event_loop()