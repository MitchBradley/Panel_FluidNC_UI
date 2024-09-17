# FluidNC Tablet UI for 7" ESP32 Display

## Resources

(Thonny)[https://thonny.org/]

(MicroPython Font files)[https://github.com/uraich/lv_mpy_examples_v8/tree/main/assets/font]

(Elecrow MicroPython builds)[https://www.elecrow.com/wiki/image/9/9e/MicroPython_7inch.zip]

The A version in MicroPython_7inch/firmware/firmware-7.0-A.bin includes tft_config.py and gt911.py as frozen modules.  The B version in MicroPython_7inch/driver+firmware/firmware-7.0-B.bin omits those driver modules, in favor of the versions in that directory - so you can change the config if you want.

(Newer MicroPython build)[https://forum.elecrow.com/uploads/018/QSXRZ8J45Z5G.zip]

Install micropython.bin at 0x10000
partition-table.bin at 0x8000
bootloader.bin at 0

(Adafruit ESPTool)[https://adafruit-esptool.glitch.me]
