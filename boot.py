# This file is executed on every boot (including wake-boot from deepsleep)
print('boot...')

from price_tracker import prepare, entry
import sleepscheduler as sl


def on_cold_boot():
    print('on_cold_boot...')
    sl.schedule_immediately(__name__, entry, 60 * 5)


prepare()
sl.init()
sl.schedule_on_cold_boot(on_cold_boot)
sl.run_forever()
