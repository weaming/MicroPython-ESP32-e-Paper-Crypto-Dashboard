"""
copy from https://github.com/mcauser/micropython-waveshare-epaper/blob/master/epaper7in5b.py

MicroPython Waveshare 7.5" Black/White/Red GDEY075Z08 e-paper display driver
MicroPython Waveshare 7.5" Black/White/Yellow GDEW075C64 e-paper display driver
"""

from micropython import const
from utime import sleep_ms
import ustruct

# Display resolution
# https://www.e-paper-display.cn/products_detail/productId=474.html
EPD_WIDTH = const(800)
EPD_HEIGHT = const(480)

# Display commands, copy from https://github.com/zhufucdev/gdey075z08_driver/blob/main/src/gdey075z08_driver/driver.py
PANEL_SETTING = 0x00
POWER_SETTING = 0x01
POWER_OFF = 0x02
POWER_OFF_SEQUENCE_SETTING = 0x03
POWER_ON = 0x04
POWER_ON_MEASURE = 0x05
BOOSTER_SOFT_START = 0x06
DEEP_SLEEP = 0x07
DATA_START_TRANSMISSION_1 = 0x10
DATA_STOP = 0x11
DISPLAY_REFRESH = 0x12
DATA_START_TRANSMISSION_2 = 0x13
LUT_FOR_VCOM = 0x20
LUT_BLUE = 0x21
LUT_WHITE = 0x22
LUT_GRAY_1 = 0x23
LUT_GRAY_2 = 0x24
LUT_RED_0 = 0x25
LUT_RED_1 = 0x26
LUT_RED_2 = 0x27
LUT_RED_3 = 0x28
LUT_XON = 0x29
PLL_CONTROL = 0x30
TEMPERATURE_SENSOR_COMMAND = 0x40
TEMPERATURE_CALIBRATION = 0x41
TEMPERATURE_SENSOR_WRITE = 0x42
TEMPERATURE_SENSOR_READ = 0x43
VCOM_AND_DATA_INTERVAL_SETTING = 0x50
LOW_POWER_DETECTION = 0x51
TCON_SETTING = 0x60
TCON_RESOLUTION = 0x61
SPI_FLASH_CONTROL = 0x65
REVISION = 0x70
GET_STATUS = 0x71
AUTO_MEASUREMENT_VCOM = 0x80
READ_VCOM_VALUE = 0x81
VCM_DC_SETTING = 0x82
FLASH_MODE = const(0xE5)

BUSY = const(0)  # 0=busy, 1=idle


class EPD:
    def __init__(self, spi, cs, dc, rst, busy):
        self.spi = spi
        self.cs = cs
        self.dc = dc
        self.rst = rst
        self.busy = busy
        self.cs.init(self.cs.OUT, value=1)
        self.dc.init(self.dc.OUT, value=0)
        self.rst.init(self.rst.OUT, value=0)
        self.busy.init(self.busy.IN)
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT

    def _command(self, command, data=None):
        self.dc(0)
        self.cs(0)
        print('cmd', command, data)
        self.spi.write(bytearray([command]))
        self.cs(1)
        if data is not None:
            self._data(data)

    def _data(self, data):
        self.dc(1)
        self.cs(0)
        if isinstance(data, int):
            data = data.to_bytes(1, 'big')
        self.spi.write(data)
        self.cs(1)

    def init(self):
        print('init...')
        self.reset()
        self._command(POWER_SETTING, b'\x37\x00')
        self._command(PANEL_SETTING, b'\xCF\x08')
        self._command(BOOSTER_SOFT_START, b'\xC7\xCC\x28')
        self._command(POWER_ON)
        self.wait_until_idle()
        self._command(PLL_CONTROL, b'\x3C')
        self._command(TEMPERATURE_CALIBRATION, b'\x00')
        self._command(VCOM_AND_DATA_INTERVAL_SETTING, b'\x77')
        self._command(TCON_SETTING, b'\x22')
        self._command(TCON_RESOLUTION, ustruct.pack(">HH", EPD_WIDTH, EPD_HEIGHT))
        self._command(VCM_DC_SETTING, b'\x1E')  # decide by LUT file
        self._command(FLASH_MODE, b'\x03')
        print('inited.')

    def wait_until_idle(self):
        ms = 100
        ms_max = 3000
        while self.busy.value() == BUSY:
            print('wait for idle')
            if ms < ms_max:
                ms *= 2
            sleep_ms(min(ms, ms_max))

    def reset(self):
        self.rst(0)
        sleep_ms(200)
        self.rst(1)
        sleep_ms(200)

    # to wake call reset() or init()
    def sleep(self):
        self._command(POWER_OFF)
        self.wait_until_idle()
        self._command(DEEP_SLEEP, b'\xA5')

    def clear_frame(self, buf_white, buf_yellow=None):
        for i in range(int(self.width * self.height / 8)):
            buf_white[i] = 0xFF
            if buf_yellow is not None:
                buf_yellow[i] = 0xFF

    def display_frame(self, buf_white, buf_yellow=None):
        print('display_frame...')
        if buf_white is not None:
            print('draw white layer...')
            self._command(DATA_START_TRANSMISSION_1)
            sleep_ms(100)
            for i in range(0, self.width * self.height / 8):
                temp = 0x00
                # 0xC0 = 0b11000000
                # 0x80 = 0b10000000
                for bit in range(0, 4):
                    if buf_white[i] & (0x80 >> bit) != 0:
                        temp |= 0xC0 >> (bit * 2)
                self._data(temp)

                temp = 0x00
                for bit in range(4, 8):
                    if buf_white[i] & (0x80 >> bit) != 0:
                        temp |= 0xC0 >> ((bit - 4) * 2)
                self._data(temp)
            sleep_ms(100)
        elif buf_yellow is not None:
            print('clear white layer...')
            self._command(DATA_START_TRANSMISSION_1)
            sleep_ms(100)
            for i in range(0, self.width * self.height / 8):
                self._data(0xFF)  # white
            sleep_ms(100)

        if buf_yellow is not None:
            print('draw yellow layer...')
            self._command(DATA_START_TRANSMISSION_2)
            sleep_ms(100)
            for i in range(0, self.width * self.height / 8):
                self._data(buf_yellow[i])
            sleep_ms(100)
        elif buf_white is not None:
            print('clear yellow layer...')
            self._command(DATA_START_TRANSMISSION_2)
            sleep_ms(100)
            for i in range(0, self.width * self.height / 8):
                self._data(0xFF)  # white
            sleep_ms(100)

        print('display refresh ...')
        self._command(DISPLAY_REFRESH)
        self.wait_until_idle()

    def display_frame_v2(self, buf_white, buf_yellow=None):
        print('display_frame_v2...')

        def write_buffer(buf):
            for data in buf:
                self._data(data)

        self._command(DATA_START_TRANSMISSION_1)
        write_buffer(buf_white)

        if buf_yellow is not None:
            self._command(DATA_START_TRANSMISSION_2)
            write_buffer(buf_yellow)

        print('display refresh ...')
        self._command(DISPLAY_REFRESH)
        self.wait_until_idle()
