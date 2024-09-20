# Based on https://github.com/MitchBradley/json-streaming-parser.git
# which in turn was based on https://github.com/squix78/json-streaming-parser
# Converted to Python with the help of ChatGPT

class JsonStreamingParser:
    STATE_START_DOCUMENT = 0
    STATE_IN_STRING = 1
    STATE_IN_ARRAY = 2
    STATE_IN_OBJECT = 3
    STATE_END_KEY = 4
    STATE_AFTER_KEY = 5
    STATE_START_ESCAPE = 6
    STATE_UNICODE = 7
    STATE_UNICODE_SURROGATE = 8
    STATE_AFTER_VALUE = 9
    STATE_IN_NUMBER = 10
    STATE_IN_TRUE = 11
    STATE_IN_FALSE = 12
    STATE_IN_NULL = 13
    STATE_DONE = 14
    
    STACK_KEY = 0
    STACK_STRING = 1
    STACK_ARRAY = 2
    STACK_OBJECT = 3

    BUFFER_MAX_LENGTH = 1024

    def __init__(self):
        self.reset()

    def reset(self):
        self.state = self.STATE_START_DOCUMENT
        self.bufferPos = 0
        self.unicodeEscapeBufferPos = 0
        self.unicodeBufferPos = 0
        self.characterCounter = 0
        self.stackPos = 0
        # self.myListener = None
        self.buffer = [''] * self.BUFFER_MAX_LENGTH
        self.unicodeEscapeBuffer = [''] * 4
        self.unicodeBuffer = [''] * 4
        self.stack = [0] * 1024

    def setListener(self, listener):
        self.myListener = listener

    def parse_line(self, line):
        for c in line:
            self.parse(c)

    def parse(self, c):
        if (c in [' ', '\t', '\n', '\r'] and
                self.state not in [self.STATE_IN_STRING, self.STATE_UNICODE,
                                   self.STATE_START_ESCAPE, self.STATE_IN_NUMBER, self.STATE_START_DOCUMENT]):
            return

        if self.state == self.STATE_IN_STRING:
            if c == '"':
                self.endString()
            elif c == '\\':
                self.state = self.STATE_START_ESCAPE
            elif ord(c) < 0x1f or ord(c) == 0x7f:
                raise Exception(f"Unescaped control character encountered: {c} at position {self.characterCounter}")
            else:
                self.buffer[self.bufferPos] = c
                self.increaseBufferPointer()

        elif self.state == self.STATE_IN_ARRAY:
            if c == ']':
                self.endArray()
            else:
                self.startValue(c)

        elif self.state == self.STATE_IN_OBJECT:
            if c == '}':
                self.endObject()
            elif c == '"':
                self.startKey()

        elif self.state == self.STATE_END_KEY:
            if c != ':':
                raise Exception(f"Expected ':' after key. Instead got {c} at position {self.characterCounter}")
            self.state = self.STATE_AFTER_KEY

        elif self.state == self.STATE_AFTER_KEY:
            self.startValue(c)

        elif self.state == self.STATE_START_ESCAPE:
            self.processEscapeCharacters(c)

        elif self.state == self.STATE_UNICODE:
            self.processUnicodeCharacter(c)

        elif self.state == self.STATE_AFTER_VALUE:
            within = self.stack[self.stackPos - 1]
            if within == self.STACK_OBJECT:
                if c == '}':
                    self.endObject()
                elif c == ',':
                    self.state = self.STATE_IN_OBJECT
                else:
                    raise Exception(f"Expected ',' or '}}' while parsing object. Got: {c}.")
            elif within == self.STACK_ARRAY:
                if c == ']':
                    self.endArray()
                elif c == ',':
                    self.state = self.STATE_IN_ARRAY
                else:
                    raise Exception(f"Expected ',' or ']' while parsing array. Got: {c}.")
            else:
                raise Exception(f"Finished a literal, but unclear what state to move to. Last state: {self.characterCounter}")

        elif self.state == self.STATE_IN_NUMBER:
            if c.isdigit():
                self.buffer[self.bufferPos] = c
                self.increaseBufferPointer()
            elif c == '.':
                if '.' in self.buffer[:self.bufferPos]:
                    raise Exception("Cannot have multiple decimal points in a number.")
                self.buffer[self.bufferPos] = c
                self.increaseBufferPointer()
            elif c in ['e', 'E']:
                if 'e' in self.buffer[:self.bufferPos]:
                    raise Exception("Cannot have multiple exponents in a number.")
                self.buffer[self.bufferPos] = c
                self.increaseBufferPointer()
            elif c in ['+', '-']:
                last = self.buffer[self.bufferPos - 1]
                if last not in ['e', 'E']:
                    raise Exception(f"Can only have '+' or '-' after the 'e' or 'E' in a number.")
                self.buffer[self.bufferPos] = c
                self.increaseBufferPointer()
            else:
                self.endNumber()
                self.parse(c)

        elif self.state == self.STATE_IN_TRUE:
            self.buffer[self.bufferPos] = c
            self.increaseBufferPointer()
            if self.bufferPos == 4:
                self.endTrue()

        elif self.state == self.STATE_IN_FALSE:
            self.buffer[self.bufferPos] = c
            self.increaseBufferPointer()
            if self.bufferPos == 5:
                self.endFalse()

        elif self.state == self.STATE_IN_NULL:
            self.buffer[self.bufferPos] = c
            self.increaseBufferPointer()
            if self.bufferPos == 4:
                self.endNull()

        elif self.state == self.STATE_START_DOCUMENT:
            self.myListener.startDocument()
            if c == '[':
                self.startArray()
            elif c == '{':
                self.startObject()
            elif c == ' ':
                pass
            else:
                raise Exception("Document must start with object or array.")
        self.characterCounter += 1

    def increaseBufferPointer(self):
        self.bufferPos = min(self.bufferPos + 1, self.BUFFER_MAX_LENGTH)

    def endString(self):
        popped = self.stack[self.stackPos - 1]
        self.stackPos -= 1
        if popped == self.STACK_KEY:
            self.buffer[self.bufferPos] = '\0'
            key = ''.join(self.buffer[:self.bufferPos])
            self.myListener.key(key)
            self.state = self.STATE_END_KEY
        elif popped == self.STACK_STRING:
            self.buffer[self.bufferPos] = '\0'
            value = ''.join(self.buffer[:self.bufferPos])
            self.myListener.value(value)
            self.state = self.STATE_AFTER_VALUE
        self.bufferPos = 0

    def startValue(self, c):
        if c == '[':
            self.startArray()
        elif c == '{':
            self.startObject()
        elif c == '"':
            self.startString()
        elif self.isDigit(c):
            self.startNumber(c)
        elif c == 't':
            self.state = self.STATE_IN_TRUE
            self.buffer[self.bufferPos] = c
            self.increaseBufferPointer()
        elif c == 'f':
            self.state = self.STATE_IN_FALSE
            self.buffer[self.bufferPos] = c
            self.increaseBufferPointer()
        elif c == 'n':
            self.state = self.STATE_IN_NULL
            self.buffer[self.bufferPos] = c
            self.increaseBufferPointer()

    def isDigit(self, c):
        return c.isdigit() or c == '-'

    def endArray(self):
        popped = self.stack[self.stackPos - 1]
        self.stackPos -= 1
        if popped != self.STACK_ARRAY:
            raise Exception("Unexpected end of array encountered.")
        self.myListener.endArray()
        self.state = self.STATE_AFTER_VALUE
        if self.stackPos == 0:
            self.endDocument()

    def startKey(self):
        self.stack[self.stackPos] = self.STACK_KEY
        self.stackPos += 1
        self.state = self.STATE_IN_STRING

    def endObject(self):
        popped = self.stack[self.stackPos - 1]
        self.stackPos -= 1
        if popped != self.STACK_OBJECT:
            raise Exception("Unexpected end of object encountered.")
        self.myListener.endObject()
        self.state = self.STATE_AFTER_VALUE
        if self.stackPos == 0:
            self.endDocument()

    def processEscapeCharacters(self, c):
        escape_chars = {
            '"': '"', '\\': '\\', '/': '/', 'b': '\b',
            'f': '\f', 'n': '\n', 'r': '\r', 't': '\t'
        }
        if c in escape_chars:
            self.buffer[self.bufferPos] = escape_chars[c]
            self.increaseBufferPointer()
        elif c == 'u':
            self.state = self.STATE_UNICODE
        else:
            raise Exception(f"Expected escaped character after backslash. Got: {c}")
        if self.state != self.STATE_UNICODE:
            self.state = self.STATE_IN_STRING

    def processUnicodeCharacter(self, c):
        if not self.isHexCharacter(c):
            raise Exception(f"Expected hex character for escaped Unicode character. Got: {c}")
        self.unicodeBuffer[self.unicodeBufferPos] = c
        self.unicodeBufferPos += 1
        if self.unicodeBufferPos == 4:
            codepoint = self.getHexArrayAsDecimal(self.unicodeBuffer, self.unicodeBufferPos)
            self.endUnicodeCharacter(codepoint)

    def isHexCharacter(self, c):
        return c.isdigit() or 'a' <= c <= 'f' or 'A' <= c <= 'F'

    def getHexArrayAsDecimal(self, hexArray, length):
        result = 0
        for i in range(length):
            current = hexArray[length - i - 1]
            if current.isdigit():
                result += (16 ** i) * int(current)
            else:
                current = current.lower()
                result += (16 ** i) * (ord(current) - ord('a') + 10)
        return result

    def endUnicodeCharacter(self, codepoint):
        self.unicodeBufferPos = 0
        if 0xd800 <= codepoint <= 0xdbff:
            self.highSurrogate = codepoint
            self.state = self.STATE_UNICODE_SURROGATE
        elif 0xdc00 <= codepoint <= 0xdfff:
            raise Exception("Missing high surrogate character")
        else:
            self.unicodeChar = chr(codepoint)
            self.insertUnicharIntoBuffer()

    def insertUnicharIntoBuffer(self):
        self.buffer[self.bufferPos] = self.unicodeChar
        self.increaseBufferPointer()
        self.state = self.STATE_IN_STRING

    def startArray(self):
        self.stack[self.stackPos] = self.STACK_ARRAY
        self.stackPos += 1
        self.myListener.startArray()
        self.state = self.STATE_IN_ARRAY

    def startObject(self):
        self.stack[self.stackPos] = self.STACK_OBJECT
        self.stackPos += 1
        self.myListener.startObject()
        self.state = self.STATE_IN_OBJECT

    def startString(self):
        self.stack[self.stackPos] = self.STACK_STRING
        self.stackPos += 1
        self.state = self.STATE_IN_STRING

    def startNumber(self, c):
        self.state = self.STATE_IN_NUMBER
        self.buffer[self.bufferPos] = c
        self.increaseBufferPointer()

    def endNumber(self):
        self.buffer[self.bufferPos] = '\0'
        self.myListener.value(float(''.join(self.buffer[:self.bufferPos])))
        self.bufferPos = 0
        self.state = self.STATE_AFTER_VALUE

    def endTrue(self):
        if ''.join(self.buffer[:self.bufferPos]) == "true":
            self.myListener.value(True)
        else:
            raise Exception("Invalid true literal found")
        self.state = self.STATE_AFTER_VALUE
        self.bufferPos = 0

    def endFalse(self):
        if ''.join(self.buffer[:self.bufferPos]) == "false":
            self.myListener.value(False)
        else:
            raise Exception("Invalid false literal found")
        self.state = self.STATE_AFTER_VALUE
        self.bufferPos = 0

    def endNull(self):
        if ''.join(self.buffer[:self.bufferPos]) == "null":
            self.myListener.value(None)
        else:
            raise Exception("Invalid null literal found")
        self.state = self.STATE_AFTER_VALUE
        self.bufferPos = 0

    def endDocument(self):
        self.myListener.endDocument()
        self.state = self.STATE_DONE
        self.reset()
