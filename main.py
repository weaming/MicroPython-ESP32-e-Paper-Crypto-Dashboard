import device
import framebuf2
from epaper7in5b import EPD, white, black, yellow

device.connect_device()
device.print_mem()
# device.connect_wifi()


def display_test(epd: EPD):
    w, h = epd.width, epd.height
    buf = bytearray(w * h // 8)
    # buf = bytearray(w * h // 8 // 2 * 3)  # for 3 colors
    # epd.clear_frame(buf)

    epd.clear_screen()

    fb = framebuf2.FrameBuffer(buf, w, h, framebuf2.MHMSB)
    fb.fill(white)
    fb.text('hello', 60, 10, black, size=3)
    epd.write_white_layer(buf, False)

    fb.fill(white)
    fb.text('world', 60, 60, yellow, size=3)
    epd.write_yellow_layer(buf, True)


display_test(device.epd)

# import coin_pricer as dashboard
# dashboard.display(device.epd)
