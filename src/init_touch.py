from i2c import I2C
import gt911

I2C_BUS = I2C.Bus(
    host=1,
    scl=20,
    sda=19,
    freq=100000,
    use_locks=False
)

# Version 3 boards have a PCA9557 IO Expander chip to reset
# the touch panel.
import pca9557
import time
def reset_tp():
    pca = pca9557.PCA9557(I2C_BUS, 0x18)
    pca.setPolarity(0)    # All active high
    pca.setDirection(0)   # All out
    pca.output(0) # All pins low
    time.sleep_ms(20)
    pca.output(1) # Set IO0 high
    time.sleep_ms(100)
    pca.setDirection(2) # IO1 in

try:
    reset_tp()
except:
    pass

TOUCH_DEVICE = I2C.Device(
    I2C_BUS,
    dev_id=gt911.I2C_ADDR,
    reg_bits=gt911.BITS
)

indev = gt911.GT911(TOUCH_DEVICE)

_WIDTH = const(800)
_HEIGHT = const(480)

if indev.hw_size != (_WIDTH, _HEIGHT):
    print('setting display size to the touch controller')
    print('old size:', indev.hw_size)
    fc = indev.firmware_config
    fc.width = _WIDTH
    fc.height = _HEIGHT
    fc.save()
    print('new size:', indev.hw_size)
    del fc

indev.enable_input_priority()
