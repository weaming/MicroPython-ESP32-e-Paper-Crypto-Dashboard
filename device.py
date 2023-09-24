# https://gitee.com/corogoo/epaper-7.5-weather-station-plus
"""
https://zhuanlan.zhihu.com/p/57885639
总结常用的就是一根线、两根线、三根线、四根线、八根线:
一根线：单总线
两根线：I2C总线，CAN总线，485总线，USB等
三根线：RS232(常用连接三根线 TX RX GND）
四根线：SPI总线（SCK MISO MOSI CS）
八根线：网线（实际网线省掉4根，只用其中四根线也可以，速度慢一些，千兆网必须8根线）

https://randomnerdtutorials.com/esp32-spi-communication-arduino/
https://en.wikipedia.org/wiki/Serial_Peripheral_Interface

MISO: Master In Slave Out
MOSI: Master Out Slave In
SCK: Serial Clock
CS/SS: Chip Select (used to select the device when multiple peripherals are used on the same SPI bus)

On a slave-only device, like sensors, displays, and others, you may find a different terminology:

MISO may be labeled as SDO (Serial Data Out)
MOSI may be labeled as SDI (Serial Data In)


DC: Data/Command
RST: ReST
SCK: Serial ClocK
"""

import network
import ntptime
import utime
import gc
from machine import Pin, SPI
import epaper7in5b as epaper
from config import WIFI_SSID, WIFI_PASSWORD


# GxEPD2_3C<GxEPD2_750c_Z08, GxEPD2_750c_Z08::HEIGHT>
# display(GxEPD2_750c_Z08(/CS=5/ 5, /DC=/ 19, /RST=/ 16, /BUSY=/ 17));
# same as gitee schema
cs = Pin(5)
dc = Pin(19)
rst = Pin(16)
busy = Pin(17)

# https://docs.singtown.com/micropython/zh/latest/esp32/esp32/quickref.html#id5
# same as gitee schema
miso = Pin(19)
mosi = Pin(23)
sck = Pin(18)

# https://docs.micropython.org/en/latest/library/machine.SPI.html#machine.SPI.init
spi = SPI(2, baudrate=20000000, polarity=0, phase=0, sck=sck, miso=miso, mosi=mosi)
epd = epaper.EPD(spi, cs, dc, rst, busy)

# global shared flag
wifi = False
# global shared buf to save memory
buf = bytearray(epaper.EPD_WIDTH * epaper.EPD_HEIGHT // 8)


def connect_device():
    epd.init()


def print_mem():
    alloc = gc.mem_alloc()
    free = gc.mem_free()
    print(f'Memory: allocated {alloc} bytes, free {free} bytes, total {alloc+free} bytes')


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        print(f'connect the network with {WIFI_SSID}:{WIFI_PASSWORD} ', end='')
        wlan.active(True)
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            print(".", end="")
            utime.sleep(1)

    # IP address, netmask, gateway, DNS
    print('\nnetwork config:', wlan.ifconfig())


# the time is kept during deep sleep
def calibration_time():
    year, *_ = utime.localtime()
    if not str(year).startswith('202'):  # default is 2000-01-01 00:00:00
        # set the time from the network
        ntptime.host = 'ntp.aliyun.com'
        ntptime.NTP_DELTA = 3155644800  # 东八区 UTC+8偏移时间（秒）
        ntptime.settime()
        print("calibration_time to: {}".format(utime.localtime()))
