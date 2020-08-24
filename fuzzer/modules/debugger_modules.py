class DebuggerModule:
    def __init__(self, baseAddress):
        self._modules = []
        self.base_address = baseAddress
        self.base_size = 0
        self.name = ""
        self.path = ""
        self.pid = 0
        self.handle = 0

    def __repr__(self):
        return "Module @%08x [%d] : %s"%(self.base_address, self.base_size, self.path)

class DebuggerModules:
    def __init__(self):
        self._modules = []

    def add(self, base_address):
        mod = DebuggerModule(base_address)
        self._modules.append(mod)
        return mod

    def remove(self, base_address):
        for mod in self._modules:
            if mod.base_address == base_address:
                return self._modules.remove(mod)

    def find_by_addr(self, address):
        for mod in self._modules:
            if mod.base_address >= address >= mod.base_size + mod.base_address:
                return mod
        return None

    def get_all(self):
        return self._modules
