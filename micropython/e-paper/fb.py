
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

    def __init__(self, EPD_WIDTH, EPD_HEIGHT):
        self.EPD_WIDTH = EPD_WIDTH
        self.EPD_HEIGHT = EPD_HEIGHT
        self.width = self.EPD_WIDTH
        self.height = self.EPD_HEIGHT

        gc.collect()  # Precaution before instantiating framebuf

        self.buf = bytearray(EPD_WIDTH * EPD_HEIGHT // 8)
        self.fb = DummyDisplay(self.buf, EPD_WIDTH, EPD_HEIGHT, framebuf.MONO_HLSB)

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
        x = (self.EPD_WIDTH - len) // 2

        writer.Writer.set_textpos(self.fb, y, x)
        wri.printstring(str, True)

    def clear(self, x = None, y = None, w = None, h = None):
        if x == None or y == None or w == None or h == None:
            self.fb.fill(white)
        else:
            self.fb.fill_rect(x, y, w, h, white)
            
    def render(self):
        return self.buf