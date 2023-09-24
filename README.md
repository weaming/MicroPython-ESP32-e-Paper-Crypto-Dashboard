# MicroPython-ESP32-e-Paper-Crypto-Display

Driver for 7.5 inch e-Paper display on ESP32 with MicroPython, for Crypto Price Tracker.

## Todo list:

- [x] Display white/black/yellow colors
- [x] Price Tracker from DexScreener/[hope.money](https://hope.money)
- [x] Deep Sleep
- [ ] WiFi Manager

## Playing

1. Install pymakr extension in VSCode
2. In pymakr pannel:
    1. Connect device
    2. Sync project to device
    3. Create terminal:
        1. Run `import machine as m; m.reset()` to restart