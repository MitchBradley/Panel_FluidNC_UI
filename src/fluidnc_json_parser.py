from json_streaming_parser import JsonStreamingParser
parser = JsonStreamingParser()

reading_macros = False
macro_parser = None

def initListener():
    parser.setListener(initialListener)

def fileinfoSortKey(file):
    # If the file is a directory, prepend a DEL (0x7f) character
    # to the name as the sort key, so it will collate after
    # ordinary file names.  Tricky!
    if file[1] == -1:
        return '\x7f' + file[0]
    return file[0]

class FilesListListener:
    def __init__(self):
        self.haveNewFile = False
        self.currentKey = ""
        self.fileVector = []
        self.name = ""
        self.size = 0

    def setCallback(self, cb):
        self.callback = cb
        pass

    def whitespace(self, c):
        pass

    def startDocument(self):
        pass

    def startArray(self):
        self.fileVector.clear()
        self.haveNewFile = False

    def startObject(self):
        pass

    def key(self, _key):
        self.currentKey = _key
        if _key == "name":
            self.haveNewFile = True

    def value(self, value):
        if self.currentKey == "name":
            self.name = value
        elif self.currentKey == "size":
            self.size = int(value)

    def endArray(self):
        self.fileVector.sort(key=fileinfoSortKey)
        self.callback(self.fileVector)
        parser.setListener(initialListener)

    def endObject(self):
        if self.haveNewFile:
            self.fileVector.append((self.name, self.size))
            self.haveNewFile = False

    def endDocument(self):
        # Assuming DEBUG_FILE_LIST is set somewhere to control debugging output
        if 'DEBUG_FILE_LIST' in globals():
            for ix, vi in enumerate(self.fileVector):
                dbgPrintf(f"[{ix}] type: {'dir' if vi.isDir() else 'file'}:\"{vi.fileName}\", size: {vi.fileSize}\r\n")

        initListener()

filesListListener = FilesListListener()

macros = []

class MacroListListener():
    def __init__(self):
        self.valuep = None
        self.name = ""
        self.filename = ""
        self.target = ""

    def setCallback(self, cb):
        self.callback = cb
        pass

    def whitespace(self, c):
        pass

    def startDocument(self):
        pass

    def startArray(self):
        macros.clear()

    def startObject(self):
        self.name = ""
        self.target = ""
        self.filename = ""

    def key(self, _key):
        if _key == "name":
            self.valuep = self.name
        elif _key == "filename":
            self.valuep = self.filename
        elif _key == "target":
            self.valuep = self.target
        else:
            self.valuep = None

    def value(self, value):
        if self.valuep is not None:
            self.valuep = value

    def endArray(self):
        pass

    def endObject(self):
        if self.target == "ESP":
            self.filename = "/localfs" + self.filename
        elif self.target == "SD":
            self.filename = "/sd" + self.filename
        else:
            return
        macros.append((self.name, self.filename))

    def endDocument(self):
        self.callback(macros)
        initListener()

macroListListener = MacroListListener()

class MacrocfgListener:
    def __init__(self):
        self.valuep = None
        self.name = ""
        self.filename = ""
        self.target = ""
        self.level = 0

    def whitespace(self, c):
        pass

    def startDocument(self):
        pass

    def startArray(self):
        macro_menu.remove_all_items()

    def startObject(self):
        self.level += 1
        if self.level == 2:
            self.name = ""
            self.target = ""
            self.filename = ""

    def key(self, _key):
        if _key == "name":
            self.valuep = "name"
        elif _key == "filename":
            self.valuep = "filename"
        elif _key == "target":
            self.valuep = "target"
        else:
            self.valuep = None

    def value(self, value):
        if self.valuep == "name":
            self.name = value
        elif self.valuep == "filename":
            self.filename = value
        elif self.valuep == "target":
            self.target = value

    def endArray(self):
        self.callback(macros)
        parser.setListener(initialListener)

    def endObject(self):
        self.level -= 1
        if self.level == 1:
            if self.target == "ESP":
                self.filename = "/localfs" + self.filename
            elif self.target == "SD":
                self.filename = "/sd" + self.filename
            else:
                return
            macros.append((self.name, self.filename))

    def endDocument(self):
        pass

macrocfgListener = MacrocfgListener()

class PreferencesListener:
    def __init__(self):
        self.valuep = None
        self.name = ""
        self.filename = ""
        self.target = ""
        self._key = ""
        self.level = 0
        self.in_macros_section = False

    def whitespace(self, c):
        pass

    def startDocument(self):
        pass

    def startArray(self):
        if self.in_macros_section:
            macro_menu.remove_all_items()

    def endArray(self):
        if self.in_macros_section:
            self.in_macros_section = False
            onMacrosList()

    def startObject(self):
        self.level += 1

    def key(self, _key):
        self.currentKey = _key
        if self.level < 2:
            return
        if self.level == 2 and _key == "macros":
            self.in_macros_section = True
            return
        if self.in_macros_section:
            if _key == "action":
                self.valuep = "filename"
            elif _key == "type":
                self.valuep = "target"
            elif _key == "name":
                self.valuep = "name"
            else:
                self.valuep = None

    def value(self, value):
        if self.valuep == "name":
            self.name = value
        elif self.valuep == "filename":
            self.filename = value
        elif self.valuep == "target":
            self.target = value

    def endObject(self):
        self.level -= 1
        if self.in_macros_section:
            if self.target == "FS":
                self.filename = "/localfs/" + self.filename
            elif self.target == "SD":
                self.filename = "/sd/" + self.filename
            elif self.target == "CMD":
                self.filename = "cmd:" + self.filename
            else:
                return
            macro_menu.add_item(MacroItem(self.name, self.filename))
        if self.level == 0:
            parser.setListener(initialListener)

    def endDocument(self):
        pass

preferencesListener = PreferencesListener()

class FileLinesListener:
    def __init__(self):
        self.inArray = False
        self._key = ""
        self.lines = []
        self.first_line = 0
        self.path = ""

    def setCallback(self, cb):
        self.callback = cb

    def whitespace(self, c):
        pass

    def startDocument(self):
        pass

    def startArray(self):
        global reading_macros, macro_parser
        if reading_macros:
            reading_macros = False
            macro_parser = JsonStreamingParser()
            macro_parser.setListener(macroLinesListener)
            return
        self.lines.clear()
        self.inArray = True

    def endArray(self):
        self.inArray = False
        global macro_parser
        if macro_parser != None:
            del macro_parser
            macro_parser = None
            parser.setListener(initialListener)

    def startObject(self):
        pass

    def key(self, _key):
        self._key = _key

    def value(self, value):
        global macro_parser
        if macro_parser != None:
            macro_parser.parse_line(value)
            return
        if self.inArray:
            self.lines.append(value)
        if self._key == "firstline":
            self.first_line = int(value)
        elif self._key == "path":
            self.path = value
        self._key = ""

    def endObject(self):
        parser.setListener(initialListener)
        self.callback(self.first_line, self.lines, self.path)

    def endDocument(self):
        pass

fileLinesListener = FileLinesListener()

def is_file(string, filename):
    s = string.find(filename)
    return s != -1 and len(string[s:]) == len(filename)

class InitialListener:
    def __init__(self):
        self.currentKey = None
        self.cmd = ""
        self.argument = ""
        self.status = "ok"
        self.isJsonFile = False
        self.fileListener = None

    def setCallback(self, cb):
        self.callback = cb

    def whitespace(self, c):
        pass

    def startDocument(self):
        self.currentKey = None
        self.isJsonFile = False
        self.status = "ok"

    def value(self, value):
        if self.currentKey == "path":
            global reading_macros
            reading_macros = is_file(value, "macrocfg.json")
        elif self.currentKey == "cmd":
            self.cmd = value
            if value == "$File/SendJSON":
                self.isJsonFile = True
        elif self.currentKey == "argument":
            self.argument = value
            if self.isJsonFile:
                self.isJsonFile = False
                if is_file(value, "macrocfg.json"):
                    self.fileListener = macrocfgListener
                elif is_file(value, "preferences.json"):
                    self.fileListener = preferencesListener
                else:
                    self.fileListener = None
        elif self.currentKey == "status":
            self.status = value
        elif self.currentKey == "error":
            self.callback(self.currentKey, value)
        self.currentKey = None

    def endArray(self):
        pass

    def endObject(self):
        pass

    def endDocument(self):
        if self.status != "ok" and self.fileListener:
            self.status = "ok"
            try_next_macro_file(self.fileListener)

    def startArray(self):
        pass

    def startObject(self):
        pass

    def key(self, _key):
        if _key == "files":
            parser.setListener(filesListListener)
        elif _key == "file_lines":
            parser.setListener(fileLinesListener)
        elif _key == "result" and self.fileListener:
            parser.setListener(self.fileListener)
        else:
            self.currentKey = _key

initialListener = InitialListener()

initListener()
