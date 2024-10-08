class POLL:
    def __init__(self, input_devs):
        self._in = input_devs
        self.line = ""
        self.pos = -1
    def ready(self, ms):
        if self.pos != -1:
            return True
        self.pos = self.line.find('\n')
        if self.pos != -1:
            return True
        n = self._in[0].any()
        if n == 0:
            return False
        by = self._in[0].read(n)
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
