import lvgl as lv
lv.init()
import fs_driver

WIDTH = 800
HEIGHT = 480

using_SDL = False

try:
    import SDL
    import utime as time
    using_SDL = True
    SDL.init(w=WIDTH,h=HEIGHT)
    flush_cb = SDL.monitor_flush
    # import fs_driver
    # Register SDL display driver.
    disp_buf = lv.disp_draw_buf_t()
    buf1 = bytearray(WIDTH*10)
    disp_buf.init(buf1, None, len(buf1)//4)
    # register display driver
    disp_drv = lv.disp_drv_t()
    disp_drv.init()
    disp_drv.draw_buf = disp_buf
    disp_drv.flush_cb = flush_cb
    disp_drv.hor_res = WIDTH
    disp_drv.ver_res = HEIGHT
    disp_drv.register()

    # Regsiter SDL mouse driver
    indev_drv = lv.indev_drv_t()
    indev_drv.init()
    indev_drv.type = lv.INDEV_TYPE.POINTER
    indev_drv.read_cb = SDL.mouse_read
    indev_drv.register()
except:
    import lv_utils
    import tft_config
    import time
    import gt911
    from machine import Pin, I2C, WDT
    # tft drvier
    tft = tft_config.config()
    # touch drvier
    i2c = I2C(1, scl=Pin(20), sda=Pin(19), freq=400000)
    tp = gt911.GT911(i2c, width=800, height=480)
    tp.set_rotation(tp.ROTATION_INVERTED)
    if not lv_utils.event_loop.is_running():
        event_loop=lv_utils.event_loop()
        print(event_loop.is_running())

    flush_cb = tft.flush
    # create a display 0 buffer
    disp_buf = lv.disp_draw_buf_t()
    buf1 = bytearray(WIDTH * 50)
    disp_buf.init(buf1, None, len(buf1) // lv.color_t.__SIZE__)
    # register display driver
    disp_drv = lv.disp_drv_t()
    disp_drv.init()
    disp_drv.draw_buf = disp_buf
    disp_drv.flush_cb = flush_cb
    disp_drv.hor_res = WIDTH
    disp_drv.ver_res = HEIGHT
    disp = disp_drv.register()
    # disp_drv.user_data = {"swap": 0}
    lv.disp_t.set_default(disp)

    # touch driver init
    indev_drv = lv.indev_drv_t()
    indev_drv.init()
    indev_drv.disp = disp
    indev_drv.type = lv.INDEV_TYPE.POINTER
    indev_drv.read_cb = tp.lvgl_read
    indev = indev_drv.register()

    def bye():
        WDT(timeout=1000)

# 1. Create a display screen. Will need to display the component added to the screen to display
screen = lv.obj()  # scr====> screen
fs_drv = lv.fs_drv_t()
fs_driver.fs_register(fs_drv, 'S')
f24 = lv.font_load("S:montserrat-24.fnt")
f28 = lv.font_load("S:montserrat-28.fnt")
screen = lv.scr_act()
screen.clean()
# Create screen
# screen = lv.obj()
# screen.set_size(800, 480)

screen.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
# Set style for screen, Part: lv.PART.MAIN, State: lv.STATE.DEFAULT.
MAINDEF = lv.PART.MAIN|lv.STATE.DEFAULT

screen.set_style_bg_opa(0, MAINDEF)

# Create screen_cont_run
def make_area(x, y, w, h, color):
    area = lv.obj(screen)
    area.set_pos(x, y)
    area.set_size(w, h)
    # area.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
    # area.set_style_border_width(0, MAINDEF)
    area.set_style_radius(0, MAINDEF)
    area.set_style_bg_color(lv.color_hex(color), MAINDEF)
    area.set_style_pad_all(0, MAINDEF)
    return area

screen_cont_run = make_area(0, 0, 800, 70, 0xc0c0ff)

def clicked_button_text(e, label, text):
    code = e.get_code()
    if (code == lv.EVENT.PRESSED):
        pass
        label.set_text(text)

def button_font(btn, size):
    # btn.set_style_text_font(test_font("montserratMedium", size), MAINDEF)
    pass

def button_bg(btn, color):
    btn.set_style_bg_color(lv.color_hex(color), MAINDEF)

def basic_style(obj, x, y, w, h, border, fontsize):
    obj.set_pos(x, y)
    obj.set_size(w, h)
    obj.set_style_border_width(border, MAINDEF)
    obj.set_style_radius(5, MAINDEF)
    obj.set_style_pad_all(0, MAINDEF)
    obj.set_style_bg_color(lv.color_hex(0xffffff), MAINDEF)
    # obj.set_style_text_font(lv.font_montserrat_16, MAINDEF)
    obj.set_style_text_font(f28, MAINDEF)
    obj.set_style_text_color(lv.color_hex(0x0), MAINDEF)
    obj.set_style_text_align(lv.TEXT_ALIGN.CENTER, MAINDEF)
    obj.set_style_border_color(lv.color_hex(0x0), MAINDEF)

def basic_button(parent, x, y, w, h, border, fontsize):
    btn = lv.btn(parent)
    basic_style(btn, x, y, w, h, border, fontsize)
    if not border:
       btn.set_style_bg_opa(0, MAINDEF)
       btn.set_style_shadow_width(0, MAINDEF)
    return btn

firsttime = True
def interior_text(parent, text):
    label = lv.label(parent)
    label.set_text(text)
    label.set_long_mode(lv.label.LONG.CLIP)
    label.align(lv.ALIGN.CENTER, 0, 0)
    return label

def make_button(text, parent, x, y, w, h, fontsize, cb=None):
    btn = basic_button(parent, x, y, w, h, 1, fontsize)
    label = interior_text(btn, text)
    label.set_width(lv.pct(100))
    if cb:
        btn.add_event_cb(cb, lv.EVENT.ALL, None)
    return label

from numpad import Numpad

def make_run_button(parent, x, y, text, color, clicked_text):
    btn = basic_button(parent, x, y, 160, 50, 1, 34)
    button_bg(btn, color)
    label = interior_text(btn, text)
    btn.add_event_cb(lambda e: clicked_button_text(e, label, clicked_text), lv.EVENT.ALL, None)
    return [btn, label]

btnStart = make_run_button(screen_cont_run, 238, 11, "Start", 0x6efe77, "Go")
btnStop = make_run_button(screen_cont_run, 406, 11, "Pause", 0xff521e, "Stop")

def make_dropdown(parent, x, y, w, h, name, items, fontsize, arrow):
    obj = lv.dropdown(parent) # screen_ddlist_menu
    obj.set_text(name)
    obj.set_options(items)
    if not arrow:
        obj.set_symbol(None)
    basic_style(obj, x, y, w, h, 1, fontsize)
    obj.set_style_pad_all(8, MAINDEF)
    # Checked style
    checked = lv.style_t()
    checked.init()
    checked.set_border_width(1)
    checked.set_border_color(lv.color_hex(0x0))
    checked.set_border_side(lv.BORDER_SIDE.FULL)
    checked.set_radius(5)
    checked.set_bg_color(lv.color_hex(0x00a1b5))
    obj.get_list().add_style(checked, lv.PART.SELECTED|lv.STATE.CHECKED)
    # Default style
    default = lv.style_t()
    default.init()
    default.set_max_height(480)
    default.set_text_color(lv.color_hex(0x0))
    # default.set_text_font(test_font("montserratMedium", 24))
    default.set_border_width(1)
    default.set_border_color(lv.color_hex(0xe1e6ee))
    default.set_border_side(lv.BORDER_SIDE.FULL)
    default.set_radius(5)
    default.set_bg_color(lv.color_hex(0xffffff))
    obj.get_list().add_style(default, MAINDEF)
    # Scrollbar style
    scrollbar = lv.style_t()
    scrollbar.init()
    scrollbar.set_radius(5)
    scrollbar.set_width(10)
    scrollbar.set_bg_color(lv.color_hex(0x00ff00))
    obj.get_list().add_style(scrollbar, lv.PART.SCROLLBAR|lv.STATE.DEFAULT)
    return obj

ddmenu = make_dropdown(screen_cont_run, 681, 11, 111, 50, 'Menu', "Jog\nHome\nProbe\nUnlock\nReset", 28, False)

def make_label(parent, x, y, w, h, text, fontsize):
    # invisible container
    field = basic_button(parent, x, y, w, h, 0, fontsize)
    label = interior_text(field, text)
    return label

state_name = make_label(screen_cont_run, 10, 10, 220, 50, 'Idle', 30) # screen_label_state
runtime = make_label(screen_cont_run, 579, 10, 92, 50, '0:00', 30) # screen_label_runtime

screen_cont_dro = make_area(0, 70, 800, 130, 0xffff80)

def clicked_dro(e, label):
    if (e.get_code() != lv.EVENT.PRESSED):
        return
    np.attach(label, 9)

def make_dro(text, x, y, w, h):
    make_label(screen_cont_dro, x, y, 32, h, text, 30)
    button = basic_button(screen_cont_dro, x+28, y, w, h, 1, 30)
    label = interior_text(button, "0.00")
    return [button, label]
    # dro.add_event_cb(lambda e: clicked_dro(e, label), lv.EVENT.ALL, None)
    # return label

def sendCommand(msg):
    print(msg)
    messages.add_text('\n' + msg)

# units_btn = make_button("mm", screen_cont_dro, 7, 69, 71, 50, 28)
def toggle_units(e):
    if (e.get_code() != lv.EVENT.PRESSED):
        return
    text = units_btn.get_text() 
    if text == 'mm':
        cmd = 'G20'
        units_btn.set_text('Inch')  # Do this from status parser
    else:
        cmd = 'G21'
        units_btn.set_text('mm')  # Do this from status parser
    sendCommand(cmd)

units_btn = make_button("mm", screen_cont_dro, 7, 7, 71, 50, 28, lambda e: toggle_units(e))

class DRO:
    def __init__(self, axis, x, y, w, h):
        [self.button, self.label] = make_dro(axis, x, y, w, h)
        self.axis = axis
        self.button.add_event_cb(lambda e: self.on_click(e), lv.EVENT.ALL, None)
    def set(self, value):
        self.label.set_text(value)
    def get(self):
        return self.label.get_text()
    def goto(self, value):
        self.set(value)
        goto_axis_pos(self.axis, value)
        pass
    def set_wco(self, value):
        self.set(value)
        set_axis_wco(self.axis, value)
        pass
    def on_click(self, e):
        if (e.get_code() != lv.EVENT.PRESSED):
            return
        np.attach(self, 9)

# dro_x = make_dro('X', 96, 10, 140, 45)
# dro_y = make_dro('Y', 276, 10, 140, 45)
# dro_z = make_dro('Z', 458, 10, 140, 45)
# dro_a = make_dro('A', 634, 10, 130, 45)

dro_x = DRO('X', 96, 10, 140, 45)
dro_y = DRO('Y', 276, 10, 140, 45)
dro_z = DRO('Z', 458, 10, 140, 45)
dro_a = DRO('A', 634, 10, 130, 45)


# # Create screen_label_wcs
# def make_label(text, parent, x, y, w, h):
#     label = lv.label(parent)
#     label.set_text(text)
#     label.set_pos(x, y)
#     label.set_size(w, h)
#     label.set_long_mode(lv.label.LONG.CLIP)
#     # label.set_width(lv.pct(100))
#     label.set_style_border_width(0, MAINDEF)
#     label.set_style_radius(0, MAINDEF)
#     label.set_style_text_color(lv.color_hex(0x000000), MAINDEF)
#     label.set_style_text_font(test_font("montserratMedium", 30), MAINDEF)
#     label.set_style_text_letter_space(2, MAINDEF)
#     label.set_style_text_line_space(0, MAINDEF)
#     label.set_style_text_align(lv.TEXT_ALIGN.CENTER, MAINDEF)
#     label.set_style_bg_opa(0, MAINDEF)
#     label.set_style_pad_all(0, MAINDEF)
#     return label

# wcs = make_label("G54", screen_cont_dro, 6, 17, 72, 33)
wcs = make_label(screen_cont_dro, 6, 70, 72, 50, 'G54', 28)
    
def set_axis_wco(axis, coord):
    cmd = "G10 L20 P0 " + axis + str(coord)
    sendCommand(cmd)

def goto_axis_pos(axis, coord):
    cmd = "G0 " + axis + str(coord)
    sendCommand(cmd)

def send_zero_command(e, text):
    if (e.get_code() != lv.EVENT.PRESSED):
        return
    if text[1] == '=':
        set_axis_wco(text[0], 0)
    elif text[0] == '>':
        goto_axis_pos(text[1], 0)

def make_zero_button(text, x):
    return make_button(text, screen_cont_dro, x, 69, 67, 50, 28, lambda e: send_zero_command(e, text))

make_zero_button("X=0", 103)
make_zero_button(">X0", 193)
make_zero_button("Y=0", 283)
make_zero_button(">Y0", 373)
make_zero_button("Z=0", 463)
make_zero_button(">Z0", 553)
make_zero_button("A=0", 645)
make_zero_button(">A0", 727)

# Create screen_cont_jog
screen_cont_jog = make_area(0, 200, 800, 180, 0x80ff80)

def get_jog_distance():
    option = bytearray(10)
    jog_distance.get_selected_str(option, len(option))
    return option.decode("utf-8").rstrip('\0')

def send_jog(e, text):
    if (e.get_code() != lv.EVENT.PRESSED):
        return
    feedrate = 1000
    cmd = "$J=G91F" + str(feedrate) + text + get_jog_distance()
    sendCommand(cmd)

def make_jog_button(text, x, y):
    return make_button(text, screen_cont_jog, x, y, 120, 50, 28, lambda e: send_jog(e, text))

make_jog_button('Y+', 136,  10)
make_jog_button('Z+', 388,  10)
make_jog_button('X-',  10,  66)
make_jog_button('X+', 262,  66)
make_jog_button('Y-', 136, 122)
make_jog_button('Z-', 388, 122)

def set_jog_distance(e, text):
    if (e.get_code() != lv.EVENT.PRESSED):
        return
    options = jog_distance.get_options().split()
    index = options.index(text)
    jog_distance.set_selected(index)

def make_inc_button(text, x, y):
    return make_button(text, screen_cont_jog, x, y, 60, 50, 24, lambda e: set_jog_distance(e, text))

inc_00 = make_inc_button('.01', 522, 10)
inc_10 = make_inc_button( '.1', 591, 10)
inc_20 = make_inc_button(  '1', 660, 10)
inc_30 = make_inc_button( '10', 729, 10)

inc_01 = make_inc_button('.03', 522, 66)
inc_11 = make_inc_button( '.3', 591, 66)
inc_21 = make_inc_button(  '3', 660, 66)
inc_31 = make_inc_button( '30', 729, 66)

inc_02 = make_inc_button('.05', 522, 122)
inc_12 = make_inc_button( '.5', 591, 122)
inc_22 = make_inc_button(  '5', 660, 122)
inc_32 = make_inc_button( '50', 729, 122)

# Create screen_label_distance_mode
distance_mode = make_label(screen_cont_jog, 20, 10, 100, 50, "G90", 30)

jog_distances = ".001\n.003\n.005\n.01\n.03\n.05\n.1\n.3\n.5\n1\n3\n5\n10\n30\n50\n100\n300\n500"
jog_distance = make_dropdown(screen_cont_jog, 394, 69, 111, 44, None, jog_distances, 24, True)
jog_distance.set_dir(2) # Display the menu to the right


def make_message_box(parent, text, placeholder, x, y, w, h, maxlen, fontsize):
    ta = lv.textarea(parent)
    ta.set_text(text)
    ta.set_placeholder_text(placeholder)
    ta.set_pos(x, y)
    ta.set_size(w, h)
    ta.set_password_bullet("*")
    ta.set_password_mode(False)
    ta.set_one_line(False)
    ta.set_accepted_chars("")
    ta.set_max_length(maxlen)
    ta.set_style_text_color(lv.color_hex(0x000000), MAINDEF)
    # ta.set_style_text_font(test_font("montserratMedium", fontsize), MAINDEF)
    ta.set_style_text_letter_space(2, MAINDEF)
    ta.set_style_text_align(lv.TEXT_ALIGN.LEFT, MAINDEF)
    ta.set_style_bg_color(lv.color_hex(0xffffff), MAINDEF)
    ta.set_style_border_width(1, MAINDEF)
    ta.set_style_border_color(lv.color_hex(0x0), MAINDEF)
    ta.set_style_border_side(lv.BORDER_SIDE.FULL, MAINDEF)
    ta.set_style_pad_top(4, MAINDEF)
    ta.set_style_pad_right(4, MAINDEF)
    ta.set_style_pad_left(4, MAINDEF)
    ta.set_style_radius(5, MAINDEF)
    ta.set_style_bg_color(lv.color_hex(0x2195f6), lv.PART.SCROLLBAR|lv.STATE.DEFAULT)
    ta.set_style_radius(0, lv.PART.SCROLLBAR|lv.STATE.DEFAULT)
    ta.set_scrollbar_mode(lv.SCROLLBAR_MODE.ON)

    return ta

messages = make_message_box(screen, '', 'Messages', 0, 380, 400, 100, 2000, 20)
gcode = make_message_box(screen, '', 'GCode', 400, 380, 400, 100, 2000, 20)
# kbarea = make_area(400, 380, 400, 100, 0xff00ff)
# kb = lv.keyboard(kbarea)
# kb.set_textarea(messages)

np = Numpad(screen, make_button, f28)

screen.update_layout()

# 4. Displays the contents of the screen object
lv.scr_load(screen)


# ------------------------------ Guard dog to restart ESP32 equipment --start------------------------
if using_SDL:
    while SDL.check():
        time.sleep_ms(5)
else:
    try:
        from machine import WDT
        wdt = WDT(timeout=8000)  # enable it with a timeout of 2s
        print("Hint: Press Ctrl+C to end the program")
        while True:
            wdt.feed()
            time.sleep(0.1)
    except KeyboardInterrupt as ret:
        print("The program stopped running, ESP32 has restarted...")
        tft.deinit()
        time.sleep(10)
        # ------------------------------ Guard dog to restart ESP32 equipment --stop-------------------------
