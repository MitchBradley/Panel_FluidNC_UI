# Communications interface between the CrowPanel and a FluidNC controller,
# using the CrowPanel's UART port. That port's pins are shared with
# the USB serial port which MicroPython always uses for its REPL via
# the ESP32's UART0 block.  It is not possible to disconnect UART0 from
# the REPL without modifying the MicroPython source code, so we use a
# trick.  We setup the UART1 block and assign to it the same Rx and Tx
# pins that are used for UART0, thus disconnecting them from UART0.  The
# UART0 block remains active and attached to the REPL, but it no longer
# receives input from the Rx pin nor sends output over the Tx pin.
# Debugging can still be done, though, by using the WebREPL over WiFi.

class FluidNC():
    def __init__(self, time_cb):
        from machine import UART
        self.line = ""
        self.pos = -1
        self.uart = UART(1, 1000000, rx=44, tx=43, flow=UART.XONXOFF)
        self._time_cb = time_cb
        print(self.uart)

    # Send a line-oriented command
    def send(self, msg):
        self.uart.write(msg)
        self.uart.write("\n")

    # Send a GRBL single-byte "real character"
    def sendRealtimeChar(self, c):
        self.uart.write(c)

    # Poll (non-blocking) for input, collecting it into a buffer.
    # Returns True when the buffer contains a complete line, otherwise False.
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
        self._time_cb()
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

    # Returns the first complete line from the input buffer and
    # removes it from the buffer.  Should be called only after
    # ready() has returned True.  The returned string does not
    # have a trailing newline character.
    def get_line(self):
        retline = self.line[:self.pos]
        self.line = self.line[self.pos+1:]
        self.pos = -1
        return retline
