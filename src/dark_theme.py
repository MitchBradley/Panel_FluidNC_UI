import lvgl as lv

border_width = 1
radius = 8

red = lv.color_hex(0xff0000)
green = lv.color_hex(0x00ff00)
yellow = lv.color_hex(0xffff00)
gray = lv.palette_main(lv.PALETTE.GREY)
darkgray = lv.palette_darken(lv.PALETTE.GREY, 1)
lightgray = lv.palette_lighten(lv.PALETTE.GREY, 3)
white = lv.color_white()
black = lv.color_black()

bg = black
fg = white
border_color = darkgray
stripe_color = lv.palette_darken(lv.PALETTE.GREY, 3)
jog_bg = lv.color_hex(0x203f20)
messages_bg = lv.color_hex(0x2195f6)
zeroing_bg = lv.color_hex(0xc0ffc0)
files_bg = lv.color_hex(0xffa0a0)
jog_bg = lv.color_hex(0x7f4040)
dro_bg = lv.color_hex(0x407f40)
scrollbar_bg = lv.color_hex(0xc0ffc0)
checked_bg = lv.color_hex(0x00a1b5)
run_bg = lv.color_hex(0x40407f)
disabled_bg = darkgray
run_disabled_bg = darkgray
numpad_bg = lv.color_hex(0x7f4040)
highlight_bg = lv.color_hex(0x40407f)
placeholder_fg = gray
