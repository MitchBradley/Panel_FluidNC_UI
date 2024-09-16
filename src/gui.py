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
    from FluidNCSim import FluidNC

    import uselect
    import poll
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

    class FluidNC():
        def __init__(self, reply):
            self.reply = reply

        def send(self, msg):
            print(msg)

        def sendRealtimeChar(self, code):
            print(hex(code))

def fluidnc_input(msg):
    messages.add_text(msg + '\n')

fluidnc = FluidNC(fluidnc_input)

def has(state, key):
    return key in state and state[key] != None

def set_btn_text(state, key, btn):
    if has(state, key):
        btn.set_text(state[key])

wco = [0, 0, 0, 0, 0, 0]

class GrblCallback:
    def __init__(self):
        pass
    def update_state(self, state):
        set_btn_text(state,'stateName', state_name)
        if has(state, 'wco'):
            global wco
            wco = state['wco']
        if has(state, 'wpos'):
            for i in range(len(state['wpos'])):
                dro[i].set(str(state['wpos'][i]))
        if has(state, 'mpos'):
            for i in range(len(state['mpos'])):
                wpos = state['mpos'][i] - wco[i]
                dro[i].set(str(wpos))
        if has(state, 'spindleSpeed'):
            spindle_speed.get_child(0).set_text('S' + str(state['spindleSpeed']))
        # message
        # feedrate
        # spindle
        # spindleSpeed
        # ovr
        # lineNumber
        # flood
        # mist
        # pins
        print(state)
    def update_modal(self, modal):
        print(modal)
        set_btn_text(modal, 'distance', distance_mode.get_child(0))
        if has(modal, 'units'):
            set_units(modal['units'])
        if has(modal, 'wcs'):
            set_wcs(modal['wcs'])

    def refresh_files(self):
        print("Refresh Files")
        pass
    def handle_reset(self):
        print("Grbl Reset")
        pass
    def handle_error(self, msg):
        print("Grbl Error:", msg)
        pass
    def handle_ok(self):
        print("Grbl ok")
        pass
    def probe_failed(self, msg):
        print("Grbl Probe Failed:", msg)
        pass

grbl_callback = GrblCallback()

from grblclass import GrblHandler

grbl = GrblHandler(grbl_callback)

# 1. Create a display screen. Will need to display the component added to the screen to display
screen = lv.obj()  # scr====> screen
fs_drv = lv.fs_drv_t()
fs_driver.fs_register(fs_drv, 'S')
try:
    f16 = lv.font_montserrat_16
except:
    f16 = lv.font_load("S:montserrat-16.fnt")
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

def button_font(btn, size):
    # btn.set_style_text_font(test_font("montserratMedium", size), MAINDEF)
    pass

def button_bg(btn, color):
    btn.set_style_bg_color(lv.color_hex(color), MAINDEF)

def basic_style(obj, x, y, w, h, border, font):
    obj.set_pos(x, y)
    obj.set_size(w, h)
    obj.set_style_border_width(border, MAINDEF)
    obj.set_style_radius(5, MAINDEF)
    obj.set_style_pad_all(0, MAINDEF)
    obj.set_style_bg_color(lv.color_hex(0xffffff), MAINDEF)
    # obj.set_style_text_font(lv.font_montserrat_16, MAINDEF)
    obj.set_style_text_font(font, MAINDEF)
    obj.set_style_text_color(lv.color_hex(0x0), MAINDEF)
    obj.set_style_text_align(lv.TEXT_ALIGN.CENTER, MAINDEF)
    obj.set_style_border_color(lv.color_hex(0x0), MAINDEF)

def basic_button(parent, x, y, w, h, border, font):
    btn = lv.btn(parent)
    basic_style(btn, x, y, w, h, border, font)
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

def make_button(text, parent, x, y, w, h, font, cb=None):
    btn = basic_button(parent, x, y, w, h, 1, font)
    label = interior_text(btn, text)
    label.set_width(lv.pct(100))
    if cb:
        btn.add_event_cb(cb, lv.EVENT.CLICKED, None)
    return label

from numpad import Numpad

def do_go(e):
    pass

def do_stop(e):
    pass

def make_run_button(parent, x, y, text, cb):
    btn = basic_button(parent, x, y, 160, 50, 1, f28)
    btn.set_style_bg_color(lv.palette_lighten(lv.PALETTE.GREY, 2), MAINDEF)
    # btn.clear_flag(lv.obj.FLAG.CLICKABLE)
    label = interior_text(btn, text)
    btn.add_event_cb(cb, lv.EVENT.CLICKED, None)
    return btn

btnStart = make_run_button(screen_cont_run, 238, 11, lv.SYMBOL.PLAY, do_go)
# btnStop = make_run_button(screen_cont_run, 406, 11, lv.SYMBOL.STOP, do_stop)
btnStop = make_run_button(screen_cont_run, 406, 11, lv.SYMBOL.FILE, do_stop)

def make_dropdown(parent, x, y, w, h, name, items, font, arrow):
    obj = lv.dropdown(parent) # screen_ddlist_menu
    obj.set_text(name)
    obj.set_options(items)
    if not arrow:
        obj.set_symbol(None)
    basic_style(obj, x, y, w, h, 1, font)
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
    default.set_text_font(f24)
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

def option_index(menu, key):
    return menu.get_options().split().index(key)

def select_menu_option(menu, text):
    menu.set_selected(option_index(menu, text))

def show(obj):
        obj.clear_flag(lv.obj.FLAG.HIDDEN)

def hide(obj):
        obj.add_flag(lv.obj.FLAG.HIDDEN)

def menu_handler(e):
    obj = e.get_target()
    option = " "*10
    obj.get_selected_str(option, len(option))
    name = option.split('\x00')[0]
    if name == 'Home':
        sendCommand('$H')
    elif name == 'Jog':
        show(jogbox)
        hide(filesbox)
    elif name == 'Files':
        hide(jogbox)
        show(filesbox)
    elif name == 'Probe':
        pass
    elif name == 'Unlock':
        sendCommand('$X')
    elif name == 'Reset':
        sendRealtimeChar(0x18);

ddmenu = make_dropdown(screen_cont_run, 681, 11, 111, 50, 'Menu', "Jog\nFiles\nHome\nProbe\nUnlock\nReset", f28, False)
ddmenu.add_event_cb(menu_handler, lv.EVENT.VALUE_CHANGED, None)

def make_label(parent, x, y, w, h, text, font):
    # invisible container
    field = basic_button(parent, x, y, w, h, 0, font)
    label = interior_text(field, text)
    return label

state_name = make_label(screen_cont_run, 10, 10, 220, 50, 'Idle', f28) # screen_label_state
runtime = make_label(screen_cont_run, 579, 10, 92, 50, '0:00', f28) # screen_label_runtime

screen_cont_dro = make_area(0, 70, 800, 65, 0xffff80)

def clicked_dro(e, label):
    np.attach(label, 9)

def sendRealtimeChar(code):
    messages.add_text('Sending ' + hex(code) + '\n')
    fluidnc.sendRealtimeChar(code)

def sendCommand(msg):
    fluidnc.send(msg)
    messages.add_text(msg + '\n')

def in_inches():
    return units.get_text() == 'Inch'

def toggle_units(e):
    cmd = 'G21' if in_inches() else 'G21'
    sendCommand(cmd)

def is_rotary(axis):
    return axis == 'A' or axis == 'B' or axis == 'C'

def linear_dro_values():
    values = []
    for i in range(3):
        fval = float(dro[i].get())
        if in_inches():
            fval *= 25.4
        values.append(fval)
    return values

units = make_button("mm", screen_cont_dro, 7, 7, 71, 50, f28, toggle_units)

def format_dro(axis, value):
    fval = value if type(value) == type(0.0) else float(value)
    fmt = "{:.3f}"
    if is_rotary(axis):
        fmt = "{:.2f}"
    elif in_inches():
        fmt = "{:.4f}"
        fval /= 25.4
    return fmt.format(fval)

class DRO:
    def __init__(self, axis, x, y, w, h):
        make_label(screen_cont_dro, x, y, 32, h, axis, f28)
        self.button = basic_button(screen_cont_dro, x+30, y, w, h, 1, f28)
        self.label = interior_text(self.button, "0.00")
        self.axis = axis
        self.button.add_event_cb(self.on_click, lv.EVENT.CLICKED, None)
    def set(self, value):
        self.label.set_text(format_dro(self.axis, value))
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
        np.attach(self, 9)

dro = []
dro.append(DRO('X', 96, 10, 140, 45))
dro.append(DRO('Y', 276, 10, 140, 45))
dro.append(DRO('Z', 458, 10, 140, 45))
dro.append(DRO('A', 634, 10, 130, 45))

# The text inside a DRO depends on the units mode - G20 or G21,
# both in terms of the scaling of the value and the number of decimals.
# If the units change, we fix the displayed value immediately, instead
# of waiting for a new status report with axis values.
def reformat_dros(values):
    for i in range(3):
        dro[i].set(values[i])
    
def set_units(gmode):
    inches = in_inches()
    if inches and gmode == 'G21':
        values = linear_dro_values()
        units.set_text('Inch')
        reformat_dros(values)
    elif not inches and gmode == 'G20':
        values = linear_dro_values()
        units.set_text('mm')
        reformat_dros(values)

def set_wcs(new_wcs):
    select_menu_option(wcs, new_wcs)

# wcs = make_label("G54", screen_cont_dro, 6, 17, 72, 33)
coordinate_systems = "G54\nG55\nG56\nG57\nG58\nG59";
def wcs_handler(e):
    obj = e.get_target()
    option = " "*10
    obj.get_selected_str(option, len(option))
    name = option.split('\x00')[0]
    sendCommand(name)

screen_cont_zeroing = make_area(0, 135, 800, 65, 0xffff80)

wcs = make_dropdown(screen_cont_zeroing, 6, 5, 72, 50, None, coordinate_systems, f28, False)
wcs.add_event_cb(wcs_handler, lv.EVENT.VALUE_CHANGED, None)
    
def set_axis_wco(axis, coord):
    cmd = "G10 L20 P0 " + axis + str(coord)
    sendCommand(cmd)

def goto_axis_pos(axis, coord):
    cmd = "G0 " + axis + str(coord)
    sendCommand(cmd)

def send_zero_command(e):
    text = e.get_target().get_child(0).get_text()
    if text[1] == '=':
        set_axis_wco(text[0], 0)
    elif text[0] == '>':
        goto_axis_pos(text[1], 0)

def make_zero_button(text, x):
    return make_button(text, screen_cont_zeroing, x, 5, 67, 50, f28, send_zero_command)

make_zero_button("X=0", 103)
make_zero_button(">X0", 193)
make_zero_button("Y=0", 283)
make_zero_button(">Y0", 373)
make_zero_button("Z=0", 463)
make_zero_button(">Z0", 553)
make_zero_button("A=0", 645)
make_zero_button(">A0", 727)

def filemenu_handler(e):
    obj = e.get_target()
    option = " "*50
    obj.get_selected_str(option, len(option))
    name = option.split('\x00')[0]
    sendCommand("$SD/Run="+name)

def draw_event_cb(e):
    obj = e.get_target()
    dsc = lv.obj_draw_part_dsc_t.__cast__(e.get_param())
    # If the cells are drawn...
    if dsc.part == lv.PART.ITEMS:
        row = dsc.id //  obj.get_col_cnt()
        col = dsc.id - row * obj.get_col_cnt()
        dsc.rect_dsc.outline_pad = 0
        dsc.rect_dsc.border_width = 0
        if col == 2:
            dsc.label_dsc.align = lv.TEXT_ALIGN.RIGHT
        # Make every 2nd row grayish
        if (row % 2) == 0:
            dsc.rect_dsc.bg_color = lv.palette_main(lv.PALETTE.GREY).color_mix(dsc.rect_dsc.bg_color, lv.OPA._10)
            dsc.rect_dsc.bg_opa = lv.OPA.COVER

filesbox = make_area(0, 200, 800, 180, 0xff8080)
filestable = lv.table(filesbox)

def change_event_cb(e):
    obj = e.get_target()
    row = lv.C_Pointer()
    col = lv.C_Pointer()
    #filestable.get_selected_cell(row, col)
    obj.get_selected_cell(row, col)
    print("row: ",row.uint_val)

    # chk = filestable.has_cell_ctrl(row.uint_val, 0, lv.filestable.CELL_CTRL.CUSTOM_1)
    # if chk:
    #     filestable.clear_cell_ctrl(row.uint_val, 0, lv.filestable.CELL_CTRL.CUSTOM_1)
    # else:
    #     filestable.add_cell_ctrl(row.uint_val, 0, lv.filestable.CELL_CTRL.CUSTOM_1)

filenames = [
    ("..", -1),
    ("Downer", -1),
    ("Foo.nc", 1234),
    ("Barfer.gcode", 20998),
    ("JunkyWunky.gc", 1234567),
    ("FunkyMonkeyy.gc", 100000),
    ("0Test.gc", 1211),
    ("4RodHoles.gc", 5268)
    ];

# Set a smaller height to the table. It'll make it scrollable
# filestable.set_size(760, 160)
filestable.set_height(180)

filestable.set_row_cnt(len(filenames))  # Not required but avoids a lot of memory reallocation lv_table_set_set_value
filestable.set_col_width(0, 42)
filestable.set_col_width(1, 230)
filestable.set_col_width(2, 130)
filestable.set_col_cnt(3)
# filestable.set_style_pad_all(0, 0);
#filestable.set_style_pad_all(5, lv.PART.ITEMS);
filestable.set_style_pad_top(4, lv.PART.ITEMS);
filestable.set_style_pad_bottom(0, lv.PART.ITEMS);
filestable.set_style_text_font(lv.font_montserrat_20, lv.PART.ITEMS)

# Don't make the cell pressed, we will draw something different in the event
# filestable.remove_style(None, lv.PART.ITEMS | lv.STATE.PRESSED)

for i in range(len(filenames)):
    file = filenames[i]
    name = file[0]
    size = file[1]
    filestable.set_cell_value(i, 0, lv.SYMBOL.DIRECTORY if size == -1 else lv.SYMBOL.FILE)
    # filestable.set_cell_value(i, 0, lv.SYMBOL.DIRECTORY)
    filestable.set_cell_value(i, 1, name)
    filestable.set_cell_value(i, 2, "" if size == -1 else str(size))
    # filestable.set_style_height(30, i)


# filestable.align(lv.ALIGN.CENTER, 0, -20)

# Add an event callback to apply some custom drawing
filestable.add_event_cb(draw_event_cb, lv.EVENT.DRAW_PART_BEGIN, None)
filestable.add_event_cb(change_event_cb, lv.EVENT.VALUE_CHANGED, None)

# filemenu = lv.roller(filesbox)
# files = ("\n").join([
#     ":Down",
#     ":DDowner",
#     ";Foo.nc 1234",
#     ";Barfer.gcode 20998",
#     ";JunkyWunky.gc 1000000",
#     ";FunkyMonkeyy.gc 100000"
#     ]);
# files.replace(":", lv.SYMBOL.DIRECTORY)
# files.replace(";", lv.SYMBOL.FILE)
# filemenu.set_options(files, lv.roller.MODE.NORMAL)
# basic_style(filemenu, 10, 10, 300, 160, 1, f16)
# # make_dropdown(filesbox, 500, 11, 290, 50, 'Files', "Foo.nc     1234\nbar.nc    23456", f28, False)
# filemenu.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
# filemenu.add_event_cb(filemenu_handler, lv.EVENT.VALUE_CHANGED, None)

# Create screen_cont_jog
jogbox = make_area(0, 200, 800, 180, 0x80ff80)
jogbox.set_grid_dsc_array(
    [118, 118, 118, 118, 60, 60, 60, 60, lv.GRID_TEMPLATE.LAST],
    [53, 53, 53, lv.GRID_TEMPLATE.LAST])
jogbox.set_style_pad_all(3, MAINDEF)
jogbox.set_style_pad_row(4, MAINDEF)

def get_jog_distance():
    option = bytearray(10)
    jog_distance.get_selected_str(option, len(option))
    return option.decode("utf-8").rstrip('\0')

def send_jog(e):
    obj = e.get_target()
    label = obj.get_child(0)
    text = label.get_text()
    feedrate = 1000
    cmd = "$J=G91F" + str(feedrate) + text + get_jog_distance()
    sendCommand(cmd)

def make_grid_button(text, container, col, row, cb=None):
    obj = lv.obj(container)
    obj.set_grid_cell(lv.GRID_ALIGN.STRETCH, col, 1, lv.GRID_ALIGN.STRETCH, row, 1)
    obj.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
    obj.set_style_border_width(1, MAINDEF)
    obj.set_style_radius(5, MAINDEF)
    obj.set_style_border_color(lv.color_black(), MAINDEF)
    label = lv.label(obj)
    label.set_text(text)
    label.set_style_text_font(f28, MAINDEF)
    label.center()
    label.set_style_text_color(lv.color_black(), MAINDEF)
    if cb:
        obj.add_event_cb(cb, lv.EVENT.CLICKED, None)
    else:
        # Buttons without callbacks are labels without a background
        obj.set_style_bg_opa(0, lv.PART.MAIN | lv.STATE.DEFAULT)
        obj.set_style_border_width(0, lv.PART.MAIN | lv.STATE.DEFAULT)
    return obj

def make_jog_button(text, col, row):
    return make_grid_button(text, jogbox, col, row, send_jog)

make_jog_button('Y+', 1, 0)
make_jog_button('Z+', 3, 0)
make_jog_button('X-', 0, 1)
make_jog_button('X+', 2, 1)
make_jog_button('Y-', 1, 2)
make_jog_button('Z-', 3, 2)

def set_jog_distance(e):
    text = e.get_target().get_child(0).get_text()
    select_menu_option(jog_distance, text)

def make_inc_button(text, col, row):
    return make_grid_button(text, jogbox, col, row, set_jog_distance)

inc_00 = make_inc_button('.01', 4, 0)
inc_10 = make_inc_button( '.1', 5, 0)
inc_20 = make_inc_button(  '1', 6, 0)
inc_30 = make_inc_button( '10', 7, 0)

inc_01 = make_inc_button('.03', 4, 1)
inc_11 = make_inc_button( '.3', 5, 1)
inc_21 = make_inc_button(  '3', 6, 1)
inc_31 = make_inc_button( '30', 7, 1)

inc_02 = make_inc_button('.05', 4, 2)
inc_12 = make_inc_button( '.5', 5, 2)
inc_22 = make_inc_button(  '5', 6, 2)
inc_32 = make_inc_button( '50', 7, 2)

# Create screen_label_distance_mode
# distance_mode = make_label(jogbox, 20, 10, 100, 50, "G90", 30)
distance_mode = make_grid_button("G90", jogbox, 0, 0)

spindle_speed = make_grid_button("", jogbox, 1, 1)

jog_distances = ".001\n.003\n.005\n.01\n.03\n.05\n.1\n.3\n.5\n1\n3\n5\n10\n30\n50\n100\n300\n500"
jog_distance = make_dropdown(jogbox, 394, 69, 111, 44, None, jog_distances, f24, True)
jog_distance.set_dir(2) # Display the menu to the right
jog_distance.set_grid_cell(lv.GRID_ALIGN.STRETCH, 3, 1, lv.GRID_ALIGN.STRETCH, 1, 1)

def make_message_box(parent, text, placeholder, x, y, w, h, maxlen, font):
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
    ta.set_style_text_font(font, MAINDEF)
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

messages = make_message_box(screen, '', 'Messages', 0, 380, 400, 100, 2000, f16)
gcode = make_message_box(screen, '', 'GCode', 400, 380, 400, 100, 2000, f16)

# kbarea = make_area(10, 10, 780, 300, 0xffffff)
# kb = lv.keyboard(kbarea)
# kb.set_size(780, 300)
# kb.set_pos(0, 0)
# kb.set_style_text_font(f24, MAINDEF)
# kb.set_textarea(messages)

np = Numpad(screen, make_button, f28)

screen.update_layout()

# 4. Displays the contents of the screen object
lv.scr_load(screen)

while True:
    if using_SDL:
        SDL.check()
        if poll.poll_input(10):
            grbl.handle_message(poll.get_line())
    else:
        msg = input()
        if input == "quit":
            break
        grbl.handle_message(msg)

# ------------------------------ Guard dog to restart ESP32 equipment --start------------------------
# if using_SDL:
#     while SDL.check():
#         time.sleep_ms(5)
# else:
#     try:
#         from machine import WDT
#         # wdt = WDT(timeout=8000)  # enable it with a timeout of 2s
#         print("Hint: Press Ctrl+C to end the program")
#         while True:
#             # wdt.feed()
#             time.sleep(0.1)
#     except KeyboardInterrupt as ret:
#         print("The program stopped running, ESP32 has restarted...")
#         #tft.deinit()
#         #WDT(timeout=500)
#         #time.sleep(10)
#         # ------------------------------ Guard dog to restart ESP32 equipment --stop-------------------------
