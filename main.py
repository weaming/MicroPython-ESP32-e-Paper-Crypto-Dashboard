import device

device.connect_device()
# device.connect_wifi()

import coin_pricer as dashboard

dashboard.display(device.epd)
