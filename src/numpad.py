import lvgl as lv

class Numpad():
    def __init__(self, container, button_maker, font):
        self.font = font
        self.max_digits = 9
        self.make_button = button_maker
        overlay = lv.obj(container)
        overlay.set_pos(0, 0)
        overlay.set_size(container.get_width(), container.get_height())
        overlay.set_style_bg_opa(0, lv.PART.MAIN | lv.STATE.DEFAULT)
        overlay.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        self.overlay = overlay
        background = lv.obj(overlay)
        background.set_pos(100, 114)
        background.set_size(540, 330)
        background.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        background.set_style_bg_color(lv.color_hex(0xffc0c0), lv.PART.MAIN | lv.STATE.DEFAULT)
        cols = [100, 100, 100, 36, 110, lv.GRID_TEMPLATE.LAST]
        rows = [56, 0, 48, 48, 48, 48, lv.GRID_TEMPLATE.LAST]

        background.set_grid_dsc_array(cols, rows)
        self.background = background
        self.make_buttons()
        self.display = self.make_display(1, 0)
        self.axis_label = self.make_axis_label(3, 0)
        self.hide()

    def make_basic_button(self, text, col, row, color):
        obj = lv.obj(self.background)
        obj.set_grid_cell(lv.GRID_ALIGN.STRETCH, col, 1, lv.GRID_ALIGN.STRETCH, row, 1)
        obj.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)

        label = lv.label(obj)
        label.set_text(text)
        label.set_style_text_font(self.font, lv.PART.MAIN | lv.STATE.DEFAULT)
        label.center()
        label.set_style_text_color(color, 0)
        return obj

    def show(self):
        self.overlay.clear_flag(lv.obj.FLAG.HIDDEN)

    def hide(self):
        self.overlay.add_flag(lv.obj.FLAG.HIDDEN)

    def make_axis_label(self, col, row):
        obj = self.make_basic_button("", col, row, lv.color_black())
        obj.set_style_bg_opa(0, lv.PART.MAIN | lv.STATE.DEFAULT)
        obj.set_style_border_width(0, lv.PART.MAIN | lv.STATE.DEFAULT)
        return obj

    def button(self, text, col, row, color=lv.color_black()):
        self.make_basic_button(text, col, row, color).add_event_cb(self.button_action, lv.EVENT.ALL, None)

    def make_buttons(self):
        red = lv.palette_darken(lv.PALETTE.RED, 3)
        green = lv.palette_darken(lv.PALETTE.GREEN, 3)
        self.button("Goto", 0, 0, red)
        self.button("Set", 4, 0, red)

        self.button("1", 0, 2)
        self.button("2", 1, 2)
        self.button("3", 2, 2)
        self.button(lv.SYMBOL.BACKSPACE, 4, 2)

        self.button("4", 0, 3)
        self.button("5", 1, 3)
        self.button("6", 2, 3)
        self.button("Clear", 4, 3)

        self.button("7", 0, 4)
        self.button("8", 1, 4)
        self.button("9", 2, 4)
        self.button("Get", 4, 4, green)

        self.button("+-", 0, 5)
        self.button("0", 1, 5)
        self.button(".", 2, 5)
        self.button("Cancel", 4, 5, red)
        
    def button_action(self, e):
        if (e.get_code() != lv.EVENT.PRESSED):
            return
        obj=e.get_target() 
        label = obj.get_child(0)
        text = label.get_text()

        current = self.display.get_text()
        if text.isdigit():
            if len(current) < self.max_digits:
                if current == "0":
                    self.display.set_text(text)
                else:
                    self.display.set_text(current + text)
        elif text == ".":
            if "." not in self.display.get_text():
                self.display.set_text(current + ".")
        elif text == lv.SYMBOL.BACKSPACE:
            if len(self.display.get_text()) == 1:
                self.display.set_text("0")
            else:
                self.display.del_char()
                # self.display.set_text(current[0:-1])
        elif text == "C":
            self.display.set_text("0")
        elif text == "+-":
            if current[0] == "-":
                self.display.set_text(current[1:])
            else:
                self.display.set_text("-" + current)
        elif text == "Set":
            self.dro.set_wco(current)
            self.hide()
        elif text == "Goto":
            self.dro.goto(current)
            self.hide()
        elif text == "Get":
            self.display.set_text(self.dro.get())
        elif text == "Cancel":
            self.hide()

    def make_display(self, col, row):
        ta = lv.textarea(self.background)
        ta.set_text("0")
        ta.set_style_text_align(lv.TEXT_ALIGN.CENTER, lv.PART.MAIN | lv.STATE.DEFAULT)
        ta.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        ta.set_style_text_font(self.font, lv.PART.MAIN | lv.STATE.DEFAULT)
        ta.set_style_bg_color(lv.color_hex(0xe0e0ff), lv.PART.MAIN | lv.STATE.DEFAULT)
        ta.set_style_radius(5, lv.PART.MAIN | lv.STATE.DEFAULT)
        ta.set_style_border_width(3, lv.PART.MAIN | lv.STATE.DEFAULT)
        ta.set_style_border_color(lv.color_hex(0x0), lv.PART.MAIN | lv.STATE.DEFAULT)
        ta.set_grid_cell(lv.GRID_ALIGN.STRETCH, col, 2, lv.GRID_ALIGN.STRETCH, row, 1)
        return ta

    def attach(self, dro, max_digits=255):
        self.dro = dro
        self.axis_label.get_child(0).set_text(dro.axis)
        self.display.set_text("0")
        self.max_digits = max_digits
        self.show()
