
class DebuggerBreakpoint:
    def __init__(self):
        self.address = -1
        self.backup = ""
        self.condition = None
        self.handler = None

    def __repr__(self):
        return "Breakpoint at %08x -> %s"%(self.address, self.handler.__name__)

class DebuggerBreakpoints:
    def __init__(self):
        self.breakpoints = dict()

    def add(self, address):
        if not self.breakpoints.has_key(address):
            bp = DebuggerBreakpoint()
            bp.address = address
            self.breakpoints[address] = bp
            return bp
        else:
            return None

    def get_all(self):
        return self.breakpoints.values()

    def get(self, address):
        if self.breakpoints.has_key(address):
            return self.breakpoints.get(address)
        else:
            return None

    def remove(self, address):
        if self.breakpoints.has_key(address):
            return self.breakpoints.pop(address)
        else:
            return None

    def count(self):
        return len(self.breakpoints)
