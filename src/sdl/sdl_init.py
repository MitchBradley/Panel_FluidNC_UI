from micropython import const  # NOQA

_WIDTH = const(800)
_HEIGHT = const(480)

_BUFFER_SIZE = _WIDTH * _HEIGHT * 2

import lcd_bus  # NOQA

bus = lcd_bus.SDLBus(flags=0)

buf1 = bus.allocate_framebuffer(_BUFFER_SIZE, 0)

import lvgl as lv  # NOQA
import sdl_display  # NOQA

lv.init()

display = sdl_display.SDLDisplay(
    data_bus=bus,
    display_width=_WIDTH,
    display_height=_HEIGHT,
    frame_buffer1=buf1,
    color_space=lv.COLOR_FORMAT.RGB565
)

display.init()

import sdl_pointer

mouse = sdl_pointer.SDLPointer()
