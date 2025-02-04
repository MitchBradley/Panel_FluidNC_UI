# FluidNC 7" Touch Display

![panel](doc/panel-fluidnc.png)

## Overview
Touch display for FluidNC that enables you to operate your machine independently without being connected to a PC, Mac etc.

The display is based on the tablet plugin from the FluidNC WebUI and adapted to run on the 7" display from Elecrow.

<br>

## Features



<br>

## Parts
The display is designed to use the same interface boards as the pendant, they offer protection from EMC/EMI without compromising update speed of the display. This also means you need a controller board that has a module socket for pendant interfaces.

### Display & interface boards
**Display:** Elecrow 7" touch display with a builtin ESP32, Crowpanel 7.0". You can get this with or without an acrylic case depending on your use case. See below for options regarding cases.
[Elecrow Crowpanel 7"](https://www.elecrow.com/esp32-display-7-inch-hmi-display-rgb-tft-lcd-touch-screen-support-lvgl.html)


**Interface boards:** Fluiddial display module and fluiddial wiring kit are sold separately, you need one of each.
https://www.elecrow.com/fluiddial-rj12-wiring-kit.html
https://www.elecrow.com/fluidnc-rj12-pendant-display-module.html

**RJ12 Cable:** To connect the two modules, you need a 6 pin cable with RJ12 connectors in both ends to connect the display with FluidNC. These can be sourced from multiple vendors, here an example from :
[Aliexpress](https://www.aliexpress.com/w/wholesale-rj12-cable-6p6c.html)

### FluidNC controller boards
Your FluidNC controller board must have a module socket for pendant interfaces. Below are examples of boards with module socket:

https://www.elecrow.com/6-pack-cnc-controller-for-external-stepper-drivers.html
https://www.elecrow.com/6x-cnc-controller-for-fluidnc.html
https://www.elecrow.com/4x-cnc-controller-integrated-esp32-and-tmc2209.html
https://www.elecrow.com/tmc2209-pen-laser-fluidnc-cnc-controller.html

For a full list of boards pls. check -> [Existing hardware on FluidNC Wiki](http://wiki.fluidnc.com/en/hardware/existing_hardware)


### Case
A couple of options exists, if you bought the acrylic case from Elecrow, then a stand might be option for you: [Thingiverse](https://www.thingiverse.com/thing:6859400)

Should you want a full case then this design could an option: [Link to Bart's case](http://unknown.link)

<br>

## Installation
**[Installation guide](doc/installation.md)**

## Usage
**[User guide](doc/usage.md)**



<br>
<br>
<br>

---

Updated: Feb. 2025

---


<!--




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

-->