class FluidNC():
    def __init__(self, reply):
        self.reply = reply

    def send(self, msg):
        print(msg)

    def sendRealtimeChar(self, code):
        print(hex(code))
        if code == 0x18:
            self.reply("Grbl 3.3 (FluidNC)")

