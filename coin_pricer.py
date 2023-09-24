# import framebuf  # https://docs.micropython.org/en/latest/library/framebuf.html#framebuf.FrameBuffer
import utime

import framebuf2
import urequests as requests
from epaper7in5b import EPD
from device import white, black, yellow, connect_wifi, calibration_time


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


# TODO
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


def display(epd: EPD):
    w, h = epd.width, epd.height
    buf = bytearray(w * h // 8)
    fb = framebuf2.FrameBuffer(buf, w, h, framebuf2.MHMSB)
    fb.rotation = 0  # 调整显示的方向，可以在0/1/2/3之间选择

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

    # fb.print()
    epd.display_frame(buf)


def init_on_cold_boot(wifi=False):
    import sleepscheduler as sl

    print('init_on_cold_boot...')
    if wifi:
        connect_wifi()
        calibration_time()  # the time is kept during deep sleep

    sl.schedule_immediately(__name__, display, 60 * 5)
