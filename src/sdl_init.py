import SDL

SDL.init(w=WIDTH,h=HEIGHT)
_flush_cb = SDL.monitor_flush
# import fs_driver
# Register SDL display driver.
_disp_buf = lv.disp_draw_buf_t()
buf1 = bytearray(WIDTH*10)
_disp_buf.init(_buf1, None, len(_buf1)//4)
# register display driver
disp_drv = lv.disp_drv_t()
disp_drv.init()
disp_drv.draw_buf = _disp_buf
disp_drv.flush_cb = _flush_cb
disp_drv.hor_res = WIDTH
disp_drv.ver_res = HEIGHT
disp_drv.register()

# Regsiter SDL mouse driver
indev_drv = lv.indev_drv_t()
indev_drv.init()
indev_drv.type = lv.INDEV_TYPE.POINTER
indev_drv.read_cb = SDL.mouse_read
indev_drv.register()
