import lvgl as lv

class Numpad():
    def __init__(self, container, button_maker, font):
        self.font = font
        self.max_digits = 9
        self.make_button = button_maker
        overlay = lv.obj(container)
        overlay.set_pos(0, 0)
        overlay.set_size(container.get_width(), container.get_height())
        overlay.set_style_bg_opa(0, 0)
        overlay.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        self.overlay = overlay
        background = lv.obj(overlay)
        background.set_pos(100, 114)
        background.set_size(600, 330)
        background.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        background.set_style_bg_color(lv.color_hex(0xffc0c0), 0)
        cols = [100, 100, 100, 100, 110, lv.GRID_TEMPLATE_LAST]
        rows = [56, 0, 48, 48, 48, 48, lv.GRID_TEMPLATE_LAST]

        background.set_grid_dsc_array(cols, rows)
        self.background = background
        self.make_buttons()
        self.display = self.make_display(1, 0)
        # self.axis_label = self.make_axis_label(3, 5)
        self.hide()

    def make_basic_button(self, text, col, row, color, cb=None):
        obj = lv.obj(self.background)
        obj.set_grid_cell(lv.GRID_ALIGN.STRETCH, col, 1, lv.GRID_ALIGN.STRETCH, row, 1)
        obj.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        if cb:
            obj.set_style_bg_color(lv.color_white(), 0)
            obj.add_event_cb(cb, lv.EVENT.CLICKED, None)
            obj.set_style_border_width(1, 0)
        else:
            obj.set_style_bg_opa(0, 0)
            obj.set_style_border_width(0, 0)

        label = lv.label(obj)
        label.set_text(text)
        label.set_style_text_font(self.font, 0)
        label.center()
        label.set_style_text_color(color, 0)
        return obj

    def show(self):
        self.overlay.remove_flag(lv.obj.FLAG.HIDDEN)

    def hide(self):
        self.overlay.add_flag(lv.obj.FLAG.HIDDEN)

    def make_axis_label(self, col, row):
        obj = self.make_basic_button("", col, row, lv.color_black())
        return obj

    def button(self, text, col, row, color=lv.color_black()):
        self.make_basic_button(text, col, row, color, self.button_action)

    def make_buttons(self):
        red = lv.palette_darken(lv.PALETTE.RED, 3)
        green = lv.palette_darken(lv.PALETTE.GREEN, 3)
        self.button("Goto", 0, 0, red)
        self.button(lv.SYMBOL.HOME, 3, 0, red)
        self.button("Set", 4, 0, red)

        self.button("1", 0, 2)
        self.button("2", 1, 2)
        self.button("3", 2, 2)
        self.button(lv.SYMBOL.BACKSPACE, 4, 2)

        self.button("4", 0, 3)
        self.button("5", 1, 3)
        self.button("6", 2, 3)
        self.button(lv.SYMBOL.LEFT, 3, 3)
        self.button("Clear", 4, 3)

        self.button("7", 0, 4)
        self.button("8", 1, 4)
        self.button("9", 2, 4)
        self.button(lv.SYMBOL.RIGHT, 3, 4)
        self.button("Get", 4, 4, green)

        self.button("+-", 0, 5)
        self.button("0", 1, 5)
        self.button(".", 2, 5)
        self.button("Cancel", 4, 5, red)
        
    def button_action(self, e):
        obj=e.get_target_obj() 
        label = obj.get_child(0)
        text = label.get_text()

        current = self.display.get_text()
        self.display.add_state(lv.STATE.FOCUSED) 
        print(self.display.get_cursor_pos())
        if text.isdigit():
            if len(current) < self.max_digits:
                # The check for cursor_pos == 1 handles the situation
                # where the user has moved the cursor to the left
                # of the zero (so cursor_pos == 0), where the likely
                # intent is to insert a digit before the 0
                if current == "0" and self.display.get_cursor_pos() == 1:
                    self.display.set_text(text)
                else:
                    self.display.add_text(text)
        elif text == ".":
            if "." not in self.display.get_text():
                self.display.add_text(text)
        elif text == lv.SYMBOL.BACKSPACE:
            if len(self.display.get_text()) == 1:
                self.display.set_text("0")
            else:
                self.display.del_char()
                # self.display.set_text(current[0:-1])
        elif text == lv.SYMBOL.LEFT:
            self.display.cursor_left()
        elif text == lv.SYMBOL.RIGHT:
            self.display.cursor_right()
        elif text == "Clear":
            self.display.set_text("0")
        elif text == "+-":
            if current[0] == "-":
                self.display.set_text(current[1:])
            else:
                self.display.set_text("-" + current)
        elif text == "Set":
            self.dro.set_wco(current)
            self.detach()
        elif text == "Goto":
            self.dro.goto(current)
            self.detach()
        elif text == "Get":
            self.display.set_text(self.dro.get())
        elif text == "Cancel":
            self.detach()
        elif text == lv.SYMBOL.HOME:
            self.dro.home()
            self.detach()

    def make_display(self, col, row):
        ta = lv.textarea(self.background)
        ta.set_text("0")
        ta.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
        ta.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        ta.set_style_text_font(self.font, 0)
        ta.set_style_text_color(lv.color_black(), 0)
        ta.set_style_bg_color(lv.color_hex(0xe0e0ff), 0)
        ta.set_style_radius(8, 0)
        ta.set_style_border_width(1, 0)
        ta.set_style_border_color(lv.color_hex(0x0), 0)
        ta.set_grid_cell(lv.GRID_ALIGN.STRETCH, col, 2, lv.GRID_ALIGN.STRETCH, row, 1)
        return ta

    def attach(self, dro, max_digits=255):
        self.dro = dro
        #self.axis_label.get_child(0).set_text(dro.axis)
        self.display.set_text("0")
        self.max_digits = max_digits
        self.display.add_state(lv.STATE.FOCUSED) 
        self.dro.highlight()
        self.show()
    def detach(self):
        self.dro.lowlight()
        self.hide()
