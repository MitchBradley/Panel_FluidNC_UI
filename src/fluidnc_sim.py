import sys
import uselect

class FluidNC():
    def __init__(self):
        self._in = sys.stdin
        self.poller = uselect.poll()
        self.poller.register(self._in, uselect.POLLIN)
        self.line = ""

    def send(self, msg):
        print(msg)

    def sendRealtimeChar(self, code):
        print(hex(code))

    def ready(self):
        if self.poller.poll(0):
            ch = self._in.read(1)
            if ch == '\x0c':
                self.poller.unregister(self._in)
                # sys.exit(0)
            elif ch == '\x08':
                if len(line):
                    line=line[:-1]
            elif ch == '\n':
                return True
            elif ch == '\r':
                pass
            else:
                line += ch
        return False
    def get_line(self):
        ret = self.line
        self.line = ""
        return ret
     
