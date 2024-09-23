# Screen and touch setup for Elecrow "CrowPanel 7"  800x480 display
# https://www.elecrow.com/wiki/esp32-display-702727-intelligent-touch-screen-wi-fi26ble-800480-hmi-display.html
# It is a 7 inch touchscreen panel that uses EK9716BD3 as the display driver
# and GT911 for the touch interface. The module include an ESP32-S3-WROOM-1-N4R8
# with 4 MiB of Quad SPI FLASH and 8 MiB of Octal SPI PSRAM.

from micropython import const
import lcd_bus
import lvgl as lv
import rgb_display
from i2c import I2C
import gt911

_WIDTH = const(800)
_HEIGHT = const(480)
_BUFFER_SIZE = const(768000)  # width * height * 2

bus = lcd_bus.RGBBus(
    hsync=39,
    vsync=40,
    de=41,
    pclk=0,
    data0=15,
    data1=7,
    data2=6,
    data3=5,
    data4=4,
    data5=9,
    data6=46,
    data7=3,
    data8=8,
    data9=16,
    data10=1,
    data11=14,
    data12=21,
    data13=47,
    data14=48,
    data15=45,
    freq=12000000, # The display creeps if this is too fast
    hsync_idle_low=False,
    hsync_front_porch = 40,
    hsync_pulse_width = 48,
    hsync_back_porch  = 40,
    vsync_idle_low=False,
    vsync_front_porch = 1,
    vsync_pulse_width = 31,
    vsync_back_porch  = 13,
    de_idle_high=False,
    pclk_idle_high=False,
    pclk_active_low=1,
    disp = -1,
)

buf1 = bus.allocate_framebuffer(_BUFFER_SIZE, lcd_bus.MEMORY_SPIRAM)
buf2 = bus.allocate_framebuffer(_BUFFER_SIZE, lcd_bus.MEMORY_SPIRAM)

display = rgb_display.RGBDisplay(
    data_bus=bus,
    display_width=_WIDTH,
    display_height=_HEIGHT,
    frame_buffer1=buf1,
    frame_buffer2=buf2,
    backlight_pin=2,
    backlight_on_state=rgb_display.STATE_PWM,
    color_space=lv.COLOR_FORMAT.RGB565,
    rgb565_byte_swap=False
)

display.set_power(True)
display.init()
display.set_backlight(100)
# display.set_rotation(lv.DISPLAY_ROTATION._90)

# For reference, the I2C IRQ is on pin 38
I2C_BUS = I2C.Bus(
    host=1,
    scl=20,
    sda=19,
    freq=400000,
    use_locks=False
)

TOUCH_DEVICE = I2C.Device(
    I2C_BUS,
    dev_id=gt911.I2C_ADDR,
    reg_bits=gt911.BITS
)

indev = gt911.GT911(TOUCH_DEVICE)
