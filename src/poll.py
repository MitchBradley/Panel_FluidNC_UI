import sys
import uselect

poller=uselect.poll()        # Set up an input polling object.
poller.register(sys.stdin,uselect.POLLIN)    # Register polling object.

line = ""

def poll_input(ms):
    global line
    if poller.poll(ms):
        ch = sys.stdin.read(1)
        if ch == '\x0c':
            poller.unregister(sys.stdin)
            sys.exit(0)
        elif ch == '\x08':
            if len(line):
                line=line[:-1]
        elif ch == '\n':
            return True
        else:
            line += ch
    return False

def get_line():
    global line
    ret = line
    line = ""
    return ret
