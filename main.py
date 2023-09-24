import device
import framebuf2
from device import white, black, yellow
from epaper7in5b import EPD

device.connect_device()
device.print_mem()
# device.connect_wifi()


def display_test(epd: EPD):
    w, h = epd.width, epd.height
    buf = bytearray(w * h // 8)
    epd.clear_frame(buf)

    fb = framebuf2.FrameBuffer(buf, w, h, framebuf2.MHMSB)
    fb.rotation = 0
    fb.fill(white)
    fb.text('hello', 60, 10, black, size=3)
    epd.display_frame(buf)


display_test(device.epd)

# import coin_pricer as dashboard
# dashboard.display(device.epd)
