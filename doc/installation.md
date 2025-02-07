# FluidNC 7" Touch Display - Installation

![panel](./panel-fluidnc.png)

## Overview

Before taking your display into use, there are a couple of steps you need to perform. The steps are as follows:

- Assemble display and fluiddial module in the case you have selected/printed, connect module and display
- Upload firmware to the display
- Insert display module in FluidNC controller
- Connect the two modules using RJ12 cable
- Add uart sections to FluidNC configuration
- Restart FluidNC

Each step are described in detail below.

## Assembly



Assemble display and fluiddial module in the case you have selected

**Bart** to take picture of new module with cable


## Upload firmware to the Display

Can we use the same installer as when uploading firmware to FluidNC controller??

Describe steps...

## Insert display in FluidNC controller


## Connect modules using RJ12 cable


## Add uart sections to FluidNC configuration

FluidNC requires two new sections to be added to the configuration. Pin numbers for txd and rxd are determined by the controller board you have. 

### Configuration template

```
uart1:
  txd_pin: gpio.25    <-- see table
  rxd_pin: gpio.27    <-- see table
  rts_pin: NO_PIN
  cts_pin: NO_PIN
  baud: 1000000
  mode: 8N1

uart_channel1:
  report_interval_ms: 75
  uart_num: 1 
  message_level: info
```
<br>

| Board | Pin description |
|---|---|
| 6x | txd_pin: gpio.25 <br> rxd_pin: gpio.27 |
| 6 Pack <br> External stepper <br> socket #1 | txd_pin: gpio.26 <br> rxd_pin: gpio.4 |
| 6 Pack <br> External stepper <br> socket #2 | txd_pin: gpio.14 <br> rxd_pin: gpio.13 |
| FluidNC Pen <br> Laser TMC2209 v2 |  txd_pin: gpio.4 <br> rxd_pin: gpio.15 |



