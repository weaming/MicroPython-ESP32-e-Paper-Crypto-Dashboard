# import framebuf  # https://docs.micropython.org/en/latest/library/framebuf.html#framebuf.FrameBuffer
import utime
import network

import framebuf2
import urequests as requests
import device
from epaper7in5b import EPD, white, black, EPD_WIDTH as w, EPD_HEIGHT as h


def get_symbol_price():
    """
    {
        "hope_price_list": [
            [
                0.459488902720515,
                1695556800
            ],
            [
                0.45924640220177904,
                1695558717
            ]
        ],
        "btc_index_price": 26586.176666666666,
        "eth_index_price": 1592.9533333333336,
        "hope_index_price": 0.45924640220177904,
        "k": 1.080180484347501e-05
    }
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.request('GET', 'https://hope.money/hope-index-stage-2?period=3600', headers=headers)
        response = res.json()
        btc_price = response['btc_index_price']
        eth_price = response['eth_index_price']
        hope_price = response['hope_index_price']
        ts = response['hope_price_list'][1][1]  # seconds
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
        resp = requests.request('GET', f'https://api.dexscreener.com/latest/dex/pairs/{chain_id}/{pair_address}')
        lt_last_price = resp.json()['pair']['priceUsd']
        return lt_last_price
    except Exception as e:
        print(e)
        return '--'


def get_vars() -> dict:
    btc, eth, hope, ts = get_symbol_price()  # 延迟比 dexscreener 更低
    lt = get_lt_price()
    return dict(ts=ts, btc=btc, eth=eth, hope=hope, lt=lt)


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
    # 如esp32模块的rtc初始时钟是 2000-01-01 00:00:00 UTC = 946684800 secs
    # UTC+8 0 点需要加上 28800
    # 所以1970年时间戳需要转换为 RTC UTC+8 时间戳: 1686140724 - 946656000
    year, month, day, hours, minutes, seconds, weekday, yearday = utime.localtime(ts - 946656000)
    return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}".format(year, month, day, hours, minutes)


def utime_secs_to_epoch_secs(ts):
    return ts + 946684800


X_LEFT = 30
Y_TOP = 20
Y_BODY = Y_TOP + 100
BODY_LEFT = X_LEFT + 120
BODY_LINE_HEIGHT = 55
FONT_TITLE = 8
FONT_BODY = 5


def display(epd: EPD):
    data = get_vars()
    ts_str = ts_as_datetime_str(data['ts'])
    print(ts_str, data)

    epd.clear_screen()
    fb = framebuf2.FrameBuffer(device.buf, w, h, framebuf2.MHMSB)

    fb.fill(white)
    fb.text('Crypto!', 400, Y_TOP, black, size=FONT_TITLE)
    offset = 150
    fb.text(f'{data["btc"]}', BODY_LEFT + offset, Y_BODY + BODY_LINE_HEIGHT, black, size=FONT_BODY)
    fb.text(f'{data["eth"]}', BODY_LEFT + offset, Y_BODY + BODY_LINE_HEIGHT * 2, black, size=FONT_BODY)
    fb.text(f'{data["hope"]}', BODY_LEFT + offset, Y_BODY + BODY_LINE_HEIGHT * 3, black, size=FONT_BODY)
    fb.text(f'{data["lt"]}', BODY_LEFT + offset, Y_BODY + BODY_LINE_HEIGHT * 4, black, size=FONT_BODY)
    epd.write_yellow_layer(device.buf, False)

    fb.fill(white)
    fb.text('Hello', X_LEFT + 50, Y_TOP, black, size=FONT_TITLE)
    fb.rect(0, Y_TOP + 80, w, 2, black, fill=True)
    fb.text(ts_str, X_LEFT + 200, Y_TOP + 90, black, size=3)
    fb.text(f' BTC: ', BODY_LEFT, Y_BODY + BODY_LINE_HEIGHT, black, size=FONT_BODY)
    fb.text(f' ETH: ', BODY_LEFT, Y_BODY + BODY_LINE_HEIGHT * 2, black, size=FONT_BODY)
    fb.text(f'HOPE: ', BODY_LEFT, Y_BODY + BODY_LINE_HEIGHT * 3, black, size=FONT_BODY)
    fb.text(f'  LT: ', BODY_LEFT, Y_BODY + BODY_LINE_HEIGHT * 4, black, size=FONT_BODY)

    epd.write_black_layer(device.buf, True)


def prepare():
    device.connect_device()
    device.print_mem()

    if device.connect_wifi_if_not():
        device.calibrate_time()


def entry():
    if device.connect_wifi_if_not():
        device.calibrate_time()
    display(device.epd)
