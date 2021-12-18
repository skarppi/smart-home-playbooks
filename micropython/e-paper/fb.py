
import framebuf

black = 0
white = 1

# Display orientation
ROTATE_0                                    = 0
ROTATE_90                                   = 1
ROTATE_180                                  = 2
ROTATE_270                                  = 3

class Canvas:

    def __init__(self, orientation, EPD_WIDTH, EPD_HEIGHT):
        self.EPD_WIDTH = EPD_WIDTH
        self.EPD_HEIGHT = EPD_HEIGHT
        self.rotate(orientation)

        self.buf = bytearray(EPD_WIDTH * EPD_HEIGHT // 8)
        self.fb = framebuf.FrameBuffer(self.buf, EPD_WIDTH, EPD_HEIGHT, framebuf.MONO_HLSB)

        #self.buf_output = bytearray(EPD_WIDTH * EPD_HEIGHT // 8)

        self.clear()

    def rotate(self, rotate):
        if (rotate == ROTATE_0):
            self.rotate = ROTATE_0
            self.width = self.EPD_WIDTH
            self.height = self.EPD_HEIGHT
        elif (rotate == ROTATE_90):
            self.rotate = ROTATE_90
            self.width = self.EPD_HEIGHT
            self.height = self.EPD_WIDTH
        elif (rotate == ROTATE_180):
            self.rotate = ROTATE_180
            self.width = self.EPD_WIDTH
            self.height = self.EPD_HEIGHT
        elif (rotate == ROTATE_270):
            self.rotate = ROTATE_270
            self.width = self.EPD_HEIGHT
            self.height = self.EPD_WIDTH

    def text(self, str, x, y):
        self.fb.text(str, x, y, black)

    # this could be useful as a new method in FrameBuffer
    def text_wrap(self, str, x, y, w, h, border=black):
        # optional box border
        if border is not None:
            self.fb.rect(x, y, w, h, border)
        cols = w // 8
        # for each row
        j = 0
        for i in range(0, len(str), cols):
            # draw as many chars fit on the line
            self.text(str[i:i+cols], x, y + j)
            j += 8
            # dont overflow text outside the box
            if j >= h:
                break


    def clear(self):
        self.fb.fill(white)

    def render(self):
        return self.buf

        # for y in range(self.height):
        #     for x in range(self.width):
        #         newx = y
        #         newy = self.height - x - 1
        #         # if pixels[x, y] == 0:
        #         self.buf_output[int((newx + newy*self.height) / 8)] = self.buf[(x + y*self.height) // 8]

        # return self.buf_output

        # Move frame buffer bytes to e-paper buffer to match e-paper bytes oranisation.
        # That is landscape mode to portrait mode.
        # x=0; y=-1; n=0; m=0

        # rows = self.width // 8
        # cols = self.height // 8

        # for i in range(0, cols):
        #     for j in range(0, self.width):
        #         m = (n-x)+(n-y) * (cols-1)
        #         self.buf_output[m] = self.buf[n]
        #         n += 1
        #     x = n+i+1
        #     y = n-1
        
        return self.buf_output
