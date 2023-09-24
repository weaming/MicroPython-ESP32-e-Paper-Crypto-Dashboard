import device
from test import test_display
import coin_pricer as dashboard

device.connect_device()
device.print_mem()

device.wifi = True
if device.wifi:
    device.connect_wifi()
    device.calibration_time()


# test_display(device.epd)
dashboard.display(device.epd)
