# This is your main script.

import epd3in7
import connection
import uasyncio as asyncio
import time

from fb import Canvas
from fonts import sfpro30, sfpro50, font10
from state import temp, timestamp, temp_history, format

epd = epd3in7.EPD(0)
fb = Canvas(epd.width, epd.height, epd.rotation)

w = epd.width
h = epd.height

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

    start = time.time()

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

    fb.clear(20, 420, w - 40, 50)
    graph(temp_history('pannu'), 20, 420, w - 40, 50)

    epd.display_1Gray(fb.render())

    print('render in {0} seconds'.format(time.time() - start))

    epd.sleep()
    
def graph(data, x, y, w, h):
    items = len(data)
    if items < 2:
        return

    width_per_point = (w - 50)  // (items - 1)

    max_y = max(data)
    fb.text('{:.1f}'.format(max_y), x, y, font10)

    min_y = min(data)
    fb.text('{:.1f}'.format(min_y), x, y + h - 10, font10)

    range = max_y - min_y

    y_multiplier = 1
    if range > 0:
        y_multiplier = h / range

    for i in range(1, items):
        x_previous = x + 50 + width_per_point * (i - 1)
        x_current = x + 50 + width_per_point * i

        y_previous = y + int((max_y - data[i - 1]) * y_multiplier)
        y_current = y + int((max_y - data[i]) * y_multiplier)

        fb.line(x_previous, y_previous, x_current, y_current)
        fb.line(x_previous, y_previous - 1, x_current, y_current - 1)


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