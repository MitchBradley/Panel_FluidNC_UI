import lv_utils
import tft_config
import gt911
from machine import Pin, I2C, WDT

_WIDTH = 800
_HEIGHH = 480

# tft drvier
tft = tft_config.config()

# touch drvier
i2c = I2C(1, scl=Pin(20), sda=Pin(19), freq=400000)
tp = gt911.GT911(i2c, width=_WIDTH, height=_HEIGHT)
tp.set_rotation(tp.ROTATION_INVERTED)
if not lv_utils.event_loop.is_running():
    event_loop=lv_utils.event_loop()
    print(event_loop.is_running())
_flush_cb = tft.flush

# create a display 0 buffer
_disp_buf = lv.disp_draw_buf_t()
_buf1 = bytearray(_WIDTH * 50)
_disp_buf.init(_buf1, None, len(_buf1) // lv.color_t.__SIZE__)

# register display driver
disp_drv = lv.disp_drv_t()
disp_drv.init()
disp_drv.draw_buf = _disp_buf
disp_drv.flush_cb = _flush_cb
disp_drv.hor_res = _WIDTH
disp_drv.ver_res = _HEIGHT
disp = disp_drv.register()
# disp_drv.user_data = {"swap": 0}
lv.disp_t.set_default(disp)

# touch driver init
indev_drv = lv.indev_drv_t()
indev_drv.init()
indev_drv.disp = disp
indev_drv.type = lv.INDEV_TYPE.POINTER
indev_drv.read_cb = tp.lvgl_read
indev_drv.register()
