class FluidNC():
    def __init__(self):
        from machine import UART
        self.line = ""
        self.pos = -1
        self.uart = UART(1, 1000000, rx=44, tx=43, flow=4)
        print(self.uart)

    def send(self, msg):
        self.uart.write(msg)
        self.uart.write("\n")

    def sendRealtimeChar(self, c):
        self.uart.write(c)

    def ready(self):
        if self.pos != -1:
            return True
        self.pos = self.line.find('\n')
        if self.pos != -1:
            return True
        n = self.uart.any()
        if n == 0:
            return False
        by = self.uart.read(n)
        #print(type(by))
        #if type(by) == type(b'a'):
        #    print("Decoding")
        #    try:
        #        by = b.decode('ascii')
        #    except:
        #        print("Bad character in", by)
        for b in by:
            ch = chr(b)
            if ch == '\r':
                pass
            elif ch == '\n':
                if self.pos == -1:
                    self.pos = len(self.line)
                self.line += ch
            else:
                self.line += ch
        return self.pos != -1

    def get_line(self):
        retline = self.line[:self.pos]
        self.line = self.line[self.pos+1:]
        self.pos = -1
        return retline
