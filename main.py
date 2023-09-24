import device
import framebuf2
from epaper7in5b import EPD, EPD_WIDTH as w, EPD_HEIGHT as h, white, black, yellow

device.connect_device()
device.print_mem()
# device.connect_wifi()

# global shared buf to save memory
buf = bytearray(w * h // 8)


def display_test(epd: EPD):
    epd.clear_screen()

    fb = framebuf2.FrameBuffer(buf, w, h, framebuf2.MHMSB)
    fb.fill(white)
    fb.text('hello', 60, 30, black, size=10)
    epd.write_white_layer(buf, False)

    fb.fill(white)
    fb.text('BTC', 60, 120, yellow, size=20)
    epd.write_yellow_layer(buf, True)


display_test(device.epd)

# import coin_pricer as dashboard
# dashboard.display(device.epd)
