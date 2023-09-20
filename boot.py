# This file is executed on every boot (including wake-boot from deepsleep)

# import esp
# import webrepl
# esp.osdebug(None)
# webrepl.start()

import sleepscheduler as sl
import coin_price_dashboard

sl.schedule_on_cold_boot(coin_price_dashboard.init_on_cold_boot)
sl.run_forever()
