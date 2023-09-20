import sys
import ntptime
import utime
import network
import urequests as requests

from machine import Pin, SPI
import newframebuf
import framebuf
import epaper7in5b as epaper

import sleepscheduler as sl
from config import WIFI_SSID, WIFI_PASSWORD, SCREEN_WIDTH as w, SCREEN_HEIGHT as h

sys.path.append('.')

"""
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

# v0
miso = Pin(0)
mosi = Pin(19)
sck = Pin(18)
cs = Pin(12)
dc = Pin(0)
rst = Pin(17)
busy = Pin(32)

# HSPI on ESP32
miso = Pin(12)
mosi = Pin(13)
sck = Pin(14)
cs = Pin(15)

# VSPI on ESP32
miso = Pin(19)
mosi = Pin(23)
sck = Pin(18)
cs = Pin(5)  # or 33 ?

dc = Pin(32)
rst = Pin(19)
busy = Pin(35)

# GDEY075Z08
sck = Pin(13)
dc = Pin(11)
cs = Pin(12)
rst = Pin(10)
busy = Pin(9)

# https://docs.micropython.org/en/latest/library/machine.SPI.html#machine.SPI.init
spi = SPI(2, baudrate=20000000, polarity=0, phase=0, sck=sck, miso=miso, mosi=mosi)

e = epaper.EPD(spi, cs, dc, rst, busy)
e.init()

black = 0
white = 1
yellow = 2


def get_symbol_price():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.request('GET', 'https://hope.money/hope-index-stage-2?period=3600', headers=headers)
        """
        {
        "hope_price_list": [
            [
            0.4925987029447829,
            1686139200
            ],
            [
            0.49105454893639217,
            1686140724
            ]
        ],
        "btc_index_price": 26801.25,
        "eth_index_price": 1865.9166666666667,
        "hope_index_price": 0.49105454893639217,
        "k": 0.00001080180484347501
        }
        """
        response = res.json()
        btc_price = response['btc_index_price']
        eth_price = response['eth_index_price']
        hope_price = response['hope_index_price']
        ts = response['hope_price_list'][1][1]  # 1686140724
        return btc_price, eth_price, hope_price, ts
    except:
        return '--', '--', '--', 0


def get_lt_price():
    try:
        chain_id = 'ethereum'
        pair_address = '0xa9ad6a54459635a62e883dc99861c1a69cf2c5b3'  # LT / USDT
        # pair_address = '0x1c2ad915cd67284cdbc04507b11980797cf51b22'  # HOPE / USDT
        # pair_address = '0x11b815efb8f581194ae79006d24e0d814b7697f6'  # WETH / USDT
        # pair_address = '0x9db9e0e53058c89e5b94e29621a205198648425b'  # WBTC / USDT
        resp = requests.request(
            'GET', 'https://api.dexscreener.com/latest/dex/pairs/{}/{}'.format(chain_id, pair_address)
        )
        lt_last_price = resp.json()['pair']['priceUsd']
        return lt_last_price
    except:
        return '--'


def get_bgb_price():
    try:
        resp = requests.get("https://api.bitget.com/api/spot/v1/market/ticker?symbol=BGBUSDT_SPBL")
        last_price = resp.json()['data']['close']
        return last_price
    except:
        return '--'


def wifi_connect():
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        print("connecting to network")
        wlan.active(True)
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            print(".", end="")
            utime.sleep(1)
    print('network config:', wlan.ifconfig())


def get_vars() -> dict:
    btc, eth, hope, ts = get_symbol_price()
    lt = get_lt_price()
    # todo 上面两个接口可以整合为一个，可以都从dex screener上获取，但是需要考虑到HOPE的价格在dex screener可能有延迟
    bgb = get_bgb_price()

    return {}


def ts_as_datetime_str(ts):
    """
    utime.localtime([secs]):

    year includes the century (for example 2014).
    month is 1-12
    mday is 1-31
    hour is 0-23
    minute is 0-59
    second is 0-59
    weekday is 0-6 for Mon-Sun
    yearday is 1-366
    """
    # 这里需要的ts时间戳是以模块rtc时钟初始值以起点计算的秒数
    # 如esp32模块的rtc初始时钟是 2000年1月1日
    # 所以1970年时间戳 需要转换为 rtc时间戳: 1686140724 - 946656000
    year, month, day, hours, minutes, seconds, weekday, yearday = utime.localtime(ts - 946656000)
    return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}".format(year, month, day, hours, minutes)


buf = bytearray(w * h // 8)
fb = newframebuf.FrameBuffer(buf, h, w, newframebuf.MHMSB)
fb.rotation = 0  # 调整显示的方向，可以在0/1/2/3之间选择


def display():
    # wifi_connect()

    fb.fill(white)
    fb.text("hello", 60, 10, black, size=3)
    # fb.text(ts_as_datetime_str(1695230423), 60, 10, black, size=3)

    # data = get_vars()
    # fb.text('BTC: {}'.format(btc), 30, 60, black, size=3)
    # fb.text('ETH: {}'.format(eth), 30, 100, black, size=3)
    # fb.text('HOPE: {}'.format(hope), 30, 140, black, size=3)
    # fb.text('LT: {}'.format(lt), 30, 180, black, size=3)
    # fb.text('BGB: {}'.format(bgb), 30, 220, black, size=3)

    fb.rect(0, 40, w, 4, black, fill=True)  # line: (x, y, width, 1, color, fill=True)
    # fb.circle(50, 150, 10, black)

    e.display_frame(buf)


def calibration_time():
    year, *_ = utime.localtime()
    if not str(year).startswith('202'):  # default is 2000-01-01 00:00:00
        # set the time from the network
        ntptime.host = "ntp1.aliyun.com"
        ntptime.NTP_DELTA = 3155644800  # 东八区 UTC+8偏移时间（秒）
        ntptime.settime()
        print("calibration_time to: {}".format(utime.localtime()))


def init_on_cold_boot():
    print('init_on_cold_boot...')
    # wifi_connect()

    # the time is kept during deep sleep
    calibration_time()

    sl.schedule_immediately(__name__, display, 60 * 5)
