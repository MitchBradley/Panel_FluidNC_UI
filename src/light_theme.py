import lvgl as lv

border_width = 1
radius = 8

red = lv.color_hex(0xff0000)
green = lv.color_hex(0x00ff00)
yellow = lv.color_hex(0xffff00)
gray = lv.palette_lighten(lv.PALETTE.GREY, 2)
darkgray = lv.palette_darken(lv.PALETTE.GREY, 1)
white = lv.color_white()
black = lv.color_black()

bg = white
fg = black
border_color = black
stripe_color = lv.palette_lighten(lv.PALETTE.GREY, 3)
jog_bg = lv.color_hex(0x80ff80)
messages_bg = lv.color_hex(0x2195f6)
zeroing_bg = lv.color_hex(0xc0ffc0)
files_bg = lv.color_hex(0xffa0a0)
jog_bg = lv.color_hex(0xc0ffc0)
dro_bg = lv.color_hex(0xffff80)
scrollbar_bg = lv.color_hex(0x00ff00)
checked_bg = lv.color_hex(0x00a1b5)
run_bg = lv.color_hex(0xc0c0ff)
disabled_bg = gray
run_disabled_bg = gray
numpad_bg = lv.color_hex(0xffc0c0)
highlight_bg = lv.color_hex(0xe0e0ff)
placeholder_fg = darkgray
