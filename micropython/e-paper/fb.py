
import framebuf
import gc
from writer import writer

black = 0
white = 1
class DummyDisplay(framebuf.FrameBuffer):
    def __init__(self, buffer, width, height, format):
        self.height = height
        self.width = width
        self.buffer = buffer
        self.format = format
        super().__init__(buffer, width, height, format)

class Canvas:

    def __init__(self, EPD_WIDTH, EPD_HEIGHT, rotation):
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT

        gc.collect()  # Precaution before instantiating framebuf

        self.buf = bytearray(EPD_WIDTH * EPD_HEIGHT // 8)

        if rotation == 0 or rotation == 180:
            format = framebuf.MONO_HLSB
        elif rotation == 90 or rotation == 270:
            format = framebuf.MONO_VLSB

        self.fb = DummyDisplay(self.buf, EPD_WIDTH, EPD_HEIGHT, format)

        self.clear()

    def line(self, x1, y1, x2, y2):
        self.fb.line(x1, y1, x2, y2, black)

    def rect(self, x, y, w, h):
        self.fb.rect(x, y, w, h, black)

    def text(self, str, x, y, font):
        wri = writer.Writer(self.fb, font, False)

        writer.Writer.set_textpos(self.fb, y, x)
        wri.printstring(str, True)

    def text_center(self, str, y, font):
        print(str)

        wri = writer.Writer(self.fb, font, False)
        
        len = wri.stringlen(str)
        x = (self.width - len) // 2

        writer.Writer.set_textpos(self.fb, y, x)
        wri.printstring(str, True)

    def clear(self, x = None, y = None, w = None, h = None):
        if x == None or y == None or w == None or h == None:
            self.fb.fill(white)
        else:
            self.fb.fill_rect(x, y, w, h, white)
            
    def render(self):
        return self.buf