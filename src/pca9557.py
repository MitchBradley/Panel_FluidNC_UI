"""Driver for PCA9557 I2C I/O Expander"""

REG_INP = 0
REG_OUT = 1   # Default: 0x00
REG_INV = 2   # Invert input pins. Defaults to 0xF0
REG_DIR = 3   # Direction: 1=In, 0=Out. Defaults to 0xFF


class PCA9557():
    """I2C I/O Expander Driver"""

    def __init__(self, i2c, address):
        self.i2c = i2c
        self.addr = address
        self.resultbuf = bytearray(1)
        self.cached_out = 0

    def read(self, reg):
        """Read 8-bit register"""
        self.i2c.writeto(self.addr, reg.to_bytes(1, 'big'))

        self.i2c.readfrom_into(self.addr, self.resultbuf)
        val = self.resultbuf[0]

        return val


    def write(self, reg, val):
        """Write 8-bit register"""
        cmd = bytes((reg, val))
        self.i2c.writeto(self.addr, cmd)


    def output(self, val):
        """Cached write to output port"""
        if val != self.cached_out:
            self.write(REG_OUT, val)
            self.cached_out = val

    def setDirection(self, val):
        """Set direction register"""
        self.write(REG_DIR, val)

    def setPolarity(self, val):
        """Set polarity register"""
        self.write(REG_INV, val)

    def setbits(self, mask, do_set):
        """Bitmask write to ouput port"""
        val = self.cached_out
        if do_set:
            val |= mask
        else:
            val &= ~mask

        self.output(val)
