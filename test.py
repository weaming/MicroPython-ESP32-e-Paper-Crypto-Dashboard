import framebuf2
from epaper7in5b import EPD, EPD_WIDTH as w, EPD_HEIGHT as h, white, black, yellow
from device import buf


def test_display(epd: EPD):
    epd.clear_screen()

    fb = framebuf2.FrameBuffer(buf, w, h, framebuf2.MHMSB)
    fb.fill(white)
    fb.text('hello', 60, 30, black, size=10)
    epd.write_black_layer(buf, False)

    fb.fill(white)
    fb.text('BTC', 60, 120, yellow, size=20)
    epd.write_yellow_layer(buf, True)
