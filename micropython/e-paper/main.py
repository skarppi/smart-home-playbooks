# This is your main script.

import epd3in7
import connection
import sensors
import uasyncio as asyncio
import time

from fb import Canvas
from fonts import sfpro40, sfpro50, font10
from state import temp, timestamp, temp_history, raw

epd = epd3in7.EPD(0)
fb = Canvas(epd.width, epd.height, epd.rotation)

w = epd.width
h = epd.height

winter = False

if winter:
    top = 120
    top_graph = False
    middle = 240
    middle_graph = False
    bottom = 360
    bottom_graph = True
else:
    top = 120
    top_graph = True
    middle = 280
    middle_graph = True
    bottom = 420
    bottom_graph = False


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
    fb.text('Kello', w - 140, 0, font10)

    # roof
    fb.line(10, 125, w // 2, 70)
    fb.line(w // 2, 70, w - 10, 125)
    fb.line(10, 125, 10, h - 10)
    fb.line(w - 10, 125, w - 10, h - 10)

    # upstairs
    fb.text_center('Ylakerta', top - 20, font10)
    #divider = top + 25 + (middle - top) / 2
    divider(top + 25 + (middle - top) / 2)

    # downstairs
    fb.text_center('Alakerta', middle - 20, font10)
    divider(middle + 25 + (bottom - middle) / 2)

    # cellar
    fb.text_center('Patteri', bottom - 20, font10)
    divider(h - 10)

    epd.display_1Gray(fb.render())


def partial():
    # Wake up the screen from sleep
    epd.reset()

    start = time.time()

    # Deep sleep forgets the previous buffer and partial refresh cannot know changes. Put back the old state.
    epd.display_1Gray(fb.render(), False)

    fb.clear(10, 20, w // 2 - 30, 40)
    fb.text(temp('takapiha', 1), 10, 20, sfpro40)

    fb.clear(w - 140, 20, 140, 40)
    fb.text(timestamp(), w - 140, 20, sfpro40)

    fb.clear(30, top, w - 60, 50)
    fb.text_center(temp('vintti', 1), top, sfpro50)
    if top_graph:
        fb.clear(20, top + 60, w - 40, 50)
        graph(temp_history('vintti'), 20, top + 60, w - 40, 50)

    fb.clear(30, middle, w - 60, 50)
    fb.text_center(temp('indoor', 1), middle, sfpro50)
    if middle_graph:
        fb.clear(20, middle + 60, w - 40, 50)
        graph(temp_history('indoor'), 20, middle + 60, w - 40, 50)

    fb.clear(30, bottom, w - 60, 50)
    fb.text_center(temp('pannu', 1), bottom, sfpro50)
    fb.text('/ {0}'.format(raw('pannu/command')), w - 50, 400, font10)

    if bottom_graph:
        fb.clear(20, bottom + 60, w - 40, 50)
        graph(temp_history('pannu'), 20, bottom + 60, w - 40, 50)

    epd.display_1Gray(fb.render())

    print('render in {0} seconds'.format(time.time() - start))

    epd.sleep()


def divider(y):
    fb.line(10, int(y), w - 10, int(y))


def graph(data, x, y, w, h):
    items = len(data)
    if items < 2:
        return

    width_per_point = (w - 50) // (items - 1)

    max_y = max(data)
    fb.text('{:.1f}'.format(max_y), x, y, font10)

    min_y = min(data)
    fb.text('{:.1f}'.format(min_y), x, y + h - 11, font10)

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
    asyncio.create_task(sensors.start())
    full()

    while True:
        partial()
        await asyncio.sleep(raw('indoor/refreshrate') * 60)

try:
    asyncio.run(main())
finally:
    print("EOF main.py")
    asyncio.new_event_loop()
