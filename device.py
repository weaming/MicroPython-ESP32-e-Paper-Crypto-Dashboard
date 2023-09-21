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
import utime
from machine import Pin, SPI
import epaper7in5b as epaper
from config import WIFI_SSID, WIFI_PASSWORD


# GxEPD2_3C<GxEPD2_750c_Z08, GxEPD2_750c_Z08::HEIGHT>
# display(GxEPD2_750c_Z08(/CS=5/ 5, /DC=/ 19, /RST=/ 16, /BUSY=/ 17));
# from gitee schema
cs = Pin(5)
dc = Pin(19)
rst = Pin(16)
busy = Pin(17)

# https://docs.singtown.com/micropython/zh/latest/esp32/esp32/quickref.html#id5
# same as gitee schema
miso = Pin(19)
mosi = Pin(23)
sck = Pin(18)
# from spec of GDEW075C64
# sck = Pin(13)
# cs = Pin(12)
# dc = Pin(11)
# rst = Pin(10)
# busy = Pin(9)

# ESP32 Driver Board 电子墨水屏无线网络驱动板
# https://www.waveshare.net/shop/e-Paper-ESP32-Driver-Board.htm
# miso = Pin(0)  # blank
# mosi = Pin(12)
# sck = Pin(15)
# cs = Pin(16)
# dc = Pin(11)
# rst = Pin(10)
# busy = Pin(9)

# k1 = Pin(35)
# k2 = Pin(32)
# k3 = Pin(34)

black = 0
white = 1
yellow = 2

# https://docs.micropython.org/en/latest/library/machine.SPI.html#machine.SPI.init
spi = SPI(2, baudrate=20000000, polarity=0, phase=0, sck=sck, miso=miso, mosi=mosi)
epd = epaper.EPD(spi, cs, dc, rst, busy)


def connect_device():
    epd.init()


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        print("connecting network...")
        wlan.active(True)
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            print(".", end="")
            utime.sleep(1)
    print('network config:', wlan.ifconfig())
