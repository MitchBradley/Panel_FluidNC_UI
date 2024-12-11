# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
from machine import reset
def bye():
    reset()
import web.wifi
# from gui import *
