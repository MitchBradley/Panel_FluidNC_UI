from credentials import *
import network
import time
sta_if = network.WLAN(network.STA_IF)
if not sta_if.isconnected():
    sta_if.active(True)
    sta_if.connect(ssid, password)
    while not sta_if.isconnected():
        time.sleep_ms(200)
print(sta_if.ifconfig()[0])
import webrepl
webrepl.start()
