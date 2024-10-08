import lvgl as lv
lv.init()
import fs_driver
import time

WIDTH = 800
HEIGHT = 480

using_SDL = False
try:
    import sdl_init9
    using_SDL = True
    from fluidnc_sim import FluidNC
except:
    import crowpanel7_init
    from fluidnc_uart import FluidNC

# red = lv.palette_main(lv.PALETTE.RED)
# green = lv.palette_main(lv.PALETTE.GREEN)
# yellow = lv.palette_lighten(lv.PALETTE.YELLOW, 1)
red = lv.color_hex(0xff0000)
green = lv.color_hex(0x00ff00)
yellow = lv.color_hex(0xffff00)
gray = lv.palette_lighten(lv.PALETTE.GREY, 2)
darkgray = lv.palette_darken(lv.PALETTE.GREY, 1)
white = lv.color_white()
black = lv.color_black()

try:
    import theme as theme
except:
    try:
        import dark_theme as theme
    except:
        import light_theme as theme

# # theme = lv.theme_theme_get()
# # lvdisp = lv.display_t.__cast__(theme.disp)
# lvdisplay = lv.display_get_default()
# theme= lv.theme_t()
# style = lv.style_t()
# style.init()
# style.set_bg_color(lv.palette_lighten(lv.PALETTE.RED, 3))
# theme.color_primary.red = 255
# theme.color_secondary.green = 255
# def apply_cb(self, th, obj):
#     print(th, obj.get_class())
#     if obj.get_class() == lv.btn_class:
#         obj.add_style(style, 0)
# theme.set_apply_cb(apply_cb)
# # th_act = lv.theme_get_from_obj(lv.screen_active())
# # theme.set_parent(th_act)
# lvdisplay.set_theme(theme)


def add_message(line):
    messages.set_cursor_pos(0x7fff)  # Set to end
    maxlen = messages.get_max_length()
    if maxlen:
        pos = messages.get_cursor_pos()
        if pos + len(line) + 1 >= maxlen:
            messages.set_cursor_pos(0)  # Set to beginning
            for i in range(1000):       # Make some space
                messages.del_char()
                messages.set_cursor_pos(0x7fff)  # Set to end
    messages.add_text(line + '\n')

def has(state, key):
    return key in state and state[key] != None

def set_btn_text(state, key, btn):
    if has(state, key):
        btn.set_text(state[key])

wco = [0, 0, 0, 0, 0, 0]

# Create the screen object that everything else is on top of
# font_load -> binfont_create
screen = lv.obj()
fs_drv = lv.fs_drv_t()
fs_driver.fs_register(fs_drv, 'S')
try:
    f16 = lv.font_montserrat_16
except:
    f16 = lv.binfont_create("S:font/montserrat-16.fnt")
try:
    f18 = lv.font_montserrat_18
except:
    f18 = lv.binfont_create("S:font/montserrat-18.fnt")
try:
    f20 = lv.font_montserrat_20
except:
    f20 = lv.binfont_create("S:font/montserrat-20.fnt")
f24 = lv.binfont_create("S:font/montserrat-24.fnt")
f28 = lv.binfont_create("S:font/montserrat-28.fnt")
screen = lv.screen_active()
screen.clean()

screen.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)

screen.set_style_bg_opa(0, 0)

def make_area(parent, x, y, w, h, color):
    area = lv.obj(parent)
    area.set_pos(x, y)
    area.set_size(w, h)
    # area.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
    # area.set_style_border_width(0, 0)
    area.set_style_radius(0, 0)
    area.set_style_bg_color(color, 0)
    area.set_style_pad_all(0, 0)
    area.set_style_border_width(0, 0)
    return area

run_area = make_area(screen, 0, 0, WIDTH, 70, theme.run_bg)

def button_font(btn, size):
    # btn.set_style_text_font(test_font("montserratMedium", size), 0)
    pass

def button_bg(btn, color):
    btn.set_style_bg_color(lv.color_hex(color), 0)

def basic_style(obj, x, y, w, h, font):
    obj.set_pos(x, y)
    obj.set_size(w, h)
    obj.set_style_border_width(theme.border_width, 0)
    obj.set_style_radius(theme.radius, 0)
    obj.set_style_pad_all(0, 0)
    obj.set_style_bg_color(theme.bg, 0)
    # obj.set_style_text_font(lv.font_montserrat_16, 0)
    obj.set_style_text_font(font, 0)
    obj.set_style_text_color(theme.fg, 0)
    obj.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
    obj.set_style_border_color(theme.border_color, 0)

def basic_button(parent, x, y, w, h, font):
    btn = lv.button(parent)
    basic_style(btn, x, y, w, h, font)
    return btn

firsttime = True
def interior_text(parent, text):
    label = lv.label(parent)
    label.set_text(text)
    label.set_long_mode(lv.label.LONG.CLIP)
    label.align(lv.ALIGN.CENTER, 0, 0)
    return label

def make_button(text, parent, x, y, w, h, font, cb=None):
    btn = basic_button(parent, x, y, w, h, font)
    label = interior_text(btn, text)
    label.set_width(lv.pct(100))
    if cb:
        btn.add_event_cb(cb, lv.EVENT.CLICKED, None)
    return label

from numpad import Numpad

def runGCode():
    if loadedFile != None:
        sendCommand("$SD/Run=" + loadedFile)

def make_run_button(parent, x, y, handler):
    btn = basic_button(parent, x, y, 160, 50, f28)
    btn.set_style_bg_color(theme.disabled_bg, 0)
    btn.remove_flag(lv.obj.FLAG.CLICKABLE)
    interior_text(btn, "")
    btn.add_event_cb(handler, lv.EVENT.CLICKED, None)
    return btn

go_cb = None
def go_event_handler(e):
    global go_cb
    if go_cb != None:
        go_cb()
    
stop_cb = None
def stop_event_handler(e):
    global stop_cb
    if stop_cb != None:
        stop_cb()

btnStart = make_run_button(run_area, 238, 11, go_event_handler)
btnStop = make_run_button(run_area, 406, 11, stop_event_handler)

def set_run_button(btn, color, text):
    label = btn.get_child(0)
    label.set_text(text)
    if color != None:
        btn.set_style_bg_color(color, 0)
    else:
        btn.set_style_bg_color(theme.run_disabled_bg, 0)
    btn.update_flag(lv.obj.FLAG.CLICKABLE, color != gray)

def set_left_button(color, text, cb):
    set_run_button(btnStart, color, text)
    global go_cb
    go_cb = cb

def set_right_button(color, text, cb):
    set_run_button(btnStop, color, text)
    global stop_cb
    stop_cb = cb

set_left_button(None, lv.SYMBOL.PLAY, None)
set_right_button(None, lv.SYMBOL.STOP, None)

def make_dropdown(parent, x, y, w, h, name, items, font, arrow):
    obj = lv.dropdown(parent) # screen_ddlist_menu
    obj.set_text(name)
    obj.set_options(items)
    if not arrow:
        obj.set_symbol(None)
    basic_style(obj, x, y, w, h, font)
    obj.set_style_pad_all(8, 0)
    # Checked style
    checked = lv.style_t()
    checked.init()
    checked.set_border_width(1)
    checked.set_border_color(theme.border_color)
    checked.set_border_side(lv.BORDER_SIDE.FULL)
    checked.set_radius(5)
    checked.set_bg_color(theme.checked_bg)
    obj.get_list().add_style(checked, lv.PART.SELECTED|lv.STATE.CHECKED)
    # Default style
    default = lv.style_t()
    default.init()
    default.set_max_height(HEIGHT)
    default.set_text_color(theme.fg)
    # default.set_text_font(test_font("montserratMedium", 24))
    default.set_text_font(f24)
    default.set_border_width(1)
    default.set_border_color(theme.border_color) # lv.color_hex(0xe1e6ee)
    default.set_border_side(lv.BORDER_SIDE.FULL)
    default.set_radius(5)
    default.set_bg_color(theme.bg)
    obj.get_list().add_style(default, 0)
    # Scrollbar style
    scrollbar = lv.style_t()
    scrollbar.init()
    scrollbar.set_radius(5)
    scrollbar.set_width(10)
    scrollbar.set_bg_color(theme.scrollbar_bg)
    obj.get_list().add_style(scrollbar, lv.PART.SCROLLBAR|lv.STATE.DEFAULT)
    return obj

def option_index(menu, key):
    return menu.get_options().split().index(key)

def select_menu_option(menu, text):
    menu.set_selected(option_index(menu, text))

def show(obj):
        obj.remove_flag(lv.obj.FLAG.HIDDEN)

def hide(obj):
        obj.add_flag(lv.obj.FLAG.HIDDEN)

def unlock():
    sendCommand('$X')

def requestModes():
    sendCommand('$G')

def stopGCode():
    sendRealtimeChar('\x18')

def resumeGCode():
    sendRealtimeChar('~')

def pauseGCode():
    sendRealtimeChar('!')

def requestStatusReport():
    sendRealtimeChar('?')

def stopAndRecover():
    stopGCode()
    # To stop GRBL you send a reset character, which causes some modes
    # be reset to their default values.  In particular, it sets G21 mode,
    # which affects the coordinate display and the jog distances.
    requestModes()

def menu_handler(e):
    obj = e.get_target_obj()
    option = " "*10
    obj.get_selected_str(option, len(option))
    name = option.split('\x00')[0]
    if name == 'Home':
        home('')
    elif name == 'Jog':
        select_overlay('jog')
    elif name == 'Files':
        select_overlay('files')
    elif name == 'Probe':
        pass
    elif name == 'Unlock':
        unlock()
    elif name == 'Reset':
        stopGCode()

ddmenu = make_dropdown(run_area, 681, 11, 111, 50, 'Menu', "Jog\nFiles\nProbe\nUnlock\nReset", f28, False)
ddmenu.add_event_cb(menu_handler, lv.EVENT.VALUE_CHANGED, None)

def make_label(parent, x, y, w, h, text, font):
    # invisible container
    field = basic_button(parent, x, y, w, h, font)
    field.set_style_border_width(0, 0)
    field.set_style_bg_opa(0, 0)
    field.set_style_shadow_width(0, 0)
    label = interior_text(field, text)
    return label

state_name = make_label(run_area, 10, 10, 220, 50, 'Idle', f28) # screen_label_state
runtime = make_label(run_area, 579, 10, 92, 50, '0:00', f28) # screen_label_runtime

dro_area = make_area(screen, 0, 70, WIDTH, 65, theme.dro_bg)

overlays = []
overlay_y = 135
overlay_h = HEIGHT-overlay_y

def make_overlay(name, color):
    overlay = make_area(screen, 0, overlay_y, WIDTH, overlay_h, color)
    dict = {'name': name, 'area': overlay}
    overlays.append(dict)
    return overlay

def select_overlay(name):
    for o in overlays:
        if o['name'] == name:
            show(o['area'])
        else:
            hide(o['area'])

jog_overlay = make_overlay('jog', theme.jog_bg)
files_overlay = make_overlay('files', theme.files_bg)
select_overlay('jog')

def clicked_dro(e, label):
    np.attach(label, 9)

def sendRealtimeChar(c):
    add_message('>' + c)
    fluidnc.sendRealtimeChar(c)

def sendCommand(msg):
    # add_message(">" + msg)
    fluidnc.send(msg)

dirName = "/sd"
dirLevel = 0

def requestFileList():
    global dirName
    sendCommand("$Files/ListGCode=" + dirName)

def dirDown(name):
    global dirName, dirLevel
    dirName += "/" + name
    dirLevel += 1
    requestFileList()
    
def dirUp():
    global dirName, dirLevel
    if dirLevel:
        pos = dirName.rfind('/')
        if pos != -1:
            dirName = dirName[0:pos]
            dirLevel -= 1
    else:
        dirLevel = 0
        dirName = "/sd"
    requestFileList()

nlines = 10
def requestFilePreview(name, firstline):
    # gcode.add_cell_ctrl(0, 0, lv.table.CELL_CTRL.MERGE_RIGHT)
    gcode.set_cell_value(0, 0, "Get")
    gcode.set_cell_value(0, 1, name)
    for i in range(1,gcode.get_row_count()):
        gcode.set_cell_value(i, 0, "")
        gcode.set_cell_value(i, 1, "")
    global nlines
    lastline = firstline + nlines
    sendCommand("$File/ShowSome=" + str(firstline) + ":" + str(lastline) + "," + name)

loadedFile = None

def loadFile(name):
    global loadedFile
    loadedFile = dirName + '/' + name
    requestFilePreview(loadedFile, 0)
    setRunControls()

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
        fval = float(dros[i].get())
        if in_inches():
            fval *= 25.4
        values.append(fval)
    return values

units = make_button("mm", dro_area, 7, 7, 71, 50, f28, toggle_units)

def format_dro(axis, value):
    fval = value if type(value) == type(0.0) else float(value)
    fmt = "{:.3f}"
    if is_rotary(axis):
        fmt = "{:.2f}"
    elif in_inches():
        fmt = "{:.4f}"
        fval /= 25.4
    return fmt.format(fval)

def home(axis):
    sendCommand('$H'+axis)

class DRO:
    def __init__(self, axis, x, y, w, h):
        make_label(dro_area, x, y, 32, h, axis, f28)
        self.button = basic_button(dro_area, x+30, y, w, h, f28)
        self.label = interior_text(self.button, "0.000")
        self.axis = axis
        self.bg_color = self.button.get_style_bg_color(0)
        self.button.add_event_cb(self.on_click, lv.EVENT.CLICKED, None)
    def set(self, value):
        self.label.set_text(format_dro(self.axis, value))
    def get(self):
        return self.label.get_text()
    def home(self):
        home(self.axis)
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
    def highlight(self):
        self.button.set_style_bg_color(theme.highlight_bg, 0)
    def lowlight(self):
        self.button.set_style_bg_color(self.bg_color, 0)
    def arm(self, armed):
        # if armed:
        #     self.button.add_flag(lv.obj.FLAG.CLICKABLE)
        # else:
        #     self.button.remove_flag(lv.obj.FLAG.CLICKABLE)
        self.button.update_flag(lv.obj.FLAG.CLICKABLE, armed)

dros = []
dros.append(DRO('X', 96, 10, 140, 45))
dros.append(DRO('Y', 276, 10, 140, 45))
dros.append(DRO('Z', 458, 10, 140, 45))
dros.append(DRO('A', 634, 10, 130, 45))

# The text inside a DRO depends on the units mode - G20 or G21,
# both in terms of the scaling of the value and the number of decimals.
# If the units change, we fix the displayed value immediately, instead
# of waiting for a new status report with axis values.
def reformat_dros(values):
    for i in range(3):
        dros[i].set(values[i])
    
def set_units(gmode):
    inches = in_inches()
    if inches and gmode == 'G21':
        values = linear_dro_values()
        units.set_text('mm')
        reformat_dros(values)
        set_inc_buttons(gmode)
    elif not inches and gmode == 'G20':
        values = linear_dro_values()
        units.set_text('Inch')
        reformat_dros(values)
        set_inc_buttons(gmode)

def set_axis_wco(axis, coord):
    cmd = "G10 L20 P0 " + axis + str(coord)
    sendCommand(cmd)

def goto_axis_pos(axis, coord):
    cmd = "G0 " + axis + str(coord)
    sendCommand(cmd)

def send_zero_command(e):
    text = e.get_target_obj().get_child(0).get_text()
    if text[1] == '=':
        set_axis_wco(text[0], 0)
    elif text[0] == '>':
        goto_axis_pos(text[1], 0)

zeroing_y = 0
# zeroing_h = 54
zeroing_h = 0
zeroing_area = make_area(jog_overlay, 0, zeroing_y, WIDTH, zeroing_h, theme.zeroing_bg)

zeroing_area.set_grid_dsc_array(
    [84, 78, 80, 78, 80, 78, 80, 72, 72, lv.GRID_TEMPLATE_LAST],
    [45, lv.GRID_TEMPLATE_LAST],
    )
zeroing_area.set_style_pad_all(3, 0)
#zeroing_area.set_style_bg_opa(0, 0)
# zeroing_area.set_style_border_width(0, 0)

def make_grid_button(text, container, col, row, cb=None):
    obj = lv.obj(container)
    obj.set_grid_cell(lv.GRID_ALIGN.STRETCH, col, 1, lv.GRID_ALIGN.STRETCH, row, 1)
    obj.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
    obj.set_style_border_width(1, 0)
    obj.set_style_radius(theme.radius, 0)
    obj.set_style_border_color(theme.border_color, 0)
    obj.set_style_bg_color(theme.bg, 0)
    label = lv.label(obj)
    label.set_text(text)
    label.set_style_text_font(f28, 0)
    label.center()
    label.set_style_text_color(theme.fg, 0)
    if cb:
        obj.add_event_cb(cb, lv.EVENT.CLICKED, None)
    else:
        # Buttons without callbacks are labels without a background
        obj.set_style_bg_opa(0, 0)
        obj.set_style_border_width(0, 0)
    return obj

def make_zero_button(text, col):
    return make_grid_button(text, zeroing_area, col, 0, send_zero_command)

make_zero_button("X=0", 1)
make_zero_button(">X0", 2)
make_zero_button("Y=0", 3)
make_zero_button(">Y0", 4)
make_zero_button("Z=0", 5)
make_zero_button(">Z0", 6)
make_zero_button("A=0", 7)
make_zero_button(">A0", 8)

homing_y = zeroing_y + zeroing_h
homing_h = 0
#homing_h = 54
#homing_area = make_area(jog_overlay, 100, homing_y, WIDTH-100, homing_h, lv.color_hex(0xc0ffc0))
#homing_area.set_grid_dsc_array(
#    [60, 60, 60, 60, lv.GRID_TEMPLATE_LAST],
#    [50, lv.GRID_TEMPLATE_LAST],
#    )
#homing_area.set_grid_align(lv.GRID_ALIGN.SPACE_AROUND, lv.GRID_ALIGN.START)
## homing_area.set_style_pad_column(100, 0)
#homing_area.set_style_pad_row(0, 0)
#
#def send_homing_command(e):
#    text = e.get_target_obj().get_child(0).get_text()[1:]
#    home(text)
#
#def make_homing_button(axis, col):
#    obj = make_grid_button(lv.SYMBOL.HOME + axis, homing_area, col, 0, send_homing_command)
#    obj.set_grid_cell(lv.GRID_ALIGN.STRETCH, col, 1, lv.GRID_ALIGN.STRETCH, 0, 1)
#    return obj
#
#make_button(lv.SYMBOL.HOME, jog_overlay, 10, homing_y, 50, 50, f28, send_homing_command)
#make_homing_button('X', 0)
#make_homing_button('Y', 1)
#make_homing_button('Z', 2)
#make_homing_button('A', 3)


def filemenu_handler(e):
    obj = e.get_target_obj()
    option = " "*50
    obj.get_selected_str(option, len(option))
    name = option.split('\x00')[0]
    sendCommand("$SD/Run="+name)

def files_draw_event_cb(e):
    obj = e.get_target()
    task = e.get_draw_task()
    dscb = task.draw_dsc
    base_dsc = lv.draw_dsc_base_t.__cast__(task.draw_dsc)
    # If the cells are drawn...
    if base_dsc.part == lv.PART.ITEMS:
        row = base_dsc.id1
        col = base_dsc.id2
        label_dsc = task.get_label_dsc()
        fill_dsc = task.get_fill_dsc()
        border_dsc = task.get_border_dsc()
        if border_dsc != None:
            border_dsc.width = 0
        if col == 2 and label_dsc != None:
            label_dsc.align = lv.TEXT_ALIGN.RIGHT
        # Make every 2nd row grayish
        if (row % 2) == 0 and fill_dsc != None:
            fill_dsc.color = theme.stripe_color
            fill_dsc.opa = lv.OPA.COVER

filestable = lv.table(files_overlay)

def files_change_event_cb(e):
    obj = e.get_target_obj()
    rowp = lv.C_Pointer()
    colp = lv.C_Pointer()
    obj.get_selected_cell(rowp, colp)
    row = rowp.uint_val
    # col = colp.uint_val
    if row == 0:
        requestFileList()
        return
    isdir = obj.get_cell_value(row, 2) == ''
    name = obj.get_cell_value(row, 1)
    if name == None or name == '':
        return
    if name == '.. (Up)':
        dirUp()
    elif isdir:
        dirDown(name)
    else:
        loadFile(name)

# Set a smaller height to the table. It'll make it scrollable
filestable.set_size(WIDTH//2, overlay_h)
# filestable.set_height(overlay_h)

# filestable.set_row_count(len(filenames))  # Not required but avoids a lot of memory reallocation
filestable.set_column_width(0, 42)
filestable.set_column_width(1, 230)
filestable.set_column_width(2, 130)
filestable.set_column_count(3)
# filestable.set_style_pad_all(0, 0);
#filestable.set_style_pad_all(5, lv.PART.ITEMS);
filestable.set_style_pad_left(3, lv.PART.ITEMS);
filestable.set_style_pad_right(8, lv.PART.ITEMS);
filestable.set_style_pad_top(4, lv.PART.ITEMS);
filestable.set_style_pad_bottom(0, lv.PART.ITEMS);
filestable.set_style_text_font(f24, lv.PART.ITEMS)
filestable.set_style_text_color(theme.fg, lv.PART.ITEMS)
filestable.set_style_bg_color(theme.bg, 0);
filestable.add_cell_ctrl(0, 0, lv.table.CELL_CTRL.MERGE_RIGHT)
filestable.add_cell_ctrl(0, 0, lv.table.CELL_CTRL.MERGE_RIGHT)

# Don't make the cell pressed, we will draw something different in the event
# filestable.remove_style(None, lv.PART.ITEMS | lv.STATE.PRESSED)

# Add an event callback to apply some custom drawing
filestable.add_event_cb(files_draw_event_cb, lv.EVENT.DRAW_TASK_ADDED, None)
filestable.add_flag(lv.obj.FLAG.SEND_DRAW_TASK_EVENTS);
filestable.add_event_cb(files_change_event_cb, lv.EVENT.VALUE_CHANGED, None)

filestable.set_cell_value(0, 0, "Files in " + dirName)

def onFilesList(files):
    global dirLevel, dirName
    toprows = 2 if dirLevel else 1
    filestable.set_row_count(toprows + len(files))  # Preallocate
    filestable.add_cell_ctrl(0, 0, lv.table.CELL_CTRL.MERGE_RIGHT)
    filestable.add_cell_ctrl(0, 0, lv.table.CELL_CTRL.MERGE_RIGHT)
    filestable.set_cell_value(0, 0, "Files in " + dirName)
    if toprows == 2:
        filestable.set_cell_value(1, 0, lv.SYMBOL.DIRECTORY)
        filestable.set_cell_value(1, 1, ".. (Up)")
        filestable.set_cell_value(1, 2, "")
    for i in range(len(files)):
        file = files[i]
        name = file[0]
        size = file[1]
        filestable.set_cell_value(toprows+i, 0, lv.SYMBOL.DIRECTORY if size == -1 else lv.SYMBOL.FILE)
        filestable.set_cell_value(toprows+i, 1, name)
        filestable.set_cell_value(toprows+i, 2, "" if size == -1 else str(size))

jog_grid_y = homing_y + homing_h
jog_grid_h = 172
jog_grid = make_area(jog_overlay, 0, jog_grid_y, WIDTH, jog_grid_h, theme.jog_bg)
jog_grid.set_grid_dsc_array(
    [118, 118, 118, 118, 60, 60, 60, 60, lv.GRID_TEMPLATE_LAST],
    [53, 53, 53, lv.GRID_TEMPLATE_LAST])
jog_grid.set_style_pad_all(3, 0)
jog_grid.set_style_pad_row(4, 0)
jog_grid.set_style_bg_opa(0, 0)
jog_grid.set_style_border_width(0, 0)

def get_jog_distance():
    option = bytearray(10)
    jog_distance.get_selected_str(option, len(option))
    return option.decode("utf-8").rstrip('\0')

def send_jog(e):
    obj = e.get_target_obj()
    label = obj.get_child(0)
    text = label.get_text()
    feedrate = 1000
    cmd = "$J=G91F" + str(feedrate) + text + get_jog_distance()
    sendCommand(cmd)

def make_jog_button(text, col, row):
    return make_grid_button(text, jog_grid, col, row, send_jog)

make_jog_button('Y+', 1, 0)
make_jog_button('Z+', 3, 0)
make_jog_button('X-', 0, 1)
make_jog_button('X+', 2, 1)
make_jog_button('Y-', 1, 2)
make_jog_button('Z-', 3, 2)

def set_jog_distance(e):
    text = e.get_target_obj().get_child(0).get_text()
    select_menu_option(jog_distance, text)

def make_inc_button(text, col, row):
    btn = make_grid_button(text, jog_grid, col, row, set_jog_distance)
    btn.get_child(0).set_style_text_font(f24, 0)
    return btn

# G20 mode uses cols 0..3, while G21 mode uses cols 1..4
jog_increments = (
    (".001", ".01", ".1", "1", "10"),
    (".003", ".03", ".3", "3", "30"),
    (".005", ".05", ".5", "5", "50")
)
jog_buttons = [
    [None, None, None, None],
    [None, None, None, None],
    [None, None, None, None]
]

for i in range(len(jog_buttons)):
    for j in range(len(jog_buttons[0])):
        text = jog_increments[i][j+1]
        jog_buttons[i][j] = make_inc_button(text, j+4, i)

def set_inc_buttons(gmode):
    offset = 0 if gmode == "G20" else 1
    for i in range(len(jog_buttons)):
        for j in range(len(jog_buttons[0])):
            text = jog_increments[i][j+offset]
            jog_buttons[i][j].get_child(0).set_text(text)

# Create screen_label_distance_mode
# distance_mode = make_label(jog_grid, 20, 10, 100, 50, "G90", 30)
distance_mode = make_grid_button("G90", jog_grid, 0, 2)

def set_wcs(new_wcs):
    select_menu_option(wcs, new_wcs)

coordinate_systems = "G54\nG55\nG56\nG57\nG58\nG59";
def wcs_handler(e):
    obj = e.get_target_obj()
    option = " "*10
    obj.get_selected_str(option, len(option))
    name = option.split('\x00')[0]
    sendCommand(name)

# wcs = make_dropdown(zeroing_area, 0, 0, 72, 45, None, coordinate_systems, f28, False)
wcs = make_dropdown(jog_grid, 8, 6, 72, 45, None, coordinate_systems, f28, False)
wcs.add_event_cb(wcs_handler, lv.EVENT.VALUE_CHANGED, None)
    

def home_all(e):
    home('')
make_grid_button(lv.SYMBOL.HOME, jog_grid, 1, 1, home_all)

jog_distances = ".001\n.003\n.005\n.01\n.03\n.05\n.1\n.3\n.5\n1\n3\n5\n10\n30\n50\n100\n300\n500"
jog_distance = make_dropdown(jog_grid, 394, 69, 111, 44, None, jog_distances, f28, True)
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
    ta.set_style_text_color(theme.fg, 0)
    ta.set_style_text_color(theme.placeholder_fg, lv.PART_TEXTAREA.PLACEHOLDER)
    ta.set_style_text_font(font, 0)
    ta.set_style_text_letter_space(2, 0)
    ta.set_style_text_align(lv.TEXT_ALIGN.LEFT, 0)
    ta.set_style_bg_color(theme.bg, 0)
    ta.set_style_border_width(1, 0)
    ta.set_style_border_color(theme.border_color, 0)
    ta.set_style_border_side(lv.BORDER_SIDE.FULL, 0)
    ta.set_style_pad_top(4, 0)
    ta.set_style_pad_right(4, 0)
    ta.set_style_pad_left(4, 0)
    ta.set_style_radius(theme.radius, 0)
    ta.set_style_bg_color(theme.messages_bg, lv.PART.SCROLLBAR|lv.STATE.DEFAULT)
    ta.set_style_radius(0, lv.PART.SCROLLBAR|lv.STATE.DEFAULT)
    ta.set_scrollbar_mode(lv.SCROLLBAR_MODE.ON)

    return ta

message_y = jog_grid_y + jog_grid_h
message_h = overlay_h - message_y
messages = make_message_box(jog_overlay, '', 'Messages', 0, message_y, WIDTH, message_h, 20000, f18)
# messages = make_message_box(jog_overlay, '', 'Messages', 0, 380-135, 400, 100, 2000, f16)
gcode_x = WIDTH//2
gcode_w = WIDTH - gcode_x
# gcode = make_message_box(files_overlay, '', 'GCode', gcode_x, 0, gcode_w, overlay_h, 2000, f16)
gcode = lv.table(files_overlay)
gcode.set_pos(gcode_x, 0)
gcode.set_size(gcode_w, overlay_h)
gcode.set_column_count(2)
gcode.set_column_width(0, 80)
gcode.set_column_width(1, gcode_w - 80)
gcode.set_style_bg_color(theme.bg, 0)
gcode.set_style_bg_color(theme.bg, lv.PART.ITEMS)
gcode.set_style_pad_top(0, lv.PART.ITEMS);
gcode.set_style_pad_left(3, lv.PART.ITEMS);
gcode.set_style_pad_right(3, lv.PART.ITEMS);
gcode.set_style_pad_bottom(0, lv.PART.ITEMS);
gcode.set_style_text_font(f20, lv.PART.ITEMS)
# gcode.add_cell_ctrl(0, 0, lv.table.CELL_CTRL.MERGE_RIGHT)
# gcode.add_cell_ctrl(0, 0, lv.table.CELL_CTRL.MERGE_RIGHT)

def gcode_draw_event_cb(e):
    obj = e.get_target_obj()
    task = e.get_draw_task()
    dscb = task.draw_dsc
    base_dsc = lv.draw_dsc_base_t.__cast__(task.draw_dsc)
    # If the cells are drawn...
    if base_dsc.part == lv.PART.ITEMS:
        row = base_dsc.id1
        col = base_dsc.id2
        label_dsc = task.get_label_dsc()
        fill_dsc = task.get_fill_dsc()
        border_dsc = task.get_border_dsc()
        if border_dsc != None:
            border_dsc.width = 0
        if row != 0 and col == 0:
            if label_dsc != None:
                label_dsc.align = lv.TEXT_ALIGN.RIGHT
                label_dsc.color = theme.gray
            # if fill_dsc != None:
            #     fill_dsc.color = lv.palette_main(lv.PALETTE.GREY)

gcode.add_event_cb(gcode_draw_event_cb, lv.EVENT.DRAW_TASK_ADDED, None)
gcode.add_flag(lv.obj.FLAG.SEND_DRAW_TASK_EVENTS);

gcode.set_cell_value(0, 0, "GCode")
gcode.set_cell_value(0, 1, "Preview")

def onFileLines(first_line, lines, path):
    # gcode.set_text("")
    # gcode.add_cell_ctrl(0, 0, lv.table.CELL_CTRL.MERGE_RIGHT)
    gcode.set_cell_value(0, 0, "GCode")
    gcode.set_cell_value(0, 1, "Preview" if path == "" else ("from " + path))
    for i in range(len(lines)):
        # line = str(i+first_line) + " " + lines[i] + "\n"
        # gcode.add_text(line)
        gcode.set_cell_value(i+1, 0, str(i+first_line))
        gcode.set_cell_value(i+1, 1, lines[i])

# kbarea = make_area(screen, 10, 10, 780, 300, theme.bg)
# kb = lv.keyboard(kbarea)
# kb.set_size(780, 300)
# kb.set_pos(0, 0)
# kb.set_style_text_font(f24, 0)
# kb.set_textarea(messages)

np = Numpad(screen, make_button, f28)

screen.update_layout()

# 4. Displays the contents of the screen object
lv.screen_load(screen)

import fluidnc_json_parser

fluidnc_json_parser.filesListListener.setCallback(onFilesList)
fluidnc_json_parser.fileLinesListener.setCallback(onFileLines)
# fluidnc_json_parser.macroCfgListener.setCallback(onMacros)
# fluidnc_json_parser.macroCfgListener.setCallback(onMacros)
# fluidnc_json_parser.macroListListener.setCallback(onMacros)
# fluidnc_json_parser.initialListener.setCallback(onError)

def setRunControls():
    if loadedFile != None:
        # A GCode file is ready to go
        set_left_button(green, lv.SYMBOL.PLAY, runGCode)
        set_right_button(None, lv.SYMBOL.STOP, None)
    else:
        # Can't start because no GCode to run
        set_left_button(None, lv.SYMBOL.PLAY, None)
        set_right_button(None, lv.SYMBOL.STOP, None)

previous_state = 'Idle'
startTime = 0

class GrblCallback:
    def __init__(self):
        pass
    def update_state(self, state):
        canClick = True
        if has(state, 'stateName'):
            stateName = state['stateName']
            state_name.set_text(stateName)
            canClick = stateName not in ['Run', 'Hold']
            for dro in dros:
                dro.arm(canClick)
            # XXX Switch to run screen?
            if stateName == 'Sleep':
                set_left_button(None, '', None)
                set_right_button(red, 'Reset', stopAndRecover)
            elif stateName == 'Alarm':
                set_left_button(yellow, 'Unlock', unlock);
                set_right_button(red, 'Reset', stopAndRecover);
            elif stateName == 'Idle':
                setRunControls();
            elif stateName == 'Door1':
                set_left_button(None, '', None);
                set_right_button(red, 'Stop', stopAndRecover);
            elif stateName in ['Door0', 'Hold']:
                set_left_button(green, 'Resume', resumeGCode);
                set_right_button(red, 'Stop', stopAndRecover);
            elif stateName == 'Run':
                global previous_state, startTime
                if previous_state == 'Idle':
                    startTime = time.time()
                else:
                    elapsed = time.time() - startTime
                    minutes = int(elapsed//60)
                    seconds = int(elapsed%60)
                    runtime.set_text("{:d}:{:02d}".format(minutes, seconds))
                set_left_button(None, lv.SYMBOL.PLAY, None);
                set_right_button(red, lv.SYMBOL.PAUSE, pauseGCode);
            elif stateName == 'Home':
                set_left_button(None, lv.SYMBOL.PLAY, None);
                set_right_button(red, lv.SYMBOL.STOP, stopAndRecover);
            elif stateName in ['Jog', 'Home', 'Run']:
                set_left_button(None, lv.SYMBOL.PLAY, None);
                set_right_button(red, lv.SYMBOL.PAUSE, pauseGCode);
            elif stateName == 'Check':
                set_left_button(None, lv.SYMBOL.PLAY, None);
                set_right_button(red, lv.SYMBOL.STOP, stopAndRecover);
            previous_state = stateName

        # XXX account for grbl reporting units
        factor = 25.4 if in_inches() else 1.0

        if has(state, 'wco'):
            global wco
            wco = state['wco']
        if has(state, 'wpos'):
            for i in range(len(state['wpos'])):
                dros[i].set(str(state['wpos'][i]))
        if has(state, 'mpos'):
            for i in range(len(state['mpos'])):
                wpos = state['mpos'][i] - wco[i]
                try:
                    dros[i].set(str(wpos))
                except:
                    pass  # In case there are too many axes
        # if has(state, 'spindleSpeed'):
        #    spindle_speed.get_child(0).set_text('S' + str(state['spindleSpeed']))
        # message
        # feedrate
        # spindle
        # spindleSpeed
        # ovr
        # lineNumber
        # flood
        # mist
        # pins
    def update_modal(self, modal):
        if has(modal, 'distance'):
            obj = distance_mode.get_child(0)
            value = modal['distance']
            obj.set_text(value)
            obj.set_style_text_color(theme.fg if value == 'G90' else red, 0)
        if has(modal, 'units'):
            set_units(modal['units'])
        if has(modal, 'wcs'):
            set_wcs(modal['wcs'])

    def refresh_files(self):
        requestFileList()
        pass
    def handle_reset(self):
        print('Grbl Reset')
        pass
    def handle_error(self, msg):
        print("Grbl Error:", msg)
        pass
    def handle_ok(self):
        pass
    def probe_failed(self, msg):
        print("Grbl Probe Failed:", msg)
        pass
    def handle_json(self, msg):
        fluidnc_json_parser.parser.parse_line(msg)
        pass

grbl_callback = GrblCallback()

from grbl_parser import GrblParser

grbl = GrblParser(grbl_callback)

import task_handler
task_handler.TaskHandler()



fluidnc = FluidNC()
sendCommand('')  # Empty command to flush junk
sendRealtimeChar('\x11')  # XON to enable software flow control
sendRealtimeChar('\x0c')  # Ctrl-L to disable echoing
requestStatusReport()
requestFileList()

while True:
    if using_SDL:
        SDL.check()
    while fluidnc.ready():
        msg = fluidnc.get_line()
        if len(msg):
            if not grbl.handle_message(msg):
                add_message(msg)
    time.sleep_ms(1)

# while True:
#     if using_SDL:
#         import uselect
#         import poll
#         SDL.check()
#         if poll.poll_input(10):
#             grbl.handle_message(poll.get_line())
#     else:
#         msg = input()
#         if input == "quit":
#             break
#         grbl.handle_message(msg)
