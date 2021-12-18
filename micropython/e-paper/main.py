# This is your main script.

import epd3in7
from fb import Canvas

epd = epd3in7.EPD()
print("init and Clear")
epd.init(0)
epd.Clear(0xFF, 0)

# epd.display_1Gray(image)

fb = Canvas(0, epd3in7.EPD_WIDTH, epd3in7.EPD_HEIGHT)

fb.text('Hello World', 30, 4)
# fb.pixel(30, 10, black)
# fb.hline(30, 30, 10, black)
# fb.vline(30, 50, 10, black)
# fb.line(30, 70, 40, 80, black)
# fb.rect(30, 90, 10, 10, black)
# fb.fill_rect(30, 110, 10, 10, black)
# for row in range(0,36):
# 	fb.text(str(row), 0, row*8)
# fb.text('Line 36', 0, 288)

# fb.text('Line 36', 0, 350)

epd.display_1Gray(fb.render())

# fb.clear()
# # display as much as this as fits in the box
# str = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam vel neque in elit tristique vulputate at et dui. Maecenas nec felis lectus. Pellentesque sit amet facilisis dui. Maecenas ac arcu euismod, tempor massa quis, ultricies est.'

# # draw text box 1
# # box position and dimensions
# print('Box 1')
# bw = 112 #  = 14 cols
# bh = 112 #  = 14 rows (196 chars in total)
# fb.text_wrap(str, 8, 8, bw, bh)
# epd.display_1Gray(fb.render())

epd.sleep()

# # draw text box 2
# print('Box 2 & 3')
# bw = epd.width # 128 = 16 cols
# bh = 6 * 8 # 48 = 6 rows (96 chars in total)
# fb.text_wrap(str, 0, 128, bw, bh)

# # draw text box 3
# bw = epd.width//2 # 64 = 8 cols
# bh = 8 * 8 # 64 = 8 rows (64 chars in total)
# fb.text_wrap(str, 0, 184, bw, bh, None)
# epd.display_1Gray(fb.render())

