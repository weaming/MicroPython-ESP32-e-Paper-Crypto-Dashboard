# This file is executed on every boot (including wake-boot from deepsleep)
print('boot...')

"""
import sleepscheduler as sl
import coin_pricer as dashboard
from device import connect_wifi, calibration_time


def init_on_cold_boot(wifi=False):
    import sleepscheduler as sl

    print('init_on_cold_boot...')
    if wifi:
        connect_wifi()
        calibration_time()

    sl.schedule_immediately(__name__, dashboard.display, 60 * 5)


def bgtask():
    sl.init()
    sl.schedule_on_cold_boot(init_on_cold_boot)
    sl.run_forever()


bgtask()
"""
