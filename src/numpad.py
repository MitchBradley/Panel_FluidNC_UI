import lvgl as lv

class Numpad():
    def __init__(self, container, button_maker, font):
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
        self.background = background
        self.make_buttons(0, -10)
        self.display = self.make_display(140, -10, 200, 60, font)
        self.hide()

    def show(self):
        self.overlay.clear_flag(lv.obj.FLAG.HIDDEN)

    def hide(self):
        self.overlay.add_flag(lv.obj.FLAG.HIDDEN)

    def skip(self):
        self.x += 116

    def next_row(self, yinc=56):
        self.x = self.button_x
        self.y += yinc

    def buttonator(self, text):
        self.make_button(text, self.background, self.x, self.y, 110, 46, 28, lambda e: self.button_action(e))
        self.skip()

    def make_buttons(self, x, y):
        self.button_x = x
        self.x = self.button_x
        self.y = y
        extra_x = 36

        self.buttonator("Goto")
        self.skip()
        self.skip()
        self.x += extra_x
        self.buttonator("Set")
        self.next_row(80)

        self.buttonator("1")
        self.buttonator("2")
        self.buttonator("3")
        self.x += extra_x
        self.buttonator(lv.SYMBOL.BACKSPACE)
        self.next_row()

        self.buttonator("4")
        self.buttonator("5")
        self.buttonator("6")
        self.x += extra_x
        self.buttonator("C")
        self.next_row()

        self.buttonator("7")
        self.buttonator("8")
        self.buttonator("9")
        self.x += extra_x
        self.buttonator("Get")
        self.next_row()

        self.buttonator("+-")
        self.buttonator("0")
        self.buttonator(".")
        self.x += extra_x
        self.buttonator("Cancel")
        
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

    def make_display(self, x, y, w, h, font):
        ta = lv.textarea(self.background)
        ta.set_text("0")
        # ta.set_max_length(10)
        # ta.set_one_line(True)
        # ta.set_width(180)
        ta.set_size(w, h)
        # ta.set_pos((800-180)//2, 131)
        #ta.set_pos((600 -180)//2, 0)
        ta.set_pos(x, y)
        # ta.set_size(180,50)
        ta.set_style_text_align(lv.TEXT_ALIGN.CENTER, lv.PART.MAIN | lv.STATE.DEFAULT)
        ta.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        ta.set_style_text_font(font, lv.PART.MAIN | lv.STATE.DEFAULT)
        ta.set_style_bg_color(lv.color_hex(0xe0e0ff), lv.PART.MAIN | lv.STATE.DEFAULT)
        ta.set_style_radius(5, lv.PART.MAIN | lv.STATE.DEFAULT)
        ta.set_style_border_width(3, lv.PART.MAIN | lv.STATE.DEFAULT)
        ta.set_style_border_color(lv.color_hex(0x0), lv.PART.MAIN | lv.STATE.DEFAULT)
        return ta

    def attach(self, dro, max_digits=255):
        self.dro = dro
        self.display.set_text("0")
        self.max_digits = max_digits
        self.show()
